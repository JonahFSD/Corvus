#!/usr/bin/env python3
"""Generate an atomic-note Obsidian graph for the Foundry research, into the Palantir vault.
Notes are organized into numbered domain folders. Obsidian resolves [[wikilinks]] by note
name regardless of folder, so the layout can change freely without breaking any links."""
import os, re, textwrap, glob

# The vault lives next to this script in the `Vault/` folder. Resolve it relative
# to the script's own location so re-runs work from any session, mount, or CWD.
VAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Vault")

# ---------------------------------------------------------------------------
# Invariant hubs (the 5 larger ideas everything connects up to)
# ---------------------------------------------------------------------------
INVARIANTS = {
    "Semantic Model Over Data": "Users work with real-world *things* and their relationships, not tables and columns. Meaning is defined once, centrally, and reused everywhere.",
    "Versioned Data Foundation": "The data underneath is immutable and historied — you can always ask 'what did this look like then?' and trace any value to its origin.",
    "Governed Writeback": "All changes flow through defined, validated, audited actions — never ad-hoc edits. Logic is written once and enforced no matter who or what triggers it.",
    "Security Travels With Data": "Access control is a property of the objects and rows themselves, on by default, not bolted onto each app.",
    "End-to-End Lineage": "Source → dataset → object → action → audit log is one continuous, inspectable chain.",
}

# Layer hubs (Maps of Content). key -> (display title, blurb)
LAYER_HUBS = {
    "data":      ("Data Integration & Pipeline Layer", "The data foundation: how source data is ingested, versioned, transformed, and kept fresh as Ontology-ready datasets."),
    "semantic":  ("Ontology — Semantic Layer", "The model of *what exists*: object types, properties, links — the nouns of the business, materialized over versioned data."),
    "kinetic":   ("Ontology — Kinetic Layer", "The model of *what can happen*: actions and functions — governed, validated, audited change to the Ontology."),
    "dynamic":   ("Ontology — Dynamic Layer", "The model of *what could happen next*: Scenarios (immutable, delta-only forks), models and simulation/optimization, and the temporal/streaming substrate — the forward-looking, simulatable dimension that makes the Ontology a living digital twin. Mostly post-MVP (defer)."),
    "security":  ("Security & Governance Layer", "Cross-cutting access control, audit, and lineage that thread through every other layer."),
    "app":       ("App-Building Layer", "How operational apps are built and bound to the Ontology: Workshop (the reactive no-code builder), Slate (legacy power-user), Object Views, and the widget/variable model."),
    "aip":       ("AIP Layer", "The AI layer: LLMs and agents wired to the Ontology as *governed tools* — AIP Logic, Chatbot Studio, Evals, the model gateway. The LLM only asks; the platform executes in the user's permissions."),
    "platform":  ("Platform & Ecosystem Layer", "How the engine is deployed, upgraded, packaged, and distributed: Apollo (continuous delivery), Marketplace, Rubix (the Kubernetes substrate), and the Gotham→Foundry lineage. Mostly droppable for an internal clone."),
}

# Pending layers — all eight reconstructed.
PENDING_LAYERS = {}

LAYER_TAG = {"data":"data","semantic":"semantic","kinetic":"kinetic","dynamic":"dynamic","security":"security",
             "crosscutting":"crosscutting","app":"app","aip":"aip","platform":"platform"}

# Domain folders (numbered to sort in stack order). Concepts + each layer's hub live together.
MAPS_FOLDER = "00 Maps & Views"
INVARIANTS_FOLDER = "01 Invariants"
LAYER_FOLDER = {
    "crosscutting": "02 Foundations",
    "data":         "03 Data Foundation",
    "semantic":     "04 Ontology - Semantic",
    "kinetic":      "05 Ontology - Kinetic",
    "dynamic":      "06 Ontology - Dynamic",
    "app":          "07 App-Building",
    "aip":          "08 AIP",
    "security":     "09 Security & Governance",
    "platform":     "10 Platform & Ecosystem",
}

# ---------------------------------------------------------------------------
# Concepts. Each: dict(t=title, L=layer, k=kind, d=defn, b=body,
#                      inv=[invariants], rel=[related titles], clone=optional, src=source)
# ---------------------------------------------------------------------------
CONCEPTS = []

# ---- Cross-cutting big ideas ----------------------------------------------
CONCEPTS += [
 dict(t="The Closed Loop", L="crosscutting", k="pattern",
   d="Foundry's defining motion: data flows up into meaning, decisions flow back down into systems of record.",
   b="Raw data is integrated, given meaning as objects, acted on through governed [[Action Type|actions]], and the decision is written back to systems of record. The platform is part of operations, not a window onto them. Every other capability exists to make some part of this loop faster, safer, or smarter.",
   inv=["Governed Writeback","Semantic Model Over Data"], rel=["Operational Application","Digital Twin","Writeback Path"],
   src="Conceptual Map"),
 dict(t="Digital Twin", L="crosscutting", k="concept",
   d="The Ontology as a living model that mirrors the real organization and updates as it changes.",
   b="The [[Ontology]] is meant to be a faithful, current model of the business's entities, relationships, and decisions. As operations change, the model changes; security and state stay live rather than static. Its forward-looking, simulatable dimension — [[Scenario|scenarios]], [[Model|models]], and [[Simulation]] over a temporal substrate — is the [[Ontology — Dynamic Layer|dynamic layer]].",
   inv=["Semantic Model Over Data"], rel=["Ontology","The Closed Loop","Read-Your-Writes","Scenario","Simulation","Ontology — Dynamic Layer"],
   src="Conceptual Map"),
 dict(t="Operational Application", L="crosscutting", k="pattern",
   d="An app built to drive a decision and capture it via writeback — as opposed to a read-only dashboard.",
   b="Where a dashboard delivers read-only insight, an operational application lets users take an [[Action Type|action]] and commit the decision back to the [[Ontology]]. This is the dividing line between Foundry and ordinary BI.",
   inv=["Governed Writeback"], rel=["The Closed Loop","Action Type","Edits-Only-via-Actions"],
   src="Conceptual Map"),
 dict(t="Define-Once Reuse", L="crosscutting", k="pattern",
   d="A concept defined once in the model means the same thing in every screen, query, rule, and agent.",
   b="An object, property, link, function, or action is authored once and reused everywhere. One definition → every app; one logic → every surface; one permission model → every access path. This is the core payoff of a [[Semantic Model Over Data|semantic layer]].",
   inv=["Semantic Model Over Data","Governed Writeback"], rel=["Ontology","Function","Action Type"],
   src="Conceptual Map"),
 dict(t="Read-Your-Writes", L="crosscutting", k="property",
   d="After a change is committed, reads promptly reflect it — users trust that what they just did is what they now see.",
   b="In Foundry this is guaranteed at the index: once an [[Action Type|action]]'s edit is sent to the [[Object Data Funnel]], subsequent object reads include it. For a small clone, an ordinary database transaction gives this for free.",
   inv=["Governed Writeback"], rel=["Writeback Path","Object Data Funnel","Action Atomicity"],
   src="Kinetic reconstruction"),
 dict(t="Git for Data", L="crosscutting", k="concept",
   d="The data foundation behaves like version control: immutable, historied, branchable commits.",
   b="Every [[Dataset]] is a linear sequence of [[Transaction Model|transactions]] (commits) per [[Dataset Branch|branch]]; the current state is a replay. Versioning, [[Incremental Computation|incrementality]], branching, and retention all derive from this one idea.",
   inv=["Versioned Data Foundation"], rel=["Dataset","Transaction Model","Dataset Branch","End-to-End Lineage"],
   src="Data reconstruction"),
 dict(t="Minimum Viable Foundry", L="crosscutting", k="pattern",
   d="The smallest system still recognizably Foundry-like: versioned store + semantic model + governed actions + audit + roles.",
   b="The v1 target for our clone. In: a [[Versioned Data Foundation|versioned store]], [[Object Type|object]]/[[Link Type|link]] model, [[Object Set|object sets]], [[Action Type|governed actions]] with [[Submission Criteria|validation]], an [[Audit Log]], and [[Role|roles]]. Out (deferrable without rework): distributed compute, the connector tier, [[AIP Layer|AIP]], [[Platform & Ecosystem Layer|Apollo]]. See [[Design Decisions]].",
   inv=["Governed Writeback","Semantic Model Over Data","Versioned Data Foundation"], rel=["Design Decisions","The Closed Loop"],
   src="Design Constraints spec"),
]

