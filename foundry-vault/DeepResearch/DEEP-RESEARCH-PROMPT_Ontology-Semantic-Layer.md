# Deep Research Prompt — Reverse-Engineering Foundry's Ontology *Semantic Layer*

**What this is:** a ready-to-run, deeply-scoped deep-research prompt. Its single job is to reconstruct, as exhaustively as the public record allows, how Palantir Foundry's **Ontology semantic layer** is modeled, stored, indexed, secured, versioned, and queried — at the level of concrete mechanics, not marketing.

**How to use it:** paste everything below the line into any deep-research tool (Claude, ChatGPT/o-series deep research, Gemini, Perplexity, etc.). It's tool-agnostic. The **Confirmed starting leads** section at the bottom gives the agent real entry points so it doesn't waste cycles. Trim the seed list if your tool has a tight input limit; keep the role, scope, question bank, methodology, and output spec.

**Scope note:** semantic layer *only* (objects, properties, links + the storage/indexing/security/versioning/API that back them). The kinetic layer (Actions, Functions) and everything above the Ontology are explicitly out of scope except where they touch the semantic model.

---

# ▼▼▼ PASTE FROM HERE ▼▼▼

## Role

You are a senior platform-architecture researcher and reverse-engineer specializing in enterprise data platforms and semantic/knowledge-graph systems. You are rigorous, source-driven, and allergic to marketing language. Your task is to reconstruct the internal design of **one specific subsystem** of Palantir Foundry: the **semantic layer of the Foundry Ontology**.

## Objective

Produce an **exhaustive, citation-backed technical reconstruction** of how Foundry's Ontology semantic layer is conceived, modeled, stored, indexed, secured, versioned, queried, and exposed to developers — detailed enough that a competent engineering team could use your report as the functional-and-architectural reference to design a faithful clone. **Prioritize concrete mechanics** (data structures, service names, storage engines, constraints, cardinalities, API shapes, limits) over conceptual or promotional descriptions. Where the concept is already obvious, spend your effort on *how it is actually implemented*.

## Precise scope: what "semantic layer" means here

**In scope** — the parts of the Ontology that describe *what exists* and how it is represented, stored, and accessed:

- **Object types & object instances** — identity, primary keys, title properties, resource identifiers (RIDs), lifecycle/status, API name vs. display name, metadata.
- **Properties** — the full set of base types; value/semantic types; struct, array, derived/computed, geospatial, time-series/series, sensor, media-set, attachment, and marking properties; rendering hints; constraints/validation; required and mandatory-control properties.
- **Link types** — cardinalities (1:1, 1:many, many:many); how each is implemented (object-backed vs. foreign-key/property-backed vs. join/mapping-dataset-backed); directionality; metadata; limits.
- **Interfaces / shared property types** — any polymorphism, inheritance, or shared-schema mechanism.
- **The backing-data model** — how datasources (datasets, streams, restricted views, virtual tables) map into objects; column→property mapping; the one-datasource-per-object-type rule; excluded column types; sync/materialization; edit-only/writeback-only objects.
- **Storage & indexing backend** — Object Storage V1 ("Phonograph"), Object Storage V2, the Object Data Funnel, indexing pipelines, "ontology query compute": storage engines, data structures, write/read paths, consistency model, incrementality, latency, scale/limits.
- **Object sets & the query surface** — search, filter, aggregation, typeahead, geo/time queries; the object-set abstraction and its lifecycle/permissioning.
- **Security woven into the semantic model** — granular permissions, object security policies (row-level), property-level security/classification, markings, mandatory control properties; how they relate to backing-dataset/restricted-view permissions.
- **Metadata, versioning & lifecycle** — where ontology definitions are stored/served; ontology branching; Ontology proposals; schema evolution/migration; breaking-change handling; one-vs-many ontologies; ontology RID.
- **Developer/API/SDK surface for reading the model** — the Ontology API (load/search/aggregate/link-traversal/metadata), the Ontology SDK (OSDK), the foundry-platform SDKs, public repos, request/response shapes.

