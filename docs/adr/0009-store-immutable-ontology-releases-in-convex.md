# ADR-0009: Store immutable Ontology releases in Convex

- Status: accepted
- Date: 2026-07-26

## Context

The Investigation module needs identity resolution, bounded graph traversal, source-scoped retrieval, and vector-assisted discovery across a Bible-sized dataset. ADR 0008 requires deterministic structure, source-attributed interpretation, and algorithmic Discovery candidates to remain distinct policy classes. ADRs 0003 and 0004 keep the repository manifest and compiler authoritative for Corpus admission, authority scope, provenance, and rights.

Corvus uses Vercel and Convex. The historical build spec's PostgreSQL/pgvector design is not part of the selected product stack. Convex provides typed schemas, consistent queries and mutations, vector indexes, isolated deployments, backups, and first-party Vercel integration, but it does not provide relational foreign keys, recursive SQL, or vector search inside a query transaction. Those differences must be represented in the architecture rather than hidden.

The runtime retains no conversations or Answer evidence packages and does not persist YouVersion display text. Storage must support deterministic fixtures, immutable release provenance, rollback, rights revocation, and bounded production behavior.

## Decision

Use Convex as the only production application database and vector index. Do not add PostgreSQL, pgvector, Neo4j, a separate hosted vector database, an independent search cluster, or a second application database unless a later benchmark-driven ADR supersedes this decision.

Keep Convex behind a small `OntologyReadStore` interface owned by the Investigation module. MCP tools and the Evidence component never receive Convex table names, document IDs, arbitrary graph-query controls, or vector scores presented as evidence.

### Immutable release model

Compile the Bible ontology and Corpus registry into immutable, content-digested releases. Every persisted ontology, provenance, and Corpus-membership document belongs to exactly one `releaseId`. A published release is never patched or deleted by an application path; corrections produce a new semantic version and digest.

Use separate tables with literal discriminants and schema validators:

- `ontologyReleases`: semantic version, root digest, schema/compiler version, state (`staging | sealed | validated | published | retired`), expected and actual counts, validation digest, and publication metadata;
- `activeOntology`: exactly one record under the fixed logical key `active`, containing the active `ReleasePin` and compare-and-set version;
- `entities`;
- `structuralRelations`;
- `interpretiveAssertions`;
- `discoveryCandidates`;
- `embeddings`;
- `corpusSnapshots` and `corpusMemberships`; and
- internal-only `publicationJobs` and `publicationChunks`.

Do not recreate the historical generic `nodes` and `edges` design. Every retrieval index begins with `releaseId`, followed by the concrete lookup keys. Vector indexes declare `releaseId`, policy class, and Corpus snapshot identity as filter fields.

Convex validators enforce document shape. The repository compiler and privileged publication functions enforce cross-document invariants that a relational database would otherwise enforce: release-scoped stable-key uniqueness, referential closure, policy-class compatibility, exact source and locator identity, authority scope, rights decisions, Corpus membership, and embedding provenance.

### Publication protocol

Publication is an offline administrative workflow, never an MCP operation:

1. The repository compiler validates the source manifest and policy rules, produces canonical chunked artifacts, computes per-chunk digests and one root digest, and records expected counts.
2. A resumable CI-only internal mutation stages idempotent chunks. The compiler keeps each candidate chunk below 8 MiB and 8,000 writes, but actual `stageChunk` transactions must also pass local-backend and isolated-deployment tests with the real vector and secondary indexes because index work counts toward Convex's transaction limits.
3. One short `sealRelease` mutation verifies the complete expected chunk set, per-chunk digests, counts, and root digest, then changes `staging` to `sealed`. Every staging mutation rejects a sealed release. Validation never reads a mutable staging set.
4. A resumable internal validation action scans only the sealed release through bounded internal queries. It verifies counts, digests, stable-key uniqueness, referential closure, Corpus membership, policy separation, rights, and embedding provenance, then records an immutable validation result and changes `sealed` to `validated`.
5. One short internal mutation verifies that result and the current active compare-and-set version, marks the release published, and atomically replaces the sole `activeOntology` record with its complete `ReleasePin`. It fails unless the fixed logical key resolves to exactly one record.
6. Rollback performs the same singleton, compare-and-set, target-state, and validation-digest checks before atomically selecting a previously validated published pin. It never edits release documents.

Runtime reads accept a complete verified `ReleasePin`; lower-level reads never infer `latest`. Every Answer evidence package and Operation receipt records the ontology and Corpus versions and digests it actually used. Replay either resolves the recorded retained release or returns an explicit expiration/release-unavailable result.

Only the release publisher can stage, seal, validate, publish, retire, or prune releases. The Vercel runtime has no publisher credential. Convex team roles restrict production data-write, internal-function execution, backup import/restore, and environment-management permissions to the release authority and an audited break-glass administrator; ordinary developers and deploy automation cannot edit production data in the dashboard. Retirement stops new reference issuance for that release. Retention and backup gates must pass before pruning, and a retired release remains addressable for at least seven days plus five minutes so every Citation or Replay reference that could have been emitted before retirement has expired.

### Read path and trust boundary

The Vercel MCP runtime is the only production caller of the ontology read surface. The browser and Evidence component never connect to Convex directly.

Enable Vercel OIDC with team-issuer mode. The Vercel Function obtains its short-lived Vercel-issued token at request time, exchanges it for a Convex-specific audience, and supplies that token to the Convex client. Convex custom-JWT configuration pins the Vercel team issuer and that exact audience; every exported read function additionally requires the exact approved Vercel project and documented environment encoded in the token subject. Production and staging use separate Vercel projects and separate Convex projects/deployments, so their identities do not depend on an undocumented custom-environment claim. No long-lived database secret is introduced.