# ---- DATA LAYER -----------------------------------------------------------
CONCEPTS += [
 dict(t="Dataset", L="data", k="concept",
   d="The fundamental unit of data storage: a versioned wrapper around files in a backing file system.",
   b="Files live in a backing Hadoop FileSystem (commonly S3), most often as Parquet, with [[Schema|schema]] stored as metadata. A dataset is versioned by [[Transaction Model|transactions]] and identified by a [[RID]]. It is the substrate that [[Object Backing|backs object types]].",
   inv=["Versioned Data Foundation"], rel=["Transaction Model","Dataset Branch","Schema","Object Backing","RID"],
   clone="Keep, simplified — likely rows/tables in one database rather than files on S3.",
   src="Data reconstruction §3"),
 dict(t="Transaction Model", L="data", k="mechanism",
   d="A dataset is a linear sequence of atomic commits; the current view is computed by replaying them.",
   b="Four transaction types: **SNAPSHOT** (replace the view), **APPEND** (add files), **UPDATE** (add/replace files), **DELETE** (remove references). The view begins at the latest SNAPSHOT and replays forward. This single mechanism underlies versioning, [[Incremental Computation|incrementality]], [[Dataset Branch|branching]], and retention.",
   inv=["Versioned Data Foundation"], rel=["Dataset","Git for Data","Incremental Computation","Dataset Branch"],
   clone="Keep the concept; a DB transaction + history/change-log is likely enough (see D2).",
   src="Data reconstruction §3.2"),
 dict(t="Dataset Branch", L="data", k="mechanism",
   d="A named pointer to the most recent transaction on a linear sequence; supports dev→prod separation.",
   b="Each branch is an independent transaction sequence (most datasets have a root branch `master`). Unlike Git there is **no merge**. Builds use branch fallbacks (e.g., develop → master). Pairs with [[Project|project]]-based dev→prod flow.",
   inv=["Versioned Data Foundation"], rel=["Transaction Model","Build System","Project"],
   src="Data reconstruction §3.3"),
 dict(t="View (virtual dataset)", L="data", k="concept",
   d="A file-less resource that is the deduplicated union of backing datasets, computed at read time.",
   b="Builds near-instantly because no data is moved; can be a transform input but not an output. Can be used to stop [[Marking|marking]] propagation. Distinct from the point-in-time *view* computed by the [[Transaction Model]].",
   inv=["Versioned Data Foundation"], rel=["Dataset","Transaction Model","Marking"],
   src="Data reconstruction §3.5"),
 dict(t="Schema", L="data", k="concept",
   d="Metadata on a dataset view defining how its files are interpreted — column names and types.",
   b="Stored alongside the dataset (internally the `foundry-metadata` service). Can be applied manually or inferred (see [[Schema Inference]]). Schema evolution rules constrain incremental outputs (same-named columns must keep their type).",
   inv=["Versioned Data Foundation"], rel=["Dataset","Schema Inference","Incremental Computation"],
   src="Data reconstruction §3.4"),
 dict(t="Schema Inference", L="data", k="mechanism",
   d="Automatic detection of column names and types from data (e.g., CSV/JSON, semi-structured input).",
   b="Often the first step of a pipeline on raw data; internally `foundry-schema-inference`. Turns untyped bytes into a typed [[Schema]] the rest of the pipeline and the [[Object Type|object model]] can rely on.",
   inv=["Versioned Data Foundation"], rel=["Schema","Transform"],
   src="Data reconstruction §3.4"),
 dict(t="Incremental Computation", L="data", k="mechanism",
   d="Process only what changed since the last run — and decide that automatically by inspecting input transaction types.",
   b="Incrementality is **derived, not declared**: the `@incremental` decorator reads build history and runs incrementally iff inputs only had files added ([[Transaction Model|APPEND]]). A SNAPSHOT input forces a full rebuild. The keystone efficiency mechanism.",
   inv=["Versioned Data Foundation"], rel=["Transaction Model","Transform","Build System"],
   clone="Keep the concept; trivial at her scale (small data).",
   src="Data reconstruction §5.3"),
 dict(t="Transform", L="data", k="concept",
   d="A declarative mapping from input datasets to output datasets, bundling compute logic and resources.",
   b="Authored in [[Code Repositories]] (PySpark/Python/Java/SQL) or generated by [[Pipeline Builder]]. Registered in a pipeline; run by the [[Build System]]; can be [[Incremental Computation|incremental]]. Produces the curated datasets that [[Object Backing|back objects]].",
   inv=["Versioned Data Foundation","End-to-End Lineage"], rel=["Code Repositories","Pipeline Builder","Build System","Incremental Computation"],
   src="Data reconstruction §4"),
 dict(t="Code Repositories", L="data", k="mechanism",
   d="Git-backed authoring environment for code transforms (Python, PySpark, Java, SQL).",
   b="Committing transform code publishes [[Build System|JobSpecs]]; Preview runs on sampled inputs without committing. The code-first counterpart to [[Pipeline Builder]].",
   inv=["Versioned Data Foundation"], rel=["Transform","Pipeline Builder","Build System"],
   src="Data reconstruction §4.2"),
 dict(t="Pipeline Builder", L="data", k="mechanism",
   d="Foundry's no-/low-code pipeline tool; compiles to a general transform backend rather than to user code.",
   b="A point-and-click, type-safe graph that targets multiple engines (Spark, Flink, and the Rust/DataFusion [[Faster Pipelines]] engine). Outputs can be datasets, [[Object Type|object types]], links, streams, or exports.",
   inv=["Versioned Data Foundation"], rel=["Transform","Faster Pipelines","Object Type"],
   src="Data reconstruction §4.3"),
 dict(t="Build System", L="data", k="service",
   d="The data-driven orchestrator (internally 'Build2') that computes new dataset versions.",
   b="Dependencies are defined between datasets via transforms; Foundry builds a DAG of **jobs** from **JobSpecs**. Skips 'fresh' outputs (unchanged inputs+logic); supports retries/aborts. Driven by [[Schedule & Trigger|schedules]].",
   inv=["Versioned Data Foundation","End-to-End Lineage"], rel=["Transform","Schedule & Trigger","Data Lineage Graph"],
   clone="Simplify — minimal scheduled refresh; no build-graph service needed at our scale.",
   src="Data reconstruction §5.1"),
 dict(t="Schedule & Trigger", L="data", k="mechanism",
   d="Runs builds over time (cron) or in response to events (an input dataset updating).",
   b="Trigger types: time-based, event/transaction-based, and streaming. Project-scoped is recommended over user-scoped. The automation that keeps the [[Versioned Data Foundation|data foundation]] fresh.",
   inv=["Versioned Data Foundation"], rel=["Build System"],
   src="Data reconstruction §5.2"),
 dict(t="Data Connection", L="data", k="service",
   d="Foundry's connectivity layer (engine name: Magritte) for moving data in and out.",
   b="Defines [[Source & Capability|sources]] and runs ingestion via [[Agent (Magritte)|agents]] or direct connections in isolated [[Foundry Worker|Foundry workers]]. The on-ramp to the [[Versioned Data Foundation|data foundation]].",
   inv=["Versioned Data Foundation"], rel=["Magritte","Source & Capability","Agent (Magritte)","Foundry Worker","Connector"],
   clone="Drop the tier — a thin ingestion path for a few sources is enough.",
   src="Data reconstruction §2"),
 dict(t="Magritte", L="data", k="service",
   d="The long-standing engine behind Data Connection (coordinator: `magritte-coordinator`).",
   b="Agents and the Bootstrapper connect back to `magritte-coordinator` via websocket. Sources are addressed `ri.magritte..source.*`. The enterprise plumbing for reaching hundreds of source systems across firewalls.",
   inv=["Versioned Data Foundation"], rel=["Data Connection","Agent (Magritte)","Foundry Worker"],
   clone="Drop — vastly over-scoped for one carrier-relations use case.",
   src="Data reconstruction §2"),
 dict(t="Source & Capability", L="data", k="concept",
   d="A source is one connection to an external system; capabilities are the discrete functions it can run.",
   b="Capability families: ingest into Foundry, push out ([[Export]]), virtualize ([[Virtual Table]]), and interactive requests. Each [[Connector]] page lists which capabilities it supports.",
   inv=["Versioned Data Foundation"], rel=["Connector","Export","Virtual Table","Data Connection"],
   src="Data reconstruction §2.1"),
 dict(t="Connector", L="data", k="concept",
   d="A pre-built integration to a specific source type (S3, JDBC, Salesforce, Kafka, SAP, …).",
   b="Foundry advertises a large library across cloud storage, relational, warehouse, enterprise-app, streaming, and NoSQL families. Each exposes a set of [[Source & Capability|capabilities]].",
   inv=["Versioned Data Foundation"], rel=["Source & Capability","Data Connection"],
   clone="Drop almost all — start with spreadsheet upload + one API.",
   src="Data reconstruction §2.1"),
 dict(t="Agent (Magritte)", L="data", k="mechanism",
   d="A downloadable program installed in the customer network to reach private data sources.",
   b="Two modes: **agent-proxy** ('thin mode', a pure network tunnel to Foundry) and the legacy **agent worker** ('thick mode', runs connector code on the host). See [[Agent-Proxy vs Agent Worker]].",
   inv=["Versioned Data Foundation","Security Travels With Data"], rel=["Agent-Proxy vs Agent Worker","Foundry Worker","Magritte"],
   src="Data reconstruction §2.2"),
 dict(t="Agent-Proxy vs Agent Worker", L="data", k="concept",
   d="The two connectivity axes: where compute runs (Foundry worker vs agent host) and how the network is crossed.",
   b="Modern **agent-proxy** keeps compute in an isolated [[Foundry Worker]] and uses the agent only as a websocket tunnel; legacy **agent worker** runs Java on the customer host. Proxy is recommended; worker is legacy-supported.",
   inv=["Security Travels With Data"], rel=["Agent (Magritte)","Foundry Worker"],
   src="Data reconstruction §2.2"),
 dict(t="Foundry Worker", L="data", k="service",
   d="An isolated container with scalable compute that runs connector/processing code on Foundry's side.",
   b="Handles authenticated, encrypted requests; network egress is administered in-platform via egress policies. The modern alternative to running connector code on a customer host.",
   inv=["Security Travels With Data"], rel=["Agent-Proxy vs Agent Worker","Data Connection"],
   src="Data reconstruction §2.3"),
 dict(t="Virtual Table", L="data", k="mechanism",
   d="A pointer to an external table (Delta/Iceberg/BigQuery/Snowflake/…) queried without ingesting it.",
   b="No-copy federation: always-current, no storage cost, with optional compute pushdown — but reads depend on the source and lack Foundry's full [[Transaction Model|transactional]] guarantees.",
   inv=["Versioned Data Foundation"], rel=["Source & Capability","Dataset"],
   src="Data reconstruction §2.4"),
 dict(t="Export", L="data", k="mechanism",
   d="Pushing Foundry data back out to an external system (file, table, streaming).",
   b="Governed by [[Marking|markings]] — exporting is treated as removing markings and requires permission. One way the [[The Closed Loop|loop]] reaches external systems of record.",
   inv=["Security Travels With Data","End-to-End Lineage"], rel=["Marking","Source & Capability","Webhook"],
   src="Data reconstruction §2.5"),
 dict(t="Faster Pipelines", L="data", k="mechanism",
   d="A pipeline acceleration backend powered by DataFusion, an open-source query engine written in Rust.",
   b="Speeds up small-to-medium batch/incremental pipelines vs Spark; doesn't support LLM/geo/media operations. Related to single-node [[Lightweight Transform|lightweight transforms]].",
   inv=["Versioned Data Foundation"], rel=["Pipeline Builder","Lightweight Transform","Spark Profile"],
   clone="A reminder we likely need no distributed engine at all.",
   src="Data reconstruction §4.3"),
 dict(t="Lightweight Transform", L="data", k="mechanism",
   d="A transform that runs on a single node without Spark (Polars/pandas), for small-to-medium data.",
   b="Faster and cheaper than Spark for suitable jobs; supports bring-your-own-container. Evidence that distributed compute is optional for modest data volumes.",
   inv=["Versioned Data Foundation"], rel=["Transform","Faster Pipelines","Spark Profile"],
   src="Data reconstruction §4.2"),
 dict(t="Spark Profile", L="data", k="concept",
   d="A configuration of distributed compute resources (driver/executor cores, memory, executor count).",
   b="Selects how a Spark transform is resourced; metered in [[Compute-Seconds]]. One of several [[Faster Pipelines|compute backends]] (Spark, lightweight, DataFusion, Flink).",
   inv=["Versioned Data Foundation"], rel=["Compute-Seconds","Faster Pipelines","Lightweight Transform"],
   clone="Drop — Palantir scale tuning, irrelevant for us.",
   src="Data reconstruction §8.1"),
 dict(t="Compute-Seconds", L="data", k="concept",
   d="Foundry's unit of metered compute: max(vCPU, GiB/7.5) × seconds, summed across driver + executors.",
   b="A billing/scale artifact (7.5 GiB-per-core ratio). Useful context for understanding Foundry's economics; not a requirement to replicate.",
   inv=["Versioned Data Foundation"], rel=["Spark Profile","Build System"],
   clone="Drop entirely.",
   src="Data reconstruction §8.2"),
 dict(t="Data Lineage Graph", L="data", k="service",
   d="The dependency graph tracing source → dataset → transform → object → app.",
   b="Branch-aware and inspectable; it computes out-of-date datasets, powers [[Data Health & Expectations|health checks]], and structures propagation of security. The backbone of [[End-to-End Lineage]].",
   inv=["End-to-End Lineage"], rel=["Build System","Data Health & Expectations","Object Backing"],
   clone="Keep, simplified (dataset-level 'produced by').",
   src="Data reconstruction §6.2"),
 dict(t="Data Health & Expectations", L="data", k="mechanism",
   d="Two quality mechanisms: post-build health checks (warn/alert) and in-build data expectations (block).",
   b="Health checks validate freshness, row counts, schema, uniqueness; **data expectations** run during a build and fail it if violated (e.g., primary-key uniqueness, row-count bounds). Guards the integrity feeding the [[Object Type|object model]].",
   inv=["Versioned Data Foundation","End-to-End Lineage"], rel=["Build System","Primary Key"],
   src="Data reconstruction §6.1"),
 dict(t="Materialization", L="data", k="mechanism",
   d="An optional dataset (OSv2) reflecting object/writeback state — formerly the 'writeback dataset'.",
   b="Persists Ontology object state back to a dataset; carries `__`-prefixed metadata columns. Propagates backing [[Marking|markings]]. The seam where [[Governed Writeback|kinetic edits]] re-enter the [[Versioned Data Foundation|data foundation]].",
   inv=["Versioned Data Foundation","End-to-End Lineage"], rel=["Writeback Path","Object Backing","Marking"],
   src="Kinetic reconstruction §7"),
 dict(t="Dataset Projection", L="data", k="mechanism",
   d="An independently-stored, compacted query representation that reorganizes data as volume grows.",
   b="Breaks out of the strict append-only model to keep reads fast over many small files; readers transparently combine projection + canonical data. A scale optimization.",
   inv=["Versioned Data Foundation"], rel=["Dataset","Transaction Model"],
   clone="Drop — small-file scale artifact.",
   src="Data reconstruction §3.6"),
 dict(t="RID", L="data", k="concept",
   d="Resource Identifier: Foundry's universal addressing scheme, ri.<service>.<instance>.<type>.<locator>.",
   b="Every resource — dataset, transaction, object type, action type, source, build — has a stable RID. The naming substrate that makes [[End-to-End Lineage|lineage]] and references possible.",
   inv=["End-to-End Lineage"], rel=["Dataset","Object Type","Action Type"],
   src="Data reconstruction §3.6"),
]

# ---- SEMANTIC LAYER -------------------------------------------------------
CONCEPTS += [
 dict(t="Ontology", L="semantic", k="concept",
   d="Foundry's semantic + kinetic model of the business — the operational layer over integrated data.",
   b="Simultaneously a database, an API, a permission system, and a workflow engine. Its semantic half ([[Object Type|objects]], [[Property|properties]], [[Link Type|links]]) says what exists; its [[Ontology — Kinetic Layer|kinetic]] half ([[Action Type|actions]], [[Function|functions]]) says what can happen. The [[Digital Twin]] of the organization.",
   inv=["Semantic Model Over Data"], rel=["Object Type","Link Type","Action Type","Function","Digital Twin"],
   src="Semantic reconstruction"),
 dict(t="Object Type", L="semantic", k="concept",
   d="The schema definition of a kind of real-world entity or event (a Carrier, a Circuit, a Contract).",
   b="Has a [[Primary Key]], a [[Title Property]], and typed [[Property|properties]]; its instances are [[Object|objects]]. Materialized from a backing dataset (see [[Object Backing]]). The nouns of the [[Semantic Model Over Data|model]].",
   inv=["Semantic Model Over Data"], rel=["Object","Property","Link Type","Primary Key","Title Property","Object Backing"],
   clone="Keep (core). One DB table per type, or a generic store — see [[Design Decisions|D5]].",
   src="Semantic reconstruction §2.1"),
 dict(t="Object", L="semantic", k="concept",
   d="A single instance of an object type — one set of primary-key + property values.",
   b="Analogous to a row, but a first-class thing users search, view, and act on. Carries a [[RID]] and [[Primary Key|primary key]]; addressable, traversable via [[Link Type|links]], and editable only through [[Action Type|actions]].",
   inv=["Semantic Model Over Data"], rel=["Object Type","Property","Primary Key","Object Set"],
   src="Semantic reconstruction §2.1"),
 dict(t="Property", L="semantic", k="concept",
   d="A typed attribute of an object type (a circuit's bandwidth, a carrier's account manager).",
   b="Has a [[Property Base Type|base type]] and optional [[Value Type|value type]] for validation, plus metadata (formatting, visibility, render hints). One property may be the [[Primary Key]] or [[Title Property]].",
   inv=["Semantic Model Over Data"], rel=["Property Base Type","Value Type","Primary Key","Title Property","Derived Property"],
   src="Semantic reconstruction §2.2"),
 dict(t="Property Base Type", L="semantic", k="type",
   d="The underlying datatype of a property (string, integer, date, boolean, geopoint, …).",
   b="Determines the operations available. A small core (text/number/date/boolean) covers most needs; advanced types add geo, time-series, media, struct, vector. See [[Advanced Property Types]].",
   inv=["Semantic Model Over Data"], rel=["Property","Value Type","Advanced Property Types"],
   clone="Keep a small core; defer advanced types (D7).",
   src="Semantic reconstruction §2.2"),
 dict(t="Value Type", L="semantic", k="type",
   d="A reusable semantic wrapper over a base type that adds constraints (email regex, enum, range).",
   b="Defined once, reused across object types and pipelines, versioned and permissioned — conceptually like RDF/OWL/XSD typing. The mechanism for [[Define-Once Reuse|define-once]] validation.",
   inv=["Semantic Model Over Data","Governed Writeback"], rel=["Property Base Type","Property","Submission Criteria"],
   clone="Keep — constrained/enumerated values are high-value at v1.",
   src="Semantic reconstruction §2.3"),
 dict(t="Primary Key", L="semantic", k="concept",
   d="The property uniquely identifying each object instance; should be deterministic.",
   b="Must be unique in the backing dataset; cannot be edited by an [[Action Type|action]] (that would be delete + create). Certain types (geo, arrays, real numbers) can't be primary keys.",
   inv=["Semantic Model Over Data"], rel=["Object Type","Object","Object Backing"],
   src="Semantic reconstruction §2.1"),
 dict(t="Title Property", L="semantic", k="concept",
   d="The human-readable display property shown for an object across applications.",
   b="e.g., a person's full name or a circuit's ID. A small but important piece of [[Define-Once Reuse]] — one display rule, everywhere.",
   inv=["Semantic Model Over Data"], rel=["Object Type","Property"],
   src="Semantic reconstruction §2.1"),
 dict(t="Link Type", L="semantic", k="concept",
   d="A first-class, named, traversable relationship between two object types.",
   b="Supports the three [[Link Cardinality|cardinalities]] (1:1, 1:N, N:M). Implemented via foreign keys, join-table datasets, or an [[Object-Backed Link]]. The edges of the [[Semantic Model Over Data|model]] ('show me this carrier's circuits').",
   inv=["Semantic Model Over Data"], rel=["Link Cardinality","Object-Backed Link","Object Type"],
   clone="Keep (core). FK for 1:N, join table for N:M, or a unified edge table — see [[Design Decisions|D6]].",
   src="Semantic reconstruction §9 / Kinetic §9"),
 dict(t="Link Cardinality", L="semantic", k="concept",
   d="The multiplicity of a relationship: one-to-one, one-to-many, or many-to-many.",
   b="1:1 and many:1 use a foreign-key property; N:M uses a join-table dataset (or an [[Object-Backed Link]] when the link itself needs properties).",
   inv=["Semantic Model Over Data"], rel=["Link Type","Object-Backed Link"],
   src="Kinetic reconstruction §9.1"),
 dict(t="Object-Backed Link", L="semantic", k="mechanism",
   d="A link type that carries its own object type, so the relationship can hold properties.",
   b="Extends many-to-one with first-class storage and metadata (e.g., a Flight Manifest linking Pilot and Aircraft). Adds link-level attributes at the cost of an extra object type.",
   inv=["Semantic Model Over Data"], rel=["Link Type","Link Cardinality","Object Type"],
   src="Kinetic reconstruction §9.1"),
 dict(t="Interface (Ontology)", L="semantic", k="concept",
   d="An abstract shape (shared properties + link constraints) that object types implement — polymorphism.",
   b="Cannot be instantiated directly; object types map local properties onto required interface properties. Enables searching/acting across many types uniformly. An enterprise-modeling feature.",
   inv=["Semantic Model Over Data"], rel=["Object Type","Shared Property","Property"],
   clone="Defer — add when multiple types need a shared contract.",
   src="Semantic reconstruction §2.7"),
 dict(t="Shared Property", L="semantic", k="concept",
   d="A property reusable across multiple object types for consistent modeling and centralized metadata.",
   b="Can satisfy [[Interface (Ontology)|interface]] requirements. Another expression of [[Define-Once Reuse]] at the property level.",
   inv=["Semantic Model Over Data"], rel=["Property","Interface (Ontology)"],
   src="Semantic reconstruction §2.8"),
 dict(t="Object Set", L="semantic", k="concept",
   d="A saved or temporary query over objects (static list or dynamic filter), served by the Object Set Service.",
   b="The unit of 'show me all circuits with degraded SLA this quarter'. Composable, shareable, and permissioned; the read surface over the [[Object Type|object model]].",
   inv=["Semantic Model Over Data"], rel=["Object Set Service (OSS)","Object","Object Type"],
   clone="Keep (core) — saved filters over objects.",
   src="Semantic reconstruction §5.1"),
 dict(t="Object Backing", L="semantic", k="mechanism",
   d="The handoff where a curated dataset materializes an object type: rows → objects, columns → properties.",
   b="The seam between the [[Data Integration & Pipeline Layer|data layer]] and the [[Ontology — Semantic Layer|semantic layer]]. The semantic layer is a *view of meaning* over the [[Versioned Data Foundation|versioned store]], not a separate source of truth.",
   inv=["Semantic Model Over Data","Versioned Data Foundation","End-to-End Lineage"], rel=["Dataset","Object Type","Property","Materialization"],
   clone="Keep — the data→object handoff must be first-class.",
   src="Semantic reconstruction §3.1"),
 dict(t="Object Storage V2 (OSv2)", L="semantic", k="service",
   d="The next-gen backend that indexes/serves objects across multiple storage backends in parallel.",
   b="Replaces [[Phonograph (OSv1)]]; separates indexing from querying for scale (tens of billions of objects/type). Comprises the [[Object Data Funnel]], [[Object Set Service (OSS)]], and [[Ontology Metadata Service (OMS)]].",
   inv=["Semantic Model Over Data"], rel=["Phonograph (OSv1)","Object Data Funnel","Object Set Service (OSS)","Ontology Metadata Service (OMS)","Object Indexing"],
   clone="Drop the decomposition — objects live in our DB.",
   src="Semantic reconstruction §4.2"),
 dict(t="Phonograph (OSv1)", L="semantic", k="service",
   d="The legacy object backend (Elasticsearch-based); end-of-life after June 30, 2026.",
   b="Foundry's original object database for indexing, edits, and writeback. Superseded by [[Object Storage V2 (OSv2)]]. Historical context, not a clone target.",
   inv=["Semantic Model Over Data"], rel=["Object Storage V2 (OSv2)","Object Indexing"],
   clone="Drop (legacy).",
   src="Semantic reconstruction §4.1"),
 dict(t="Object Data Funnel", L="semantic", k="service",
   d="The OSv2 microservice that orchestrates writes into the Ontology and indexing of datasources + edits.",
   b="Receives modification instructions from the [[Action Type|Actions]] service into an offset-tracked queue, applies them to the live index immediately, and flushes periodically to a durable [[Materialization|merged dataset]]. Enables [[Read-Your-Writes]] at scale.",
   inv=["Governed Writeback","Versioned Data Foundation"], rel=["Writeback Path","Object Indexing","Materialization","Read-Your-Writes"],
   clone="Drop — a DB commit is our write; no queue needed.",
   src="Kinetic reconstruction §7"),
 dict(t="Object Set Service (OSS)", L="semantic", k="service",
   d="The OSv2 service that serves reads — searching, filtering, aggregating, loading objects.",
   b="Determines which compute engine runs a query and produces [[Object Set|object sets]]. For our scale, ordinary database queries cover this.",
   inv=["Semantic Model Over Data"], rel=["Object Set","Object Storage V2 (OSv2)","Object Indexing"],
   clone="Drop — DB queries replace it.",
   src="Semantic reconstruction §5.2"),
 dict(t="Ontology Metadata Service (OMS)", L="semantic", k="service",
   d="The service that defines the set of ontological entities — object, link, and action types.",
   b="The source of truth for the *structure* of the [[Ontology]] (vs the data). Records definition changes; tracks legacy usage during migration.",
   inv=["Semantic Model Over Data"], rel=["Ontology","Object Type","Link Type","Action Type"],
   clone="Becomes our schema/metadata store (could be plain DB tables).",
   src="Semantic reconstruction §7.1"),
 dict(t="Object Indexing", L="semantic", k="mechanism",
   d="Turning dataset rows and user edits into searchable, queryable objects in an object database.",
   b="Incremental in OSv2; the index is ephemeral (durability comes from datasources + [[Materialization|merged datasets]]). The 'live' feeling of objects comes from here.",
   inv=["Semantic Model Over Data"], rel=["Object Storage V2 (OSv2)","Object Data Funnel","Object Backing"],
   clone="Drop a separate index tier — DB indexes suffice (D8).",
   src="Semantic reconstruction §4.2"),
 dict(t="Derived Property", L="semantic", k="mechanism",
   d="A property computed at runtime from other properties or linked objects (counts, sums, lookups).",
   b="Read-only; traverses up to a few link levels; cannot be a primary key or carry constraints. Useful for live rollups without storing redundant data.",
   inv=["Semantic Model Over Data"], rel=["Property","Link Type","Function"],
   src="Semantic reconstruction §2.4"),
 dict(t="Advanced Property Types", L="semantic", k="type",
   d="The richer property types beyond the core: geospatial, time-series, media, attachment, struct, vector, marking.",
   b="Each needs special configuration (e.g., vector for semantic search, geotime for tracks, media reference for large files). Powerful but optional — implement on real need.",
   inv=["Semantic Model Over Data"], rel=["Property Base Type","Mandatory Control Property"],
   clone="Defer most; add per real requirement (D7).",
   src="Semantic reconstruction §2.5"),
 dict(t="Ontology Branching & Proposals", L="semantic", k="mechanism",
   d="PR-style review of model changes: a proposal groups ontology edits for approval before merge.",
   b="Integrates with Global Branching; reviewers approve per-resource changes. Valuable when many people build the model; heavier than a small team needs initially.",
   inv=["Governed Writeback"], rel=["Dataset Branch","Ontology Metadata Service (OMS)"],
   clone="Defer — simpler change management at v1.",
   src="Semantic reconstruction §7.2"),
 dict(t="Mandatory Control Property", L="semantic", k="concept",
   d="A property carrying markings/organizations/classifications that enforce access at the storage level.",
   b="An object violating its mandatory-control constraints fails to index; invalid edits are rejected at submit. The point where [[Security Travels With Data|security]] becomes part of the object itself.",
   inv=["Security Travels With Data","Semantic Model Over Data"], rel=["Marking","Object Security Policy","Property"],
   src="Semantic reconstruction §4.5"),
]

