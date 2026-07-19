# Foundry Clone — Design Constraints (Distillation)

> **Project:** "Foundry for Unity Fiber" — a Foundry-like operational platform for carrier-relations management.
> **This document:** the bridge from research to build. It distills the three deep reconstructions (data foundation, Ontology semantic layer, Ontology kinetic layer) into a **technology-neutral** set of design constraints — *what we must replicate*, *what we can drop*, and *what's still open to decide*.
> **Status:** Draft 1 · 2026-06-13 · The spec we work backwards from. Phase 2 (mapping the carrier-relations role onto this) comes next.
> **Source artifacts:** `Palantir-Foundry-Conceptual-Map.md`, `RESEARCH_Ontology-Semantic-Layer_*.md`, `RESEARCH_Ontology-Kinetic-Layer_*.md`, `RESEARCH_Data-Integration-Pipeline-Layer_*.md`.

---

## 0. How to read this document

Each layer below is split into three buckets, and that split *is* the point:

- **MUST replicate** — the invariant behaviors and contracts that make a system recognizably "Foundry-like." These are technology-neutral: they say *what* must be true, never *how*. If we drop one of these, we've built something else.
- **CAN drop / simplify** — Palantir-specific implementation artifacts: their microservice names, their storage engines, their exact numeric limits, and the heavy enterprise plumbing that exists only because Palantir serves the Fortune 500. None of these are requirements for us.
- **OPEN decisions** — the genuine forks where we get to choose, captured here and consolidated into a register in §8 so they become explicit spec decisions later.

A rule of thumb separates the first two buckets: **a MUST is a promise to the user; a CAN-drop is a tactic Palantir used to keep that promise at their scale.** We keep the promises and choose our own tactics.

---

## 1. The irreducible essence

Strip Foundry to what cannot be removed without it ceasing to be Foundry, and you get **five invariants plus one motion**.

**The five invariants:**

1. **A semantic model over the data.** Users work with real-world *things* (a carrier, a circuit, a contract) and their *relationships*, not tables and columns. Meaning is defined once, centrally, and reused everywhere.
2. **Versioned data underneath.** The data foundation is immutable and historied — you can always ask "what did this look like then?" and trace any value to its origin.
3. **Governed writeback as the only way to change things.** All changes flow through defined, validated, audited *actions* — never ad-hoc edits. Logic is written once and enforced no matter who or what triggers it.
4. **Security that travels with the data.** Access control is a property of the objects and rows themselves, on by default, not bolted onto each app.
5. **End-to-end lineage.** Source → dataset → object → action → audit log is one continuous, inspectable chain.

**The one motion (the closed loop):** raw data flows *up* into meaning; decisions flow *back down* into systems of record. The platform is part of operations, not a window onto them. Everything else — the apps, the AI, the connectors — exists to make some part of this loop faster, safer, or smarter.

> Everything in §§2–4 is in service of these six things. When a "CAN drop" feels scary to drop, check it against this list: if it isn't one of these six, it's a tactic, not a promise.

---

## 2. Data foundation — design constraints

*What Foundry calls: Data Connection / Magritte, datasets, transactions, transforms, the Build system, Pipeline Builder.*

### 2.1 MUST replicate (the promises)

- **Versioned datasets.** Data is stored as immutable, historied units. We can reconstruct any past state and never silently overwrite history. *(This is the keystone — see the note below.)*
- **A transaction/commit model.** Changes to a dataset are atomic commits with types analogous to **replace (snapshot)** and **add (append)**; the "current state" is computed by replaying commits. Versioning, incremental processing, and point-in-time reads all derive from this one mechanism.
- **Derived incrementality.** The system should be able to process *only what changed* — and decide that automatically by inspecting what kind of change occurred, rather than making the author wire it up by hand.
- **A clean data → object handoff.** A curated dataset can *back* an object type: rows become object instances, columns become properties. This seam is where the data layer meets the semantic layer and must be first-class.
- **Lineage capture.** Every dataset records what produced it (which inputs, which logic), forming an inspectable dependency graph.

### 2.2 CAN drop / simplify (Palantir's tactics)

