# Deep Research Prompt — Reverse-Engineering Foundry's *Data Integration & Pipeline* Layer

**What this is:** the third in the set (after the Ontology semantic and kinetic layers). Its single job is to reconstruct, as exhaustively as the public record allows, how Palantir Foundry's **data integration and pipeline layer** works — from a source system's bytes to a clean, curated, Ontology-ready dataset kept fresh with lineage and health — at the level of concrete mechanics, not marketing.

**How to use it:** paste everything below the line into any deep-research tool (Claude, ChatGPT/o-series deep research, Gemini, Perplexity, etc.). It's tool-agnostic. The **Confirmed starting leads** section gives real entry points. Trim the seed list if your tool has a tight input limit; keep role, scope, question bank, methodology, and output spec.

**Scope note:** the **data foundation** only — connectivity/ingestion, datasets/transactions, transforms and the Build system, pipeline tooling, data health and lineage, and data-layer governance. The Ontology (objects/links/actions/functions) is covered in the two companion reconstructions and is out of scope here except at the exact seam where a curated dataset *backs* an object type.

---

# ▼▼▼ PASTE FROM HERE ▼▼▼

## Role

You are a senior data-platform architect and reverse-engineer specializing in data integration, lakehouse/dataset storage, distributed compute (Spark), and pipeline orchestration. You are rigorous, source-driven, and allergic to marketing language. Your task is to reconstruct the internal design of the **data integration and pipeline layer of Palantir Foundry** — the "data foundation" that ingests source data and turns it into clean, governed, versioned, Ontology-ready datasets.

## Objective

Produce an **exhaustive, citation-backed technical reconstruction** of how Foundry connects to source systems, ingests and stores data as datasets, transforms it through pipelines, orchestrates builds, keeps data fresh incrementally, and tracks quality and lineage — detailed enough that a competent engineering team could use your report as the functional-and-architectural reference to build a faithful clone of this layer. **Prioritize concrete mechanics** (connector/agent architecture, the dataset transaction model, schema/branch semantics, the transforms API surface, the Build/orchestration model, the incremental-compute engine, data-health checks, lineage, and storage internals) over conceptual or promotional descriptions.

## Precise scope: what "data integration & pipeline layer" means here

**In scope** — everything between an external source system and a curated, Ontology-ready dataset:

- **Connectivity & ingestion (Data Connection / "Magritte")** — sources and connectors; the **capability** model (ingest in, push out, virtualize, interactive requests); **agents** (agent-proxy / "thin mode," agent worker) vs. **direct/cloud** connections; the **Foundry worker** isolated-container model; **egress policies** and networking; credential/secret management; sync types (**batch, incremental, streaming/CDC**); file ingestion and **schema inference**; **exports** (data out of Foundry); **virtual tables** (federation / no-copy over Delta/Iceberg/etc.); interactive/external requests.
- **Dataset & storage model** — the **dataset** abstraction; the **transaction model** (**SNAPSHOT / APPEND / UPDATE / DELETE**) and how each is used; **branches**; **views**; **schemas** and schema evolution; the physical storage (files — Parquet/Avro; the Foundry file system / catalog); dataset **RIDs**; the catalog/transaction service.
- **Transforms & authoring** — the **transform** abstraction (input datasets → output datasets); **Code Repositories** (Python, PySpark, Java, SQL) and the **transforms API** (`@transform`, `@transform_df`, `@incremental`, `strict_append`, etc.); **Pipeline Builder** (no-/low-code) and how it relates to / compiles down to transforms; SQL transforms; container/"lightweight" (non-Spark) transforms.
- **The Build system & orchestration** — the **build graph/DAG**, jobs, and the build/orchestration service; **scheduling and triggers** (schedules, event-based/streaming builds); the **incremental-compute engine** (semantics, snapshot-vs-append handling, how incrementality is determined and maintained); **compute backends** (Spark, **Spark profiles**/executor config, non-Spark/lightweight compute); abort/retry; **build compute metering** (compute-seconds).
- **Data quality & lineage** — the **data-health / checks / Expectations** framework (schema, freshness, row-count, custom checks); the end-to-end **lineage/provenance** graph; monitoring/alerting on pipelines.
- **Governance in the data layer** — **markings/classifications** on datasets, **restricted views** (row-level), column-level controls, **projects/folders** and the resource hierarchy with roles/permissions, purpose-based controls — specifically as they apply to datasets and pipelines.
- **Patterns & philosophy** — the recommended layered pipeline (**raw → clean → ontology**-style), project structure, and **dev→prod branching**.
- **APIs/SDK & internal architecture** — the datasets and transforms APIs, foundry-platform SDK data endpoints, and the named internal services (verify: **magritte-coordinator**, the catalog/transaction service, schema service, the build-orchestration service).

