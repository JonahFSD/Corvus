# ADR-0012: Require runtime rights for first-class tradition coverage

- Status: accepted
- Date: 2026-07-26

## Context

Corvus guarantees First-class tradition coverage for Catholic, Eastern Orthodox, Oriental Orthodox, Anglican, Baptist, Lutheran, Pentecostal, Reformed/Presbyterian, and Wesleyan/Methodist positions. ADRs 0002–0004 define a repository-governed Tradition corpus with exact editions, tradition-relative authority, rights metadata, and benchmark-driven Topic packs. The evidence contract permits a Tradition position only when its source set is resolvable, admissible, deliverable, and sufficient.

The 2026-07-26 primary-source artifact audit found that most exact official English Source-spine presentations are publicly readable but do not grant the rights required for corpus ingestion, model input, or user-facing excerpts. Current examples include the Catholic catechism, modern Orthodox council and catechetical pages, the Church of England's 1662 prayer-book presentation, Baptist body statements, WAGF's statement, current Reformed translations, and UMC standards. Public availability, official authority, and stable locators do not create a runtime licence.

Only a small set is presently plausible for inclusion without new permission: the LCMS-hosted public-domain 1921 _Book of Concord_ translation and a separately acquired and reviewed public-domain 1900 translation of early councils. Those sources do not satisfy the guaranteed cross-tradition coverage by themselves. Treating `reference_only` sources, provider snippets, or model recollection as evidence would make the public product claim false and bypass source owners' rights.

## Decision

Make runtime-admissible source coverage a hard production-release gate for every guaranteed tradition family and every required position in the deterministic benchmark. Do not weaken the First-class tradition coverage promise, count `reference_only` artifacts as evidentiary coverage, or ship a benchmark whose mandatory positions can only abstain for corpus-rights reasons.

This gate defines the guaranteed release envelope; it does not claim exhaustive coverage of every doctrine, jurisdiction, denomination, or historical dispute. Questions outside the benchmarked envelope may still expose an honest Evidence gap and Evidentiary abstention.

### Coverage gate

A Corpus snapshot is eligible for production only when automated validation proves all of the following:

1. Every guaranteed tradition family has at least one runtime-admissible primary Source-spine artifact whose recognizing-body scope is represented accurately.
2. Every required benchmark Position membership has a sufficient runtime-admissible primary source set for the concrete proposition being tested.
3. Where a family is structurally plural or the benchmark exposes a material internal disagreement, separately scoped bodies have separately admissible sources and Position memberships. One federation, province, denomination, local church, or historic formulary cannot silently represent the entire family.
4. Every admitted artifact has an exact work, edition or translation, digital artifact, locator scheme, checksum, acquisition provenance, authority assertion, rights decision, and Corpus-snapshot membership. A `fetch_only` artifact also has an immutable version or revision, a versioned retrieval locator, and a guaranteed availability window covering the seven-day Citation lifetime and 24-hour Replay lifetime, plus five minutes of clock skew, after its last possible reference issuance.
5. Every delivered excerpt, model-visible fragment, Citation target, transformation, retrieval index, and embedding is authorized by that artifact's specific rights policy.
6. The Corpus snapshot compiler rejects any required source or benchmark obligation in `reference_only`, `blocked`, expired, revoked, ambiguous, or unreviewed state.

`reference_only` remains useful for work identity, authority and recognition metadata, edition discovery, stable locators, and an optional safe external target when linking is permitted. Its text, snippets, provider search results, or page content cannot be stored, chunked, uploaded to Gloo, embedded, supplied to a model, delivered to the component, quoted in native narration, or used to support an Answer statement.

`fetch_only` is not a workaround for a missing licence or mutable source. It requires affirmative authorization for runtime retrieval and every downstream use actually performed, plus exact-byte reproducibility for the full inspection and replay window. Every fetch verifies the recorded checksum before content can enter evidence. A changed, missing, or non-versioned artifact fails closed and cannot support a replayable or first-class claim. If the source owner authorizes viewing but not model input or user delivery, or cannot provide an immutable versioned artifact, the artifact remains non-admissible for that operation.

### Permission contract

For a copyrighted artifact to become `included` or `fetch_only`, the rights record and its human review must resolve, as applicable:

