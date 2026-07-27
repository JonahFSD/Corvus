# ADR-0008: Use the Bible ontology as an evidence and discovery index

- Status: accepted
- Date: 2026-07-26

## Context

The historical Bible ontology spec described a broad graph containing structural, narrative, semantic, and theological relationships. It treated `TENSION_WITH`, `TYPE_OF`, fulfillment, generated Claims, tradition arrays, and numeric confidence as similar edge metadata, and proposed an LLM extraction pass to populate the graph.

That model conflates three different things: directly verifiable scriptural structure, an identifiable source's interpretation, and an algorithm or model's retrieval hypothesis. A high-scoring association does not acquire theological authority. A tension or typology recognized by one tradition is not automatically a universal fact, and Gloo synthesis is not provenance. The Answer evidence package also deliberately defers reusable global Claim records until fixtures prove they are warranted.

## Decision

Use the Bible ontology as a versioned typed evidence and discovery index. It helps the Investigation module find, join, and attribute evidence; it does not declare universal theological truth.

### Record classes

Every ontology record belongs to one of three policy classes.

1. **Deterministic structure** records stable, source-verifiable identity or containment such as books, chapters, verses, pericopes, exact source and edition identities, scriptural collection membership, explicit quotation locators, and admitted lexical or morphological identifiers. Canonical-collection membership remains tradition-relative and names the recognizing body rather than pretending that one collection is universal.
2. **Source-scoped interpretation** records what an admitted source asserts about a relationship such as fulfillment, typology, thematic association, genre, reception, doctrinal relevance, or tension. It carries exact source and locator, edition, recognizing body when applicable, tradition and authority scope, corpus version, and relationship type. The ontology records the attributable assertion, not the assertion as universal truth.
3. **Discovery candidate** records an algorithmic or model-proposed association used only to widen or rank retrieval. It carries origin, generator and version, input or source fingerprint where rights permit, operational score, and creation policy. It is quarantined from admissible evidence.

The schema uses a discriminated policy class rather than a generic edge whose `confidence`, `source`, and `traditions[]` fields callers must interpret loosely. Runtime queries may return all three classes internally, but evidence compilation accepts only deterministic structure and source-scoped interpretation records that independently pass source, authority, rights, scope, and sufficiency policy.

### Theological relationships

`TENSION_WITH`, `TYPE_OF`, `FULFILLS`, `PROPHESIES`, `ABOUT`, and similar interpretive relationships are never universal merely because a model, embedding, cross-reference vote, or project maintainer proposes them. They are either:

- source-scoped interpretive assertions with exact admitted provenance; or
- package-local Comparative synthesis derived through ADR 0005's validated `derivedFrom` lineage.

A Discovery candidate may lead the Investigation module to retrieve useful passages or sources. It cannot authorize an Answer statement, establish a Tradition position, satisfy an Answer obligation, repair an Evidence gap, or appear as evidence in the Evidence graph. No numeric threshold promotes it automatically. Promotion into the admitted index occurs only through the repository-governed corpus or ontology release process with an independently admitted source and complete policy metadata.

### Scores and Claims

Similarity, cross-reference vote, hop penalty, and other scores are operational retrieval signals. They may order candidate work but never express theological truth, source authority, evidentiary admissibility, statement sufficiency, or Answer outcome. They remain internal and do not enter the user-visible Answer evidence package as confidence.

Do not create reusable global Claim records in the initial ontology. Human-readable substantive propositions live as package-local Answer statements under ADR 0005. A later accepted decision may introduce reusable Claims only after fixtures demonstrate genuine reuse and define lifecycle, identity, revision, and evidence semantics.

### Gloo and runtime mutation

Gloo receives bounded, rights-permitted evidence and explicit Analysis scope to produce candidate structured analysis. Its output is parsed as untrusted model data and must pass the deterministic evidence gate. Gloo does not establish provenance, confer source authority, promote Discovery candidates, or write theological assertions into the production ontology during a user request.

The runtime treats ontology and Corpus snapshots as immutable. New or corrected deterministic structure, source-scoped interpretation, and Discovery candidates enter through offline, versioned, reproducible release tooling rather than live answer traffic.

## Consequences

The ontology can still support graph traversal, hybrid retrieval, cross-reference discovery, original-language lookup, and tradition-aware comparison. It preserves the distinction between what a text structurally is, what an admitted source says it means, and what an algorithm suggests examining.

Ingestion requires more explicit provenance and policy metadata than the historical generic edge table. Retrieval code must carry policy class through the pipeline and prevent Discovery candidates from leaking into evidence compilation. This is intentional: the alternative makes model-generated associations indistinguishable from admitted theological evidence.

The physical store, indexing engine, table layout, vector strategy, and exact admitted object/link vocabulary remain separate decisions.
