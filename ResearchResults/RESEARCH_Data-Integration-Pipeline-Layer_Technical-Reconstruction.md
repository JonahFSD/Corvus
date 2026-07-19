---
**Artifact:** Deep-research output — technical reconstruction of Foundry's *data integration & pipeline* layer.
**Produced:** 2026-06-13, by a deep-research agent run on `DEEP-RESEARCH-PROMPT_Data-Integration-Pipeline-Layer.md`.
**Independent spot-check (by Claude, 2026-06-13):** Confirmed **verbatim** against primary docs — the four-transaction model (SNAPSHOT/APPEND/UPDATE/DELETE), faster pipelines = **DataFusion (Rust)** + Velox native acceleration, and the **compute-seconds formula** (`max(vCPU, GiB/7.5) × seconds`, 7.5 GiB/core). The Magritte/agent-proxy connectivity model and Parquet/S3 storage also match prior findings. High-confidence.
**Read with care:** the **internal service `api_name` strings** (`foundry-catalog`, `foundry-metadata`, `foundry-schema-inference`, `build2`, `foundry-data-proxy`) come from the third-party open-source `foundry-dev-tools` SDK (emdgroup), *not* Palantir docs — the report flags these `[Inferred, Medium]`. The "200+" connector count is marketing-approximate. Exact physical file-layout internals remain a known unknown. Numeric limits are Palantir-specific scale artifacts, not requirements for our clone.
---

# Reverse-Engineering the Palantir Foundry Data Integration & Pipeline Layer: A Functional-and-Architectural Reference

*Compiled from primary Palantir documentation, the public Foundry API reference, Palantir patents and engineering blog, and (for internal service names) the third-party open-source foundry-dev-tools SDK. Access date: June 13, 2026. Evidence tags: [Documented] = primary Palantir source; [Inferred] = derived/third-party; [Speculative] = best hypothesis where the record is silent.*

## 1. Executive Summary

Foundry's data foundation is a **versioned, transaction-based dataset store ("Git for data")** fronted by a connectivity layer (Data Connection / Magritte), authored over by a transform layer (Code Repositories + Pipeline Builder), and driven by a data-driven build orchestrator (internally "Build2"). The unit of currency is the **dataset**: a wrapper around files in a backing Hadoop FileSystem (commonly S3), with Parquet as the default structured format, versioned by four transaction types (SNAPSHOT, APPEND, UPDATE, DELETE).

Most important reverse-engineering findings:

1. **The transaction model is the keystone.** Every dataset is a linear sequence of transactions per branch; the "current view" is computed by replaying transactions from the latest SNAPSHOT forward. This single mechanism underlies versioning, incrementality, branching, and retention. [Documented, High]
2. **Incrementality is derived, not declared.** The `@incremental` decorator reads build history from output datasets and inspects the transaction types committed to inputs since the last run. Append-only (APPEND/UPDATE-add) → incremental; SNAPSHOT or file-modifying UPDATE/DELETE → forced full rebuild (unless marked `snapshot_inputs` / `allow_retention`). [Documented, High]
3. **Connectivity has two orthogonal axes: networking (how) and worker (where).** Modern "Foundry worker" runs connector code in an isolated Foundry-side container; the legacy "agent worker" runs Java on a customer host. The agent-proxy ("thin mode") makes the agent a pure network tunnel via websocket back to `magritte-coordinator`. [Documented, High]
4. **Internal services are identifiable:** the catalog/transaction service (`foundry-catalog`/Catalog), schema store (`foundry-metadata`) plus inference (`foundry-schema-inference`), build orchestrator (`Build2`, public `api/v2/orchestration`), and byte-level data proxy (`foundry-data-proxy`). [Documented public APIs / Inferred internal names from third-party SDK, Medium-High]
5. **Pipeline Builder compiles to a general transform backend, not to user code.** Per Palantir docs it "uses a next-generation data transformation backend specifically designed to act as an intermediary between logic creation and execution," targeting multiple engines (Spark, Flink, and a Rust/DataFusion "faster pipelines" engine) behind a point-and-click graph. [Documented, High]
6. **Governance propagates with the data.** Markings propagate downstream through transforms automatically; restricted views and granular policies enforce row-level security on the backing dataset; Projects are the primary security boundary. [Documented, High]
7. **Compute is metered in compute-seconds** = `max(num_vcpu, GiB_RAM/7.5) * seconds`, summed across driver + executors (7.5 GiB-per-core default memory-to-core ratio). [Documented, High]
8. **Virtual tables provide no-copy federation** over Delta/Iceberg/BigQuery/Snowflake/Databricks with optional compute pushdown. [Documented, High]

---

## 2. Connectivity & Ingestion (Data Connection / Magritte)

### 2.1 Core concepts: sources, capabilities

A **Source** represents a single connection to an external system. Sources expose **capabilities** — discrete functionalities that run over the connection. The documented capability families are: ingesting data into Foundry, pushing data out of Foundry, virtualizing externally-stored data, and making interactive requests to other systems. [Documented, High]

Foundry advertises a large connector library (its source-type overview page enumerates connector families but publishes no single authoritative total — a precise "200+" count is not corroborated by a named primary source and should be treated as approximate marketing language). The source-type families are:

| Family | Example connectors |
|---|---|
| Cloud object storage / file | Amazon S3, OneLake/Azure Blob Filesystem (ABFS), Google Cloud Storage, HDFS, SMB, SFTP, FTP/FTPS, SharePoint Online, Agent-level filesystem |
| Relational (JDBC) | Microsoft SQL Server, Oracle, PostgreSQL, MySQL, MariaDB, IBM Db2, Informix, SQLite, Sybase, Vertica, Amazon Athena, Hive |
| Cloud data warehouses | AWS Redshift, Azure Synapse, BigQuery, Databricks, Netezza, Snowflake, Teradata |
| Enterprise apps | SAP (ERP/ECC/S4 HANA), Salesforce, Oracle NetSuite, HubSpot |
| Streaming/messaging | Apache Kafka, ActiveMQ, Amazon Kinesis, Amazon SNS, Amazon SQS, Google Pub/Sub, MQTT, RabbitMQ, Solace |
| NoSQL | Amazon DynamoDB, Azure Cosmos DB, Apache HBase, Cassandra, CouchDB |
| Foundry-to-Foundry | Foundry connector (one enrollment as a source on another) |

Each connector page lists supported capabilities (e.g., Exploration, batch sync, incremental sync, streaming sync, exports, virtual tables). [Documented, High]

### 2.2 Agents: agent-proxy ("thin mode") vs agent worker

An **agent** is a downloadable program (Java, runs on its own JDK compiled for Linux/x86-64; RHEL 8+/Ubuntu 22.04+ recommended) installed inside the customer network and managed from Data Connection. Connectivity decomposes into two orthogonal axes [Documented, High]:

- **Networking (how target is reached):** direct connection egress policies (Foundry → internet-reachable system) vs. agent-proxy egress policies (route through agent for private networks). Agent proxy policies are only available on enrollments running on **Rubix**, Palantir's Kubernetes-based infrastructure.
- **Worker (where compute runs):** **Foundry worker** (isolated Foundry-side container) vs. **agent worker** (legacy; code runs on the customer host).

**Architecture details by mode:**

| Mode | Network path | Where compute runs | Credentials | Status |
|---|---|---|---|---|
| Direct connection (Foundry worker) | Foundry → system over internet; system must accept inbound from Foundry; egress managed in-platform | Foundry worker (isolated container, scalable compute) | AES-256-GCM server-side encryption; decryptable only by containers triggered by authorized users | Recommended |
| Agent-proxy ("thin mode" / "agent proxy") | Agent initiates outbound **websocket** to Foundry; agent acts as pure network tunnel, no data processing | Foundry worker; communicates with external system via the websocket | AES-256-GCM server-side encryption | Recommended for private/on-prem |
| Agent worker ("thick mode") | Agent polls Foundry via unidirectional outbound HTTPS for tasks; networking configured on agent host (firewalls/DNS/proxy); Foundry egress policies do NOT apply | Java code on the agent host directly | AES-128-GCM encryption with keys stored on the agent; decrypted locally in-memory, deleted after execution; credentials encrypted in browser with each agent's public key | Legacy (no further development; full support remains) |

The **Agent Manager** connects back to Foundry's `magritte-coordinator`. Connectivity is validated with `curl -s https://<domain>/magritte-coordinator/api/ping`. The Agent Manager runs as `magritte-bootvisor`; a **Bootstrapper** also connects to `magritte-coordinator`. Proxy settings for the Agent-to-Foundry path are configured in both Agent and Bootstrapper configs (`runtime.yml`, with a `service-discovery: services: magritte-coordinator:` block). [Documented, High]

**Data upload modes for agents:** "data proxy mode" (default; uploads via the public Foundry API gateway, the data proxy service) and the older "direct mode" (uploads directly to underlying storage buckets in the Foundry data catalog; not available on new agents/enrollments after June 2024). [Documented, High]

High availability is offered at the source level: a source assigned to multiple agents will have ingestions dispatched to a healthy agent. [Documented, High]

### 2.3 Foundry worker isolated-container model & egress

All data-connection and computation capabilities in modern connections execute in a **Foundry worker** — "an isolated container with scalable compute resources that processes data and communicates with external systems via the provided websocket." Network egress from Foundry is administered in-platform via direct-connection egress policies (and agent-proxy egress policies when routing through an agent). Both can be assigned to the same source (e.g., fetch credentials from an internet system, then use them on an on-prem system). [Documented, High]

### 2.4 Virtual tables (federation / no-copy)

Virtual tables let Foundry query tables in external platforms **without first storing the data in a Foundry dataset** — a virtual table is a pointer to an external table. [Documented, High]

- **Supported sources/formats:** Delta Lake, Apache Iceberg (via Iceberg catalogs, incl. Databricks Unity Catalog), BigQuery, Databricks, Snowflake, S3/GCS/ABFS (Avro/CSV/Parquet). Require a **Foundry worker** source (agent worker not supported).
- **Update detection:** Foundry polls the source on a schedule; if the source format supports versioning (Delta, Iceberg) Foundry detects changes and only triggers downstream builds when necessary; otherwise every poll is a potential update (risking unnecessary builds). Once enabled, a virtual table input can be used as a schedule trigger.
- **Registration:** individual, bulk (tabular sources like Databricks/BigQuery/Snowflake), or automatic (periodic registration of all accessible tables into a designated project).
- **Compute modes:** Foundry-native Spark compute (can combine multiple sources + Foundry datasets; no lightweight Polars/Pandas engines), or **compute pushdown** (all inputs/outputs must be virtual tables on the same pushdown-compatible source; e.g., BigQuery uses the BigQuery Spark connector with predicate pushdown; Databricks via Databricks Connect). Incremental via `@incremental` is not supported with compute pushdown. Delta incremental relies on Change Data Feed; Iceberg on incremental reads.
- **Trade-offs:** no ingest/storage cost and always-current; but reads depend on source availability/network, lack Foundry's full transactional/versioning guarantees, and incremental support is constrained.

The transforms-tables library (`TableInput`/`TableOutput`, `DatabricksTable`, `BigQueryTable`, etc.) writes virtual-table outputs; output sources are referenced by `ri.magritte..source.<id>`. [Documented, High]

### 2.5 Exports & interactive/external requests