**Out of scope** (mention only where it touches the semantic model, do not deep-dive): the kinetic layer — **Actions** and **Functions** — except exactly where they read/write the semantic model (e.g., writeback creating/editing objects, function-backed derived properties); the application layer (Workshop, Quiver, Contour, Object Explorer, Map, Slate); **AIP**; **Apollo**; the general pipeline/transform system except as it produces backing datasources; and high-level philosophy/marketing (already understood — do not re-explain "digital twin," etc.).

## Research question bank

Answer **every** question you can substantiate; for each you cannot, record it explicitly as a known unknown (see methodology). Organize your findings under these headings.

**A. Conceptual data model**
1. Enumerate **every property base type** and, for each, the operations/queries it supports and any storage notes. Quote the documented exclusions (e.g., types not valid as base types).
2. What are **value types / semantic types** vs. base types? How are they defined, what validation/constraints do they add, and how are they stored?
3. How are **struct**, **array**, and **derived/computed** properties defined, stored, and queried?
4. How are **geospatial** (geopoint/geohash/geoshape), **time-series/series**, **sensor**, **media-set**, **attachment**, and **marking** properties represented?
5. **Primary-key** semantics, **title property**, object **RID**/identity, uniqueness guarantees, and how identity is generated for writeback-only objects.
6. **API name vs. display name**; object-type **status/lifecycle** (experimental/active/deprecated) and what each implies.
7. **Interfaces**: definition, shared properties, polymorphism, when introduced, and any limits.
8. Per-object and per-property **metadata**: descriptions, visibility, formatting/render hints, icons, groupings.

**B. Link / relationship model**
9. Each **link cardinality** (1:1, 1:many, many:many) and exactly how it is implemented.
10. **Object-backed link types** vs. **property/foreign-key-backed** vs. **join/mapping-dataset-backed** links — when each is used and the trade-offs.
11. How **many-to-many** is realized (intermediary datasets/objects), including any "backing object type" mechanism.
12. Link **directionality**, display names, metadata, and documented **limits/constraints**.

**C. Backing data & materialization**
13. The **datasource → object-type** relationship; the **one-datasource-per-object-type** rule; **column → property** auto-mapping behavior.
14. **Excluded** backing column types (e.g., Map/Struct/Binary) and the reasons.
15. Backing by **streams** (real-time objects), **restricted views** (row security), **virtual tables** (federation/no-copy), and **edit-only/writeback-only** object types.
16. The **sync/indexing process**: batch vs. **incremental**; how dataset builds trigger reindex; end-to-end latency; what happens on schema change or branch.

**D. Storage & indexing architecture — the core reverse-engineering**
17. **Object Storage V1 (Phonograph)**: architecture, underlying storage/indexing technology, capabilities, limitations, and the reasons for deprecation (note the documented end-of-life: after **June 30, 2026**).
18. **Object Storage V2 (OSv2)**: the re-architecture; substantiate the documented claim that it can back object storage with **"multiple data storage types in parallel"** — *which* stores serve *which* access patterns (point lookups, full-text/typeahead search, aggregations, geo, time-series)? Confirm specifics or mark as unknown with a best hypothesis.
19. **Object Data Funnel**: its role orchestrating writes into the Ontology and reads from datasources and user edits; **Funnel batch pipelines**; the write path for **dataset syncs vs. user edits**.
20. What underlying technologies power **indexing/search/aggregation/query** (e.g., a search index, columnar store, KV store)? Confirm from primary sources or clearly label as inference.
21. **Ontology query compute**: how object queries are planned, executed, and costed/metered.
22. **Incremental indexing** mechanics; the **consistency model** (e.g., eventual consistency, read-after-write for edits); conflict handling.
23. **Scale & limits**: documented caps on object counts, properties per type, index size, sync latency, query result sizes, aggregation limits, quotas. Quote exact numbers where published.

