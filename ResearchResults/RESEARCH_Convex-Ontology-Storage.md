# Convex as storage for immutable Ontology releases

**Research date:** 2026-07-26
**Scope:** Current first-party Convex documentation, supplemented only for the Vercel service-identity boundary by first-party Vercel documentation. The findings are applied by [ADR-0009](../docs/adr/0009-store-immutable-ontology-releases-in-convex.md).

## Decision in brief

**Implement Corvus's immutable Ontology-release store in Convex, with no PostgreSQL or pgvector baseline.** The design must move relational constraints, publication validation, and read-only enforcement into the repository compiler plus privileged Convex internal mutations. Convex is capable of this within a deliberately bounded release and traversal envelope; its documented limits become hard release gates, not conditions to hand-wave away.

Convex has useful strengths: declared schemas produce TypeScript types and runtime validation; queries and mutations are consistent transactions; its deployment model cleanly separates production, developer, and preview data; it offers vector indexes, export/import, backups, and Vercel integration. [Schemas](https://docs.convex.dev/database/schemas), [Overview and transaction guarantees](https://docs.convex.dev/understanding/overview), [Multiple deployments](https://docs.convex.dev/production/multiple-deployments), [Vector search](https://docs.convex.dev/search/vector-search), [Backup & restore](https://docs.convex.dev/database/backup-restore), [Vercel](https://docs.convex.dev/production/hosting/vercel)

The decisive constraint is that the required retrieval primitive—**release-pinned, bounded multi-hop graph traversal with policy-class joins and stable evidence provenance**—must be deliberately implemented, rather than delegated to SQL. Convex documents no query language for joins, aggregation, or group-by; joins are application-level loops over a table/index lookup and `db.get`. It consequently has no recursive-query primitive. [Reading data](https://docs.convex.dev/database/reading-data/) Each traversal must use indexed, release-prefixed adjacency reads, explicit visited-set/depth/fan-out budgets, and a bounded TypeScript BFS/DFS under the 1-second query/mutation user-code limit and transaction ceilings. [Limits](https://docs.convex.dev/production/state/limits)

Its vector facility cannot provide an atomic candidate-to-admitted-evidence path: vector search runs **only in an action**, returns just IDs and scores, and action calls to a query/mutation are separate transactions. Convex explicitly warns that a selected document can change or disappear before the subsequent load, and says additional transactional queries/mutations cannot be performed from the vector result. [Vector search](https://docs.convex.dev/search/vector-search) Corvus therefore treats it as a quarantined discovery phase, then reloads and revalidates candidates in a release-pinned internal query before they can influence retrieval.

## Required change from the historical storage proposal

The prior planning draft selected PostgreSQL/pgvector. The Vercel + Convex decision replaces it with a **single Convex production ontology database** (including Convex vector indexes), with no PostgreSQL, pgvector, hosted graph database, or separate vector database.

| ADR-0009 property | Required Convex design | Guarantee location |
| --- | --- | --- |
| One managed PostgreSQL database and pgvector | Convex document database plus Convex vector indexes | Convex schema/index declarations and release-scoped documents. |
| Explicit relational policy tables and constraints | Separate Convex tables with literal-tagged validators and indexes | Schema validators for local shape; compiler and privileged mutations for cross-document invariants. |
| Atomic stage/validate/digest/publish transaction | Chunked internal staging, compiler validation, then one small internal activation mutation | Staging validity is compiler/mutation-owned; only active-pointer change is atomic. |
| Read-only production DB role | No public writes; internal mutation-only publisher; least-privilege deploy key | Function-surface and CI/IAM boundary. |
| Release-pinned recursive SQL traversal | TypeScript BFS/DFS across indexed relation documents | `TraversalSpec` budgets and internal query implementation. |
| pgvector nearest-neighbour candidates joined to release policy | Action-only Convex vector search, then release-pinned internal reload | Discovery quarantine and revalidation. |
| PostgreSQL migrations/real DB integration tests | Schema deployment validation and Convex migrations component plus `convex-test`/local backend | Convex migration/runbook and real-backend acceptance suite. |

This is a material supersession, not a minor implementation detail: it changes the enforcement model, publication protocol, traversal implementation, and operational threat model. The remainder of this report is the required Convex design.

## Requirement-by-requirement assessment

### 1. Immutable Ontology releases and activation

Convex mutations are transactional and queries are consistent; writes in a failed mutation roll back. This is enough for a small activation record such as `{ activeReleaseId, digest }`. [Overview and transaction guarantees](https://docs.convex.dev/understanding/overview) Store every ontology document with `releaseId`, never patch/delete documents of a published release, and let one short internal mutation move a validated release from `staged` to `published` and update the singleton active-release pointer.

It is **not** enough to safely load, cross-validate, digest, and publish an entire release in one transaction. A query/mutation may read or write at most 16 MiB, scan at most 32,000 documents, read at most 4,096 index ranges, and write at most 16,000 documents; query/mutation user code has a 1-second execution limit. [Limits](https://docs.convex.dev/production/state/limits) Chunked ingestion needs a resumable, internal importer and durable counters/checkpoints. The final activation can be atomic only after a separate validation phase proves the staged release complete.

That protocol protects runtime readers but is more implementation-heavy than a single relational publication transaction. It must additionally defend against a partially loaded release becoming queryable: every runtime query must require `release.state === "published"`, and no caller may accept a raw release document ID.

### 2. Corpus registry and immutable Corpus snapshots

Treat the repository manifest and compiler as the admission authority, exactly as ADR-0009 requires. Convex should store only a release-local, content-digested **snapshot descriptor**: snapshot ID/digest, source artifact identity, edition, recognizing-body and authority scope, permitted operations, locator rules, rights decision, compiler/provenance version, and counts. The source text itself remains out of the runtime store unless the compiled rights decision permits that exact durable use.

Convex documents have a 1 MiB maximum size, 1,024 fields, nesting depth 16, and arrays up to 8,192 elements. [Limits](https://docs.convex.dev/production/state/limits) Thus a snapshot must be normalized into source/edition/membership documents rather than one manifest-shaped document or a source-text blob. This is compatible with the corpus model, but adds application-managed referential integrity and makes snapshot-wide validation a batch job.

### 3. Typed policy-class records

Convex schemas support object validators, unions, literal discriminants, document IDs, generated TypeScript types, and runtime validation for schema-covered tables. A schema can represent a discriminated `structural_relation`, `interpretive_assertion`, `discovery_candidate`, and `ontology_embedding` rather than returning to a generic edge table. Existing documents are checked when a modified schema is deployed, and deployment fails if they do not conform. [Schemas](https://docs.convex.dev/database/schemas)

However, this is **document shape validation**, not a relational constraint layer. Convex's own schema documentation explains that required circular IDs cannot be inserted in one step; one reference must be nullable and later patched. [Schemas](https://docs.convex.dev/database/schemas) More broadly, no documented foreign-key, composite-unique, or check constraint mechanism replaces release-scoped keys such as `(releaseId, stableEntityId)` and policy-class cross-table assertions. Required invariants are therefore enforced in privileged mutation code and compiler validation, and every future write path must pass the same gate.

Required Convex safeguards:

- Keep literal policy tags and separate tables, never `v.any()` for policy records.
- Denormalize only query keys and immutable source/snapshot identity needed for a safe result; keep canonical provenance in the record.
- Centralize writes in `internalMutation`s that call pure validation helpers; do not expose a public bulk import/publish mutation.
- Have a release validator scan paginated, bounded sets and write a signed/digested validation result; activation checks it.

This is the required data-plane pattern under the Convex decision. Its safeguards must be tested as release gates, rather than assumed from document validation alone.

### 4. Constrained graph traversal

Convex can model adjacency as a `relations` table with index prefixes such as `(releaseId, fromEntityId, relationType)` and `(releaseId, toEntityId, relationType)`. Index range expressions work from an ordered prefix of equality predicates and optional range bounds, and indexed `take(n)` is the essential guard against scanning a full table. [Indexes](https://docs.convex.dev/database/reading-data/indexes/)

Traversal itself must happen in TypeScript: for each frontier entity, query a release-prefixed adjacency index, cap each edge read, update a visited set, then continue until a hard depth/node/edge/result budget is reached. Convex says complex joins are JavaScript logic; its example joins a relation table by index then does parallel document `get`s. [Reading data](https://docs.convex.dev/database/reading-data/) This makes the following non-negotiable:

- `TraversalSpec` must include `releaseId`, allowed node/relation types, direction, max depth, max frontier, max visited nodes, max edges read, and a deterministic sort/tie-breaker.
- Indexes must put `releaseId` first; otherwise every query risks cross-release scanning.
- Never use an unbounded `.collect()` or post-query `.filter()` for a release traversal. A filter does not reduce scanned documents. [Indexes](https://docs.convex.dev/database/reading-data/indexes/)
- A runtime query must return a bounded evidence-ready projection, not raw graph documents or arbitrary client query controls.

The Convex implementation therefore owns these responsibilities in one internal `traverse` query: it rejects over-budget requests before reads, processes only indexed release-prefixed adjacency pages, and returns a structured `budgetExhausted` result rather than continuing or broadening. This design is valid only while the measured graph envelope stays within the hard gates below.

### 5. Vector candidate discovery

Convex vector search is a credible **discovery-only** index. It has one vector field, 2–4,096 dimensions, up to 16 configured filter fields, maximum four vector indexes per table (and 32 indexes total), up to 64 filter expressions, and returns at most 256 IDs ordered by approximate cosine-similarity relevance. The index is fully up to date: a newly written vector is immediately searchable. [Vector search](https://docs.convex.dev/search/vector-search)

For Corvus, index only embeddings whose snapshot rights decision explicitly permits durable derived indexing. Put `releaseId`, `policyClass`, and perhaps `corpusSnapshotId` in the vector filter fields, query with those equality constraints, and label every returned score as operational ranking only. The vector result must not become an `interpretive_assertion`, evidence source, authority measure, sufficiency decision, or user-facing confidence.

The material caveat is consistency composition. Vector search is available only from an action; actions are outside the transactional sync engine. A subsequent `runQuery`/`runMutation` is separate, and Convex warns that matching records may have been mutated/deleted in between. [Vector search](https://docs.convex.dev/search/vector-search), [Actions](https://docs.convex.dev/functions/actions) Since releases are immutable after activation, this race can be made harmless **only** if the action filters to a published release and the loader rechecks the release and each candidate's immutable `releaseId` and policy. Still, it cannot serve as an atomic evidence read.

### 6. Read-only production behavior and publication authority

Convex has no PostgreSQL-style application database role that restricts a particular production runtime credential to `SELECT`. The boundary is exported functions and deployment credentials. Public functions are client callable; internal functions cannot be called directly by a Convex client, though Convex still recommends validation/authentication for their invariants. [Internal functions](https://docs.convex.dev/functions/internal-functions)

Production exposes only narrow authenticated read queries. All corpus ingestion, validation, release publishing, activation, and rollback are internal functions invoked by a separately authorized CI/release process. Vercel's production `CONVEX_DEPLOY_KEY` has only `deployment:deploy` permission; do not grant it data/env/admin powers absent a separate reviewed release workflow. Convex deploy-key permissions are configurable in deployment settings, and the Vercel guide specifically calls for `deployment:deploy`. [Deployment settings](https://docs.convex.dev/dashboard/deployments/deployment-settings), [Vercel](https://docs.convex.dev/production/hosting/vercel)

This achieves application immutability through the function and identity boundary rather than a database read-only role. Keep the offline compiler/release tool authoritative and use a separate, audited release identity.

### 7. Production, staging, development, and preview isolation

Convex's deployment topology is strong. A project normally has one shared production deployment and each developer has a personal dev deployment. It can also create a staging deployment or an isolated deployment per coding agent. Preview deployments are temporary per-branch deployments; documentation says they are automatically cleaned up after five days (14 days on Professional, Business, and Enterprise). [Multiple deployments](https://docs.convex.dev/production/multiple-deployments)

Convex documents a Vercel integration in which production builds use a Production deploy key and `npx convex deploy --cmd 'npm run build'`, while Preview keys create or reuse branch-named backends. Corvus must not use that combined build flow for privileged production deployment because Vercel environment variables are also available to Function runtime. Deploy Convex functions from separate CI and pass only the non-secret matching deployment URL to Vercel. [Convex on Vercel](https://docs.convex.dev/production/hosting/vercel), [Vercel environment variables](https://vercel.com/docs/environment-variables)

Corvus uses separate production and staging Convex projects/deployments. PR previews use the deterministic fixture store by default. Convex preview deployments remain optional while beta; if enabled, create them fresh, seed only synthetic fixtures, verify no prior data was reused, record automatic expiry, and explicitly clean them up. Never seed a preview with rights-restricted production corpus data. [Multiple deployments](https://docs.convex.dev/production/multiple-deployments), [Import](https://docs.convex.dev/database/import-export/import)

### 8. Authentication: Vercel, browser, and Convex

`CONVEX_DEPLOY_KEY` authenticates the **build/deploy pipeline**, not an end user or a Vercel request. Keep it only in the corresponding CI environment, never in Vercel, and scope its deployment permissions minimally. [Deployment settings](https://docs.convex.dev/dashboard/deployments/deployment-settings)

Enable Vercel OIDC in team-issuer mode. A Vercel Function receives a short-lived RSA-signed token at request time, and the token subject includes the owner, project, and environment. Configure Convex custom-JWT verification for the exact Vercel issuer and audience, then have every exported read function check `ctx.auth.getUserIdentity()` and require the approved project/environment subject. [Vercel OIDC reference](https://vercel.com/docs/oidc/reference), [Convex custom JWT](https://docs.convex.dev/auth/advanced/custom-jwt), [Convex auth best practices](https://docs.convex.dev/understanding/best-practices)

Corvus's MCP host is server-side and the product promises provider credentials never enter tool results. Do not use browser Convex access as an alternate privileged ontology plane. The Vercel/MCP server authenticates anonymous ChatGPT calls at the Apps/MCP boundary, then uses its Vercel deployment identity only for narrow Convex reads. The Convex deploy key, release-publisher identity, and Gloo/YouVersion credentials are distinct authorities and never enter runtime results.

### 9. Schema evolution and data migrations

Convex schema changes deploy with `npx convex dev`/`deploy`; the first deployment validates existing documents and fails if they do not match, while later inserts/updates are validated. [Schemas](https://docs.convex.dev/database/schemas) This means a breaking schema change cannot be safely “just deployed” over old release documents. The database docs point to the Convex migrations component for resumable online migrations with dry-run validation. [Writing data](https://docs.convex.dev/database/writing-data)

For immutable releases, prefer **expand-and-publish** rather than mutating old records:

1. Add an optional/additive schema field and reader support.
2. Compile a new ontology/corpus release with the new `schemaVersion`; do not rewrite old published releases.
3. Validate new release documents and dual-read only where an explicit compatibility window is necessary.
4. Activate the new release pointer atomically; retain the prior readable release for rollback.
5. Remove an old field/reader only after all retained releases/export policies no longer require it.

This is consistent with immutable provenance, but Convex's schema is deployment-wide, not release-scoped. It requires a documented reader-compatibility matrix and makes dropping validators/fields more delicate than a PostgreSQL versioned-reader approach.

### 10. Backups, export, restore, region, and hard limits

Convex backups are consistent snapshots of table data (optionally file storage). Manual backups live seven days; scheduled daily backups live seven days and weekly backups 14 days, with periodic backup requiring Pro. Restore is destructive: it replaces existing data, and backup data omits code, configuration, pending scheduled functions, and environment variables. [Backup & restore](https://docs.convex.dev/database/backup-restore) Export produces a ZIP; a streaming export is also available through the Data Sync API/integrations. [Export](https://docs.convex.dev/database/import-export/export)

Import is currently documented as beta. ZIP import preserves `_id` and `_creationTime`; imports can atomically create/replace tables except `--append`. [Import](https://docs.convex.dev/database/import-export/import) A backup plus repository revision, release artifacts/digests, deployed function configuration, and secret-management record are therefore all needed for disaster recovery—backup alone does not reconstruct a release environment.

Choose a Convex region when creating the deployment. Current docs list US East (N. Virginia) and EU West (Ireland); a deployed region cannot be changed, and region migration requires a new project/deployment plus CLI export/import. [Regions](https://docs.convex.dev/production/regions) Place Vercel/server compute and downstream providers with latency/data-residency needs in mind.

Operationally relevant published limits include: 1 MiB/document; 16 MiB reads and writes/transaction; 32,000 scanned documents; 4,096 index ranges; 16,000 documents written; 1-second query/mutation user-code execution; and current serverless query concurrency starting at 16 (S16) or 256 (S256), depending on class. [Limits](https://docs.convex.dev/production/state/limits) These reinforce why all corpus compilation, embedding, and broad validation must be offline/chunked, not synchronous ontology reads.

## Concrete Convex publication and runtime protocol

### Tables and indexes

Use distinct tables, all requiring `releaseId` and immutable `contentDigest` fields:

- `ontologyReleases`: semantic version, ontology/corpus digests, schema/compiler version, state (`staging | validated | published | retired`), expected/actual counts, validation digest, timestamps.
- `activeOntology`: exactly one document holding the active published `releaseId` and immutable pin fields. It is modified only by `internal.activateRelease` and `internal.rollbackRelease`.
- `entities`, `structuralRelations`, `interpretiveAssertions`, `discoveryCandidates`, `embeddings`, `corpusSnapshots`, and `corpusMemberships`: one policy class per table, never a generic nodes/edges table.
- `publicationJobs` and `publicationChunks`: resumable, internal-only staging/checkpoint records; they contain no user questions or Answer evidence packages.

Every retrieval table gets a `by_release_*` index whose first field is `releaseId`: entity stable identity; structural relation source/destination/type; interpretive assertion source/destination/tradition/source ID; discovery origin; and embedding source identity. The vector-index table declares `releaseId`, `policyClass`, and `corpusSnapshotId` as filter fields. This turns the required policy/release filter into an index operation, consistent with Convex's ordered index ranges and vector filter rules. [Indexes](https://docs.convex.dev/database/reading-data/indexes/), [Vector search](https://docs.convex.dev/search/vector-search)

### Publication and activation

1. The repository compiler validates the manifest, source/rights/locator fields, policy-class rules, canonical serialization, duplicate stable keys, referential graph closure, embedding authorization/provenance, and expected counts; it emits chunked immutable JSONL artifacts plus a root digest.
2. A CI-only `internal.stageChunk` mutation writes one size-accounted chunk at a time, rejects an existing stable key for the same release, and records count/checkpoint/digest information. The compiler chooses chunks below a conservative 8 MiB write/read budget and below 8,000 documents, but the release gate also exercises the real schema/index transaction because vector and secondary-index work counts toward Convex's ceilings. [Limits](https://docs.convex.dev/production/state/limits)
3. One short `internal.sealRelease` mutation verifies the exact expected chunk set, digests, and counts, then makes the staged release write-closed. Every staging mutation rejects sealed releases.
4. A resumable `internal.validateRelease` action pages across only sealed documents and invokes bounded internal queries/mutations to compare counts, recompute the Merkle/root digest, validate all referenced release-local IDs and snapshot membership, verify no source class leaks into `discoveryCandidates`, and mark the release `validated`. It must never mutate release content.
5. `internal.activateRelease` is a single short mutation: verify the validation record/root digest and compare-and-set version, require exactly one active-pointer record under a fixed logical key, change the target release to `published`, and replace that pointer. The mutation's atomicity gives readers either the old or new active pin, never an intermediate pointer. [Overview and transaction guarantees](https://docs.convex.dev/understanding/overview)
6. Rollback performs the same singleton, compare-and-set, target-state, and validation-digest checks before pointing `activeOntology` to a previously validated/published release. It never overwrites release documents. Retire/prune only after the retention policy and backup/export gate have passed.

No ordinary public function can call steps 2–6. CI's deploy key is scoped only to deploy functions. A separate release HTTP action accepts only a short-lived, signed CI publisher JWT with a distinct issuer/audience, verifies it, then invokes the internal staging/publish functions; it is not included in the browser/MCP API. Convex team roles restrict production data writes, internal-function execution, backup import/restore, and environment management to the release authority and an audited break-glass administrator. All other production-facing operations are authenticated reads. This is the Convex replacement for a database read-only application role. [Convex role actions](https://docs.convex.dev/team-management/role-actions)

### Read path and Vercel-to-Convex trust

A separate CI job uses an environment-scoped `CONVEX_DEPLOY_KEY` solely to deploy functions. The key is not placed in Vercel configuration because Vercel environment values are available to both build and Function runtime. Production and nonproduction keys are separate and deployment-scoped. [Convex on Vercel](https://docs.convex.dev/production/hosting/vercel), [Vercel environment variables](https://vercel.com/docs/environment-variables)

At runtime, the Vercel/MCP server validates the caller at the MCP/application boundary, obtains its short-lived Vercel OIDC token, exchanges it for a Convex-specific audience, and supplies it to the narrow server-side Convex read client. Convex pins the Vercel team issuer and exact audience; each exported read also requires the exact project/environment subject. Production and staging use separate Vercel and Convex project pairs instead of relying on undocumented custom-environment token claims. [Vercel OIDC reference](https://vercel.com/docs/oidc/reference), [Vercel custom audiences](https://vercel.com/changelog/custom-oidc-token-audiences), [Custom JWT](https://docs.convex.dev/auth/advanced/custom-jwt), [Best practices](https://docs.convex.dev/understanding/best-practices) Vercel never receives corpus-publisher authority, and no browser client receives a Convex credential, provider credential, or raw storage query interface.

Each read first resolves the active `ReleasePin` in one query and passes that pin into every remaining store call. For graph reads, `internal.traverse` does bounded release-prefixed adjacency iteration. For vector discovery, an action runs `ctx.vectorSearch` with release/policy/snapshot filters, then calls a single internal query that rechecks the pin, policy class, and rights/provenance before returning candidate projections. Discovery candidates cannot cross into admitted assertions without the offline compiler/publication path.

## Hard release gates and reconsideration benchmark

The CI release must fail—not degrade—when any of these gates fails:

| Gate | Required proof |
| --- | --- |
| Artifact integrity | Compiler root digest, per-chunk digest, expected counts, and canonical manifest/Cursor snapshot digest match exactly. |
| Policy integrity | No generic edge table; every record validates its discriminant; all interpretive assertions have admitted source, locator, edition, tradition/authority scope, snapshot membership, and rights decision; every embedding has approved derived-index use. |
| Referential integrity | Full staged scan finds no dangling release-local entity/source/snapshot references and no duplicate release-scoped stable keys. |
| Publication atomicity | Failure injection before activation leaves the previous active pin and all its reads unchanged; activation test observes only old or new pin. |
| Traversal budget | Worst-case fixture and real-backend benchmark remain below 500 ms user-code, 8 MiB reads, 16,000 scanned documents, 2,000 index ranges, and configured node/edge/depth limits—conservative margins under Convex ceilings. |
| Vector quarantine | Every vector request supplies release/policy/snapshot filters; post-search reload rejects stale, missing, unpublished, rights-blocked, or non-candidate records; scores never serialize as evidence attributes. |
| Isolation and secrets | Separate-project tests prove production and staging URLs, functions, data, configuration, and OIDC subjects are distinct; previews are fixture-only; no production corpus/provider/publisher secret appears outside production; the production deploy key exists only in CI with no broader permission than approved. |
| Recovery | A scheduled restore rehearsal imports a downloaded backup into a non-production deployment, verifies release digests/active pointer/read fixtures, and reconstructs code/config/env from version control and secret management. |

The architecture must be reconsidered—not silently expanded—if any production-like benchmark needs a traversal above the conservative gate for representative questions; hits Convex's 1-second function user-code, transaction scan/read/write limits, or action/query consistency workaround; needs more than 256 vector candidates or filters beyond the documented vector model; cannot publish/validate in a bounded resumable window; or misses the agreed p95 retrieval latency, availability, RPO, or restore-time objectives for two consecutive measured releases. The first response is to tighten ontology projections, indexes, corpus scope, or traversal contract. If the evidence still fails, open an explicit storage-architecture decision; do not add a shadow PostgreSQL/vector store opportunistically.

## Recommended deep storage interface

Keep ADR-0009's storage seam and hide the chosen engine. The Investigation module should depend on a minimal **read-oriented** TypeScript interface, with a separate offline release writer. No MCP tool or frontend receives raw SQL, Convex table names, vector scores as evidence, or arbitrary graph query controls.

```ts
type ReleasePin = Readonly<{
  ontologyVersion: string;
  ontologyDigest: string;
  corpusSnapshotId: string;
  corpusDigest: string;
}>;

type TraversalSpec = Readonly<{
  start: EntityReference[];
  relationTypes: readonly RelationType[];
  directions: "out" | "in" | "both";
  maxDepth: number;
  maxNodes: number;
  maxEdges: number;
  allowedPolicyClasses: readonly ["structural", "interpretive"];
}>;

interface OntologyReadStore {
  resolvePublishedRelease(selector: ReleaseSelector): Promise<ReleasePin | null>;
  resolveEntities(pin: ReleasePin, refs: readonly EntityReference[]): Promise<ResolvedEntity[]>;
  traverse(pin: ReleasePin, spec: TraversalSpec): Promise<BoundedTraversal>;
  listAdmittedAssertions(
    pin: ReleasePin,
    request: AdmittedAssertionRequest,
  ): Promise<readonly AdmittedInterpretiveAssertion[]>;
  discoverCandidates(
    pin: ReleasePin,
    request: CandidateDiscoveryRequest,
  ): Promise<readonly DiscoveryCandidateHit[]>;
}

interface OntologyReleasePublisher {
  stage(compiled: CompiledOntologyRelease): Promise<StagedRelease>;
  validate(stage: StagedRelease): Promise<ReleaseValidation>;
  publish(stage: StagedRelease, validation: ReleaseValidation): Promise<ReleasePin>;
  activate(pin: ReleasePin): Promise<void>;
}
```

Contract rules:

- Every read accepts a verified `ReleasePin`; never infer “latest” in a lower-level traversal.
- `traverse` owns all limits, cycle handling, policy filtering, ordering, and cancellation. It returns an explicit truncation/budget reason rather than silently widening/partial-scanning.
- `listAdmittedAssertions` returns only Corpus-snapshot-admitted, source/locator-complete interpretive records. `discoverCandidates` is a separate return type and never feeds evidence serialization directly.
- The publisher is an offline compiler plus Convex internal CI-only functions, not an application API.
- A deterministic fixture implementation satisfies the same interface for package-policy tests; Convex local-backend and isolated-deployment tests exercise the real schema, indexes, limits, vector behavior, and publication protocol.

This is a deep module: the caller gets five high-level operations, whereas Convex tables/indexes, bounded graph iteration, provenance joins, migration details, and release mechanics remain hidden.

## Test strategy

1. **Compiler/policy unit tests:** pure fixtures reject any prohibited class mixing, missing source/locator/rights/snapshot identity, embedding without explicit durable-use permission, digest/count mismatch, or release mutation.
2. **Read-store contract suite:** run the same fixture cases against the in-memory deterministic store, `convex-test`, and the real local Convex backend. Include bounded cycles, fan-out, relation allow-lists, release isolation, deterministic order, cancellation/timeout, source-scope filtering, and discovery quarantine.
3. **Convex integration tests:** test schema validation, compiler-enforced uniqueness/integrity, publication visibility, release-prefixed indexes, vector release filter/reload, rollback by pointer, schema-version reader compatibility, import/export, and restore.
4. **Release pipeline tests:** stage malformed/boundary-size corpus releases, assert no activation; inject failure before activation and prove prior release still serves; checksum exported artifacts and exercise a documented restore rehearsal.
5. **Deployment/security tests:** prove production and staging project isolation; prove previews are fixture-only and any optional Convex preview is fresh, non-reused, expiry-recorded, and cleaned up; production runtime has no deploy or publisher credential; Vercel OIDC tests cover expiry and wrong issuer, audience, project, and environment; assert logs exclude question text, answers, credentials, and exact evidence content.

If Convex is used for an ancillary control plane, its official test path is `convex-test` with Vitest for fast function tests, plus tests against the open-source local backend for production-like limits and large imports. The docs warn the mock does not enforce limits and has simplified vector semantics, so it is not adequate as the only vector/publication test. [Testing](https://docs.convex.dev/testing/overview), [convex-test](https://docs.convex.dev/testing/convex-test), [Local backend](https://docs.convex.dev/testing/convex-backend)

## Material gaps that require a decision before implementation

1. **Authoritative choice:** replace ADR-0009 with the Convex-only storage decision, including the explicit statement that Convex vector indexes are the only vector index and that no PostgreSQL/pgvector store is introduced.
2. **Release ownership:** specify who/what holds the offline publication credential, the approval gate for activation, and whether activation is a CI deployment, a signed artifact promotion, or a human-controlled operation.
3. **Rollback/retention:** define how many releases and Corpus snapshots remain queryable, whether active-release rollback is configuration-only, and backup/export retention beyond Convex's short default windows.
4. **Scale envelope:** supply anticipated entities, structural and interpretive edges, embeddings/dimensions, corpus artifacts, QPS, latency SLO, maximum traversal depth/fan-out, and regional/data-residency requirements. Without these, Convex class/limit viability is not proven.
5. **Exact policy schemas:** define the concrete entity/relation discriminants and required source/authority/rights fields. A schema validator or SQL constraint cannot supply an undecided domain policy.
6. **Embedding authorization:** enumerate which artifacts allow durable embeddings, embedding model/version, transformation fingerprint, deletion/revocation behavior, and re-embedding plan. This remains required whichever database is selected.
7. **Service-identity spike:** prove Vercel OIDC token acquisition at Function runtime, Convex custom-JWT validation, exact subject enforcement, token expiry/refresh, local fixture composition, and zero token leakage before building the live store. The Vercel deploy key is not runtime authorization.
8. **Disaster recovery objective:** set RPO/RTO, backup cadence/location/encryption, restore-rehearsal schedule, and the required artifact/configuration inventory. Convex logical backups omit deployed code/config/env, so the runbook must restore these separately from source control and secret management.

## Bottom line

Convex is the selected one-store runtime for Corvus: typed, release-scoped documents; release-prefixed indexes; internal-query traversal; and Convex vector discovery. Its missing relational/recursive primitives are deliberately compensated for by the compiler, privileged mutation-only publication, fixed traversal budgets, release rechecks after vector lookup, and the hard gates below. The Investigation module exposes only the small storage interface above.