**Out of scope** (mention only at the seam, do not deep-dive): the **Ontology layer** (object/property/link/action/function modeling and the object-storage backend) — already reconstructed separately; touch only where a curated **dataset backs an object type** (the datasource→object-type handoff, restricted-view-backed objects, materializations as pipeline inputs). The **app-building layer**, **AIP**, and **Apollo**. High-level **philosophy/marketing**.

## Research question bank

Answer **every** question you can substantiate; for any you cannot, record it explicitly as a known unknown. Organize findings under these headings.

**A. Connectivity & sources (Data Connection / Magritte)**
1. The **source** and **connector** model; the **capability** abstraction; how the documented 200+ connectors are structured; examples across JDBC, cloud object storage (S3/GCS/Azure), SFTP/file, REST, streaming (Kafka), SAP, Salesforce, etc.
2. **Agents**: the agent-proxy ("thin mode") network-tunnel architecture vs. the **agent worker** (data-processing) mode; how the **Agent Manager** connects back to **magritte-coordinator**; when an agent is required vs. a **direct/cloud** connection.
3. The **Foundry worker** isolated-container execution model; **egress policies** (direct-connection vs. agent-proxy); credential/secret storage and rotation.
4. **Virtual tables** (federation): backing object types/datasets without ingest; supported external formats (Delta, Iceberg, BigQuery, etc.); update detection; trade-offs vs. ingested datasets.
5. **Exports** and **interactive/external requests** (data out of Foundry, calls to external systems).

**B. Ingestion & sync**
6. **Sync types** — batch, incremental, streaming/CDC — and how each is configured and scheduled.
7. **Schema inference** on ingest; handling of file formats; raw/unstructured ingestion.
8. How ingestion maps to the **dataset transaction model** (which sync produces SNAPSHOT vs. APPEND).

**C. Dataset & storage model**
9. The **dataset** as the fundamental unit: what it physically is (files + metadata), the backing **file format** (Parquet/Avro?), and the **catalog/transaction service** that versions it.
10. The **four transaction types** (SNAPSHOT/APPEND/UPDATE/DELETE): exact semantics, when each is used, and how they compose into the current "view."
11. **Branches**: the branching model (default/master vs. feature branches), how transforms and schedules target branches, and merge/promotion.
12. **Schemas**: where schema lives, schema evolution rules, and type system; **views** and dataset views.
13. Dataset **RIDs**, file structure, partitioning, and any size/scale limits.

**D. Transforms & authoring**
14. The **transform** abstraction and the **transforms API**: `@transform`, `@transform_df`, `transform_pandas`, inputs/outputs, and the `@incremental` decorator with `strict_append` and snapshot/append semantics.
15. **Languages/runtimes**: PySpark, Python (non-Spark/"lightweight"), Java, SQL; **container transforms**; how each is authored in **Code Repositories** and released.
16. **Pipeline Builder**: the no-/low-code model, its **computation modes** (batch snapshot vs. incremental), and how it relates to or compiles into transforms; parity and trade-offs vs. code.

**E. The Build system & orchestration**
17. The **build graph/DAG**: how jobs are defined, scheduled, and executed; the orchestration service.
18. **Scheduling & triggers**: time-based schedules, event/transaction-triggered builds, streaming builds; retries/aborts.
19. The **incremental-compute engine**: how incrementality is determined (input transaction types since last run), maintained, and invalidated (e.g., a SNAPSHOT input forcing a full rebuild); state/checkpointing.
20. **Compute backends**: Spark and **Spark profiles** (executor/driver config), non-Spark/lightweight compute, container compute; how compute is selected.
21. **Build compute metering** (compute-seconds) and performance/optimization levers.