- **Exports** push data out of Foundry: file export, streaming export, table export, or legacy export tasks (availability varies by connector). Table exports to JDBC use fixed `INSERT` syntax; the exported dataset's underlying files must be in **Parquet** for tabular destinations; column names/types must match 1:1 (case-sensitive).
- **Export governance:** exports are controlled by markings. An Information Security Officer must enable exports and specify exportable markings/organizations; exporting is treated as equivalent to removing markings (requires unmarking permission). Legacy export tasks are NOT integrated with marking controls.
- **Interactive/external requests:** webhooks, listeners (HTTPS, WebSocket, email, Pub/Sub, Jira, Slack), and **external transforms/functions** (`@external_systems`, `Source`, `EgressPolicy`, `Credential`) let code call external systems. REST API sources use a built-in Python `requests` client.

---

## 3. Dataset & Storage Model

### 3.1 The dataset abstraction & physical storage

A dataset is "a wrapper around a collection of files which are stored in a backing file system." The files are **not stored in Foundry itself**; instead a mapping is maintained between a file's logical Foundry path and its physical path in a backing **Hadoop FileSystem** — self-hosted HDFS or, more commonly, cloud object storage such as **Amazon S3**. Structured data is stored as files in an open-source format such as **Parquet** (Parquet is the default output format for Transforms); schema is stored as metadata alongside the dataset. [Documented, High]

Foundry exposes datasets via an S3-compatible API where the bucket = dataset RID (`ri.foundry.main.dataset.<uuid>`) and Parquet files live under a `spark/` prefix. [Documented, High]

### 3.2 Transaction model — the four transaction types

A transaction is "analogous to a commit in Git: an atomic change to the contents of a dataset." Transactions are serialized and ACID-compliant. [Documented, High]

| Type | Semantics | Primary use |
|---|---|---|
| **SNAPSHOT** | Replaces the current view with a completely new set of files. Begins a new view. | Batch pipelines; full reloads |
| **APPEND** | Adds new files to the current view; cannot modify existing files (commit fails if existing files overwritten). | Incremental ingest/computation |
| **UPDATE** | Adds files to the view and may replace existing files. | Upserts; file-level updates |
| **DELETE** | Removes file references from the view (does not delete underlying files from backing FS). | Retention / governance-driven deletion |

API enum values: `APPEND, UPDATE, SNAPSHOT, DELETE`; transaction status: `OPEN, COMMITTED, ABORTED`. Transactions carry `rid` (`ri.foundry.main.transaction.<uuid>`), `transactionType`, `status`, `createdTime`, `closedTime`. [Documented, High]

**View computation algorithm** (verbatim semantics): start with an empty file set; the view begins at the latest SNAPSHOT before the point in time (or the earliest transaction if no SNAPSHOT). For SNAPSHOT (only first) or APPEND, add all the transaction's files; for UPDATE, add files and replace existing ones; for DELETE, remove referenced files. Aborted transactions contain no data and are excluded. [Documented, High]

### 3.3 Branches

Branches are "simply a pointer to the most recent transaction on that branch" — a branch is a linear sequence of transactions ordered by commit time. Changes on one branch leave other branches' views unaltered. **Unlike Git, there is no support for merging dataset branches.** Each branch has exactly one parent (unless a root branch); most datasets have a single root branch called `master`. Deleting a branch re-parents its children. [Documented, High]

**Branching in builds:** committing transform code publishes JobSpecs to the branch. A build specifies branch **fallbacks** (e.g., `develop → master`): if no JobSpec exists on the build branch, it reads from the fallback. Dataset icon color signals JobSpec presence (gray = no JobSpec on master; blue = JobSpec present). [Documented, High]

### 3.4 Schemas & schema evolution

A schema is "metadata on a dataset view that defines how the files within the view should be interpreted" — parsing rules and column names/types. Schemas can be applied manually to CSV/JSON (auto-inferred from a subset), or inferred dynamically as the first step of a pipeline on semi-structured data. The schema store is internally the `foundry-metadata` service; inference is `foundry-schema-inference`. For incremental dynamic schemas, new columns must be type-compatible with existing output columns (same-named columns must share type). Note: JDBC timestamp columns are cast to `long` for backwards compatibility — clean in a downstream transform. [Documented, High]

### 3.5 Views (virtual datasets)

A **View** behaves like a dataset but holds no files — it is the union of backing datasets, computed at read time, with optional primary-key deduplication. Views build near-instantly (no data moved). Views can be transform **inputs** but not outputs, and require schemas. Views can be used to **stop marking propagation** (mandatory-control markings only; not Organizations). [Documented, High]

### 3.6 RIDs, partitioning, scale

Resource Identifiers follow `ri.<service>.<instance>.<type>.<locator>` (instance usually `main`): datasets `ri.foundry.main.dataset.<uuid>`, transactions `ri.foundry.main.transaction.<uuid>`, builds `ri.foundry.main.build.<uuid>`, jobs `ri.foundry.main.job.<uuid>`, sources `ri.magritte..source.<id>`, schedules `ri.scheduler.main.schedule.<uuid>`, folders `ri.compass.main.folder.<uuid>`. Many small files (from many APPEND transactions) degrade read/write performance; remedies include **dataset projections** (independently-stored, compacted query representations that break out of the append-only model and reorganize data as volume grows — readers transparently combine projection + canonical data) and Foundry Retention. [Documented, High]

---

## 4. Transforms & Authoring

### 4.1 The transform abstraction & Python transforms API

A Foundry Transform defines a mapping from input datasets to output datasets, encapsulating both compute logic and resource requirements as a declarative unit registered in a Pipeline. [Documented, High]