- **The entire Magritte/agent connectivity tier.** 200+ connectors, agent-proxy "thin mode," Foundry workers, egress policies, websocket tunnels back to `magritte-coordinator` — all of this exists to cross corporate firewalls into hundreds of source systems. For one carrier-relations use case we need a handful of simple ingests (a few spreadsheets, maybe one or two APIs). Drop the tier; keep a thin ingestion path.
- **Distributed/multi-engine compute.** Spark, Flink, DataFusion/Velox, Spark profiles, container transforms — Palantir needs many engines because customers process petabytes. Her data is small (think thousands to low-millions of rows). A single-node engine (or just the database itself) is plenty. Pick **one**.
- **Physical storage internals.** Parquet files on S3 under a `spark/` prefix, the Hadoop FileSystem mapping, dataset projections for small-file compaction — all artifacts of big-data file storage. Our store can be far simpler.
- **Compute-seconds metering** (`max(vCPU, GiB/7.5)·s`) and all the documented limits (2 MB/s indexing, etc.). Billing/scale artifacts; irrelevant.
- **The no-merge branching quirk and the JobSpec/Build2 orchestration model** — keep *versioning*, but we don't need their build-graph orchestration service for a handful of pipelines.

### 2.3 OPEN decisions

- **Storage substrate.** A relational DB (Postgres) with history tables? A file-based versioned store? Something like DuckDB/SQLite for simplicity? → *D1*
- **How literal is the transaction model?** Full snapshot/append/update/delete semantics, or a simpler "versioned rows + change log"? → *D2*
- **Do we need a separate compute step at all,** or can transformation happen in-database (SQL/views)? → *D3*
- **How much lineage** do we track — full column-level, or dataset-level "produced by"? → *D4*

> **Keystone note:** of everything in this layer, the **transaction-based versioned store** is the single most valuable idea to carry over, because the kinetic layer's audit/writeback guarantees ride on top of it. A plain database transaction already gives us atomicity for free; the design work is deciding how much *history* we keep and how we expose point-in-time reads.

---

## 3. Semantic layer (the Ontology) — design constraints

*What Foundry calls: object types, objects, properties, link types, interfaces, value types, object sets, Object Storage V2, OSS, OMS.*

### 3.1 MUST replicate (the promises)