**E. Object sets & query surface**
24. The **object set** abstraction (saved/temporary query over objects), object-set **RID**, persistence, and composition.
25. Is there an **Object Set Service** (or equivalent)? Verify its name and responsibilities.
26. **Search, filter, aggregation** capabilities and their APIs; typeahead; geo and temporal queries; pagination.
27. How object sets are **shared, cached, and permissioned**.

**F. Security as part of the semantic model**
28. **Granular permissions** and **object security policies** (row-level on object types); how they relate to backing-dataset permissions and **restricted views**.
29. **Mandatory control properties**; **property-level security/classification**; **markings** on properties.
30. How **unauthorized** objects/properties render (title/display fallback, redaction).
31. **Purpose-/classification-based** controls as they touch objects.

**G. Metadata, versioning & lifecycle**
32. Where ontology **definitions are stored and served** — is there an **Ontology Metadata Service (OMS)** or equivalent? Verify name/role.
33. **Ontology branching**, **Ontology proposals**, review/approval flow, **schema migration**, and backward-compat/breaking-change handling (cite the OSv1→OSv2 breaking-changes material).
34. **Single-ontology-per-enterprise vs. multiple ontologies**; the **ontology RID** and namespacing.

**H. Developer / API / SDK surface**
35. The **Ontology API** (v2): endpoints for loading objects, search, aggregate, link traversal, and metadata — with representative **request/response shapes**.
36. The **Ontology SDK (OSDK)**: how it generates typed clients; how it models objects/links/primary keys; pagination and error handling.
37. The **foundry-platform SDKs** (TypeScript/Python) and **public GitHub repos** (e.g., `palantir/osdk-ts`, foundry-platform SDKs, any Conjure API specs) — what they reveal about the underlying model.
38. Protocols offered (REST/GraphQL/streaming), auth, and rate limits.

**I. History, evolution & provenance**
39. Trace the **lineage of the ontology concept** from Palantir **Gotham** ("dynamic ontology") into Foundry.
40. Find and summarize **Palantir patents** on object-centric / dynamic-ontology data models (patent numbers + key claims).
41. Locate **engineering blog posts** and **AIPCon / Palantir Developers** talks that describe the backend; extract concrete architectural statements.
42. Build a **timeline** of major changes: Phonograph → OSv2, introduction of interfaces, value types, OSDK, etc.

## Source strategy (prioritized)

1. **Primary — official docs:** `palantir.com/docs/foundry/**`, especially `object-backend`, `object-databases`, `object-indexing`, `object-link-types`, `ontologies`, `ontology`, `ontology-sdk`, and the `api` reference. Read the *detail* pages, not just overviews.
2. **Primary — engineering blog & talks:** `blog.palantir.com`; Palantir Developers / AIPCon YouTube; any architecture white papers.
3. **Primary — patents & filings:** Google Patents / USPTO for "dynamic ontology" and object-centric data model; SEC filings; technical white papers.
4. **Primary — source & API refs:** `github.com/palantir` (`osdk-ts`, foundry-platform SDKs, Conjure specs), the public API v2 reference.
5. **Primary — training:** `learn.palantir.com`.
6. **Secondary — credible third parties:** consultancy/engineering deep-dives, posts by ex-Palantir engineers, conference write-ups.
7. **Tertiary — community:** r/palantir, Hacker News, Stack Overflow — for leads and corroboration only, never as sole authority.

Always prefer **primary, recent, version-stamped** sources. Capture the URL and access date for everything.

## Reverse-engineering methodology & rigor

- **Triangulate** every non-trivial claim across ≥2 independent sources where possible.
- **Tag every claim** with an evidence label — **[Documented]** (stated in a primary source), **[Inferred]** (reasoned from evidence), or **[Speculative]** (plausible, unconfirmed) — plus a **confidence** rating (High / Medium / Low) and an inline citation.
- **Separate current from legacy:** distinguish OSv2-era behavior from Phonograph/OSv1; date-stamp version-specific facts; note the Phonograph EOL (after June 30, 2026).
- **Flag contradictions** between sources explicitly rather than silently picking one.
- **Never fabricate** service names, storage engines, or internals. Where the public record is silent, say so plainly and offer the single best-supported hypothesis, clearly labeled **[Speculative]**.
- **Chase named internal components** to their source: Phonograph, Object Storage V2, Object Data Funnel, Funnel batch pipelines, ontology query compute, OSDK — and *verify the existence and role* of Ontology Metadata Service and Object Set Service.