# ---- KINETIC LAYER --------------------------------------------------------
CONCEPTS += [
 dict(t="Action Type", L="kinetic", k="concept",
   d="A governed, transactional definition of a set of edits to objects/links, plus side effects.",
   b="Bundles [[Action Parameter|parameters]] (typed inputs), [[Action Rule|rules]] (the edits), and [[Submission Criteria|submission criteria]] (validation). The *only* sanctioned way to change the [[Ontology]] — the heart of [[Edits-Only-via-Actions]].",
   inv=["Governed Writeback"], rel=["Action Parameter","Action Rule","Submission Criteria","Action Atomicity","Edits-Only-via-Actions","Function-Backed Action"],
   clone="Keep (the heart). Definition format: declarative vs code — see [[Design Decisions|D10]].",
   src="Kinetic reconstruction §2"),
 dict(t="Action Parameter", L="kinetic", k="concept",
   d="A typed input to an action — the interface between the form/caller and the rules.",
   b="Can be a primitive, object/object-set reference, attachment, etc.; supports defaults, validation, conditional visibility, and reading an object's *current* value before the edit. Binds to apps (Workshop, Object Views).",
   inv=["Governed Writeback"], rel=["Action Type","Action Rule","Submission Criteria"],
   src="Kinetic reconstruction §3"),
 dict(t="Action Rule", L="kinetic", k="concept",
   d="The logic of an action: an Ontology edit (create/modify/delete object, add/remove link) or a side effect.",
   b="Multiple rules compile to a single edit per object (last-writer-wins per property). A [[Function-Backed Action|function rule]] is exclusive — when present, no other rule may be configured. See also [[Side Effect]].",
   inv=["Governed Writeback"], rel=["Action Type","Function-Backed Action","Side Effect"],
   src="Kinetic reconstruction §4"),
 dict(t="Submission Criteria", L="kinetic", k="mechanism",
   d="Server-enforced conditions (formerly 'validations') determining whether an action can be submitted.",
   b="Encode business rules using object, link, and user attributes ('only a manager can escalate'). Enforced on the server, never trusting the client. The governance gate of [[Governed Writeback]].",
   inv=["Governed Writeback"], rel=["Action Type","Action Parameter","Value Type"],
   clone="Keep (core). Expressed as a small DSL or as functions — see [[Design Decisions|D12]].",
   src="Kinetic reconstruction §5"),
 dict(t="Function", L="kinetic", k="concept",
   d="Reusable server-side business logic that reads objects and computes results (TypeScript / Python).",
   b="The substrate for complex validation, [[Derived Property|derived data]], [[Function-Backed Action|function-backed writeback]], and (later) AI tools. Authored once, reused on every surface — [[Define-Once Reuse]].",
   inv=["Governed Writeback","Define-Once Reuse"], rel=["Function-Backed Action","Functions on Objects (FOO)","Function Runtime","Ontology Edits API"],
   clone="Keep; pick one runtime/language — see [[Design Decisions|D11]].",
   src="Kinetic reconstruction §8"),
 dict(t="Function-Backed Action", L="kinetic", k="mechanism",
   d="An action whose edits are computed by a function via the Ontology Edits API — for complex writeback.",
   b="The function's inputs derive from action parameters; it returns a batch of edits applied atomically. When this rule is present, no other rule may coexist. Enables multi-object, conditional writeback.",
   inv=["Governed Writeback"], rel=["Function","Action Type","Ontology Edits API","Action Atomicity"],
   src="Kinetic reconstruction §6"),
 dict(t="Ontology Edits API", L="kinetic", k="mechanism",
   d="The in-function API for create/update/delete object and link edits (verified surface).",
   b="TS v2 builds an edit batch (`createEditBatch` → `getEdits()`); Python uses `client.ontology.edits()` → `get_edits()`; TS v1 captures edits implicitly. Edits are collapsed to the minimal set and applied as one transaction.",
   inv=["Governed Writeback"], rel=["Function","Function-Backed Action","Action Atomicity","Writeback Path"],
   clone="Design our own edit API; the *contract* (atomic batched edits) is what matters.",
   src="Kinetic reconstruction §6"),
 dict(t="Functions on Objects (FOO)", L="kinetic", k="mechanism",
   d="Functions exposed on object types for object-aware logic and computed/derived columns.",
   b="Consumed in Workshop/Quiver/Map; the read-side counterpart to edit functions. Each execution carries a small compute-second overhead.",
   inv=["Semantic Model Over Data","Define-Once Reuse"], rel=["Function","Derived Property","Object Type"],
   src="Kinetic reconstruction §8.1"),
 dict(t="Function Runtime", L="kinetic", k="concept",
   d="The sandboxed environment functions run in (TypeScript v1/v2, Python), with limits and metering.",
   b="Default 60-second elapsed limit (TS v1: 30s CPU / 128 MB); serverless vs deployed modes; metered in compute-seconds. Scale/runtime detail Palantir needs that we can radically simplify.",
   inv=["Governed Writeback"], rel=["Function","Compute-Seconds"],
   clone="Pick one runtime, likely the app backend's own language (D11).",
   src="Kinetic reconstruction §8.2"),
 dict(t="Writeback Path", L="kinetic", k="mechanism",
   d="The end-to-end route of an edit: Action → Actions service → Object Data Funnel → index + materialization.",
   b="Index-first, persist-later: applied to the live index immediately, flushed to a durable [[Materialization|merged dataset]] periodically. Gives [[Read-Your-Writes]] at scale. With a single DB, a committed transaction *is* the write.",
   inv=["Governed Writeback","Versioned Data Foundation"], rel=["Object Data Funnel","Materialization","Action Atomicity","Read-Your-Writes"],
   clone="Drop the machinery — a DB commit replaces the whole path.",
   src="Kinetic reconstruction §7"),
 dict(t="Action Atomicity", L="kinetic", k="property",
   d="All edits an action computes succeed together or not at all — one transaction.",
   b="A function that throws produces no edits (whole-function-must-succeed). Cross-system writes (e.g., a [[Webhook]]) are *not* transactional and must be handled explicitly. A DB transaction gives us this directly.",
   inv=["Governed Writeback"], rel=["Action Type","Function-Backed Action","Writeback Path","Webhook"],
   clone="Keep — one DB transaction per action (D14).",
   src="Kinetic reconstruction §6"),
 dict(t="Edit History", L="kinetic", k="mechanism",
   d="An immutable audit trail of every object change: who, what, when, previous → new values.",
   b="Cannot be altered by end users even if edits are reverted. Rides directly on the [[Versioned Data Foundation|versioned store]]. Non-negotiable for an operational system.",
   inv=["Governed Writeback","End-to-End Lineage"], rel=["Action Log","Audit Log","Writeback Path"],
   clone="Keep — an append-only events table capturing the diff (D13).",
   src="Kinetic reconstruction §7"),
 dict(t="Action Log", L="kinetic", k="mechanism",
   d="A `[LOG]` object type that records each action submission, linked to all objects it edited.",
   b="Captures edited objects, an optional summary, and contextual properties — a queryable record of *which action* did *what*. Complements property-level [[Edit History]].",
   inv=["End-to-End Lineage","Governed Writeback"], rel=["Edit History","Action Type","Audit Log"],
   src="Kinetic reconstruction §7"),
 dict(t="Webhook", L="kinetic", k="mechanism",
   d="An action side effect that calls an external system — as writeback (before edits) or side effect (after).",
   b="A **writeback** webhook gives partial transactionality (if the external call fails, no Ontology change); a **side-effect** webhook runs after edits. One way the [[The Closed Loop|loop]] reaches systems of record.",
   inv=["Governed Writeback"], rel=["Side Effect","External Function","Action Atomicity","Export"],
   clone="Keep the concept; implement simply, defer OAuth-outbound plumbing.",
   src="Kinetic reconstruction §9"),
 dict(t="External Function", L="kinetic", k="mechanism",
   d="A function permitted to call an external API, gated through a Data Connection source.",
   b="By default functions cannot call out; a configured source enables egress. Lets governed logic integrate with outside systems without leaving the [[Governed Writeback|action]] model.",
   inv=["Governed Writeback","Security Travels With Data"], rel=["Function","Webhook","Data Connection"],
   src="Kinetic reconstruction §9"),
 dict(t="Side Effect", L="kinetic", k="concept",
   d="A non-edit action outcome: notify someone, call a webhook, trigger a build.",
   b="Runs around the edit with defined ordering/failure semantics (a failed notification doesn't roll back edits; a failed writeback webhook does). The 'and then…' of an [[Action Type|action]].",
   inv=["Governed Writeback"], rel=["Action Rule","Webhook"],
   src="Kinetic reconstruction §4"),
 dict(t="Inline Edit", L="kinetic", k="mechanism",
   d="A cell-level edit bound to a single object via an action type.",
   b="A convenience surface for quick edits that still flows through the [[Action Type|action]] machinery — preserving [[Edits-Only-via-Actions]] guarantees.",
   inv=["Governed Writeback"], rel=["Action Type","Edits-Only-via-Actions"],
   src="Kinetic reconstruction §2"),
 dict(t="Automate", L="kinetic", k="service",
   d="Running actions/functions automatically on a schedule or in response to object events.",
   b="Replaces 'Object Monitoring'; triggers effects without a human, with at-least-once semantics. Post-MVP value; the action/function model is built so it slots in later.",
   inv=["Governed Writeback"], rel=["Action Type","Function","Schedule & Trigger"],
   clone="Defer — slots in later without rework.",
   src="Kinetic reconstruction §10"),
 dict(t="AIP Tool Exposure", L="kinetic", k="mechanism",
   d="Exposing actions and functions as governed *tools* an LLM/agent can call.",
   b="The LLM only *asks* to use a tool; the platform executes it within the user's permissions. Edits still require an action — AI cannot bypass [[Governed Writeback]]. The bridge to the [[AIP Layer]].",
   inv=["Governed Writeback"], rel=["Action Type","Function","AIP Layer"],
   clone="Defer — the action model already makes AI a safe consumer.",
   src="Kinetic reconstruction §10"),
 dict(t="Edits-Only-via-Actions", L="kinetic", k="pattern",
   d="The governance pattern: objects change ONLY through defined, validated, audited actions.",
   b="What makes the platform *operational* rather than a database with a UI. A user may even create objects they can't view. This pattern + a [[Versioned Data Foundation|versioned store]] = end-to-end provenance.",
   inv=["Governed Writeback","Security Travels With Data"], rel=["Action Type","Submission Criteria","Edit History","Operational Application"],
   clone="Keep — the single most important pattern to replicate.",
   src="Kinetic reconstruction §11"),
]