**F. Data quality & lineage**
22. The **data-health / checks / Expectations** framework: built-in checks (schema, freshness, row-count) and custom checks; enforcement (warn vs. block); where checks run.
23. The **lineage/provenance** graph: how end-to-end lineage from source → dataset → transform → object is tracked, stored, and surfaced.
24. Pipeline **monitoring/alerting** and health surfaces.

**G. Governance in the data layer**
25. **Markings/classifications** on datasets and how they propagate downstream through transforms.
26. **Restricted views** (row-level) and column-level controls at the dataset layer; how they relate to Ontology object security.
27. **Projects/folders**, the resource hierarchy, roles/permissions, and dev→prod separation.

**H. Compute, performance & metering**
28. Spark execution model within Foundry; profiles; partitioning/optimization; documented limits.
29. The compute-metering model for builds and how it compares across compute backends.

**I. APIs/SDK, internal architecture & history**
30. The **datasets** and **transforms** APIs and foundry-platform SDK data endpoints (read/write transactions, branches, schemas) with representative shapes.
31. The named **internal services/architecture**: **magritte-coordinator**, the **catalog/transaction** service, **schema** service, the **build-orchestration** service, the Foundry file system — verify names and roles.
32. **History/evolution**: the Build → modern orchestration evolution, Pipeline Builder's introduction, lightweight transforms, virtual tables; and any **patents** touching data integration/versioned-dataset/lineage methods.

## Source strategy (prioritized)

1. **Primary — official docs:** `palantir.com/docs/foundry/**`, especially `data-connection/**` (architecture, core-concepts, agents, agent-proxy, agent-worker), `available-connectors/**`, `data-integration/**` (datasets), `transforms-python/**`, `transforms-python-spark/**`, `api-reference/transforms-python-library/**`, `pipeline-builder/**`, `building-pipelines/**`, `data-health/**` (or checks/expectations), `datasets/**`, `optimizing-pipelines/**` (Spark), and the `api` reference for datasets.
2. **Primary — engineering blog & talks:** `blog.palantir.com`; Palantir Developers / AIPCon YouTube (data-integration / Magritte / pipeline architecture).
3. **Primary — source & API refs:** `github.com/palantir` (foundry-platform SDKs, transforms libraries, Conjure specs), the public API reference.
4. **Primary — patents & filings:** Google Patents / USPTO for data-integration / versioned-dataset / lineage methods.
5. **Primary — training:** `learn.palantir.com`.
6. **Secondary — credible third parties:** consultancy/engineering deep-dives, ex-Palantir engineers, conference write-ups.
7. **Tertiary — community:** r/palantir, Hacker News, Stack Overflow — leads and corroboration only.

Always prefer **primary, recent, version-stamped** sources. Capture URL + access date for everything.

## Reverse-engineering methodology & rigor