## Required output structure

Produce a single, long-form technical report with these sections:

1. **Executive summary** (≈1 page) — the semantic layer in a nutshell plus the 5–10 most important reverse-engineering findings.
2. **Conceptual data model** — precise spec of object types, properties (a **complete base-type table**), link types, and interfaces; include an ER-style description and one fully annotated worked example.
3. **Backing-data & materialization model** — datasources→objects, sync/indexing, real-time and edit-only variants.
4. **Storage & indexing architecture** *(most technical)* — Phonograph vs. OSv2, the Object Data Funnel, indexing/query engines, consistency model, scale/limits.
5. **Object sets & query/search surface.**
6. **Security model within the semantic layer.**
7. **Metadata, versioning & lifecycle** — branching, proposals, migration.
8. **Developer / API / SDK surface** — with concrete request/response or SDK snippets where available.
9. **History & patents** — provenance and a change timeline.
10. **Glossary of Palantir-internal terms & service names** — definition + citation for each.
11. **Confidence & gaps register** — a table of key claims with evidence label + confidence, followed by an explicit **"known unknowns"** list and, for each, the source that would resolve it.
12. **Source bibliography** — all URLs with access dates, grouped by tier.

Use **tables** for every enumeration (base types, link cardinalities, limits, services, API endpoints). Favor precise mechanics over prose. Quote exact constraints and limits **verbatim** where they exist.

## Exhaustiveness bar (definition of done)

Do **not** stop at the conceptual overview. For each subsystem, drill until you can either (a) describe the concrete mechanism with a primary citation, or (b) explicitly record it as a known unknown with your best-supported hypothesis and the missing source. Aim for the depth of a detailed technical white paper; cite extensively (target dozens of primary sources). If two passes still leave a gap, surface it in the gaps register rather than papering over it. Neutral, technical tone throughout; no marketing language.

## Confirmed starting leads (verified — begin here, then expand)

*These were confirmed to exist as of mid-2026; treat them as entry points and verify currency.*

- **Object backend overview:** `palantir.com/docs/foundry/object-backend/overview`
- **Object Storage V1 (Phonograph)** [legacy / planned deprecation, EOL after 2026-06-30]: `palantir.com/docs/foundry/object-databases/object-storage-v1`
- **OSv1 → OSv2 migration:** `palantir.com/docs/foundry/object-backend/osv1-osv2-migration` · **breaking changes:** `…/object-backend/object-storage-v2-breaking-changes`
- **Object indexing overview:** `palantir.com/docs/foundry/object-indexing/overview` · **Funnel batch pipelines:** `…/object-indexing/funnel-batch-pipelines`
- **Ontology query compute:** `palantir.com/docs/foundry/ontologies/query-compute-usage`
- **Object & link types** (object types, link types, properties overview, **base types**, **mandatory control properties**, required properties): `palantir.com/docs/foundry/object-link-types/…`
- **Ontology overview / core concepts:** `palantir.com/docs/foundry/ontology/overview` · `…/ontology/core-concepts`
- **The Ontology system (architecture center):** `palantir.com/docs/foundry/architecture-center/ontology-system`

**Named components to chase to source:** Object Storage V1 (**Phonograph**) · **Object Storage V2** · **Object Data Funnel** · **Funnel batch pipelines** · incremental object indexing · property **base types** · **value types** · **interfaces** · **mandatory control properties** · **object security policies** · **object-backed link types** · **OSDK** · *(verify)* **Ontology Metadata Service** · *(verify)* **Object Set Service** · *(find)* Palantir **"dynamic ontology" patents**.

# ▲▲▲ PASTE TO HERE ▲▲▲
