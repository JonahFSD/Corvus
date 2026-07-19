# Foundry Clone — Build Blueprint (Phase 1.5)

> **Project:** "Foundry for Unity Fiber" — a Foundry-like operational platform for carrier-relations management.
> **This document:** the bridge from *constraints* to *architecture*. The Design Constraints spec said **what** must be true, technology-neutral. This says **how** — a concrete, buildable engine, decided now. It resolves the 15 open decisions (D1–D15), fixes the data model and the action engine, and defines the configuration format a domain expert fills in later.
> **Status:** Draft 1 · 2026-06-14 · The engine spec. Phase 2 (mapping Bailey's carrier-relations domain onto it) comes after — and needs none of it to start changing.
> **Source artifacts:** `Spec/SPEC_Foundry-Clone_Design-Constraints.md`, `Palantir-Foundry-Conceptual-Map.md`, the `Vault/` Build View (core + keep), Design Decisions (D1–D15).

---

## 0. How to read this document

The chain is: **Conceptual Map** (what Foundry is) → **Design Constraints** (what we must replicate vs. drop) → **this Blueprint** (the engine we build) → **Phase 2** (Bailey's objects, links, and actions loaded onto the engine).

The central claim of this document is that **almost nothing here depends on Bailey.** Storage substrate, transaction model, object-storage shape, the action contract, the audit schema, the authorization rule — these are *engine* decisions, not *domain* decisions. A carrier, a circuit, a contract, an escalation are content the engine carries; they are not the engine. So we can finish the engine now and standardize it, and her discovery later only populates configuration. That is the whole reason Phase 1.5 exists as a thing we can do today.

---

## 1. Architectural thesis: a metadata-driven core

Foundry's defining internal trick is the **dynamic ontology**: object types, link types, and actions are *data the platform reads*, not classes an engineer compiles. (Palantir holds a patent on exactly this — "creating data in a data store using a dynamic ontology.") We adopt the same trick, because it is precisely what lets us "standardize now, adapt to her later."

> **The engine is fixed. The ontology is configuration.** We build one platform — a versioned store, an object/link model, an action executor, an authorization decision, an audit log — and it knows nothing about carriers. Object types, properties, links, actions, value types, roles, and policies are authored as declarative **config** (§6) that the engine loads at runtime. Bailey's domain becomes a config file, not a code branch.

Three consequences follow, and they shape every choice below:

1. **No DDL per object type.** If defining a new object type required a database migration, every domain change would be an engineering change. So objects cannot live in hand-written per-type tables (this drives D5).
2. **The config format *is* the product surface for modeling.** It must express everything the five invariants need — typed properties, constrained value types, links across all cardinalities, actions with validation, row-level access — and nothing Palantir-scale.
3. **The boundary between "platform" and "deployment" must be explicit** (§7), because that boundary is the answer to "what do we standardize vs. adapt."

---

## 2. The stack (resolved)

```
┌──────────────────────────────────────────────────────────┐
│  Thin UI  — browse objects, run searches, invoke actions  │  (M5; minimal)
├──────────────────────────────────────────────────────────┤
│  Application service  — one backend, one language          │
│    • Config loader (ontology as data)                      │
│    • Object/Object-Set read API  (search, filter, traverse)│
│    • Action executor  (params → validate → atomic write)   │
│    • Authorization decision  (default-deny composition)    │
│    • Audit/edit log writer                                 │
├──────────────────────────────────────────────────────────┤
│  PostgreSQL  — the entire data foundation                  │
│    • config (schema-of-schemas)   • objects (+JSONB)        │
│    • links (edge table)           • edit_event (audit/history)│
│    • roles / policies             • generated typed views   │
└──────────────────────────────────────────────────────────┘
```

One database (Postgres), one application service, one language end-to-end. No Spark, no search cluster, no message queue, no microservice mesh — every one of those is a Palantir-scale tactic the Design Constraints already marked **drop**. At Bailey's scale (thousands to low-millions of rows) a single Postgres instance *is* the data foundation, the object store, the search index, and the audit log at once. Read-your-writes, atomicity, and durability come free from one ACID transaction.

---

## 3. The fifteen decisions, resolved

The Design Constraints register left D1–D15 as leanings. This blueprint commits them. Each is an engine choice; none waits on Phase 2.

| # | Decision | **Resolved** | Why |
|---|---|---|---|
| D1 | Storage substrate | **PostgreSQL, single instance** | One ACID store gives versioning, search, and audit without a cluster. |
| D2 | Transaction/version model | **Append-only `edit_event` log + load-versioned ingests** — not literal SNAPSHOT/APPEND/UPDATE/DELETE | Point-in-time reconstruction by replaying edits; far simpler than Foundry's four-type log, same promise. |
| D3 | Compute step | **In-database (SQL/views)** | Transforms are SQL; no separate engine to operate. |
| D4 | Lineage granularity | **Dataset-level "produced-by" + per-object edit lineage** | Column-level lineage deferred; the audit log already gives object provenance. |
| D5 | Object storage shape | **Hybrid: one `objects` table with typed system columns + a `JSONB` properties column, plus a generated typed *view* per object type** | Types stay *data* (no per-type DDL), keeping the metadata-driven thesis; typed views restore SQL ergonomics and constraints. |
| D6 | Link implementation | **One unified `links` edge table**; cardinality enforced by partial unique indexes | A single mechanism covers 1:1 / 1:N / N:M; FK denormalization is a later optimization, not a v1 need. |
| D7 | Property / value-type richness | **Core base types** (text, integer, decimal, boolean, date, timestamp, enum) **+ reusable value types** (a base type + constraints) | Advanced types (geo, time-series, vector, struct) are additive later; none blocks v1. |
| D8 | Search | **Postgres queries + full-text** (`tsvector` / `pg_trgm`) | Covers search/filter/aggregate at this scale; no Lucene tier. |
| D9 | Object liveness | **Synchronous reads** | The object store *is* the database; reads are always current. No async index to reconcile. |
| D10 | Action definition format | **Declarative config for parameters + rules + criteria; a function for complex/multi-object logic** | Mirrors Foundry's "point-and-click rules *and* function-backed actions." Config covers the common case; functions cover the rest. |
| D11 | Function runtime | **One runtime = the application-service language** (recommend **TypeScript/Node**; Python acceptable) | A single language across engine, action functions, config types, and a future React UI. The only call that is genuinely team-preference (see §10). |
| D12 | Validation expression | **Functions returning `valid \| {error}`**, plus optional small declarative predicates for trivial rules | Start with code; promote common predicates into config sugar if a pattern repeats. |
| D13 | Audit-log shape | **Append-only `edit_event` table**, one row per property change, fully queryable | This table is simultaneously the audit trail (D13) and the version history (D2). |
| D14 | Atomicity scope | **One DB transaction per action** | All of an action's edits + their `edit_event` rows commit together or not at all. |
| D15 | Access-control richness | **Role-based (RBAC) + optional row-level object policies**, evaluated by a default-deny composition | Markings/CBAC stay dropped, but the *composition order* is built in as the seam so they can be added later. |

---

## 4. The data model

Five groups of tables: **config** (the schema-of-schemas), **objects**, **links**, **edit_event** (history + audit), and **access**. DDL below is illustrative Postgres, trimmed for clarity.

### 4.1 Config — the ontology as data

The modeler writes config (§6); the loader validates it and upserts these tables. Nothing here is domain-specific — these tables would be identical for a hospital or a bank.

```sql
create table object_type (
  id            text primary key,            -- "carrier"
  title         text not null,               -- "Carrier"
  primary_key   text not null,               -- property id used as PK
  title_prop    text,                        -- property id shown as the object's label
  created_at    timestamptz default now()
);

create table property_def (
  object_type   text references object_type(id),
  id            text,                         -- "account_manager"
  base_type     text not null,               -- text|integer|decimal|boolean|date|timestamp|enum
  value_type    text references value_type(id),  -- optional reusable constrained type
  required      boolean default false,
  primary key (object_type, id)
);

create table value_type (                     -- reusable semantic type: a base type + constraints
  id          text primary key,               -- "email", "sla_status"
  base_type   text not null,
  constraint_ jsonb not null                  -- {"regex": "...@..."} or {"enum": ["green","amber","red"]}
);

create table link_type (
  id            text primary key,             -- "carrier_provides_circuit"
  from_type     text references object_type(id),
  to_type       text references object_type(id),
  cardinality   text not null,                -- one_to_one | one_to_many | many_to_many
  from_name     text,                         -- "circuits"  (traversal name)
  to_name       text                          -- "carrier"
);

create table action_type (
  id            text primary key,             -- "open_escalation"
  object_type   text references object_type(id),
  spec          jsonb not null                -- parameters + rules + submission criteria (see §5/§6)
);
```

### 4.2 Objects (D5) — one table, typed views on top

Every object of every type lives in one physical table. System columns are typed and indexed; domain properties live in validated `JSONB`. This is what makes types data instead of DDL.

```sql
create table objects (
  id           uuid primary key default gen_random_uuid(),
  object_type  text not null references object_type(id),
  pkey         text not null,                 -- business primary key, unique within a type
  title        text,                          -- denormalized title_prop for fast display
  properties   jsonb not null default '{}',   -- all domain properties, schema-validated on write
  version      integer not null default 1,    -- bumped on each action; pairs with edit_event
  created_at   timestamptz default now(),
  updated_at   timestamptz default now(),
  unique (object_type, pkey)
);
create index on objects (object_type);
create index on objects using gin (properties);            -- filter on any property
create index on objects using gin (title gin_trgm_ops);    -- full-text/fuzzy title search (D8)
```

For ergonomics and type-safety, the loader **generates a typed view per object type** from `property_def`, so analysts and SQL see real columns and the database enforces types — without the base table needing a migration:

```sql
-- generated from property_def for object_type='carrier'
create view v_carrier as
select id, pkey as carrier_id,
       title,
       (properties->>'account_manager')          as account_manager,
       (properties->>'sla_status')               as sla_status,
       (properties->>'annual_spend')::numeric    as annual_spend
from objects where object_type = 'carrier';
```

Property writes are validated against `property_def` + `value_type` **in the action executor** (§5) before they ever reach `properties`, so the JSONB is never a free-for-all. This is the crux decision (D5): table-per-type would be strongly typed but demand a migration on every model change — fatal to a config-driven platform; a pure generic store would lose all typing; the **hybrid** keeps types as data *and* recovers typed querying through generated views.

### 4.3 Links (D6) — one edge table

```sql
create table links (
  link_type   text not null references link_type(id),
  from_id     uuid not null references objects(id),
  to_id       uuid not null references objects(id),
  created_at  timestamptz default now(),
  primary key (link_type, from_id, to_id)
);
create index on links (to_id, link_type);   -- reverse traversal
-- cardinality enforced by partial unique indexes, e.g. one_to_many:
create unique index on links (link_type, to_id) where link_type = 'carrier_provides_circuit';
```

Traversal ("this carrier's circuits") is a single indexed join; at this scale that is faster and simpler than maintaining foreign keys per type, and it lets a new link type appear with zero schema change.

### 4.4 Versioning & audit (D2, D13) — one append-only log

```sql
create table edit_event (
  id            bigserial primary key,
  action_id     text,                          -- which action type produced this
  action_run    uuid not null,                 -- one run = one atomic transaction (D14)
  object_id     uuid not null references objects(id),
  op            text not null,                 -- create | update | delete | link | unlink
  property      text,                          -- for update: which property changed
  before        jsonb,
  after         jsonb,
  actor         text not null,                 -- user or service identity
  at            timestamptz not null default now()
);
create index on edit_event (object_id, at);
```

This single table is **both** the immutable audit trail and the version history. "What did this object look like on March 1?" is replaying its `edit_event` rows up to that timestamp. Dataset ingests get a coarser `load_version` (a row in a small `dataset_load` table) so source provenance is traceable to a load (D4), with column-level lineage deferred.

### 4.5 Access (D15)

```sql
create table role_def      ( id text primary key, operations text[] not null );   -- e.g. {object:read, action:open_escalation}
create table user_role     ( user_id text, role_id text references role_def(id), primary key (user_id, role_id) );
create table object_policy ( object_type text, predicate jsonb, role_id text );    -- optional row-level rule
```

The authorization decision (§5) composes these in a fixed, default-deny order so that markings/CBAC can be inserted later without rewriting callers.

---

## 5. The action engine (the kinetic core)

This is the heart — the **Edits-Only-via-Actions** invariant made concrete. Objects change *only* through the action executor; no other code path writes to `objects`, `links`, or `edit_event`. Enforce it structurally: the application service holds the only DB role with write access to those tables, and that path runs exclusively inside the executor.

**An action type declares three things** (config in `action_type.spec`, §6): typed **parameters**, **rules** (the edits to compute), and **submission criteria** (server-side validation). Execution is a single function with a single transaction:

```
execute(actionTypeId, params, actor):
  1. load action_type spec
  2. coerce + type-check params         → reject on type/value-type violation
  3. AUTHORIZE (see below)              → reject if denied
  4. evaluate submission criteria       → reject with {error} if any fails   (server-side, never trust client)
  5. compute edits                      → from rules, or by calling the action's function (D10/D12)
  6. BEGIN
       apply edits to objects/links     → validating each property vs property_def/value_type
       bump objects.version
       insert one edit_event per change (same action_run uuid)
     COMMIT                              → atomicity (D14); read-your-writes is automatic
  7. run side effects (post-commit, non-transactional, via outbox)
  8. return the new object state
```

**Authorization decision (default-deny, fixed order).** Built now even though only two gates are populated, so the deferred gates slot in without touching callers:

```
deny unless:
  (1) session valid
  (2) [reserved: mandatory controls / markings — always-pass in v1]
  (3) actor holds a role granting the operation        (RBAC, D15)
  (4) row-level object_policy (if any) admits the object
```

**Functions (D11/D12).** Complex or multi-object logic is a function in the one runtime, returning either edits or a validation error. A function-backed action is exclusive — when present it owns the whole computation (matching Foundry's "if a function rule is present, no other rule may be configured"). Submission criteria are ordinary functions returning `valid | {error}`; trivial ones may be expressed as declarative predicates in config.

**Side effects (the honest limitation).** Notifications, webhooks, external writes run *after* commit through a small **outbox** table polled by a worker. They are explicitly **not** part of the action's transaction: an external call may succeed while we roll back, or fail after we commit. We design around this rather than pretend atomicity across systems — exactly as the Design Constraints require.

---

## 6. The ontology-config format (the adapt seam)

This is where — and the *only* place where — Bailey's world enters. The engine above never changes; she authors declarative config that the loader validates against the rules in §4–§5. A minimal, carrier-flavored slice:

```yaml
value_types:
  sla_status:   { base: enum, enum: [green, amber, red] }
  email:        { base: text, regex: '^[^@]+@[^@]+$' }

object_types:
  carrier:
    title: Carrier
    primary_key: carrier_id
    title_prop: name
    properties:
      carrier_id:      { type: text,    required: true }
      name:            { type: text,    required: true }
      account_manager: { type: text }
      sla_status:      { value_type: sla_status }
      annual_spend:    { type: decimal }
  circuit:
    title: Circuit
    primary_key: circuit_id
    title_prop: circuit_id
    properties:
      circuit_id: { type: text, required: true }
      bandwidth:  { type: text }
      status:     { value_type: sla_status }

link_types:
  carrier_provides_circuit:
    from: carrier
    to: circuit
    cardinality: one_to_many
    from_name: circuits
    to_name: carrier

action_types:
  open_escalation:
    object_type: circuit
    parameters:
      circuit:  { type: object, object_type: circuit, required: true }
      reason:   { type: text, required: true }
    submission_criteria:
      - fn: onlyManagersMayEscalate        # function returning valid | {error}
    rules:
      - update: { object: $circuit, set: { status: red } }
      - create:
          object_type: escalation
          properties: { circuit_id: $circuit.circuit_id, reason: $reason, opened_by: $actor }

roles:
  carrier_manager: { operations: [object:read, action:open_escalation] }
  viewer:          { operations: [object:read] }
```

Load that and the platform has carriers, circuits, the "provides" relationship, a governed, validated, audited "open escalation" action, and two roles — with no code written. **That file is the entire surface Phase 2 produces.** Standardize the engine; adapt the config.

---

## 7. Standardize vs. adapt — the explicit boundary

The direct answer to "do it now, adapt to her later." Everything in the left column we build and freeze now; everything in the right column is per-deployment config produced in Phase 2.

| **Fixed platform (build now, standardize)** | **Per-deployment config (adapt to Bailey later)** |
|---|---|
| Postgres schema: `objects`, `links`, `edit_event`, config & access tables | Which **object types** and their **properties** |
| Config loader + validator; typed-view generator | Which **value types** (constraints/enums) |
| Object/Object-Set read API (search, filter, traverse) | Which **link types** and cardinalities |
| Action executor (validate → atomic write → audit) | Which **action types** (params, rules, criteria) |
| Authorization decision (default-deny composition) | Which **roles** and **row-level policies** |
| Audit/edit-log writer; point-in-time reconstruction | **Ingestion mappings** (which source → which object type) |
| Function runtime + the edits API | The **validation functions** for complex criteria |
| Thin UI shell (object browser, action forms) | UI labels / which objects and actions are surfaced |

If a future request would force a change in the **left** column to add something in the **right**, the engine abstraction has leaked — and that is the single design test to apply to every milestone below.

---

## 8. Build sequence — Minimum Viable Foundry, realized

Six milestones. Each one is independently demonstrable and maps to specific core + keep concepts in the Build View. This *is* the "Minimum Viable Foundry" note made executable.

- **M0 — Skeleton.** Postgres + the config tables + the loader. Demo: load the §6 config; the typed views appear. *(Realizes: the metadata-driven core.)*
- **M1 — Semantic.** `objects` table + JSONB validation + the `links` edge table + object-set read API (filter, full-text, traverse). Demo: create carriers/circuits by seed, search and traverse them. *(Object Type, Object, Property, Value Type, Link Type, Link Cardinality, Object Set, Object Backing.)*
- **M2 — Kinetic.** The action executor: params → submission criteria → atomic edits → `edit_event`. Demo: run "open escalation"; see the object change, the audit row, read-your-writes. *(Action Type, Action Parameter, Submission Criteria, Action Atomicity, Edits-Only-via-Actions, Edit History, Function, Function-Backed Action.)*
- **M3 — Governed.** Roles + the default-deny authorization decision + optional row policies. Demo: the viewer is refused the escalation; the manager is allowed. *(Authorization Decision, Role, Operation; the Security-Travels-With-Data invariant.)*
- **M4 — Ingestion.** A thin path: CSV/spreadsheet upload + one API connector → mapped into object types, with a `dataset_load` provenance row. Demo: upload a carrier sheet; objects appear with lineage. *(Data Connection simplified, Object Backing, dataset-level lineage.)*
- **M5 — Thin UI.** Browse objects, run searches, invoke actions via auto-generated forms from action params. Demo: the closed loop end-to-end from a browser. *(Operational Application, Action Form.)*

After M5 the five invariants all hold: a semantic model over data (M1), a versioned foundation (M2's log), governed writeback (M2), security that travels with data (M3), end-to-end lineage (M2+M4).

---

## 9. Deferred surfaces — and the seams that keep them addable

The discipline from the Design Constraints holds: everything deferred must be addable *without rework*. The seams are deliberately pre-cut.

- **Dynamic layer** (scenarios, models, simulation). Scenarios are a delta overlay on `objects` keyed by object id — a future `scenario_id` column on `edit_event` plus a read-time merge; no base-schema change. Models are external services called from functions. *(All defer.)*
- **AIP.** The one thing to preserve now is the **Execution-Permission Contract**: AI may only *propose* an action; the executor (§5) runs it under the user's roles. Because every write already goes through the executor, an AI layer inherits governance for free later. *(Defer the surface, keep the seam.)*
- **Platform / Apollo.** Ordinary deployment; keep only "versioned, auditable releases" as a principle. *(Drop.)*
- **Advanced property types, interfaces, ontology branching.** Additive: new `base_type` values, a `proposals` table later. *(Defer.)*
- **Markings / CBAC.** Gate (2) of the authorization decision is already reserved; populating it is additive. *(Drop now, seam kept.)*

---

## 10. The one call left to make

Every D1–D15 is resolved except a single team-preference: **D11, the implementation language.** The recommendation is **TypeScript/Node** — one language spanning the action functions, the config-as-types, the engine, and a future React UI, with strong typing where the action edits live. Python is a fine alternative if the team is stronger there; nothing in this blueprint depends on the choice beyond picking one. Make that call and M0 can start.

---

## Sources & cross-references

- `Spec/SPEC_Foundry-Clone_Design-Constraints.md` — the MUST/CAN-drop/OPEN constraints and the D1–D15 register this resolves.
- `Palantir-Foundry-Conceptual-Map.md` — the end-state model; §4 (the Ontology) and §8 (the irreducible core).
- `Vault/00 Maps & Views/Build View — What We're Cloning` — the core + keep set this build realizes.
- `Vault/02 Foundations/Minimum Viable Foundry` — the v1 target §8 makes executable.
- Reconstruction provenance: Kinetic (actions/functions/edits API, §5), Semantic (object/link/value-type model, §4), Security (the authorization composition, §4.5/§5), Data (versioned store, §4.4).