# ---- SECURITY & GOVERNANCE -----------------------------------------------
CONCEPTS += [
 dict(t="Marking", L="security", k="concept",
   d="A mandatory, all-or-nothing access control tag; a user must hold all of a resource's markings.",
   b="Propagates downstream through [[Transform|transforms]] automatically, so derived data inherits restrictions. The blunt, powerful instrument of [[Security Travels With Data]].",
   inv=["Security Travels With Data"], rel=["Restricted View","Mandatory Control Property","Classification-Based Access Control (CBAC)","Project"],
   clone="Simplify — roles + optional row rules at v1 (D15).",
   src="Security / Semantic §4.5"),
 dict(t="Restricted View", L="security", k="mechanism",
   d="Row-level security: a policy limits a dataset/object to only the rows a user may see.",
   b="Powered by [[Granular Policy|granular policies]]; can back object types for row-level object security. The mechanism behind 'security travels with the row'.",
   inv=["Security Travels With Data"], rel=["Granular Policy","Object Security Policy","Marking"],
   src="Security / Data §7.2"),
 dict(t="Granular Policy", L="security", k="mechanism",
   d="A rule set comparing user attributes, columns, and values to decide row visibility at request time.",
   b="Template-based, converted to queries on access. The engine under [[Restricted View|restricted views]] and [[Object Security Policy|object security policies]].",
   inv=["Security Travels With Data"], rel=["Restricted View","Object Security Policy"],
   src="Security §6.3"),
 dict(t="Object Security Policy", L="security", k="mechanism",
   d="Row-level visibility configured directly on an object type, independent of backing-dataset permissions.",
   b="Compares user attributes/properties to gate which object instances a user sees. With a [[Property Security Policy]], gives cell-level security.",
   inv=["Security Travels With Data"], rel=["Property Security Policy","Granular Policy","Mandatory Control Property"],
   src="Kinetic / Security §6.2"),
 dict(t="Property Security Policy", L="security", k="mechanism",
   d="Column-level security on an object type — hides specific properties (e.g., PII) from some users.",
   b="Requires an [[Object Security Policy]] first; a primary key can't be in a property policy. Together they make security a property of the [[Object|object]] itself.",
   inv=["Security Travels With Data"], rel=["Object Security Policy","Mandatory Control Property"],
   src="Kinetic / Security §6.2"),
 dict(t="Classification-Based Access Control (CBAC)", L="security", k="concept",
   d="Access granted by data classification level (and max-classification constraints on objects).",
   b="A government/enterprise-grade control layered on [[Marking|markings]] and [[Organization|organizations]]. Likely overkill for our v1.",
   inv=["Security Travels With Data"], rel=["Marking","Purpose-Based Access Control","Organization"],
   clone="Drop at v1.",
   src="Security"),
 dict(t="Purpose-Based Access Control", L="security", k="concept",
   d="Access granted based on the declared *purpose* for which a user is accessing data.",
   b="Ties usage to an approved purpose, not just identity — strong governance, but heavy. Part of Palantir's compliance posture.",
   inv=["Security Travels With Data"], rel=["Classification-Based Access Control (CBAC)","Marking"],
   clone="Drop at v1.",
   src="Security"),
 dict(t="Project", L="security", k="concept",
   d="The primary security boundary: a container of resources with roles that inherit to children.",
   b="Access is granted at the project level and flows down. Datasets, object types, sources, and apps live in projects; dev→prod separation is organized here.",
   inv=["Security Travels With Data"], rel=["Role","Marking","Dataset Branch"],
   clone="Simplify to a basic workspace/role scheme.",
   src="Data §7.3"),
 dict(t="Role", L="security", k="concept",
   d="A named set of operations (Owner, Editor, Viewer, Discoverer, …) granted on a resource.",
   b="Each role can grant equal-or-lesser roles; roles inherit to child resources. The backbone of who-can-do-what.",
   inv=["Security Travels With Data"], rel=["Project","Audit Log"],
   clone="Keep — role-based access is the v1 baseline (D15).",
   src="Data §7.3"),
 dict(t="Organization", L="security", k="concept",
   d="A top-level tenancy/marking grouping that scopes who can see a space's resources.",
   b="An object/space can be private to one organization or shared across several. Coarse, mandatory partitioning above markings.",
   inv=["Security Travels With Data"], rel=["Marking","Project"],
   clone="Drop or reduce to a single tenant at v1.",
   src="Semantic §7.4 / Security"),
 dict(t="Audit Log", L="security", k="mechanism",
   d="An append-only, platform-wide record of who did what, when, and where.",
   b="Complements object-level [[Edit History]] and [[Action Log|action logs]] with system-wide accountability. A pillar of [[End-to-End Lineage]] and governance.",
   inv=["End-to-End Lineage","Security Travels With Data"], rel=["Edit History","Action Log","Role"],
   clone="Keep — append-only events table (D13).",
   src="Kinetic §7 / Security"),
]

# ---- APP-BUILDING LAYER ---------------------------------------------------
CONCEPTS += [
 dict(t="Workshop", L="app", k="service",
   d="Foundry's modern no-code builder for operational apps, bound tightly to the Ontology.",
   b="Apps are [[Workshop Module|modules]] of [[Widget|widgets]] driven by a reactive [[Workshop Variable|variable]] graph; writeback happens through [[Action Form|action forms]]. The recommended path over [[Slate]].",
   inv=["Semantic Model Over Data","Governed Writeback"], rel=["Workshop Module","Widget","Workshop Variable","Action Form","Slate","Operational Application"],
   clone="Keep the model; an ordinary reactive front-end framework covers it at our scale.",
   src="App-Building reconstruction §2"),
 dict(t="Workshop Module", L="app", k="concept",
   d="The unit Workshop app: header → pages → sections → widgets, identified by an RID.",
   b="Only the header persists across pages. Exposes a [[Module Interface]] (its 'API') and can be reused via [[Embedded Module|embedding]]. Inherits its parent project's permissions.",
   inv=["Semantic Model Over Data"], rel=["Workshop","Widget","Module Interface","Embedded Module","App vs Data Permissions"],
   src="App-Building reconstruction §2"),
 dict(t="Widget", L="app", k="concept",
   d="A UI building block that declares a configuration shape: input/output variables, display options, and attached actions.",
   b="The catalog spans display (Object Table/List), filtering (Filter List), visualization (charts/Map), input, and AIP widgets. Inputs are [[Object Set|object sets]]/[[Workshop Variable|variables]]; selection flows back as output variables.",
   inv=["Semantic Model Over Data"], rel=["Workshop Variable","Object Set Binding","Object Set","Action Form","AIP Agent Widget"],
   src="App-Building reconstruction §3"),
 dict(t="Workshop Variable", L="app", k="concept",
   d="A typed reactive value (input or output) that moves data through a module.",
   b="Types include object set, object set filter, string, boolean, numeric, date, geo, array, struct, time-series set. Defined statically or from functions, object properties, aggregations, or object-set definitions; consumed by widgets and recomputed per the [[Reactivity Model]].",
   inv=["Semantic Model Over Data"], rel=["Reactivity Model","Recompute Behavior","Object Set Filter","Workshop Event","Functions on Objects (FOO)"],
   clone="Keep — a typed reactive state model is the heart of the app layer.",
   src="App-Building reconstruction §4"),
 dict(t="Reactivity Model", L="app", k="mechanism",
   d="A lazy dependency graph: variables compute only when displayed by a visible widget.",
   b="In view mode a variable recomputes only when shown (non-visible pages/tabs/overlays are skipped); in edit mode all compute. Function-backed variables cache on input identity. The make-or-break mechanism to replicate faithfully.",
   inv=["Semantic Model Over Data"], rel=["Workshop Variable","Recompute Behavior","Workshop Event","Slate Node Graph"],
   clone="Keep the *behavior* (lazy, demand-driven); the engine internals are unpublished (treat as our design).",
   src="App-Building reconstruction §4"),
 dict(t="Recompute Behavior", L="app", k="concept",
   d="How a variable refreshes: Automatic (default), Only-on-event, or On-load-plus-event.",
   b="Automatic recomputes when any dependency changes (and may recompute when upstream objects reload after an action or [[Auto-Refresh]]). Function results are cached; force recompute via an incrementing 'entropy' variable.",
   inv=["Semantic Model Over Data"], rel=["Reactivity Model","Workshop Variable","Auto-Refresh"],
   src="App-Building reconstruction §4"),
 dict(t="Workshop Event", L="app", k="mechanism",
   d="The explicit state-change mechanism — but events fire immediately and do NOT await downstream recomputation.",
   b="Events run sequentially in configured order; the source value is copied to the target immediately, but dependents are not up-to-date before the next event runs. **A faithful clone must replicate this fire-immediately, propagate-asynchronously semantics, not a synchronous transactional update.**",
   inv=["Semantic Model Over Data","Governed Writeback"], rel=["Reactivity Model","Workshop Variable","Action Form"],
   clone="Critical: copy the async-propagation semantics or app logic will subtly differ.",
   src="App-Building reconstruction §4 (verbatim, verified)"),
 dict(t="Module Interface", L="app", k="concept",
   d="The set of a module's externally-mappable variables — effectively the module's API.",
   b="Lets a parent map variables into an [[Embedded Module|embedded child]] and lets the URL initialize state (`?externalId=value`) for deep-linking. Another expression of [[Define-Once Reuse]].",
   inv=["Semantic Model Over Data"], rel=["Workshop Module","Embedded Module","Object View"],
   src="App-Building reconstruction §2"),
 dict(t="Embedded Module", L="app", k="mechanism",
   d="Reusing one module inside another (via a loop layout or embed widget), each with its own variable scope.",
   b="Parent↔child communication is via the [[Module Interface]]. Module-level config (routing, auto-refresh) is not inherited; children are separately permissioned. The composition unit for maintainable apps.",
   inv=["Semantic Model Over Data"], rel=["Workshop Module","Module Interface"],
   src="App-Building reconstruction §2"),
 dict(t="Action Form", L="app", k="mechanism",
   d="A UI form auto-generated from an Action Type — the app layer's writeback surface.",
   b="Parameters bind from app state (local Workshop defaults override global); [[Submission Criteria]] surface inline as issues; submit is enabled only when all parameters validate, then data refreshes. 'Writeback and the UI for it are not defined separately.'",
   inv=["Governed Writeback"], rel=["Action Type","Submission Criteria","Workshop Variable","Operational Application","Edits-Only-via-Actions"],
   clone="Keep — generating the form from the action definition is a key define-once win.",
   src="App-Building reconstruction §5"),
 dict(t="Object Set Binding", L="app", k="mechanism",
   d="How apps consume the Ontology: object sets feed widgets, and selection flows back as output object sets.",
   b="A widget reads an [[Object Set]] variable; the user's selection produces an active/selected output set; [[Object Set Filter|filters]] narrow other sets (the canonical Filter List → Object Table pattern). The read side of the app↔ontology contract.",
   inv=["Semantic Model Over Data"], rel=["Object Set","Object Set Filter","Widget","Functions on Objects (FOO)"],
   src="App-Building reconstruction §5"),
 dict(t="Object Set Filter", L="app", k="concept",
   d="A reusable variable of property/value pairs applied to object set variables to narrow them.",
   b="Output by Filter List, charts, and pivot tables; applied to a *separate* object-set variable so the base set isn't limited. The app-layer expression of querying the [[Object Set|object model]].",
   inv=["Semantic Model Over Data"], rel=["Object Set","Object Set Binding","Workshop Variable"],
   src="App-Building reconstruction §4"),
 dict(t="Auto-Refresh", L="app", k="mechanism",
   d="Module-level live data updates: watches registered object sets and refreshes when they change anywhere in Foundry.",
   b="Reflects other users' actions, upstream edits, and streaming sources without user interaction — the app-layer realization of [[Read-Your-Writes]]. Limited to [[Object Storage V2 (OSv2)|OSv2]]-backed object types.",
   inv=["Semantic Model Over Data"], rel=["Read-Your-Writes","Object Storage V2 (OSv2)","Object Set Binding"],
   src="App-Building reconstruction §5"),
 dict(t="Slate", L="app", k="service",
   d="The legacy power-user builder (HTML/JS/CSS) for pixel-level custom or public unauthenticated apps.",
   b="A [[Slate Node Graph|graph of nodes]] referenced via [[Handlebars (Slate)|Handlebars]]; higher customization at higher maintenance. Recommended only when Workshop can't express the design; legacy data paths are deprecated.",
   inv=["Semantic Model Over Data"], rel=["Slate Node Graph","Handlebars (Slate)","Workshop"],
   clone="Skip — Workshop's model is the one to emulate.",
   src="App-Building reconstruction §6"),
 dict(t="Slate Node Graph", L="app", k="mechanism",
   d="Slate's model: widgets, variables, queries, and functions are nodes whose JSON outputs reference each other.",
   b="Explicitly lazy — a node re-evaluates only when an upstream reference changes value. The same reactive idea as Workshop's [[Reactivity Model]], but hand-managed.",
   inv=["Semantic Model Over Data"], rel=["Slate","Handlebars (Slate)","Reactivity Model"],
   src="App-Building reconstruction §6"),
 dict(t="Handlebars (Slate)", L="app", k="mechanism",
   d="Slate's `{{ }}` templating syntax that both reads node outputs and declares dependencies.",
   b="References to widgets/variables/environment define the dependency edges of the [[Slate Node Graph]]. The wiring mechanism of a Slate app.",
   inv=["Semantic Model Over Data"], rel=["Slate","Slate Node Graph"],
   src="App-Building reconstruction §6"),
 dict(t="Object View", L="app", k="concept",
   d="The per-object detail surface — now itself a Workshop module (full), with legacy YAML views still supported.",
   b="Auto-created standard views show prominent properties + links; configured views use the full widget set in tabs. Permissions sync with the object type. Maps app variables onto the view via the [[Module Interface]].",
   inv=["Semantic Model Over Data","Security Travels With Data"], rel=["Workshop Module","Module Interface","Object Type","App vs Data Permissions"],
   src="App-Building reconstruction §7"),
 dict(t="Custom Widget", L="app", k="mechanism",
   d="Developer-built React frontend code embedded in Workshop, running in a restrictive sandbox.",
   b="Packaged as a [[Widget Set]]; declares parameters (host→widget) and events (widget→host); uses [[OSDK React Hooks]] under the user's permissions. No web storage, no external requests, non-configurable CSP. The escape hatch for custom UI.",
   inv=["Semantic Model Over Data","Security Travels With Data"], rel=["Widget Set","OSDK React Hooks","Bidirectional Iframe","Workshop"],
   src="App-Building reconstruction §8"),
 dict(t="Widget Set", L="app", k="concept",
   d="A deployable package of one or more custom widgets (OSDK build artifacts).",
   b="Built with `@osdk/widget.*` packages; rendered via the `FoundryWidget` root; registered under `ri.widgetregistry..widget-set`. The distribution unit for custom UI.",
   inv=["Semantic Model Over Data"], rel=["Custom Widget","OSDK React Hooks"],
   src="App-Building reconstruction §8"),
 dict(t="Bidirectional Iframe", L="app", k="mechanism",
   d="Embedding an external app that reads/writes Workshop state via `useWorkshopContext`.",
   b="The `@osdk/workshop-iframe-custom-widget` context exposes Workshop variable read/write and event execution over `postMessage`. Recommended over the plain iframe widget for custom apps (one per instance; ≤1 on-screen recommended).",
   inv=["Semantic Model Over Data"], rel=["Custom Widget","Workshop Event","Slate"],
   src="App-Building reconstruction §8"),
 dict(t="OSDK React Hooks", L="app", k="mechanism",
   d="The typed React data layer (`useObjectSet`, `useOsdkAction`, …) for custom apps and widgets.",
   b="Provide automatic caching, loading states, and real-time updates; require an `OsdkProvider2`. Calls run under the user's permissions. The bridge from custom UI to the [[Ontology]].",
   inv=["Semantic Model Over Data","Security Travels With Data"], rel=["Custom Widget","Widget Set","Object Set"],
   src="App-Building reconstruction §8 / §10"),
 dict(t="App vs Data Permissions", L="app", k="pattern",
   d="Module access is decoupled from access to the data, actions, and functions the module uses.",
   b="A user can open an app but be blocked from its objects/actions (widgets show permission errors). Security lives on the data, not the app — a direct consequence of [[Security Travels With Data]].",
   inv=["Security Travels With Data"], rel=["Workshop Module","Role","Object View","Edits-Only-via-Actions"],
   clone="Keep — enforce on the data/action, never trust the app surface.",
   src="App-Building reconstruction §9"),
 dict(t="AIP Agent Widget", L="app", k="mechanism",
   d="A Workshop widget embedding an AIP agent/chatbot — the AIP↔app seam.",
   b="Maps the agent's 'application variables' to Workshop variables (read/write); its tools include AIP Logic and [[Functions on Objects (FOO)]]. How AI reaches the user surface; see [[AIP Tool Exposure]] and the [[AIP Layer]].",
   inv=["Semantic Model Over Data","Governed Writeback"], rel=["AIP Layer","AIP Tool Exposure","Widget","Functions on Objects (FOO)"],
   clone="Defer — the AI surface is post-MVP.",
   src="App-Building reconstruction §3"),
 dict(t="Embedded Foundry Apps", L="app", k="mechanism",
   d="Embedding other Foundry surfaces (Slate, Quiver, Notepad, Vertex, Map) inside a Workshop module.",
   b="Cross-app state flows via [[Module Interface]] mappings, drag-and-drop drop zones, and app pairing. Lets a module compose analytical and custom surfaces around the operational core.",
   inv=["Semantic Model Over Data"], rel=["Workshop Module","Module Interface","Slate","Bidirectional Iframe"],
   src="App-Building reconstruction §8"),
]