| Decorator / API | Behavior |
|---|---|
| `@transform` | Injects `TransformInput`/`TransformOutput` objects (access to DataFrame and filesystem). Supports multiple inputs/outputs. Keyword names map to function params. |
| `@transform_df` | Single positional `Output`; inputs as kwargs; compute returns a PySpark DataFrame written to the single output. |
| `@transform_pandas` | Converts inputs to `pandas.DataFrame`, returns pandas (must fit in memory). |
| `@transform.using` / `@transform.spark.using` | Modern syntax (transforms ≥3.68.0 / ≥3.95.0). Default single-node (lightweight, Polars/pandas); `.spark.using` for PySpark. |
| `@configure(profile=[...], allowed_run_duration=...)` | Sets Spark profile(s) and a job timeout (polled every 5 min). |
| `@incremental(...)` | Converts inputs/outputs into incremental counterparts (see §5.3). |
| `@lightweight` | Runs without Spark on a single node (pandas + filesystem API); supports BYOC (`container_image`/`container_tag`/`container_shell_command`). |

`@incremental` parameters: `snapshot_inputs` (SNAPSHOT on these does not invalidate output; read in full/current view only), `allow_retention` (retention DELETEs don't break incrementality), `strict_append` (forces APPEND transaction type for incremental writes; overwrite raises), `require_incremental` (fail rather than run non-incrementally, except first build or `semantic_version` bump), `v2_semantics` (recommended True; required for non-Catalog incremental inputs/outputs), `semantic_version` (bump forces full recompute). Read modes: `added` (default), `current`, `previous`; write modes: `modify` (default incremental, appends) vs `replace` (default non-incremental). [Documented, High]

### 4.2 Languages/runtimes & Code Repositories

- **PySpark / Python (Spark):** distributed; configured with Spark profiles.
- **Python (lightweight/non-Spark):** single-node Polars/pandas; "faster and more cost-effective for small-to-medium data"; can process terabyte-scale on a single node for suitable transforms.
- **Java / Mesa** (a proprietary Java-based DSL).
- **SQL transforms** (e.g., `CREATE TABLE ... TBLPROPERTIES (foundry_transform_profiles = '...')`).
- **Container transforms** (BYOC) via `@lightweight` with container args.

Code is authored in **Code Repositories** (Git-backed; commit publishes JobSpecs; Preview runs on sampled inputs without committing). TLLV ("transform-level logic versioning") requires module-level imports. Releases follow dev→prod branch flow (§7). [Documented, High]

### 4.3 Pipeline Builder (no-/low-code)

Pipeline Builder is Foundry's primary data-integration app: a point-and-click graph/form interface. Per Palantir docs it "uses a next-generation data transformation backend specifically designed to act as an intermediary between logic creation and execution" — i.e., it compiles to a general transformation backend rather than to user code, and is engine-independent ("Spark, Flink, Azure instances, and more"). Key properties: type-safe functions (errors flagged before build), strict output checks, automatic build-path pruning, export-to-code, full version control/branching, media + LLM/AIP transforms. Outputs can be datasets, object types, link types, streams, time-series, or exports. [Documented, High]

**Computation modes (batch):** snapshot (transforms entire input; output fully replaced) vs incremental (only new APPENDed data). Restrictions in incremental mode: all union inputs must share a mode; window functions/aggregations/pivots operate on the current transaction only; "replay on deploy" reprocesses prior transactions (only full-input replays supported). Only Python and Java APIs support incremental computation. [Documented, High]

**Faster pipelines** (formerly "lightweight pipelines"): per Palantir docs they "use a backend powered by DataFusion, an open-source query engine written in Rust." Accelerates batch and incremental pipelines; unsupported features include LLM, geospatial, and media-set operations; minor numeric/semantic differences (e.g., decimal overflow throws an error instead of outputting NULL; floating-point last-digit variance). [Documented, High]

---

## 5. The Build System & Orchestration (Most Technical)

### 5.1 Build graph / jobs / orchestration service

The orchestration model is **data-driven**: dependencies are defined between datasets (via transforms), and Foundry builds a directed graph of datasets/transforms. [Documented, High]

- **Build:** "the mechanism used to compute new versions of datasets"; provides orchestration/coordination, reads inputs, writes outputs.
- **Job:** "a unit of work defined by shared logic that computes one or more output datasets." Multi-output jobs always build together. A job is a single transform producing one (or several) datasets, broken into Spark stages.
- **JobSpec:** "a definition of how a job should be constructed," published when transform logic is committed.
- **Job states:** `WAITING, RUN_PENDING, RUNNING, ABORT_PENDING, ABORTED, FAILED` (and success).
- **Build status (public API):** `RUNNING, SUCCEEDED, FAILED, CANCELED`.

The internal service is **Build2** (`Build2Client` with `api_submit_build`, `api_get_jobspec_for_dataset`, `api_remove_jobspecs`, `api_get_build_report`/`api_get_job_report`); the public API surface is `api/v2/orchestration/builds/ri.foundry.main.build.<uuid>` (OAuth scope `api:orchestration-read`). [Documented public API / Inferred internal name, Medium-High]

**Staleness:** an output is "fresh" if inputs and JobSpec logic are unchanged since the last build; fresh datasets are skipped. **Force build** recomputes regardless. Some sources (Object Storage V1 / Phonograph syncs, transforms with API calls, Data Connection syncs) may not show as stale and need Force Build. [Documented, High]

### 5.2 Scheduling & triggers

**Schedules** run builds over time. Trigger types: time-based (cron-like), event/transaction-based (build when an input updates; "wait until all these datasets update" option), and streaming/continuous. Schedule targets can be manual (`targetRids`) or connecting-build based. Scope modes: **user-scoped** (outputs discovered by requesting user's permissions — risky if permissions change) vs **project-scoped** (recommended). [Documented, High]

**Retries/aborts:** `retryCount` + `retryBackoffDuration` (recommended ≥3 retries, ≥1 min apart); `abortOnFailure` ("Abort build on failure" cancels other jobs when one fails). Even without configured retries, jobs may be retried during adjudication. The build-orchestration layer relaunches retriable failed jobs without failing the build. [Documented, High]

### 5.3 The incremental-compute engine

This is the make-or-break mechanism. The `@incremental` decorator "reads build history from the output datasets to determine the state of the inputs at the time of the last build." It performs a validation step before execution. [Documented, High]

**Incrementality determination:** a transform runs incrementally **iff** all non-`snapshot_inputs` inputs had only files added (APPEND, or UPDATE that does not modify existing files) since the last run — or files deleted only via Foundry Retention with `allow_retention=True`. A transform CANNOT run incrementally if any incremental input was: fully rewritten (SNAPSHOT), or had files modified/deleted via UPDATE/DELETE (non-retention). [Documented, High]

**State/checkpointing:** "we load all the past transactions on the input datasets from the last SNAPSHOT transaction to build the input view." The engine compares the **unprocessed transactions range** against the **processed transactions range**; if the branch HEAD has moved into an inconsistent state, it raises `Catalog:TransactionNotInView`. (Documented diagram: processed range (1)–(5), HEAD at (7), current view {1,2,6,7}.) [Documented, High]

**Invalidation:** a SNAPSHOT input forces a full rebuild; bumping `semantic_version` forces full recompute; first build of a never-built output runs non-incrementally even with `require_incremental=True`. [Documented, High]

**Write semantics:** incremental output default write mode `modify` (appends); non-incremental default `replace`. `strict_append=True` forces APPEND transaction type (overwrite raises; non-incremental falls back to SNAPSHOT unless `require_incremental=True`). Media sets (`transforms.mediasets`) support incremental too. [Documented, High]

### 5.4 Compute backends & selection

| Backend | Use | Selection |
|---|---|---|
| Spark (distributed) | Default for code-repo batch compute; SQL/Python/Java/Mesa | Default if no override |
| Lightweight / single-node (Polars/pandas) | Small-to-medium (and some TB-scale) | `@lightweight` / `@transform.using` |
| Container (BYOC) | Custom runtimes | `@lightweight(container_image=...)` |
| DataFusion ("faster pipelines") | Pipeline Builder acceleration | Pipeline type toggle |
| Flink | Streaming | Streaming pipelines |

Spark native acceleration via **Velox** (off-heap memory) is available for batch pipelines (requires off-heap memory configuration). [Documented, High]

### 5.5 Build compute metering

See §8.2. [Documented, High]

---

## 6. Data Quality & Lineage

### 6.1 Health checks / Expectations framework

Two related mechanisms:

- **Health checks** (Data Health): jobs generated on a dataset to validate characteristics. Categories: **job-level** (job status), **build-level** (build status, schedule status, schedule duration), **freshness** (data freshness, sync freshness, time-since-last-updated), **content/schema** (row count, column value allow-lists, regex match, uniqueness/primary-key, column similarity, file count, partitioning performance, transaction file count/size). Checks can evaluate against the last successful check result. The three freshness checks differ precisely: *time since last updated* (time since last transaction, even empty), *data freshness* (last transaction vs max of a timestamp column; only on commit), *sync freshness* (latest sync vs max datetime column). [Documented, High]
- **Data expectations** (build-time, defined in code/Pipeline Builder): run during build. Pipeline Builder currently supports **primary key** (no nulls + uniqueness of column combination) and **row count** (min/max). **If any expectation fails, the build fails** (block, not warn). Health checks (job-finish-dependent) typically warn/alert. [Documented, High]

**Monitoring at scale / monitoring views:** monitors emit metrics over a scope (single resource, Project, or multiple Projects); consecutive-schedule-failure and schedule-duration monitors replace some health checks; content/freshness/schema checks and data expectations remain health-check-only. [Documented, High]

### 6.2 Lineage / provenance graph

Foundry maintains a dependency graph recording relationships between components. The data lineage graph traces source → dataset → transform → object (and downstream Workshop apps), is branch-aware (with fallback branches), and supports save/share/export-to-SVG. The dependency graph: computes out-of-date datasets, does look-ahead schema-conflict detection, is the skeleton for data-health checks, drives lineage visualization, and structures propagation of security/access controls. [Documented, High]

### 6.3 Monitoring/alerting surfaces

Build reports (Gantt of jobs → stages), Spark details (stage timeline, parallelism ratio, disk spillage, shuffle write, executor stack traces/memory histograms), live logs (real-time), the Builds application, schedule Run History/Versions tabs, and Resource Management usage metrics. [Documented, High]

---

## 7. Governance in the Data Layer

### 7.1 Markings & propagation

**Markings** are mandatory controls (all-or-nothing): a user must satisfy all of a resource's markings to access it, regardless of role. **Markings propagate downstream** through transforms automatically — derived datasets inherit upstream markings; sharing derived data requires granting the marking. Propagation can be stopped only on **protected branches** via `stop_propagating`, or via Views (mandatory-control markings only). A common pattern is a "Raw Data" marking on raw ingests. Projects also have a "Propagate View Requirements" setting (disabled by default on new Projects) governing whether downstream viewers need upstream-project access. [Documented, High]

### 7.2 Restricted views (row-level) & column-level controls

**Restricted views** limit dataset access to only the rows a user may see, powered by **Granular Permissions / granular policies** (rules comparing user attributes, columns, values). A restricted view is built on a backing dataset and **cannot be used as a transform input**. Marking-backed restricted views: each row carries a STRING ARRAY of Marking IDs (annotated with the `marking_type.mandatory` typeclass). Restricted views can only be built on datasets (not streams). Column-level security uses markings on properties (e.g., PII/PHI). These relate to Ontology object security: each dataset row → object instance; restricted views + multi-data-source objects (MDOs) provide row/column permissioning for object types; **materializations** propagate backing-dataset markings (plus mandatory controls / Allowed markings / Allowed organizations / Max classification) to the materialized writeback dataset. (Materialized datasets carry `__`-prefixed metadata columns like `__is_deleted`, `__patch_offset`.) [Documented, High]

### 7.3 Projects/folders, roles, dev→prod

**Projects are the primary security boundary.** Default roles (most→least powerful): **Owner, Editor, Viewer, Discoverer**; each can grant equal-or-lesser roles. Roles inherit to child resources. Roles are sets of **operations** (e.g., `stemma:mutate-default-branch`). Spaces contain Projects; access requests route to Project Owners. Data Connection resources (agents/sources/syncs) are themselves resources organizable across Projects with markings; datasets produced by syncs can be imported downstream without sharing source/agent access (Edit on a source ≈ full access to the source's account credentials, so it must be tightly controlled). [Documented, High]

**Dev→prod branching:** feature branch → `dev` → `master` (production, protected; only release manager merges). Schema diffs reviewed in PRs (schema diff view in Affected Datasets); build on dev branch creates feature outputs via fallback logic. Foundry Branching extends this across datasets + Ontology + Workshop with review/approval and release management to test/prod environments. [Documented, High]

---

## 8. Compute, Performance & Metering

### 8.1 Spark execution & profiles

Spark drivers distribute work to executors. A **Spark profile** configures distributed compute resources via five variables: driver cores, driver memory (JVM only, not off-heap), executor cores, executor memory, number of executors. Profile families also configure `spark.executor.memoryOverhead` and dynamic allocation (`spark.dynamicAllocation.enabled/minExecutors/maxExecutors`). Defaults approximate the SMALL profiles: `EXECUTOR_CORES_SMALL, EXECUTOR_MEMORY_SMALL, DRIVER_CORES_SMALL, DRIVER_MEMORY_SMALL, NUM_EXECUTORS_2`. Special profiles: `KUBERNETES_OPEN_PORTS_ALL` (enables executor-to-executor networking for distributed model training). Profiles applied via `@configure(profile=[...])` (Python), `@TransformProfiles({...})` (Java), or `foundry_transform_profiles` TBLPROPERTIES (SQL); evaluated left→right with later winning. Dynamic allocation (Spark 3) auto-adjusts executor count. Best practice: bump one variable one level at a time. [Documented, High]

Optimization levers: reduce/filter data early, repartition vs coalesce, handle skew (broadcast join, salting), maximize parallelism, mind task overhead (30–60s per task ideal), managed profiles (auto scale-down based on last 5 builds), warm pools, Velox native acceleration. [Documented, High]

### 8.2 Compute-seconds metering

Foundry measures work in **compute-seconds**. Per Palantir docs, "the default memory-to-core ratio is 7.5 GiB per core," and compute-seconds are computed by "taking the maximum of two factors": `max(num_vcpu, gib_ram / 7.5)`. Per job: `driver_compute_seconds = max(num_vcpu, GiB_RAM/7.5) * seconds`; `executor_compute_seconds = num_executors * max(num_vcpu, GiB_RAM/7.5) * seconds`; total = driver + executors.

Worked example (per docs): a driver of 1 vCPU/6 GiB plus 4 executors of 1 vCPU/6 GiB running 120 seconds → `120 + 480 = 600 compute-seconds`. Compute-seconds are runtime not wall-clock (parallel jobs accrue multiple per wall-second). Different applications apply usage-rate multipliers (Contour interactive rate 15; streaming 0.5; time-series minimum 4 per query; compute-modules per-replica). Usage is recorded against the output dataset (split equally across multi-output jobs) and visible in Resource Management. Streaming: live processing (Flink job manager + task managers, statically allocated, consumes compute even with no data) plus periodic archive jobs (single Spark driver, 1 vCPU/4 GiB). [Documented, High]

### 8.3 Documented limits

Foundry-worker syncs that run >2 days are interrupted (recommend smaller files). JDBC fetch-size default suggested 500; Parquet writer in-memory buffer 128 MB, Avro 64 KB (max file size in bytes must be ≥2× buffer). JDBC precision limit rejects numerics >38 decimal places (optional). Contour/Quiver/Code Workbook CSV/XLSX export limit 100,000 rows. [Documented, Medium]

---

## 9. APIs / SDK & Internal Architecture

### 9.1 Public datasets & transforms APIs

Public REST under `/api/v1/datasets` and `/api/v2/datasets`:

- **Transactions:** `POST .../transactions?branchId=master` (create, body `{"transactionType":"SNAPSHOT"}`), `.../transactions/{rid}` (get), `.../transactions/{rid}/commit`, `.../transactions/{rid}/abort`.
- **Files:** `POST .../files/{filePath}` (upload; `Content-Type: application/octet-stream`; defaults branch `master`, transactionType `UPDATE`).
- **Schema:** `PUT /v1/datasets/{rid}/schema`, `.../getSchema?branchName=...&endTransactionRid=...`.
- **Read:** get dataset as table (export format ARROW or CSV; does not support Views).
- **Orchestration:** `/api/v2/orchestration/builds/{rid}`, schedules (create/get/pause/replace).

The **foundry-platform SDK** (`foundry_sdk` Python) exposes `client.datasets.Dataset.*` (create — a default `master` branch is created on the dataset; get_schema) and `client.orchestration.Schedule.*` (create with `action`={abortOnFailure, forceBuild, retryBackoffDuration, retryCount, fallbackBranches, branchName, notificationsEnabled, target}, get/pause/replace; scope_mode user vs project). [Documented, High]

### 9.2 Named internal services

| Service | Role | Evidence |
|---|---|---|
| `magritte-coordinator` | Data Connection coordinator; agents/Bootstrapper connect back to it via websocket | Palantir docs (agent config, ping endpoint) [Documented, High] |
| Catalog (`foundry-catalog` / `CatalogClient`) | Dataset/transaction/branch/view store; create dataset, start/commit/abort transaction, branches, files | Public datasets API; third-party SDK [Documented public / Inferred name, Medium-High] |
| `foundry-metadata` | Stores/serves dataset schemas (`api_upload_dataset_schema`, `api_get_dataset_schema`) | Third-party SDK verbatim `api_name` [Inferred, Medium] |
| `foundry-schema-inference` | Infers dataset schemas | Third-party SDK verbatim `api_name` [Inferred, Medium] |
| Build2 (`Build2Client`) | Build orchestration; JobSpec graph, submit build, reports | Third-party SDK + public `api/v2/orchestration` [Documented public / Inferred name, Medium-High] |
| `foundry-data-proxy` | Byte-level file read/write to the backing FS; the public data-proxy upload path | Third-party SDK + agent "data proxy mode" docs [Documented/Inferred, Medium] |
| Compass (`ri.compass.main.folder...`) | Resource/folder hierarchy (NOT the dataset store) | RID namespace [Documented, Medium] |
| Backing file system | Hadoop FileSystem base dir (HDFS or S3); Parquet default | Palantir docs [Documented, High] |

Caveat: internal `api_name` strings (`foundry-catalog`, `foundry-metadata`, `foundry-schema-inference`, `build2`, `foundry-data-proxy`) are sourced from the third-party open-source `foundry-dev-tools` (emdgroup) library, which reverse-engineers Foundry's private APIs — not official Palantir docs. The public REST API and architecture concepts (backing file system, Parquet, RIDs) are from palantir.com/docs.

---

## 10. History & Patents

### 10.1 Evolution

- **Magritte** is the long-standing Data Connection engine (agents, `magritte-bootvisor`/Bootstrapper, `magritte-coordinator`, sources `ri.magritte..source.*`). Agent worker ("thick mode") is the historical architecture; **Foundry worker** + agent-proxy is the modern recommendation; agent worker is legacy. "Direct mode" agent uploads were deprecated for new agents/enrollments after June 2024 in favor of data-proxy mode.
- **Build → modern orchestration:** the build system evolved to "Build2" (public `api/v2/orchestration`); the staleness/JobSpec model persists.
- **Pipeline Builder** introduced as the no-/low-code engine-independent backend (Spark + Flink), later adding **faster pipelines** (DataFusion/Rust; formerly "lightweight pipelines").
- **Lightweight transforms** (single-node, non-Spark) and **virtual tables** (federation) are more recent additions; **Iceberg tables** (managed + virtual, with Foundry natively implementing the Iceberg REST Catalog spec) are in Beta. Note divergent default-branch naming: Iceberg's `main` ≡ Foundry's `master`.

### 10.2 Patents

| Patent | Title / inventors | Relevance |
|---|---|---|
| US 10,853,338 | "Universal data pipeline" (granted 2020-12-01; App. 16/240,507; inventors Gustav Brodman, Lynn Cuthriell, Mark Elliot, Michael Garland, Michael Harris, Jonathan Hsiao, Hannah Korus, Jacob Meacham, Evelyn Nguyen, Brian Schimpf, Brian Toth) | History-preserving pipeline; "immutable and versioned datasets"; point-in-time recovery — the transaction/versioning model |
| US 9,996,595 | "Providing full data provenance visualization for versioned datasets" (granted 2018-06-12; filed 2016-02-09; inventors Quentin Spencer-Harper, Alexander Sparrow, Jose Riarola) | Provenance graph of versioned datasets (compound nodes + derivation-dependency edges) |
| US 2020/0210427 (app.) | "Column lineage and metadata propagation" | Column-level lineage from logical query plans; versioned transformation code |

The Palantir RFx blog ("Why Data Pipeline Version Control Matters") describes the dependency graph and ACID/serialized transaction requirements as the design rationale. [Documented, High]

---

## 11. Glossary

- **Source** — a configured connection to an external system.
- **Capability** — a function over a source (ingest in, push out, virtualize, interactive).
- **Agent** — customer-network program (Magritte) for connectivity.
- **Agent-proxy / thin mode** — agent as pure network tunnel (websocket to `magritte-coordinator`).
- **Agent worker / thick mode** — legacy; connector code runs on the agent host.
- **Foundry worker** — isolated Foundry-side container running connector/compute code.
- **Sync** — a task reading data from a source into Foundry (batch/incremental/streaming).
- **Dataset** — versioned wrapper around files in a backing FS.
- **Transaction** — atomic change (SNAPSHOT/APPEND/UPDATE/DELETE).
- **View (dataset view)** — effective file contents for a branch at a point in time.
- **View (resource)** — file-less union of backing datasets, deduplicated.
- **Branch** — pointer to the latest transaction; linear sequence; no merge.
- **JobSpec** — definition of how a job is constructed; published on code commit.
- **Build / Job** — orchestrated computation / unit of work producing dataset(s).
- **Schedule** — recurring/triggered builds.
- **Spark profile** — driver/executor resource configuration.
- **@incremental** — decorator enabling incremental computation.
- **Lightweight / faster pipeline** — non-Spark single-node / DataFusion compute.
- **Virtual table** — pointer to an external table (no ingest).
- **Marking** — mandatory all-or-nothing access control; propagates downstream.
- **Restricted view** — row-level secured view over a backing dataset.
- **Project** — primary security boundary.
- **Compute-second** — `max(vcpu, GiB/7.5) * seconds` unit of metered compute.
- **Magritte** — the Data Connection engine.
- **Compass** — the resource/folder hierarchy service.

---

## 12. Confidence & Gaps Register

| Claim | Evidence | Confidence |
|---|---|---|
| Four transaction types & view algorithm | palantir.com/docs datasets + API | High |
| Agent-proxy websocket to magritte-coordinator | palantir.com/docs architecture | High |
| Foundry worker isolated container; AES-256-GCM | palantir.com/docs architecture | High |
| Incremental determination from transaction types | palantir.com/docs incremental | High |
| Parquet default; backing Hadoop FS / S3 | palantir.com/docs datasets + S3 API | High |
| Compute-seconds formula (7.5 GiB/core; 600-cs example) | palantir.com/docs resource-management & code-repositories | High |
| Internal names: foundry-catalog, foundry-metadata, foundry-schema-inference, build2, foundry-data-proxy | third-party foundry-dev-tools SDK | Medium |
| `Catalog:TransactionNotInView` error token | palantir.com/docs incremental examples | High |
| No merge for dataset branches | palantir.com/docs branching | High |
| Faster pipelines = DataFusion/Rust | palantir.com/docs pipeline-types | High |
| Patent inventor lists | uspto.report / Justia / Google Patents | High |

**Known unknowns (and the source that would resolve each):**

1. The exact literal `api_name` strings in `catalog.py`/`build2.py` — would be resolved by Palantir's internal Conjure specs or unblocked GitHub raw source. [Inferred]
2. Whether Foundry's filesystem has a distinct product/proper-noun name beyond "backing file system" — no primary source found. [Known unknown]
3. Exact dataset size/file-count hard limits — docs give guidance (performance degradation, projections) but no numeric ceiling. [Known unknown]
4. Internal physical file layout/partitioning scheme beyond `spark/` prefix + Parquet — not fully documented. [Known unknown; best hypothesis, Speculative: Spark-written snappy Parquet part-files written under transaction-scoped paths, with the catalog mapping logical→physical paths per transaction.]
5. Precise count behind the marketed connector library ("200+") — docs enumerate families but no single authoritative number. [Known unknown]
6. Whether the public `api/v2/orchestration` is a 1:1 surface of the internal Build2 or a façade over additional services. [Known unknown]

---

## 13. Source Bibliography (by tier)

**Tier 1 — Official Palantir docs (palantir.com/docs/foundry/…), accessed June 13, 2026:**
- data-connection/architecture, /core-concepts, /set-up-agent, /agent-configuration-reference, /agent-worker, /agent-proxy, /agents-troubleshooting, /initial-setup-overview, /overview, /permissions, /export-overview, /export-tasks, /external-transforms, /set-up-streaming-sync, /syncs-troubleshooting
- data-integration/datasets, /branching, /builds, /views, /virtual-tables, /iceberg-tables, /change-data-capture, /source-type-overview, /flink-streaming, /health-checks
- transforms-python/* (transforms, transforms-pipelines, incremental-usage/-overview/-reference, transforms-python-api, tables-overview/-api/-databricks, lightweight-api-evolution), transforms-python-spark/* (transforms-python-api, incremental-examples, incremental-media-sets), api-reference/transforms-python-library/* (api-incremental, api-transform-df, api-transform-pandas, api-overview)
- pipeline-builder/* (overview, transforms-overview, datasets-computation-modes-for-batch, dataexpectations-overview/-configure-health-check, management-build-settings)
- building-pipelines/* (pipeline-types, incremental-overview, create-incremental-pipeline-pb, create-faster-pipeline-pb, maintaining-incremental-performance, scheduling-best-practices, schedule-troubleshooting, branching-release-process, remove-markings, infer-schema, create-batch-pipeline-cr, streaming-keys, streaming-compute-usage)
- optimizing-pipelines/* (spark-concepts, spark-profiles-reference, apply-spark-profiles, understand-spark-details, spark-ui, usage-optimization, troubleshoot-schedules)
- health-checks/* (checks-reference, check-types), maintaining-pipelines/* (recommended-health-checks, monitoring-views-intro), data-health/builds-checks-faq
- security/* (markings, restricted-views, projects-and-roles), platform-security-management/* (manage-markings, manage-granular-policies, manage-roles), object-permissioning/managing-object-security, object-edits/materializations, foundry-branching/overview
- code-repositories/compute-usage, resource-management/usage-types, contour/compute-usage, ontologies/compute-usage, compute-modules/usage, data-lineage/* (navigation, faq), foundry-s3-api
- available-connectors/* (amazon-s3, bigquery, databricks, onelake-and-azure-blob-filesystem, salesforce, sftp, sharepoint-online, kafka, sap-erp, custom-jdbc-sources, foundry)
- API reference: datasets-resources/transactions/*, datasets-v2-resources/* (transactions, files, datasets/get-dataset-schema), orchestration-v2-resources/builds/*

**Tier 1 — Palantir blog / GitHub:** blog.palantir.com "Why Data Pipeline Version Control Matters"; github.com/palantir/foundry-platform-python (Datasets, Orchestration/Schedule docs).

**Tier 1 — Patents:** US 10,853,338 (uspto.report); US 9,996,595 (Justia/Google Patents US20170039253A1); US 2020/0210427 (FreePatentsOnline).

**Tier 2 — third-party:** emdgroup foundry-dev-tools docs (internal service api_names — CatalogClient, MetadataClient, SchemaInferenceClient, Build2Client, DataProxyClient); Medium (D-ONE "@incremental Decorator" guide); Unit8 "Foundry 101."

**Tier 3 — community:** Palantir Developer Community; Medium "Foundry for Data Engineers" translators.

---
*Note on out-of-scope seams: the Ontology layer is touched only where a curated dataset backs an object type (datasource→object-type handoff: each dataset row → one object instance; restricted-view-backed objects; materializations writing object edits back to datasets with propagated markings). The app-building layer, AIP, and Apollo are referenced only as adjacent consumers/deployers and are not reconstructed here.*