`CONVEX_DEPLOY_KEY` is CI-only deployment authority. Scope production and nonproduction keys to their matching projects/deployments and the minimum deploy permission; do not store them in Vercel environment variables because those values are also available to Functions at runtime. Never expose a deploy key, publisher credential, provider secret, or privileged query surface to a component or client bundle.

All externally reachable Convex functions validate their complete arguments, authenticate the Vercel service identity, apply release and work budgets, and return evidence-ready projections. Publication functions remain internal or behind a separately authenticated CI-only release endpoint with a distinct short-lived publisher identity.

The live Convex adapter is not approved for implementation until the Vercel-to-Convex trust spike in [Implementation readiness](../implementation-readiness.md) passes every positive and negative case in an isolated deployment. Before that gate, product slices use only the deterministic fixture store. A failed spike does not authorize anonymous Convex reads, a standing runtime database secret, or a second store.

### Bounded traversal

Implement graph traversal as a single release-pinned Convex query using release-prefixed adjacency indexes and explicit TypeScript cycle handling. `TraversalSpec` owns the allowed entity and relation types, direction, maximum depth, frontier, visited nodes, edges read, index ranges, result count, and deterministic ordering.

The production gate is stricter than Convex's platform ceilings: representative worst-case traversal must remain below 500 ms of function user code, 8 MiB read volume, 16,000 scanned documents, and 2,000 index ranges, with the full data and request envelope pinned in [Implementation readiness](../implementation-readiness.md). Never use unbounded `collect`, post-query filtering over a table scan, cross-release lookup, or a client-provided raw query plan. Budget exhaustion returns a typed truncation or Evidence gap; it never silently broadens, loops, or returns an arbitrary partial graph.

### Vector discovery

Use Convex vector search only for Discovery candidates whose exact source artifact permits durable derived indexing. Each embedding records the release, Corpus snapshot, source artifact, transformation fingerprint, embedding model and version, dimensions, and rights decision.

Vector search runs in an action and is not transactionally composed with the subsequent query. The action therefore filters by release, policy class, and Corpus snapshot, then calls one internal query that rechecks the active pin and reloads every result from the immutable published release. Missing, stale, unpublished, rights-blocked, or wrong-class records are rejected. Similarity and ranking scores remain operational metadata; they never become evidence authority, sufficiency, an Answer outcome, or a user-visible theological confidence.

### Rights and content

Store source identities, locators, provenance, Corpus membership, and rights decisions. Store source text, excerpts, transformations, or embeddings only when the exact Corpus snapshot authorizes that durable use. Public availability is not permission.

Do not persist YouVersion display text, raw Gloo exchanges, user questions, answers, inferred beliefs, pastoral context, or Replay payloads. Request-time Scripture hydration expires with the investigation. Gloo deployment identifiers are deployment mappings, not evidence identities.

### Environments, tests, and recovery

Use separate Convex production and staging projects/deployments plus personal developer deployments. Production contains only published, rights-admitted releases. Staging exercises production-shaped releases and separately scoped provider credentials. PR previews use the deterministic fixture store by default and receive no production Corpus, provider, signing, or publisher secrets. Convex preview deployments are optional while the feature is beta; if enabled, each is freshly created, fixture-seeded, expiry-recorded, verified not to reuse prior data, and explicitly cleaned up without serving as durable staging.

Run one storage contract suite against the deterministic in-memory fixture store, `convex-test`, and the open-source local Convex backend. The real-backend suite covers schema validation, release-prefixed indexes, transaction limits, traversal budgets, vector filtering and reload, publication failure injection, activation visibility, rollback, import/export, and restore. `convex-test` alone is insufficient because it does not enforce all production limits and simplifies vector behavior. No live-store implementation ticket closes until these suites are wired into the repository checks required by [Implementation readiness](../implementation-readiness.md).

Create a Convex backup and a portable export after every production release, subject to artifact rights. Preserve the compiler inputs, canonical artifacts, digests, repository revision, deployed function version, configuration inventory, and secret-recovery procedure outside the deployment. A restore drill into nonproduction must verify release digests, exactly one active pointer under the fixed logical key, compare-and-set version, and the full read contract before production submission and after material storage changes.

### Reconsideration trigger

Do not introduce a shadow store opportunistically. Open a new storage ADR only if production-like benchmarks for representative required questions repeatedly demonstrate that the bounded model cannot meet an agreed retrieval latency or availability objective; hits Convex's query, scan, read, index-range, vector-result, or consistency limits; or cannot complete publication, backup, or restore inside the agreed operational objectives after indexes, projections, and traversal contracts have been tightened.

## Rejected alternatives

- Retain PostgreSQL/pgvector because the historical build spec proposed it.
- Add Convex as a control plane while keeping a second ontology database.
- Preserve generic nodes and edges with loosely interpreted JSON metadata.
- Let the UI or MCP caller send arbitrary Convex query controls.
- Expose public mutation or release-publication functions.
- Treat an active-release pointer as permission to omit complete release pins from reads and receipts.
- Treat vector results or similarity scores as admitted evidence.
- Generate embeddings from material without affirmative durable-derived-use rights.
- Use `convex-test` as the only storage test environment.

## Consequences

Corvus uses the owner's actual managed stack: one typed Convex data plane and vector facility behind one deep read interface. Immutable releases, atomic activation, isolated deployments, and a compiler-owned publication pipeline preserve reproducibility and rollback without a second database.

Convex's missing relational and recursive primitives become explicit engineering work. Cross-document integrity lives in compiler and publisher validation; traversal lives in tightly budgeted indexed TypeScript; vector discovery requires a second release-pinned validation read; application-level read-only behavior is enforced by function surfaces and service identity rather than a database role. These are mandatory implementation and release-test obligations.