# ---- AIP LAYER ------------------------------------------------------------
CONCEPTS += [
 dict(t="Execution-Permission Contract", L="aip", k="pattern",
   d="The make-or-break AIP principle: the LLM only ASKS to use a tool; the platform EXECUTES it in the invoking user's permissions.",
   b="Verbatim: 'LLMs do not have direct access to tools; LLMs can only ask to use tools, and these tool calls are then executed … within the invoking user's permissions.' The LLM never holds credentials, sees only configured data, and can mutate only through [[Action Type|actions]]. This is why AI is *safe* on top of the engine.",
   inv=["Governed Writeback","Security Travels With Data"], rel=["AI Tool","AIP Tool Exposure","Edits-Only-via-Actions","Role"],
   clone="Replicate exactly — we get a safe AI layer for free IF our action+role model is sound.",
   src="AIP reconstruction §3.3 (verbatim, verified)"),
 dict(t="AIP Logic", L="aip", k="service",
   d="A no-code builder for LLM-powered Ontology functions, composed of chained blocks.",
   b="A Logic function takes objects/primitives, runs [[Logic Block|blocks]] (prompt + tools + output), and returns a value, object, struct, or [[Edits-Only-via-Actions|ontology edits]] (only persisted when run from an action). Published as a callable [[Function]].",
   inv=["Governed Writeback","Semantic Model Over Data"], rel=["Logic Block","Use LLM Block","AI Tool","Function","Agent-as-Function"],
   clone="Defer — but its block model is a clean template if we ever add AI.",
   src="AIP reconstruction §2"),
 dict(t="Logic Block", L="aip", k="concept",
   d="A discrete step in an AIP Logic function whose output can feed later blocks.",
   b="Types: [[Use LLM Block]], Apply action, Execute function, Conditionals, Loops, Create variable. Chaining blocks builds complex operations deterministically around the non-deterministic LLM step.",
   inv=["Governed Writeback"], rel=["AIP Logic","Use LLM Block","Action Type","Function"],
   src="AIP reconstruction §2.1"),
 dict(t="Use LLM Block", L="aip", k="concept",
   d="'The heart of AIP Logic' — a block composed of a prompt, tools, and a typed output.",
   b="Supports any platform model (k-LLM via the [[Model Gateway]]); temperature configurable; per-block token limit. The point where reasoning meets the [[AI Tool|tools]] over the Ontology.",
   inv=["Semantic Model Over Data"], rel=["Logic Block","AI Tool","Model Gateway","AIP Logic"],
   src="AIP reconstruction §2.1"),
 dict(t="AI Tool", L="aip", k="concept",
   d="A platform capability an LLM can request: query objects (data), call a function (logic), or apply an action (action).",
   b="Tools map onto [[Object Type|object types]], [[Function|functions]], and [[Action Type|action types]]. Chatbots add update-variable, command, and request-clarification. The LLM's only way to touch the world — and always via the [[Execution-Permission Contract]].",
   inv=["Governed Writeback","Semantic Model Over Data"], rel=["Execution-Permission Contract","Tool-Calling Mode","Action Type","Function","Object Set"],
   src="AIP reconstruction §3.1"),
 dict(t="Tool-Calling Mode", L="aip", k="mechanism",
   d="How tools are invoked: prompted (one tool at a time, all models) or native (parallel, subset of models).",
   b="Prompted mode inserts tool instructions into the prompt; native mode uses the model's built-in tool-calling. The orchestration loop runs tools, feeds results back, and iterates until a final answer (bounded by an iterations limit).",
   inv=["Governed Writeback"], rel=["AI Tool","Use LLM Block","AIP Agent"],
   src="AIP reconstruction §3.4"),
 dict(t="AIP Chatbot Studio", L="aip", k="service",
   d="The builder for stateful conversational agents (formerly AIP Agent Studio).",
   b="Configures instructions, [[AI Tool|tools]], model + temperature, [[Application State]], and [[Retrieval Context]]. Publishes the agent as an [[Agent-as-Function]]. Surfaces in the [[AIP Agent Widget]].",
   inv=["Governed Writeback","Semantic Model Over Data"], rel=["AIP Agent","Application State","Retrieval Context","Agent-as-Function","AIP Agent Widget"],
   clone="Defer.",
   src="AIP reconstruction §4"),
 dict(t="AIP Agent", L="aip", k="concept",
   d="A stateful conversational agent that reasons over tools and retrieval context within a user's permissions.",
   b="Maintains a session (system prompt + history + injected context + [[Application State]]); reasons via a [[Tool-Calling Mode|tool-calling loop]]; cannot exceed the [[Execution-Permission Contract]]. Formerly 'AIP Agent', now 'AIP Chatbot'.",
   inv=["Governed Writeback"], rel=["AIP Chatbot Studio","Application State","Agent-as-Function","Execution-Permission Contract"],
   src="AIP reconstruction §4"),
 dict(t="Application State", L="aip", k="concept",
   d="Named string/object-set variables that hold an agent's context across turns (formerly 'parameters').",
   b="Can be tool inputs, retrieval inputs, or citation outputs; a value-visibility toggle controls whether the LLM may read each. Updated deterministically (pinned at loop start) or via the update-variable tool.",
   inv=["Semantic Model Over Data"], rel=["AIP Agent","AIP Agent Widget","Retrieval Context"],
   src="AIP reconstruction §4.2"),
 dict(t="Agent-as-Function", L="aip", k="mechanism",
   d="An agent/chatbot published as an Ontology Function with a fixed userInput/sessionRid I/O contract.",
   b="Inputs `userInput` + optional `sessionRid` (+ app variables); outputs `markdownResponse` + `sessionRid`. Makes the agent callable by [[Automate]], [[AIP Evals]], Code Repositories, and the OSDK — the same [[Define-Once Reuse]] pattern as every other [[Function]].",
   inv=["Governed Writeback","Define-Once Reuse"], rel=["AIP Agent","Function","Automate","AIP Evals"],
   src="AIP reconstruction §4.3"),
 dict(t="AIP Evals", L="aip", k="service",
   d="An evaluation harness for LLM functions/agents: test cases, evaluators, objectives, and experiments.",
   b="Tames non-determinism by scoring target functions against expected outputs with [[Evaluator|evaluators]]; pass/fail objectives and thresholds gate publishing. Experiments grid-search model × prompt to optimize cost/performance.",
   inv=["Governed Writeback","End-to-End Lineage"], rel=["Evaluator","Agent-as-Function","AIP Logic"],
   clone="The discipline (evals-as-gates) matters even for non-AI logic.",
   src="AIP reconstruction §5"),
 dict(t="Evaluator", L="aip", k="concept",
   d="A scoring function in AIP Evals: built-in (exact/range/regex), LLM-as-a-judge, Marketplace, or custom.",
   b="Returns boolean/numeric metrics per test case; an objective decides which result passes. LLM-as-a-judge lets one model grade another against a condition. The unit of measurable AI quality.",
   inv=["End-to-End Lineage"], rel=["AIP Evals"],
   src="AIP reconstruction §5.2"),
 dict(t="Retrieval Context", L="aip", k="mechanism",
   d="Information injected into the prompt on every user message: Ontology, document, or function-backed context.",
   b="Grounds generations in real data — a fixed object set or [[Semantic Search|semantic search]] over [[Object Type|objects]], document chunks, or a custom retrieval function. Foundry's RAG ('Ontology-augmented generation').",
   inv=["Semantic Model Over Data"], rel=["Semantic Search","AIP Agent","Application State","Object Set"],
   src="AIP reconstruction §7.1"),
 dict(t="Semantic Search", L="aip", k="mechanism",
   d="Nearest-neighbor retrieval over Vector-type Ontology properties (embeddings).",
   b="An embedding property (Dimension + Similarity Function) is populated via Pipeline Builder/transforms; queries embed the input and return the K most similar objects. The grounding backbone of [[Retrieval Context]] and the reason [[Advanced Property Types|vector properties]] exist.",
   inv=["Semantic Model Over Data"], rel=["Retrieval Context","Advanced Property Types","Object Type"],
   src="AIP reconstruction §7.2"),
 dict(t="Model Gateway", L="aip", k="service",
   d="The governed access layer to many LLMs ('k-LLM'): GPT, Claude, Gemini, Grok, Llama, and more.",
   b="Mediated by the [[Language Model Service]] with access controls, [[Zero Data Retention]], georestriction, and rate limits. Models are interchangeable per block/agent/node — the AI layer is model-agnostic by design.",
   inv=["Security Travels With Data"], rel=["Language Model Service","Zero Data Retention","Use LLM Block"],
   src="AIP reconstruction §6"),
 dict(t="Language Model Service", L="aip", k="service",
   d="The internal service that mediates all LLM calls between Foundry and model providers.",
   b="Fronts Azure / AWS Bedrock / Google Vertex backends; enforces [[Zero Data Retention]] and regional routing. Runs in the shared [[Platform & Ecosystem Layer|Rubix/Apollo]] mesh.",
   inv=["Security Travels With Data"], rel=["Model Gateway","Zero Data Retention","Platform & Ecosystem Layer"],
   src="AIP reconstruction §10.4"),
 dict(t="Zero Data Retention", L="aip", k="property",
   d="No customer data in prompts/completions is retained by third-party model providers, nor used to retrain.",
   b="Backed by technical + contractual guarantees; combined with georestriction it keeps AI use compliant. A precondition for putting governed enterprise data in front of external LLMs.",
   inv=["Security Travels With Data"], rel=["Model Gateway","Language Model Service"],
   src="AIP reconstruction §6.2"),
 dict(t="AIP Assist", L="aip", k="service",
   d="An in-platform AI help tool trained on Foundry docs (no access to customer data), context-aware of the current app.",
   b="The 'meta' AI surface that helps builders use Foundry itself; can be backed by custom chatbots/content sources. Distinct from app-facing agents.",
   inv=["Semantic Model Over Data"], rel=["AIP Chatbot Studio","AIP Logic"],
   src="AIP reconstruction §9"),
]