- **Object types and objects.** A schema for each real-world entity/event, and instances of it. Each object type has a **primary key**, a human-readable **title**, and a set of typed **properties**. Objects are searchable, filterable, and addressable.
- **A pragmatic property type system.** Typed properties with validation. We need a small core — text, number, date/time, boolean, and **enumerated/constrained values** (Foundry's "value types" idea — a reusable semantic type with constraints like an email regex or an allowed-status set). Richer types (geo, time-series, media, vector, struct) are optional add-ons.
- **Link types (typed relationships).** First-class, named relationships between object types, supporting the three cardinalities: **one-to-one, one-to-many, many-to-many**. Links are traversable ("show me this carrier's circuits").
- **Objects backed by data.** An object type is materialized from a backing dataset (the §2.1 handoff); the semantic layer is a *view of meaning* over the versioned store, not a separate source of truth.
- **Object sets / saved queries.** The ability to define, name, filter, and reuse a set of objects (e.g., "circuits with degraded SLA this quarter").
- **Read-your-writes.** After a change is committed, reads reflect it promptly. Users must trust that what they just did is what they now see.
- **Define-once reuse.** A concept defined in the model (an object, a property, a link) means the same thing in every screen, query, and rule. This is the whole reason the semantic layer exists.

### 3.2 CAN drop / simplify (Palantir's tactics)

- **The microservice decomposition** (OSv2, the Object Data Funnel, OSS, OMS, Phonograph). These are how Palantir indexes tens of billions of objects across "multiple storage backends in parallel." We'll likely store objects as **tables/rows in one database**; the "object backend" is just our DB.
- **A dedicated search/index tier** (their Lucene-family + Spark-over-columnar). For her scale, ordinary database queries and indexes (and built-in full-text search) cover search, filter, and aggregate.
- **The exhaustive property catalog and limits** (20+ base types, 2000 properties/type, 70 datasources/type, interfaces, struct/geotime/vector). Implement the small core in 3.1; add advanced types only when a real need appears.
- **Ontology branching / proposals** (PR-style review of model changes). Valuable at enterprise scale with many builders; for a small build we can start with simpler change management and add this later if needed.
- **Multi-datasource object types (MDOs), restricted-view-backed objects, materializations as a separate concept** — simplify to "an object type is backed by one query/table" initially.

### 3.3 OPEN decisions

- **Object storage shape.** One physical table per object type (relational, strongly-typed)? Or a generic object/property store (flexible, schema-light)? This is the biggest semantic-layer decision. → *D5*
- **Link implementation.** Foreign keys for 1:N, join tables for N:M (Foundry's approach), or a unified edge/relationship table? → *D6*
- **How rich is the property/value-type system at v1?** → *D7*
- **Search:** database queries only, or add a search index? → *D8*
- **How "live" must objects be** — synchronous DB reads (trivially current), or is any async indexing involved? (Probably synchronous for us.) → *D9*

---

## 4. Kinetic layer (Actions + Functions) — design constraints

*What Foundry calls: action types, parameters, rules, submission criteria, function-backed actions, the Ontology Edits API, Functions (TS/Python), the Actions service.*

### 4.1 MUST replicate (the promises)

- **Governed actions are the only sanctioned write path.** Objects change *only* through defined action types. An action bundles: **parameters** (typed inputs), **rules/logic** (the edits to perform), and **submission criteria** (server-enforced validation of whether the change is allowed). This "edits-only-via-actions" pattern is the heart of what makes the platform *operational* rather than just a database with a UI.
- **An action is one atomic transaction.** All edits an action computes succeed together or not at all. *(A database transaction gives us this directly.)*
- **Server-side validation.** Submission criteria are enforced on the server, never trusting the client. Business rules ("only a manager can escalate," "renewal date must be in the future") live with the action.
- **Reusable functions / business logic.** Named, reusable logic that can read objects and compute results, and — via **function-backed actions** — perform complex, multi-object writeback. Logic is authored once and reused across every surface (a human clicking a button, an automation, later an AI agent).
- **Audit / edit history.** Every change records who, what, when, and before→after values, in an immutable log. This is non-negotiable for an operational system and rides directly on the versioned store from §2.
- **Define-once enforcement.** The same action logic and validation apply identically regardless of which screen or caller invokes it.

### 4.2 CAN drop / simplify (Palantir's tactics)

- **The write-path machinery** (Actions service → Funnel queue → index-first/persist-later → 6-hour flush → offset tracking). This complexity exists to keep a distributed index consistent at scale. With a single database, **a committed transaction is the write** — we get atomicity, durability, and read-your-writes for free, no queue.
- **Three function runtimes** (TypeScript v1, TypeScript v2, Python) with serverless/deployed modes, compute-second metering, and the exact `Edits` API surface (`createEditBatch`/`getEdits`, etc.). We pick **one** language/runtime and design our own edit API.
- **The bulk/scale limits** (10,000 objects/action, 50 object types/action, on-demand Spark for big writes). Irrelevant at her scale.
- **Webhooks / external functions / egress complexity** — keep the *concept* of a side-effect (notify someone, call an external system) but implement it simply; defer the OAuth-outbound-application plumbing.
- **Automate** (scheduled/triggered automations) and **AIP tool-exposure** — both are real value, but post-MVP. The action/function model is designed so these slot in *later* without rework.
- **Cross-system non-transactionality** is a *limitation* to design around, not replicate: if we call an external system, we accept it may succeed while our write fails, and we handle it explicitly.

### 4.3 OPEN decisions

- **Action definition format.** Declarative config (JSON/YAML describing parameters + rules + criteria) or code? Foundry offers both (point-and-click rules *and* function-backed). → *D10*
- **Function language/runtime** (and is it even separate from the app's backend language at our scale?). → *D11*
- **How validation rules are expressed** (a small rule DSL, or just functions returning valid/invalid). → *D12*
- **Audit log shape** — an append-only events table capturing the diff per edit; how queryable does it need to be? → *D13*
- **Atomicity scope** — single DB transaction per action (almost certainly yes). → *D14*

---

## 5. Security & lineage (cross-cutting) — design constraints

*Not yet deep-researched as its own layer, but it threads through all three above, so the essentials belong here.*

- **MUST:** access control that travels with the data (row- and object-level visibility, not just app-level); an immutable audit trail (who/what/when/before→after); end-to-end lineage from source to audit. At minimum: **roles** (who can see/do what) and **per-object/row visibility rules**.
- **CAN drop:** Palantir's full apparatus — markings, classification-/purpose-based access controls, granular-policy weight math, restricted-view internals, Projects-as-security-boundary. These are government/enterprise-grade. We likely need simple **role-based access** plus optional **row-level rules** at v1.
- **OPEN:** how rich access control is at v1 (roles only, or roles + row rules?); whether we adopt Foundry's "security is a property on the object" model from the start. → *D15*

> If we later want this layer at the same depth as the other three, the security-layer deep-research prompt is the natural follow-on (it was option 4 at the last fork).

---

## 6. The closed loop, in our terms

The same motion Foundry runs, stripped to our parts:

```
   Sources (spreadsheets, a CRM, carrier portals/APIs)
        │   simple ingestion (no Magritte tier)
        ▼
   Versioned data store  ──────────────►  Lineage + audit
        │   backed-by handoff                    ▲
        ▼                                         │
   Semantic model: object types · links           │ every change
        │                                         │ recorded here
        ▼                                         │
   Governed actions + functions  ────────────────►┘
   (params → validate → atomic writeback)
        │
        ▼
   Systems of record / side effects (notify, external API)
```

Read upward, data becomes meaning. Read downward, decisions become recorded, governed change. That loop — not any particular technology — is what we are building.

---

## 7. Minimum Viable Foundry

The smallest thing that is still recognizably Foundry-like — our v1 target:

**In:**

- A **versioned data store** with a simple commit/history model and point-in-time read.
- A **thin ingestion path** for a few concrete sources (start: spreadsheet upload + one API).
- A **semantic model**: object types with typed properties (incl. constrained/enumerated values), and link types across all three cardinalities, backed by stored data.
- **Object sets**: filter/search/save views over objects.
- **Governed actions**: typed parameters → server-side validation (submission criteria) → atomic writeback, as the *only* write path.
- **Reusable functions** for logic and complex (function-backed) writeback.
- An **immutable audit log** of every change (who/what/when/before→after).
- **Role-based access** (+ optional row-level rules).
- A **thin UI** to browse objects, run searches, and invoke actions.

**Explicitly out (deferred, by design — the model leaves room for them):**

- Distributed/multi-engine compute (Spark/Flink/DataFusion).
- The connector tier (Magritte/agents) beyond a couple of simple ingests.
- A separate search/index service; microservice decomposition.
- Ontology branching/proposals; interfaces; the exhaustive property-type catalog.
- Webhooks/external-function plumbing; Automate; AIP/agents; Apollo-style deployment.
- Markings / classification- & purpose-based access controls.

> The discipline: **everything "out" must be *addable later without rework*.** That's the real test of whether our v1 architecture is sound — and it's why we reverse-engineered the full model before designing.

---

## 8. Consolidated mapping table

The single reference: each Foundry concept → the promise it encodes → our call.

| Foundry concept | The promise (MUST) | Our call |
|---|---|---|
| Dataset + transactions (snapshot/append/…) | Versioned, historied, point-in-time data | **Keep** (simplified commit/history model) |
| Magritte / agents / connectors | Get data in from anywhere | **Drop** → thin ingestion for a few sources |
| Spark / Flink / DataFusion / profiles | Process data at scale | **Drop** → single-node / in-DB |
| Build system / JobSpecs / schedules | Orchestrate pipelines | **Simplify** → minimal scheduled refresh |
| Incremental engine (`@incremental`) | Process only what changed | **Simplify** → keep concept, trivial at our scale |
| Object type / object | Real-world entities as first-class things | **Keep** (core) |
| Property + value types | Typed, validated, reusable attributes | **Keep** small core; defer advanced types |
| Link type (1:1/1:N/N:M) | Traversable typed relationships | **Keep** (core) |
| Object backed by dataset | Meaning is a view over versioned data | **Keep** (the handoff) |
| Object set | Saved, reusable queries over objects | **Keep** (core) |
| OSv2 / Funnel / OSS / OMS / indexing | Store & serve objects at huge scale | **Drop** → objects live in our DB |
| Interfaces / MDOs / branching | Enterprise-scale modeling features | **Defer** |
| Action type (params/rules/criteria) | Governed, validated, single write path | **Keep** (the heart) |
| Action = atomic transaction | All-or-nothing edits | **Keep** (DB transaction) |
| Submission criteria | Server-enforced business rules | **Keep** (core) |
| Function / function-backed action | Reusable logic; complex writeback | **Keep**; pick one runtime |
| Edits API / Actions service / Funnel write path | Safe writeback at scale | **Drop internals** → keep behavior via DB commit |
| Edit history / action log | Immutable audit trail | **Keep** (non-negotiable) |
| Webhooks / external functions | Side effects / external writeback | **Simplify**; defer plumbing |
| Automate / AIP tools | Run logic without a human / via AI | **Defer** (slot in later) |
| Markings / RV / CBAC / Projects | Security travels with data | **Simplify** → roles + optional row rules |
| Lineage / dependency graph | Source-to-audit traceability | **Keep** (simplified) |
| Compute-seconds / limits | Metering & scale ceilings | **Drop** |
| Apollo | Zero-downtime deployment | **Drop** (ordinary deployment) |

---

## 9. Open design decisions register

Consolidated forks to resolve when we design the architecture (Phase 3). None are answered here — by design, this doc defines *constraints*, not *choices*.

| # | Decision | Leaning (non-binding) |
|---|---|---|
| D1 | Storage substrate (Postgres / file store / DuckDB…) | A single relational DB |
| D2 | How literal the transaction/version model is | Versioned rows + change log |
| D3 | Separate compute step vs. in-database transforms | In-DB / SQL where possible |
| D4 | Lineage granularity (dataset vs. column) | Dataset-level to start |
| D5 | Object storage shape (table-per-type vs. generic store) | *Key decision — undecided* |
| D6 | Link implementation (FK + join tables vs. unified edge table) | Follow Foundry (FK / join) |
| D7 | Property/value-type richness at v1 | Small core + constrained values |
| D8 | Search (DB queries vs. search index) | DB queries + full-text |
| D9 | Object liveness (sync reads vs. async indexing) | Synchronous |
| D10 | Action definition format (declarative vs. code) | Likely both, code-first |
| D11 | Function language/runtime | One; same as backend |
| D12 | Validation-rule expression (DSL vs. functions) | Functions to start |
| D13 | Audit log shape & queryability | Append-only events table |
| D14 | Atomicity scope | One DB transaction per action |
| D15 | Access-control richness at v1 | Roles + optional row rules |

---

## 10. Next: Phase 2 (mapping the carrier-relations role)

This document is now the clean, technology-neutral **target**. Phase 2 maps the real job onto it — and the model tells us exactly what to ask:

- **Her object types** — what are the entities? (Carriers, circuits, contracts, NNIs, orders, tickets, SLAs, escalations…?)
- **Her link types** — how do those relate in the way she actually works?
- **Her actions** — what decisions does she make repeatedly, that we'd model as governed, validated writeback?
- **Her sources** — where does the data live today (spreadsheets, a CRM, carrier portals, email)?
- **Her read-only vs. operational split** — where does capturing the *decision* (the closed loop) matter most?
- **Her access rules** — who else touches this, and what should they see/do?

Answering those produces *her* object/link/action list — which we lay directly onto the MUST-replicate core in §§2–4. That intersection is the actual product spec.

> **Recommended next step:** a structured carrier-relations discovery built around those six questions.

