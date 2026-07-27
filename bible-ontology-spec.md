# Bible ontology implementation brief

Status: current implementation authority.

This brief defines the stable role of the Bible ontology inside Corvus. Detailed
product behavior belongs to the Theological assistant specification, exact
runtime envelopes belong to Implementation readiness, and architectural choices
belong to the accepted ADRs. Historical PostgreSQL, generic graph, eight-tool,
FastAPI, and Render designs remain available in Git history but are not
implementation inputs.

## Authority

Read these records together, in this order:

1. `AGENTS.md` and `CONTEXT.md` for repository rules and canonical language;
2. `docs/theological-assistant-spec.md` for product behavior and testing seams;
3. ADRs 0005 through 0013 for evidence, module, runtime, ontology, storage,
   provider, rights, and deployment decisions;
4. `docs/implementation-readiness.md` for phase gates and numerical envelopes;
5. the claimed GitHub issue for the bounded vertical slice being implemented.

When a historical research or Harvest artifact conflicts with those records,
the current records above win. A new conflicting requirement needs an explicit
superseding decision; implementation may not silently choose between them.

## Product boundary

Corvus is an invokable ChatGPT app, not a standalone chat client. One cohesive,
stateless Investigation module sits behind a thin Apps SDK and MCP adapter. The
public Streamable HTTP MCP advertises exactly three read-only tools:

- `theological_investigation`, whose only user-authored top-level input is the
  question as written;
- `inspect_source`, which accepts only a signed package-issued Citation
  reference; and
- `branch_analysis`, which accepts a signed package-issued Replay reference and
  an explicit user-authored Scope delta.

YouVersion, Gloo, ontology storage, corpus policy, validation, credentials,
publication, and provider failures remain private implementation details. There
is no public provider passthrough, arbitrary URL fetch, ontology administration,
release publication, general graph query, or direct browser-to-Convex surface.

## Ontology role

The Bible ontology is an immutable, versioned evidence and discovery index. It
helps the Investigation module resolve identity, traverse attributable
relationships, and discover candidate evidence. It does not declare universal
theological truth.

Every ontology record has one explicit policy class:

1. **Deterministic structure** records source-verifiable identity, containment,
   canonical-collection membership, passage locators, and admitted lexical or
   morphological identifiers.
2. **Source-scoped interpretation** records what one admitted Source asserts,
   with exact Artifact, locator, edition, recognizing body, tradition and
   authority scope, Corpus snapshot, and relationship type.
3. **Discovery candidate** records an algorithmic or model-proposed association
   used only to widen or rank retrieval. It cannot authorize an Answer
   statement, satisfy an obligation, establish a Position, repair an Evidence
   gap, or appear as evidence in the Evidence graph.

Interpretive relationships such as fulfillment, typology, doctrinal relevance,
or tension are never universal merely because a model, embedding, cross-reference
vote, or maintainer proposed them. They require an admitted source-scoped
assertion or remain package-local Derived statements with validated lineage.
Similarity and ranking scores are operational metadata, never authority,
sufficiency, Answer outcome, or user-visible theological confidence.

## Releases and storage

Convex is the sole production application database and vector facility. The
runtime uses release-prefixed typed records rather than generic nodes and edges.
Every runtime read pins one complete immutable Ontology release and Corpus
snapshot; lower-level code never infers `latest`.

Publication is an offline, CI-only stage, seal, validate, and atomic activate
workflow. The Vercel runtime can read approved projections but cannot stage,
publish, mutate, retire, or prune releases. Vercel rollback and Convex active-pin
rollback are separate, compatibility-checked operations.

Traversal is deterministic, indexed, release-pinned, cycle-safe, and bounded by
the envelope in Implementation readiness. Budget exhaustion creates a typed Gap
or abstaining result; it never silently truncates required evidence. Vector
search is optional and quarantined to Discovery candidates whose exact Artifacts
permit durable derived indexing.

Do not add PostgreSQL, pgvector, Neo4j, a shadow store, a second vector service,
or a browser-accessible Convex data path without production benchmark evidence
and a superseding ADR.

## Evidence contract

The Answer evidence package is the canonical substantive result. It contains
ordered atomic Answer statements, Citations, statement-owned Evidence links,
Derived-statement lineage, Analysis scope, Answer obligations and outcome,
Position memberships, Evidence gaps, provider reports, Material-operation
receipts, semantic structure links, and exact release pins.

Every substantive statement is either source-grounded through admissible exact
evidence or Derived through an acyclic lineage terminating in supported
source-grounded statements. A Citation identifies one exact Artifact, locator,
edition, content mode, delivered excerpt, and safe target when permitted. Reusing
a Citation never transfers authority, tradition scope, or support between
statements.

Sources and the Evidence graph are derived from canonical package relationships;
they are not duplicate answer models. Operation receipts expose material inputs,
outputs, failures, and replayability without recording private chain-of-thought,
credentials, raw provider exchanges, or conversation state.

## Content and rights

The repository-governed Corpus snapshot owns source identity, tradition-relative
authority, exact edition, provenance, membership, and rights decisions. Only
`included` or explicitly authorized immutable `fetch_only` Artifacts may support
substantive statements. Public readability, metadata, a provider result, or a
checksum of a mutable page does not make content runtime-admissible.

Canonical collection is independent from Scripture display edition. YouVersion
hydrates bounded Scripture only after locator selection. Passage text is never
persisted in Convex, Gloo, logs, telemetry, durable caches, or Replay references.
Gloo performs publisher-scoped retrieval and then schema-constrained analysis;
its output remains untrusted candidate data until deterministic validation.

## First fixture

The first implementation fixture asks:

> According to Matthew 22:37–40, which commandments does Jesus call greatest?

It uses reviewed public-domain World English Bible US fixture text and exact
locators for Matthew 22:37–38 and Matthew 22:39–40. It is factually bounded to
what the cited passage says and requires no tradition-bearing default or
benchmark Position plan. The fixture must exercise at least:

- preservation of the question as written;
- one requested Answer obligation;
- two atomic Textual observations with direct Scripture Evidence links;
- one derived Conclusion with explicit lineage to both observations;
- exact Source, Artifact, edition, locator, content mode, and Citation identity;
- one deterministic fixture Operation receipt and complete output links;
- an `Answered` outcome derived from the supported obligation;
- Sources and minimal Evidence-graph projections derived from package links; and
- deterministic successful, degraded, abstaining, and hostile-data variants.

The unscoped baptism comparison remains the maximum contested stress fixture. It
cannot become a supported fixture until Issue #8 checks in and accepts the
versioned benchmark category and material-Position plan.

## Implementation sequence

1. Validate the minimal package, pure evidence policy, factual fixture, in-memory
   read store, MCP harness, and minimal Evidence component.
2. Add explicit missing-plan behavior without inventing contested plans.
3. Prove fixture-backed Vercel transport and the Vercel-to-Convex trust boundary.
4. Implement live Convex storage only after every trust-spike case passes.
5. Enable live providers only after contract, rights, caller-gate, redaction,
   budget, and spend proofs pass.
6. Support unscoped contested planning only after Issue #8 is accepted.
7. Assemble production only after rights, narration, security, load, rollback,
   restore, and human release gates pass.

Every slice runs the relevant focused suites, then `npm run check`, then separate
Standards and Spec reviews from a pinned base revision.