# ---- SECURITY SPINE (deep reconstruction) ---------------------------------
CONCEPTS += [
 dict(t="Authorization Decision", L="security", k="pattern",
   d="The composition rule: access is granted only if ALL mandatory controls pass AND a role grants the operation AND any granular policy passes — default-deny.",
   b="Four gates in order: valid session → [[Mandatory Control|mandatory controls]] (all-or-nothing, override roles) → a [[Role]] granting the [[Operation]] → a [[Granular Policy]]/[[Object Security Policy]] at row/cell level. Miss any gate and access is denied. The single most important rule to replicate.",
   inv=["Security Travels With Data"], rel=["Mandatory Control","Role","Operation","Granular Policy","Marking"],
   clone="Replicate exactly: default-deny; mandatory controls beat roles.",
   src="Security reconstruction §3 (composition; [Inferred] order)"),
 dict(t="Multipass", L="security", k="service",
   d="Foundry's internal identity backbone: users, groups, key-value attributes, and tokens.",
   b="External [[Identity Provider (SSO)|IdPs]] feed it; the `multipass:` attribute prefix is reserved internally; Org RIDs are `ri.multipass..organization`. Every [[Authorization Decision]] starts from a Multipass identity.",
   inv=["Security Travels With Data"], rel=["Identity Provider (SSO)","User Attribute","Group","Authentication & Session","Organization"],
   clone="Becomes our user/identity store — far simpler (a users/groups/attrs schema).",
   src="Security reconstruction §2"),
 dict(t="Identity Provider (SSO)", L="security", k="mechanism",
   d="An external authentication source (SAML 2.0 / OIDC) that validates users and supplies attributes and groups.",
   b="Foundry is the Service Provider; email-domain rules route logins; [[User Attribute|attributes]] and provider [[Group|groups]] are mapped in on login. The federation seam — Foundry rarely owns credentials itself.",
   inv=["Security Travels With Data"], rel=["Multipass","Authentication & Session","User Attribute","Group"],
   clone="Defer SSO; start with local auth, design for an IdP later.",
   src="Security reconstruction §2"),
 dict(t="Authentication & Session", L="security", k="mechanism",
   d="MFA-backed login producing a short-lived session token (PALANTIR_TOKEN, ~16h default).",
   b="MFA is mandatory; sessions are intentionally short to force re-auth; idle accounts deactivate after 30 days. The gate-zero of every [[Authorization Decision]].",
   inv=["Security Travels With Data"], rel=["Multipass","Identity Provider (SSO)","Service User & Tokens","Authorization Decision"],
   src="Security reconstruction §2"),
 dict(t="User Attribute", L="security", k="concept",
   d="A key-value, multi-valued property on a user (or group) used by policies and services.",
   b="Populated by the [[Identity Provider (SSO)|IdP]] or admins; the `multipass:` namespace is reserved. The raw material [[Granular Policy|granular policies]] compare against. Attribute-based access control (ABAC) lives here.",
   inv=["Security Travels With Data"], rel=["Multipass","Group","Granular Policy"],
   src="Security reconstruction §2"),
 dict(t="Group", L="security", k="concept",
   d="A named collection of users (direct + inherited members; provider groups mirror the IdP).",
   b="The usual grant target — assign [[Role|roles]] and [[Marking|markings]] to groups, not individuals. Membership (direct and inherited) drives policy evaluation.",
   inv=["Security Travels With Data"], rel=["Multipass","Role","User Attribute","Project"],
   src="Security reconstruction §2"),
 dict(t="Operation", L="security", k="concept",
   d="An atomic, namespaced permission an app checks before allowing an action (e.g. compass:read-resource).",
   b="Namespaces map to subsystems (`compass:`, `stemma:`, `s3-proxy:`, `marketplace:`, `audit-export:`). [[Role|Roles]] are just sets of operations; the [[Authorization Decision]] checks for the specific operation.",
   inv=["Security Travels With Data"], rel=["Role","Role Set","Authorization Decision"],
   src="Security reconstruction §3"),
 dict(t="Role Set", L="security", k="concept",
   d="A context-scoped group of roles (Project, Ontology, or Marketplace Installation contexts).",
   b="Customizing default [[Role|roles]] means copying a role set; roles can 'Include' others to inherit [[Operation|operations]]. How role definitions are versioned and namespaced.",
   inv=["Security Travels With Data"], rel=["Role","Operation"],
   clone="Defer — start with fixed roles; add custom role sets later.",
   src="Security reconstruction §3"),
 dict(t="Mandatory Control", L="security", k="concept",
   d="The all-or-nothing access requirements that override roles: Markings, Organizations, and CBAC classifications.",
   b="A user must hold ALL applied [[Marking|markings]], belong to ≥1 applied [[Organization]], and (if CBAC) be classified ≥ the resource's max. They propagate down hierarchy and lineage and cannot be overridden by a [[Role]]. The teeth of [[Security Travels With Data]].",
   inv=["Security Travels With Data"], rel=["Marking","Organization","Classification-Based Access Control (CBAC)","Authorization Decision","Mandatory Control Property"],
   clone="Replicate Markings + a simple tenant/Org; drop CBAC at v1.",
   src="Security reconstruction §4"),
 dict(t="Scoped Session", L="security", k="mechanism",
   d="A session deliberately limited to a chosen subset of a user's Markings.",
   b="Lets a user operate at reduced privilege for a task; 'authorized group IDs' from the scope feed [[Granular Policy|policies]]. A least-privilege refinement of [[Authentication & Session]].",
   inv=["Security Travels With Data"], rel=["Authentication & Session","Marking","Granular Policy"],
   clone="Defer.",
   src="Security reconstruction §2/§5"),
 dict(t="Service User & Tokens", L="security", k="mechanism",
   d="Non-human identities and API credentials: personal access tokens (PATs) and OAuth2 (auth-code / client-credentials).",
   b="A PAT carries the creating user's permissions; client-credentials creates a service user with NO access by default. Effective access = intersection of identity permissions ∩ app scope ∩ requested scope. The programmatic on-ramp.",
   inv=["Security Travels With Data"], rel=["Authentication & Session","Multipass","Role"],
   clone="Keep — API keys/service accounts scoped by role.",
   src="Security reconstruction §2"),
 dict(t="Egress Policy", L="security", k="mechanism",
   d="Controls on outbound network access from Foundry (direct-connection vs agent-proxy), enforced by Cilium/eBPF.",
   b="Set by the Information Security Officer by domain/IP/CIDR; destinations immutable once created. Compute defaults to zero-trust (no external network until a source is attached). How the platform contains data exfiltration.",
   inv=["Security Travels With Data"], rel=["Foundry Worker","Agent-Proxy vs Agent Worker","Data Connection"],
   clone="Defer — relevant only once we have external integrations.",
   src="Security reconstruction §8"),
 dict(t="Encryption at Rest & in Transit", L="security", k="property",
   d="TLS 1.2+ in transit; application-level encryption at rest; AES-256-GCM for modern connector credentials.",
   b="Legacy agents use AES-128-GCM with keys on the host. The baseline confidentiality guarantee underneath every layer; [[Cipher]] adds field-level encryption on top.",
   inv=["Security Travels With Data"], rel=["Cipher","Egress Policy","Foundry Worker"],
   clone="Keep the baseline (TLS + at-rest); use the platform/DB defaults.",
   src="Security reconstruction §8"),
 dict(t="Cipher", L="security", k="service",
   d="In-platform field-level encryption: Channels define algorithms/keys; Licenses govern who can encrypt/decrypt.",
   b="Value- or column-level encryption/hashing (AES-GCM-SIV, AES-SIV, salted SHA), rate-limited and cell-level auditable. For data so sensitive that even authorized viewers shouldn't see plaintext.",
   inv=["Security Travels With Data"], rel=["Encryption at Rest & in Transit","Property Security Policy"],
   clone="Defer — niche field-level encryption.",
   src="Security reconstruction §8"),
 dict(t="Audit Schema", L="security", k="mechanism",
   d="The audit-log format, migrating from audit.2 to the category-based, low-latency audit.3.",
   b="audit.3 logs every event under standardized categories with promoted `entities`/`origins`/`result` fields, ~15-minute latency, pollable by SIEMs via the audit API. The queryable backbone of [[End-to-End Lineage]] and [[Audit Log]].",
   inv=["End-to-End Lineage","Security Travels With Data"], rel=["Audit Log","Edit History"],
   clone="Keep the idea (an append-only events stream); our [[Audit Log]] covers it.",
   src="Security reconstruction §7"),
 dict(t="Compliance Accreditation", L="security", k="reference",
   d="The government/enterprise certifications the platform holds: FedRAMP High, DoD IL5/IL6, CMMC Level 2, SOC 2, ISO 27001.",
   b="FedRAMP High (Dec 2024) covers Foundry/AIP/Apollo/Gotham; CMMC L2 (Sep 2025) via C3PAO. Deployed/audited through [[Platform & Ecosystem Layer|Apollo]]. Context for *why* the security model is so elaborate — almost all of it is droppable for an internal tool.",
   inv=["Security Travels With Data"], rel=["Platform & Ecosystem Layer","Audit Schema"],
   clone="Drop — irrelevant unless we ever pursue accreditation.",
   src="Security reconstruction §9 (verified dates)"),
 dict(t="Space", L="security", k="concept",
   d="A high-level container of Projects sharing one Ontology, restricted by an Organization or set of Organizations.",
   b="The first path element (`space/project/...`); a multi-org space enables cross-org collaboration. Sits above the [[Project]] in the resource hierarchy.",
   inv=["Security Travels With Data"], rel=["Project","Organization","Ontology"],
   clone="Simplify — a single workspace at v1.",
   src="Security reconstruction §6"),
]

# ---- PLATFORM & ECOSYSTEM LAYER -------------------------------------------
CONCEPTS += [
 dict(t="Apollo", L="platform", k="service",
   d="Palantir's continuous-delivery control plane: a constraint-based, pull-model system with NO single target state.",
   b="Developers register [[Apollo Product|products]] + constraints; environments subscribe to [[Release Channel|channels]]; the [[Orchestration Engine]] proposes [[Apollo Plan|Plans]] that satisfy all constraints. Deployments are versioned operational logic, not code bundles. Hosts Foundry + AIP on [[Rubix]].",
   inv=["End-to-End Lineage"], rel=["Hub-and-Spoke","Orchestration Engine","Apollo Plan","Apollo Product","Release Channel","Rubix"],
   clone="Drop for an internal tool — ordinary deployment suffices; keep only the idea of versioned, auditable releases.",
   src="Platform reconstruction §2"),
 dict(t="Hub-and-Spoke", L="platform", k="mechanism",
   d="Apollo's topology: a Hub holds the brain (catalog, settings, Orchestration Engine); Spokes are K8s clusters running a thin control plane.",
   b="All Agent→Hub traffic is encrypted, unidirectional, and outbound, authenticated by a per-Environment key signed at registration. This is what makes air-gapped/disconnected operation possible.",
   inv=["Security Travels With Data"], rel=["Apollo","Spoke Control Plane","Orchestration Engine"],
   clone="Drop — over-engineering unless shipping to many disconnected environments.",
   src="Platform reconstruction §2.1"),
 dict(t="Orchestration Engine", L="platform", k="service",
   d="Hub services that continuously evaluate all possible Plans against constraints and issue the satisfied ones.",
   b="Also drives [[Promotion Pipeline|release promotion]] using reported health. The embodiment of 'no target state' — it proposes the latest [[Release & Version|release]] allowed by [[Apollo Constraint|constraints]], not a declared desired state.",
   inv=["End-to-End Lineage"], rel=["Apollo","Apollo Plan","Apollo Constraint","Promotion Pipeline"],
   src="Platform reconstruction §2.2"),
 dict(t="Apollo Plan", L="platform", k="concept",
   d="A unit of deployment work (install / config / upgrade / uninstall / secret) issued to an agent only once all constraints pass.",
   b="Apollo surfaces Plans for transparency rather than acting silently like a control loop. Roll-off and break-glass Plans are prioritized. The atom of change in [[Apollo]].",
   inv=["End-to-End Lineage"], rel=["Orchestration Engine","Apollo Constraint","Spoke Control Plane"],
   src="Platform reconstruction §2.3"),
 dict(t="Apollo Constraint", L="platform", k="concept",
   d="A precondition a Plan must satisfy: dependencies, incompatibilities, schema versions, maintenance/suppression windows, health.",
   b="The engine can only propose changes that violate no constraint — how Apollo keeps thousands of services compatible during rolling upgrades.",
   inv=["Security Travels With Data","End-to-End Lineage"], rel=["Apollo Plan","Orchestration Engine","Apollo Product"],
   src="Platform reconstruction §2.3"),
 dict(t="Apollo Product", L="platform", k="concept",
   d="A deployable software component (Helm chart or asset) identified by Maven coordinates, with an immutable manifest.",
   b="Packaged as a tarball with declarative dependency/incompatibility/health extensions; published to the per-Hub Product catalog. The deployment counterpart to a [[Marketplace Product]].",
   inv=["End-to-End Lineage"], rel=["Release & Version","Apollo","Marketplace Product"],
   src="Platform reconstruction §3"),
 dict(t="Release & Version", L="platform", k="concept",
   d="A published, versioned artifact + immutable metadata; versions are strictly orderable so Apollo can reason about upgrades.",
   b="Identified by `group:artifactId:version`. Ordering lets the engine compute forward/backward migrations and compatibility ranges. The unit that flows through [[Release Channel|channels]].",
   inv=["End-to-End Lineage","Versioned Data Foundation"], rel=["Apollo Product","Release Channel","Recall & Roll-off"],
   src="Platform reconstruction §3.1"),
 dict(t="Entity & Environment", L="platform", k="concept",
   d="An Entity is one installed Product in one Environment; an Environment is a grouping of Entities in one cluster.",
   b="Environments are disjoint and may be disconnected when unmanaged. An Entity is defined by a Product + [[Release Channel]] (not a fixed version) — Apollo keeps it at the latest allowed state.",
   inv=["Security Travels With Data"], rel=["Apollo Product","Release Channel","Hub-and-Spoke"],
   src="Platform reconstruction §3.1"),
 dict(t="Release Channel", L="platform", k="mechanism",
   d="A named promotion tier (e.g. RELEASE → CANARY → STABLE) that environments subscribe to by stability need.",
   b="The pull-model dial: operators choose a channel; the [[Promotion Pipeline]] moves releases between channels by health and soak. Decouples 'what exists' from 'what each env runs'.",
   inv=["End-to-End Lineage"], rel=["Promotion Pipeline","Release & Version","Entity & Environment"],
   src="Platform reconstruction §4"),
 dict(t="Promotion Pipeline", L="platform", k="mechanism",
   d="Health- and time-gated automatic promotion of a release between channels (soak duration + criteria).",
   b="Promotes only after a release stays healthy across N entities for a soak window; cancels on timeout (2× soak; 7-day canary reachability); can auto-[[Recall & Roll-off|recall]] when unhealthy. The safety automation of delivery.",
   inv=["End-to-End Lineage"], rel=["Release Channel","Recall & Roll-off","Zero-Downtime Upgrade","Orchestration Engine"],
   src="Platform reconstruction §4.2"),
 dict(t="Recall & Roll-off", L="platform", k="mechanism",
   d="Marking a release bad and reverting: roll forward, allow downgrade, freeze, or per-environment.",
   b="Triggered manually, automatically (unstable promotion), or via API (e.g. CVE scans). Safety can override the no-downtime window during a recall. The rollback story.",
   inv=["End-to-End Lineage"], rel=["Release & Version","Promotion Pipeline","Apollo"],
   src="Platform reconstruction §4.3"),
 dict(t="Zero-Downtime Upgrade", L="platform", k="mechanism",
   d="Blue/green rollout on multi-node services: build a parallel 'green', shift traffic, destroy 'blue'.",
   b="Required of every service claiming zero-downtime; leverages [[Rubix]]'s opinionated API layer. How Apollo runs thousands of upgrades a day without outage.",
   inv=["Security Travels With Data"], rel=["Promotion Pipeline","Rubix","Apollo"],
   src="Platform reconstruction §4.4"),
 dict(t="Spoke Control Plane", L="platform", k="service",
   d="The thin set of Spoke-side services that execute Plans and report state: helm-chart-operator, apollo-auth-broker, expected-state-k8s, + the Agent.",
   b="`helm-chart-operator` runs lifecycle actions and manages the others; `apollo-auth-broker` brokers auth to registries; `expected-state-k8s` reports state/health to the Hub. The Spoke's whole footprint.",
   inv=["Security Travels With Data"], rel=["Hub-and-Spoke","Apollo Plan","Rubix"],
   src="Platform reconstruction §2.4 (verified)"),
 dict(t="Marketplace", L="platform", k="service",
   d="The packaging + storefront layer over Apollo: install/upgrade self-contained Products from Stores.",
   b="Products are collections of Foundry resources with bundled dependency metadata, published to Stores (Foundry / local / remote) and installed via [[Apollo]] orchestration. The distribution UX; Apollo does the execution.",
   inv=["End-to-End Lineage"], rel=["Marketplace Product","Linked Products","Foundry DevOps","Apollo"],
   clone="Drop — a simple export/import step covers our needs.",
   src="Platform reconstruction §5"),
 dict(t="Marketplace Product", L="platform", k="concept",
   d="A self-contained, portable bundle of Foundry resources with dependency metadata and mappable inputs.",
   b="Content (installed resources) + inputs (dependencies to map). Most resource types can be packaged — [[Object Type|object types]], [[Action Type|actions]], [[Function|functions]], [[Workshop Module|modules]], models — but **objects themselves cannot**. Versioned for consistent installs/rollbacks.",
   inv=["End-to-End Lineage"], rel=["Marketplace","Linked Products","Apollo Product","Object Type"],
   src="Platform reconstruction §5.1"),
 dict(t="Linked Products", L="platform", k="mechanism",
   d="One-way upstream→downstream connections that auto-map one product's outputs to another's inputs.",
   b="DevOps inspects packaged entities to derive links (a pipeline's clean datasets feed an Ontology product's inputs). Modularizes workflows; breaking changes force major-version bumps. Lineage-driven packaging.",
   inv=["End-to-End Lineage"], rel=["Marketplace Product","Foundry DevOps","Data Lineage Graph"],
   src="Platform reconstruction §5.3"),
 dict(t="Foundry DevOps", L="platform", k="service",
   d="The release-management app that packages resources from one environment and promotes them to the next.",
   b="Pairs with [[Space|Spaces]] for environment separation (Dev/Test/Prod) and with [[Marketplace]] for distribution; complementary to [[Dataset Branch|branching]] (in-environment iteration vs cross-environment promotion).",
   inv=["End-to-End Lineage"], rel=["Marketplace","Space","Dataset Branch","Marketplace Product"],
   clone="Simplify to a basic dev→prod promotion step.",
   src="Platform reconstruction §6"),
 dict(t="Rubix", L="platform", k="service",
   d="Palantir's hardened, autoscaling Kubernetes substrate running the whole stack, with nodes that live ≤48 hours.",
   b="Aggressive node cycling guards against persistent threats; Cilium/eBPF egress, Envoy proxy, zero-trust isolation, FedRAMP/IL accreditation. The infrastructure floor under [[Apollo]], Foundry, and AIP.",
   inv=["Security Travels With Data"], rel=["Compute Mesh","Apollo","Zero-Downtime Upgrade","Egress Policy"],
   clone="Drop — use ordinary managed infrastructure (a container host or a single VM).",
   src="Platform reconstruction §7.1 (verified 48h)"),
 dict(t="Compute Mesh", L="platform", k="concept",
   d="The 300+ microservice, zero-trust, autoscaling fabric that is Foundry + AIP, all powered by Apollo.",
   b="Maps into nine capability sets over six mesh-wide components (storage/compute/networking/security/governance/workspace). The 'Enterprise Operating System' in physical form. Its scale is exactly what we DON'T replicate.",
   inv=["Security Travels With Data"], rel=["Rubix","Enterprise Operating System","Apollo"],
   clone="Drop — our clone is a handful of services, not 300.",
   src="Platform reconstruction §7.2"),
 dict(t="Enterprise Operating System", L="platform", k="concept",
   d="Palantir's framing of AIP + Foundry + Apollo as one integrated operating system for an organization.",
   b="Data ([[Data Integration & Pipeline Layer|Foundry]]) + meaning ([[Ontology]]) + AI ([[AIP Layer]]) + delivery ([[Apollo]]) as a single stack. The whole that all eight reconstructed layers compose into.",
   inv=["End-to-End Lineage"], rel=["Apollo","Compute Mesh","Gotham","The Closed Loop"],
   src="Platform reconstruction §9.1"),
 dict(t="Gotham", L="platform", k="concept",
   d="Palantir's original (2008) defense/intelligence platform — the birthplace of the 'dynamic ontology'.",
   b="Pioneered mapping heterogeneous data into objects/properties/links for analysts; Foundry generalized that into the commercial [[Ontology]]. Today Gotham integrates atop the Foundry-managed Ontology via type mapping (querying through the [[Object Set Service (OSS)]]).",
   inv=["Semantic Model Over Data"], rel=["Ontology","Object Set Service (OSS)","Enterprise Operating System"],
   src="Platform reconstruction §9.2"),
 dict(t="Enrollment", L="platform", k="concept",
   d="An Organization's primary Foundry identity — the tenancy/account boundary for a deployment.",
   b="Scopes resource limits, cloud identities, network policy, and which [[Marketplace Product|products]] are enabled. The top of the practical hierarchy above [[Space|spaces]] and [[Project|projects]].",
   inv=["Security Travels With Data"], rel=["Organization","Space","Project"],
   src="Platform reconstruction §8/§10"),
]