- the exact work, edition, translation, files, site pages, territories, languages, and recognizing body covered;
- server acquisition, storage, checksums, backups, and retention;
- normalization, format conversion, segmentation, locator mapping, search indexing, and other transformations;
- upload to Gloo or another named processor, semantic search, model input, and whether provider retention or training is prohibited;
- bounded excerpts in model-visible tool data, native ChatGPT narration, the Evidence component, Source inspection, and exported challenge materials;
- external linking and deep-link construction;
- caching and embeddings as separate permissions rather than presumed derivatives;
- required attribution, copyright notice, excerpt limits, noncommercial conditions, brand restrictions, and prohibited modifications;
- embedded third-party content, especially Bible translations, images, annotations, proof texts, and editorial additions;
- effective date, term, revision/version handling, termination, revocation, takedown, and post-termination deletion; and
- for `fetch_only`, immutable artifact hosting, exact-byte/version guarantees, minimum availability through the maximum reference lifetime, checksum-mismatch behavior, and permitted archival fallback;
- the evidence of permission, reviewer, review date, and a digest or controlled reference to the governing terms.

Do not commit confidential agreements to the public repository. The public manifest records the permitted-use decision, evidence digest or controlled identifier, reviewer, review time, expiry and restrictions needed for deterministic enforcement. The actual grant remains in an access-controlled legal record. A maintainer cannot mark a source admissible merely because the work is old, the page is official, a provider indexed it, or a short excerpt might qualify as fair use.

For a public-domain artifact, review the exact edition and acquired bytes rather than only the conceptual work. Verify jurisdiction, publication facts, translation and editorial contributions, transcription provenance and quality, and embedded third-party material. Acquire from a lawful artifact, record the original and normalized checksums, and preserve transformations. A modern website transcription of a public-domain work does not inherit public-domain status automatically.

### Permission and revocation workflow

Treat source acquisition and permission as a named Human-review workstream that blocks production but does not block fixture-first implementation. Each request package should identify Corvus, the noncommercial ChatGPT use, exact materials, model processor, delivery surfaces, excerpt bounds, storage and deletion behavior, attribution, and requested term. A positive response is not activated until the rights record, artifact, locator map, and benchmark coverage pass review.

When terms expire, change, or are revoked, a deployment-level rights denylist immediately prevents new use of the affected artifact while an offline release removes it from Gloo, the Corpus snapshot, and any authorized derived indexes. The denylist is an emergency safety control, not a way to mutate historical release provenance. The next immutable Corpus snapshot records the removal and affected coverage. Backups and processors follow the governing deletion obligations.

### Implementation before clearance

Build the corpus compiler, registry, Gloo mapping, evidence gate, and benchmark with synthetic fixtures and already reviewed public-domain artifacts. Synthetic fixtures use invented source text and authorities clearly marked as test-only; do not copy rights-restricted prose into the repository merely because it is a fixture.

Production configuration fails closed unless the compiled coverage report is green for every guaranteed family and mandatory benchmark position. Development and staging may exercise explicit degraded and abstaining cases, but no environment or writeup may describe `reference_only` metadata as first-class runtime evidence.

The current rights workstream must seek or replace, at minimum, the blocked exact artifacts identified in the artifact audit: Catholic catechetical material; current Eastern and Oriental Orthodox body-specific anchors; Anglican formularies; global and internally diverse Baptist anchors; WAGF material; current Reformed/Presbyterian forms; UMC doctrinal standards; and any source needed to establish family scope beyond the LCMS public-domain Lutheran artifact and historical council translation.

## Rejected alternatives

- Ship every family label while allowing mandatory positions to abstain because their sources are `reference_only`.
- Treat public web access, robots permission, a stable URL, provider ingestion, or a source snippet as permission.
- Use fair-use assumptions as the default legal basis for a public corpus and repeatable model pipeline.
- Ingest a modern website transcription because the underlying historical work is public domain.
- Allow Gloo or another provider to supply source text outside the manifest's rights decision.
- Replace a blocked current edition silently with an older public-domain translation.
- Let one narrow recognizing body stand for an entire plural tradition family.
- Copy restricted text into fixtures and promise to remove it before production.
- Downgrade the mandatory First-class tradition coverage commitment to meet a date.

## Consequences

The product's evidence and rights promises become true by construction. The production corpus cannot convert bibliographic metadata into theological evidence, and providers cannot launder unavailable rights. The same compiler report that proves authority coverage also proves delivery eligibility for the benchmarked answer surface.

Production release is blocked until substantial external permission or independently licensed artifact work is complete. Some owners may decline model use, require narrower excerpts, prohibit embeddings, or offer only editions that do not cover the needed proposition. In those cases Corvus must negotiate, choose a genuinely equivalent and accurately labeled artifact, revise a benchmark only through an explicit product decision that preserves mandatory coverage, or remain blocked. The deadline does not relax this gate.