- **Triangulate** every non-trivial claim across ≥2 independent sources where possible.
- **Tag every claim** — **[Documented]** / **[Inferred]** / **[Speculative]** — plus **confidence** (High/Medium/Low) and an inline citation.
- **Separate current from legacy** where relevant; date-stamp version-specific facts; flag features still in development.
- **Flag contradictions** between sources explicitly.
- **Never fabricate** connector names, transaction semantics, API methods, service names, or limits. Where the record is silent (e.g., the exact physical file layout or the orchestration service's internals), say so and give a single best-supported hypothesis labeled **[Speculative]**.
- **Chase named mechanisms** to source: Magritte / **magritte-coordinator**, Foundry worker, agent-proxy/agent-worker, capabilities, virtual tables, the four transaction types, `@incremental`/`strict_append`, Spark profiles, the Expectations/checks framework. **Verify** the catalog/transaction and build-orchestration service names and the physical file format.

## Required output structure

Produce one long-form technical report:

1. **Executive summary** (≈1 page) — the data layer in a nutshell + the 5–10 most important reverse-engineering findings.
2. **Connectivity & ingestion** (Data Connection / Magritte) — sources, capabilities, agents, workers, egress; a connector/capability table.
3. **Dataset & storage model** — a **transaction-type table** (SNAPSHOT/APPEND/UPDATE/DELETE), branches, schemas, physical storage.
4. **Transforms & authoring** — the transforms-API surface, languages/runtimes, Pipeline Builder, with code snippets where available.
5. **The Build system & orchestration** *(most technical)* — build graph, scheduling/triggers, the incremental engine, compute backends, metering.
6. **Data quality & lineage** — the checks/Expectations framework and the lineage graph.
7. **Governance in the data layer** — markings, restricted views, projects/roles, downstream propagation.
8. **Compute, performance & metering.**
9. **APIs / SDK & internal architecture** — datasets/transforms endpoints and the named services.
10. **History & patents** — provenance and a change timeline.
11. **Glossary** of Palantir-internal data-layer terms.
12. **Confidence & gaps register** — claims with evidence label + confidence, plus an explicit **known-unknowns** list and the source that would resolve each.
13. **Source bibliography** — URLs + access dates, grouped by tier.

Use **tables** for every enumeration (connectors/capabilities, transaction types, sync types, transforms-API decorators, compute backends, checks, limits, endpoints). Favor precise mechanics over prose. Quote exact semantics and limits **verbatim** where they exist.

## Exhaustiveness bar (definition of done)

Do **not** stop at the conceptual overview. For each mechanism, drill until you can either (a) describe it concretely with a primary citation, or (b) explicitly record it as a known unknown with a best-supported hypothesis and the missing source. Pay special attention to the **transaction model**, the **incremental-compute engine**, and the **agent/worker connectivity architecture** — these are the make-or-break details for a clone. Aim for the depth of a detailed technical white paper; cite extensively. Neutral, technical tone; no marketing language.

## Confirmed starting leads (verified — begin here, then expand)

*Confirmed to exist as of mid-2026; treat as entry points and verify currency.*

- **Data Connection architecture & core concepts:** `palantir.com/docs/foundry/data-connection/architecture`, `…/data-connection/core-concepts`
- **Agents:** `…/data-connection/set-up-agent`, `…/agent-configuration-reference`, `…/agent-proxy` (agent "thin mode"), `…/agent-worker`, `…/agents-troubleshooting` — and the internal **magritte-coordinator** the Agent Manager connects back to
- **Available connectors:** `palantir.com/docs/foundry/available-connectors/…`
- **Datasets / transactions:** `palantir.com/docs/foundry/data-integration/datasets` (SNAPSHOT / APPEND / UPDATE / DELETE)
- **Transforms (Python / Spark):** `…/transforms-python/transforms-python-api`, `…/transforms-python-spark/transforms-python-api`, `…/api-reference/transforms-python-library/api-incremental`
- **Incremental transforms:** `…/transforms-python/incremental-usage`, `…/building-pipelines/maintaining-incremental-performance` (`@incremental`, `strict_append`)
- **Pipeline Builder:** `…/pipeline-builder/datasets-computation-modes-for-batch`
- **Spark concepts:** `palantir.com/docs/foundry/optimizing-pipelines/spark-concepts`

**Named mechanisms to chase to source:** **Magritte** / **magritte-coordinator** · **Foundry worker** (isolated container) · **agent-proxy** ("thin mode") / **agent worker** · source **capabilities** · **virtual tables** (federation) · the four transaction types **SNAPSHOT / APPEND / UPDATE / DELETE** · **`@incremental`** / **`strict_append`** · **Spark profiles** · **Code Repositories** · **Pipeline Builder** computation modes · *(verify)* the **catalog/transaction** service name · *(verify)* the **schema** service · *(verify)* the **build-orchestration** service name · *(verify)* the **data-health / Expectations** framework name · *(verify)* the physical **file format** (Parquet/Avro) · *(find)* data-integration / versioned-dataset / lineage **patents**.

# ▲▲▲ PASTE TO HERE ▲▲▲