# ---- DYNAMIC LAYER (Ontology trilogy: what could happen next) -------------
CONCEPTS += [
 dict(t="Scenario", L="dynamic", k="concept",
   d="An immutable, delta-only fork of the Ontology — staged what-if edits that never touch reality until applied.",
   b="Created by applying [[Action Type|Actions]] and evaluating [[Model|Models]]; the fork stores **only the diff** from the base — modified properties, created/deleted objects, created/deleted links — keyed to base identity, not a snapshot. It is **immutable**: to 'modify' a Scenario you create a new one. Built on Actions infrastructure, so Action limits apply transitively. The projection half of the [[Digital Twin]].",
   inv=["Governed Writeback","Versioned Data Foundation"],
   rel=["Scenario Overlay","Scenario Apply (Commit)","Scenario Comparison","Action Type","Function-Backed Action","Model","Digital Twin"],
   clone="Defer — powerful but post-MVP. When built: a copy-on-write delta keyed to base identity, append-only/versioned, not a full copy.",
   src="Dynamic reconstruction §2.1–2.4"),
 dict(t="Scenario Overlay", L="dynamic", k="mechanism",
   d="The copy-on-write delta that holds a scenario's changes, merged over the base Ontology when a scenario context is supplied.",
   b="Records property mutations and created/deleted objects and links against base identity. Whether Foundry resolves it at read time or materializes a temporary store is **undocumented** ([Speculative]); the caps — 30,000 edits, 50 Actions, 10,000 objects loaded, no attachment properties — are consistent with a *bounded read-time merge*. Reads flow through the [[Object Set Service (OSS)]], and scenario state does not auto-propagate through object sets — consumers reference a scenario variable explicitly.",
   inv=["Versioned Data Foundation"],
   rel=["Scenario","Object Set Service (OSS)","Object Storage V2 (OSv2)","Workshop Variable"],
   clone="Defer — implement as a read-time overlay keyed to identity; validate the scale assumption against your own tests before trusting it.",
   src="Dynamic reconstruction §2.3, §2.8"),
 dict(t="Scenario Apply (Commit)", L="dynamic", k="mechanism",
   d="Committing a scenario by replaying its staged Actions transactionally — all-or-nothing — never by diff-merging a blob.",
   b="Either every Action applies or none does if any fails validation. **Model results are never written back** — they are expected outputs, not modifiable values. Permission to apply equals permission to run the configured apply [[Action Type|Action]]; an optional post-apply Action's validation gates it further.",
   inv=["Governed Writeback"],
   rel=["Scenario","Action Type","Action Atomicity","Submission Criteria","Model"],
   clone="Defer — but the rule is free once Actions are transactional: replay the staged Actions, and never persist model outputs.",
   src="Dynamic reconstruction §2.6"),
 dict(t="Scenario Comparison", L="dynamic", k="mechanism",
   d="Reading scenario-vs-baseline and scenario-vs-scenario side by side to see what each what-if changes.",
   b="Scenario-aware widgets show values **only in columns that differ** and can layer many scenarios at once; in [[Vertex]] a *baseline* runs the chosen [[Model|models]] with no overrides as the reference. A read-only surface over the [[Scenario Overlay]].",
   inv=["Versioned Data Foundation"],
   rel=["Scenario","Scenario Overlay","Vertex","Workshop Variable"],
   clone="Defer — a UI affordance over overlays; trivial once overlays and a baseline exist.",
   src="Dynamic reconstruction §2.5"),
 dict(t="Model", L="dynamic", k="concept",
   d="An artifact for inference spanning ML, forecasting, optimization, physical models, and business rules.",
   b="A uniform abstraction: model artifacts (weights/container) plus a Python **adapter** that lets the platform load, initialize, and run inference on any kind of model. Bound to the Ontology as model-backed properties and consumed by [[Functions on Models]], [[Action Type|Actions]], and [[Scenario|Scenarios]].",
   inv=["Semantic Model Over Data"],
   rel=["Modeling Objective","Functions on Models","Live Deployment","Simulation","Derived Property"],
   clone="Defer — model serving is post-MVP; the clone's [[Function]] model already accommodates inference later.",
   src="Dynamic reconstruction §3.1"),
 dict(t="Modeling Objective", L="dynamic", k="service",
   d="The 'mission control' lifecycle for one modeling problem: submit → evaluate → release → deploy → monitor.",
   b="A governance + automation + CI/CD layer: a submission is an immutable copy (like a pull request); a **release** is versioned and environment-tagged (Staging/Production); a deployment takes the latest tagged release with zero-downtime cutover. Spans problems classic ML-Ops tools miss — simulation and optimization.",
   inv=["Governed Writeback","End-to-End Lineage"],
   rel=["Model","Live Deployment","Inference History","Functions on Models"],
   clone="Defer — replicate the *contract* (versioned, tagged, governed releases) cheaply once models arrive.",
   src="Dynamic reconstruction §3.2"),
 dict(t="Functions on Models", L="dynamic", k="mechanism",
   d="Auto-generated Function wrappers around a live model deployment, callable from Actions, Scenarios, and derived properties.",
   b="They mirror the model's API in [[Function]]-supported types and **defer all logic to the underlying deployment** — one function per branch, and a new model version auto-versions the function. The seam by which model output becomes object or scenario state; capped at 50 MB I/O and 30 s execution.",
   inv=["Governed Writeback"],
   rel=["Function","Model","Live Deployment","Function-Backed Action","Scenario"],
   clone="Defer — wrap inference as an ordinary [[Function]] so the rest of the system stays model-agnostic.",
   src="Dynamic reconstruction §4.1"),
 dict(t="Live Deployment", L="dynamic", k="service",
   d="A serverless, autoscaling REST endpoint that serves a model for low-latency interactive inference.",
   b="Independently permissioned, highly available (updated via CI/CD without downtime), scales from zero, adds a replica at 75% capacity, and scales down after 30 minutes idle; queried at `…/foundry-ml-live/.../v2`. Contrast the **batch deployment** — pipeline inference on an input→output dataset. Feeds [[Scenario|scenarios]] and [[Simulation]].",
   inv=["Governed Writeback"],
   rel=["Model","Functions on Models","Modeling Objective","Simulation","Compute-Seconds"],
   clone="Defer — one small inference service replaces the autoscaling tier; the numbers (75%/30 min) are Palantir-scale artifacts.",
   src="Dynamic reconstruction §4.2"),
 dict(t="Inference History", L="dynamic", k="mechanism",
   d="A dataset ledger capturing the inputs and outputs of every request to a live deployment.",
   b="The model-side audit trail — enabling drift detection, continuous retraining, and performance evaluation; gated by an edit-inference-ledger permission and co-located with its objective because the I/O is sensitive. The temporal record that ties model behavior into [[End-to-End Lineage]] (not all I/O is guaranteed to appear).",
   inv=["End-to-End Lineage"],
   rel=["Model","Modeling Objective","Live Deployment","Edit History"],
   clone="Defer — an append-only inference log mirrors our [[Edit History]] pattern.",
   src="Dynamic reconstruction §3.3"),
 dict(t="Simulation", L="dynamic", k="pattern",
   d="Running models over the Ontology inside a scenario to project outcomes, then comparing to a baseline.",
   b="Function-backed Actions invoke [[Model|models]] against a [[Scenario Overlay]]; in [[Vertex]] a scenario 'evaluates actions along with one or more modeled inputs and computes the output to reflect the real-world interactions of your digital twin.' Time-series inputs can be overridden with simulated values. The motion that makes the [[Digital Twin]] *projectable*.",
   inv=["Semantic Model Over Data"],
   rel=["Scenario","Scenario Overlay","Model","Optimization","Vertex","Time-Series Property","Digital Twin"],
   clone="Defer — emerges for free once scenarios and model functions exist.",
   src="Dynamic reconstruction §5.1, §5.3"),
 dict(t="Optimization", L="dynamic", k="concept",
   d="A model type that solves for a best decision (routing, allocation, scheduling) rather than predicting a value.",
   b="Treated as a [[Model]] wrapping a solver (LP/MILP/VRP) — Foundry integrates **NVIDIA cuOpt** (GPU decision optimization; the Oct 2025 collaboration, Lowe's as launch customer) for dynamic supply-chain use. Optimizer results are staged as [[Scenario|scenario]] edits via a [[Function-Backed Action]] for comparison before transactional apply.",
   inv=["Governed Writeback"],
   rel=["Model","Simulation","Scenario","Function-Backed Action"],
   clone="Defer — a solver is just another model behind a [[Function]]; GPU acceleration is post-MVP.",
   src="Dynamic reconstruction §5.2"),
 dict(t="Model Mesh", L="dynamic", k="mechanism",
   d="Vertex's chained-model ('simulation mesh') infrastructure that forwards one model's outputs into another's inputs.",
   b="Enabled continuous evaluation by flowing real-time sensor and configuration data through a graph of models. **Sunsetting** in Foundry — the supported path is plain [[Functions on Models]] composed inside [[Function-Backed Action|function-backed Actions]].",
   inv=["Semantic Model Over Data"],
   rel=["Vertex","Simulation","Functions on Models","Model"],
   clone="Drop — sunset feature; chain models via functions instead.",
   src="Dynamic reconstruction §5.1"),
 dict(t="Time-Series Property", L="dynamic", k="type",
   d="An object property that stores a history of timestamped values rather than a single value.",
   b="Backed by **time-series syncs** (datasets or streams) keyed by a `seriesId` that Foundry resolves against the property's data sources; requires a proprietary time-series compute database. The raw material for forecasts, simulated overrides, and [[Quiver]] analysis.",
   inv=["Versioned Data Foundation"],
   rel=["Derived Series","Geotemporal Series","Quiver","Object Type"],
   clone="Defer — a timestamped-values table covers it; the dedicated time-series engine is a scale artifact.",
   src="Dynamic reconstruction §6.1"),
 dict(t="Derived Series", L="dynamic", k="mechanism",
   d="A time series computed on the fly from other series, stored as a template rather than materialized.",
   b="The time-series analogue of a [[Derived Property]] — transforms saved in [[Quiver]] (smoothing, formulas) become reusable series without writing data, resolved at read time via template RIDs.",
   inv=["Versioned Data Foundation"],
   rel=["Time-Series Property","Derived Property","Quiver"],
   clone="Defer — compute-on-read series; add alongside the time-series feature.",
   src="Dynamic reconstruction §6.1"),
 dict(t="Geotemporal Series", L="dynamic", k="type",
   d="Time series with a geospatial component — the path of an entity over time ('tracks').",
   b="A geotemporal series object type plus a series sync (GTSS) referenced by a GTSR property; individual points are **observations**, stored as live streaming (real-time, ~14-day retention) or a persistent dataset archive. Currently **beta**.",
   inv=["Versioned Data Foundation"],
   rel=["Time-Series Property","Event Object Type","Object Type"],
   clone="Defer — niche; add only if the use case is spatial.",
   src="Dynamic reconstruction §6.2"),
 dict(t="Event Object Type", L="dynamic", k="type",
   d="An object type carrying temporal information — minimally a start and end timestamp.",
   b="Makes change-over-time first-class: [[Quiver]] computes event statistics, comparison plots, and filtering over them. The discrete-interval complement to continuous [[Time-Series Property|time series]].",
   inv=["Semantic Model Over Data","Versioned Data Foundation"],
   rel=["Object Type","Time-Series Property","Quiver"],
   clone="Defer — an object type with two timestamps; nothing special to build early.",
   src="Dynamic reconstruction §6.3"),
 dict(t="As-Of Read", L="dynamic", k="concept",
   d="Querying Ontology state as it was at a past time — a capability Foundry does NOT expose as a first-class API.",
   b="There is an experimental `transaction` parameter and a `branch` parameter, but **no general bitemporal 'as of time T' read**. The temporal record is reconstructable from the immutable [[Edit History]] / [[Action Log]] changelogs and time-series history, not a first-class query. A genuine gap — flagged so a clone is not tempted to assume it.",
   inv=["Versioned Data Foundation","End-to-End Lineage"],
   rel=["Edit History","Action Log","Transaction Model","Time-Series Property"],
   clone="Defer — reconstruct from the changelog we already keep; Foundry has no first-class as-of read either.",
   src="Dynamic reconstruction §6.4"),
 dict(t="State-Dependent Security", L="dynamic", k="property",
   d="Access that changes as object state changes — editing a policy-referenced property can grant or revoke visibility.",
   b="The *dynamic* face of [[Security Travels With Data]]: because [[Object Security Policy|policies]] and [[Mandatory Control Property|control properties]] are evaluated per query, an [[Action Type|Action]] (or a [[Scenario]]-staged edit) that mutates a referenced property immediately changes who can see the object. Policy changes propagate near-instantly; group/attribute changes are cached briefly.",
   inv=["Security Travels With Data","Governed Writeback"],
   rel=["Object Security Policy","Mandatory Control Property","Property Security Policy","Scenario"],
   clone="Simplify — falls out of per-query, data-driven security we already keep; no extra machinery needed.",
   src="Dynamic reconstruction §7.2"),
 dict(t="Vertex", L="dynamic", k="service",
   d="The graph + scenario surface: visualize and quantify cause and effect across the digital twin.",
   b="Object-backed system diagrams with [[Scenario]] creation (Actions + modeled inputs + overrides), [[Scenario Comparison|baseline comparison]], and (sunsetting) [[Model Mesh|model chaining]]; embeddable in [[Workshop]] with 'load data from scenario.' The interactive what-if surface of the [[Digital Twin]].",
   inv=["Semantic Model Over Data"],
   rel=["Scenario","Simulation","Model Mesh","Quiver","Digital Twin","Workshop"],
   clone="Defer — build a minimal what-if graph UI later; Vertex itself is a Palantir application.",
   src="Dynamic reconstruction §8.2"),
 dict(t="Quiver", L="dynamic", k="service",
   d="The time-series + scenario analysis surface: point-and-click analysis over object and time-series data.",
   b="An analysis is a graph of interdependent **cards**, offering interactive forecasts (constant/linear/formula, fit with RMSE/MAE), [[Derived Series|derived-series]] transforms, [[Event Object Type|event]] analytics, streaming rolling windows, and writeback to the Ontology via [[Action Type|Actions]]. The temporal counterpart to [[Vertex]].",
   inv=["Versioned Data Foundation"],
   rel=["Time-Series Property","Derived Series","Event Object Type","Vertex"],
   clone="Defer — a charting/forecast UI over time series; post-MVP, and a Palantir application itself.",
   src="Dynamic reconstruction §8.3"),
]

# === MORE_CONCEPTS_HERE ===

# ---------------------------------------------------------------------------
# Decisions (from the Design Constraints spec)
# ---------------------------------------------------------------------------
DECISIONS = [
 ("D1","Storage substrate (Postgres / file store / DuckDB…)","A single relational DB"),
 ("D2","How literal the transaction/version model is","Versioned rows + change log"),
 ("D3","Separate compute step vs. in-database transforms","In-DB / SQL where possible"),
 ("D4","Lineage granularity (dataset vs. column)","Dataset-level to start"),
 ("D5","Object storage shape (table-per-type vs. generic store)","Key decision — undecided"),
 ("D6","Link implementation (FK + join tables vs. unified edge table)","Follow Foundry (FK / join)"),
 ("D7","Property/value-type richness at v1","Small core + constrained values"),
 ("D8","Search (DB queries vs. search index)","DB queries + full-text"),
 ("D9","Object liveness (sync reads vs. async indexing)","Synchronous"),
 ("D10","Action definition format (declarative vs. code)","Likely both, code-first"),
 ("D11","Function language/runtime","One; same as backend"),
 ("D12","Validation-rule expression (DSL vs. functions)","Functions to start"),
 ("D13","Audit log shape & queryability","Append-only events table"),
 ("D14","Atomicity scope","One DB transaction per action"),
 ("D15","Access-control richness at v1","Roles + optional row rules"),
]

# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
def links(items):
    return " · ".join(f"[[{x}]]" for x in items)

def yl(items):
    return "".join(f"  - {x}\n" for x in items)

# Default clone-disposition per layer; overridden by a concept's own "clone" note.
LAYER_DEFAULT_CLONE = {"crosscutting":"core","data":"simplify","semantic":"keep",
                       "kinetic":"keep","dynamic":"defer","app":"simplify","aip":"defer",
                       "security":"simplify","platform":"drop"}

def disposition(c):
    t = c.get("clone","").strip().lower()
    if t:
        first = t.split()[0].strip(":—-,.()")
        m = {"replicate":"keep","keep":"keep","critical":"keep","becomes":"keep",
             "drop":"drop","skip":"drop","defer":"defer","simplify":"simplify"}
        if first in m:
            return m[first]
        if "replicate" in t or "keep" in t: return "keep"
        if "defer" in t: return "defer"
        if "simplif" in t: return "simplify"
        if "drop" in t or "skip" in t: return "drop"
    return LAYER_DEFAULT_CLONE.get(c["L"], "keep")

def alias_of(title):
    m = re.search(r"\(([^)]+)\)", title)
    if m:
        inner = m.group(1).strip()
        if " " not in inner and len(inner) <= 6 and (inner.isupper() or any(ch.isdigit() for ch in inner)):
            return [inner]
    return []

def render_concept(c):
    disp = disposition(c)
    al = alias_of(c["t"])
    tags = [f"layer/{LAYER_TAG[c['L']]}", f"kind/{c['k']}", f"clone/{disp}"]
    fm = "---\n"
    fm += ("aliases:\n" + yl(al)) if al else "aliases: []\n"
    fm += "tags:\n" + yl(tags)
    fm += f"layer: {LAYER_TAG[c['L']]}\nkind: {c['k']}\nclone: {disp}\n"
    if c.get("inv"):
        fm += "invariants:\n" + yl(f'"[[{x}]]"' for x in c["inv"])
    fm += f'source: "{c["src"]}"\nupdated: 2026-06-13\n---\n\n'
    out = fm + f"# {c['t']}\n\n> {c['d']}\n\n{c['b']}\n\n"
    if c.get("inv"):
        out += f"**Invariants:** {links(c['inv'])}\n\n"
    if c.get("rel"):
        out += f"**Related:** {links(c['rel'])}\n\n"
    if c.get("clone"):
        out += f"**For our clone:** {c['clone']}\n\n"
    out += f"*Source: {c['src']}*\n"
    return out

def write_note(title, body, folder=""):
    safe = title.replace("/", "-").replace(":", " -")
    fn = safe + ".md"
    dest_dir = os.path.join(VAULT, folder) if folder else VAULT
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, fn)
    # This mount allows rename but not unlink. Relocate any existing copy of this note
    # (e.g. a stale flat file at the root) into its destination folder via move, then
    # overwrite with fresh content. Net effect: exactly one copy, in the right place.
    for root, dirs, files in os.walk(VAULT):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if fn in files:
            cur = os.path.join(root, fn)
            if os.path.abspath(cur) != os.path.abspath(dest):
                os.replace(cur, dest)
    with open(dest, "w") as f:
        f.write(body)
    return safe

written = {}

def build():
    # concept notes -> their layer's domain folder
    # (write_note relocates any stale flat copy into place via move — see its note)
    for c in CONCEPTS:
        write_note(c["t"], render_concept(c), LAYER_FOLDER[c["L"]])
        written[c["t"]] = c

    # invariant hubs
    for inv, blurb in INVARIANTS.items():
        members = [c for c in CONCEPTS if inv in c.get("inv", [])]
        body = f"---\ntags:\n  - hub\n  - invariant\n---\n\n# {inv}\n\n> {blurb}\n\n*An invariant — a promise our clone must keep. The atomic concepts below embody it.*\n\n"
        by_layer = {}
        for c in members:
            by_layer.setdefault(c["L"], []).append(c["t"])
        order = ["crosscutting","data","semantic","kinetic","dynamic","app","aip","security","platform"]
        label = {"crosscutting":"Cross-cutting","data":"Data layer","semantic":"Semantic layer","kinetic":"Kinetic layer","dynamic":"Dynamic layer","app":"App layer","aip":"AIP layer","security":"Security layer","platform":"Platform layer"}
        for L in order:
            if by_layer.get(L):
                body += f"## {label[L]}\n\n" + "".join(f"- [[{t}]]\n" for t in sorted(by_layer[L])) + "\n"
        body += "---\n\n**Other invariants:** " + links([i for i in INVARIANTS if i != inv]) + "\n\n[[Foundry — Home (MOC)|← Home]]\n"
        write_note(inv, body, INVARIANTS_FOLDER)

    # layer hubs
    for key,(title,blurb) in LAYER_HUBS.items():
        members = [c["t"] for c in CONCEPTS if c["L"] == key]
        body = f"---\ntags:\n  - hub\n  - layer/{key}\n---\n\n# {title}\n\n> {blurb}\n\n"
        body += "## Concepts in this layer\n\n" + "".join(f"- [[{t}]]\n" for t in sorted(members)) + "\n"
        body += "---\n\n**Invariants this layer serves:** " + links(list(INVARIANTS)) + "\n\n[[Foundry — Home (MOC)|← Home]]\n"
        write_note(title, body, LAYER_FOLDER[key])

    # pending-layer placeholders
    for key,(title,blurb,prompt) in PENDING_LAYERS.items():
        body = (f"---\ntags:\n  - hub\n  - layer/{key}\n  - status/research-pending\n---\n\n# {title}\n\n> {blurb}\n\n"
                f"> [!todo] Research pending\n> This layer has not been reverse-engineered yet. Run `{prompt}` and atomize the results into notes here.\n\n"
                f"**Invariants it will touch:** {links(list(INVARIANTS))}\n\n[[Foundry — Home (MOC)|← Home]]\n")
        write_note(title, body, LAYER_FOLDER[key])

    # design decisions
    body = "---\ntags:\n  - hub\n  - decisions\n---\n\n# Design Decisions\n\n> Open forks to resolve when we design the clone's architecture (Phase 3). Non-binding leanings shown.\n\n| # | Decision | Leaning |\n|---|---|---|\n"
    for d,q,lean in DECISIONS:
        body += f"| {d} | {q} | {lean} |\n"
    body += "\n[[Minimum Viable Foundry]] · [[Foundry — Home (MOC)|← Home]]\n"
    write_note("Design Decisions", body, MAPS_FOLDER)

    # home MOC
    home = "---\ntags:\n  - hub\n  - home\n---\n\n# Foundry — Home (MOC)\n\n> Map of Content for the Palantir Foundry knowledge graph. Built from the deep-research reconstructions; open the **graph view** to see the structure.\n\n"
    home += "## The five invariants (the larger ideas)\n\n" + "".join(f"- [[{i}]]\n" for i in INVARIANTS) + "\n"
    home += "## Layers\n\n" + "".join(f"- [[{t}]]\n" for _,(t,_) in LAYER_HUBS.items()) + "\n"
    if PENDING_LAYERS:
        home += "*Research pending:*\n\n" + "".join(f"- [[{t}]]\n" for _,(t,_,_) in PENDING_LAYERS.items()) + "\n"
    else:
        home += "> [!success] All eight layers reconstructed — this vault is now the complete spec.\n\n"
    home += "## Orienting ideas\n\n- [[The Closed Loop]]\n- [[Digital Twin]]\n- [[Operational Application]]\n- [[Define-Once Reuse]]\n- [[Git for Data]]\n- [[Minimum Viable Foundry]]\n"
    home += "## Working views\n\n- [[Build View — What We're Cloning]] — every concept by keep/drop disposition\n- [[Design Decisions]] — the 15 open architecture forks\n- [[Taxonomy (Legend)]] — the metadata schema & how to query this vault\n"
    write_note("Foundry — Home (MOC)", home, MAPS_FOLDER)

    # replace default Welcome with a redirect (kept at vault root as the entry point)
    write_note("Welcome", "This vault's entry point is [[Foundry — Home (MOC)]].\n")

    # ---- Build View: every concept grouped by clone-disposition ----
    disp_order = ["core","keep","simplify","defer","drop"]
    disp_label = {"core":"Core — the irreducible essence","keep":"Keep — replicate faithfully (the build list)",
                  "simplify":"Simplify — keep the idea, shrink the implementation","defer":"Defer — add later without rework",
                  "drop":"Drop — Palantir-scale machinery we don't need"}
    layer_order = ["crosscutting","data","semantic","kinetic","dynamic","app","aip","security","platform"]
    layer_label = {"crosscutting":"Cross-cutting","data":"Data","semantic":"Semantic","kinetic":"Kinetic","dynamic":"Dynamic",
                   "app":"App","aip":"AIP","security":"Security","platform":"Platform"}
    by_disp = {}
    for c in CONCEPTS:
        by_disp.setdefault(disposition(c), {}).setdefault(c["L"], []).append(c["t"])
    bv = ("---\ntags:\n  - hub\n  - index\nupdated: 2026-06-13\n---\n\n# Build View — What We're Cloning\n\n"
          "> The actionable spec view: every concept sorted by its **`clone`** property. Advisory — a layer default unless a concept-specific call was made. Filter it live via [[Taxonomy (Legend)]].\n\n")
    for d in disp_order:
        members = by_disp.get(d, {})
        count = sum(len(v) for v in members.values())
        bv += f"## {disp_label[d]}  ({count})\n\n"
        for L in layer_order:
            if members.get(L):
                bv += f"**{layer_label[L]}:** " + " · ".join(f"[[{t}]]" for t in sorted(members[L])) + "\n\n"
    bv += "---\n\n[[Foundry — Home (MOC)|← Home]]\n"
    write_note("Build View — What We're Cloning", bv, MAPS_FOLDER)

    # ---- Taxonomy (Legend): document the schema + how to query ----
    layer_links = "".join(f"- [[{t}]]\n" for _,(t,_) in LAYER_HUBS.items())
    inv_links = "".join(f"- [[{i}]]\n" for i in INVARIANTS)
    tax = f"""---
tags:
  - hub
  - meta
updated: 2026-06-13
---

# Taxonomy (Legend)

> How this vault is categorized and queried. Every concept note carries typed **properties** (for Obsidian **Bases** / Dataview) and mirrored **tags** (for the tag pane and graph). The vault is deliberately **flat** — navigation is by MOC, organization is by property/tag.

## Properties on every concept

| Property | Meaning | Values |
|---|---|---|
| `layer` | Which Foundry layer it belongs to | data · semantic · kinetic · dynamic · app · aip · security · platform · crosscutting |
| `kind` | What kind of idea it is | concept · mechanism · service · type · pattern · property · reference |
| `clone` | Disposition for *our* build | core · keep · simplify · defer · drop |
| `invariants` | The promise(s) it embodies (links) | one or more of the 5 invariants |
| `source` | Which reconstruction it came from | text |
| `aliases` | Acronyms (OSv2, FOO, CBAC, …) | list |

## Clone dispositions

- **core** — the irreducible essence; principles we embody.
- **keep** — replicate faithfully (the build list).
- **simplify** — keep the idea, shrink the implementation.
- **defer** — add later without rework.
- **drop** — Palantir-scale machinery we don't need.

Sorted index: [[Build View — What We're Cloning]].

## Layers (MOCs)

{layer_links}
## The five invariants (MOCs)

{inv_links}
## How to query — no plugin needed

**Obsidian Bases (core):** new Base → add filters like `clone is keep` or `layer is semantic` → group by `layer`. Renders as a live table/cards.

**Property search:** in Search, type `["clone":"keep"]` or `["layer":"kinetic"]`.

**Tag pane / graph:** filter by `#clone/keep`, `#layer/semantic`, `#kind/service`.

**Dataview (optional plugin):**

```dataview
TABLE layer, clone, source
WHERE kind != null AND clone = "keep"
SORT layer ASC
```

## Why flat + MOCs + properties (not folders)

Best practice for a large reference vault: folders force a single home per note. This vault instead stays **flat** and uses **MOCs** (the [[Foundry — Home (MOC)|Home]], the 5 invariant hubs, the 8 layer hubs) for navigation, with **properties/tags** for cross-cutting filtering — so any note can appear in many views at once.

---

[[Foundry — Home (MOC)|← Home]]
"""
    write_note("Taxonomy (Legend)", tax, MAPS_FOLDER)

    # ---- validation: every wikilink target must exist ----
    titles = set(written) | set(INVARIANTS) | {t for _,(t,_) in LAYER_HUBS.items()} | {t for _,(t,_,_) in PENDING_LAYERS.items()} | {"Foundry — Home (MOC)","Design Decisions","Welcome","Build View — What We're Cloning","Taxonomy (Legend)"}
    dangling = {}
    for f in glob.glob(os.path.join(VAULT, "**", "*.md"), recursive=True):
        text = open(f).read()
        for m in re.findall(r"\[\[([^\]]+)\]\]", text):
            target = m.split("|")[0].strip()
            if target not in titles:
                dangling.setdefault(target, []).append(os.path.basename(f))
    return titles, dangling

if __name__ == "__main__":
    titles, dangling = build()
    print(f"Concepts: {len(CONCEPTS)}")
    total = sum(1 for r,_,fs in os.walk(VAULT) for f in fs if f.endswith('.md'))
    print(f"Total notes written: {total}")
    if dangling:
        print(f"\nDANGLING LINKS ({len(dangling)}):")
        for t, srcs in sorted(dangling.items()):
            print(f"  [[{t}]]  <- {len(srcs)} note(s): {srcs[0]} ...")
    else:
        print("\nLink integrity: OK (all wikilinks resolve)")
