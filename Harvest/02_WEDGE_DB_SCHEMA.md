# 02 — Wedge DB Schema (Supabase / Postgres, clean-room)

> A concrete, **runnable** Postgres schema for Bailey's one workflow. Clean-room: reconciles OpenFoundry's real `initial_ontology.sql` (`services/ontology-service/migrations/20260419100004_initial_ontology.sql`, **VERIFIED**, read in full) with our blueprint §4 and the brainstorm's leanings — and **improves on OpenFoundry exactly where it is thin** (it has no version guard, no tombstone, no edit log, no JSONB constraint, no read-side security; we add all five).
>
> **`[verified]`** — every fix below was run against **PostgreSQL 18** (PGlite in Node) in `Harvest/repro/wedge_schema_repro.mjs`; last run: *ALL CHECKS PASSED*. The audit (`SPEC_Foundry-Clone_Spec-Audit.md` L36–48) reproduced **8 defects** on PG 18.4: **A1, A2, A5, A6, C3, A3, A4, B3**. This schema is the blueprint's §4 with those 8 closed — and it additionally implements the **B2** (two-layer merge) and **B6** (compiled read WHERE) *design* resolutions, which the audit raised analytically (no Postgres repro). So: 8 reproduced defects fixed + 2 design blockers resolved.

---

## 0. What OpenFoundry's schema is, and where we diverge

OpenFoundry's entire ontology is **5 tables in ~70 lines** (`initial_ontology.sql`, VERIFIED). Its shape is genuinely worth borrowing; its omissions are exactly our differentiators.

| OpenFoundry `initial_ontology.sql` (VERIFIED) | Borrow? | Our wedge change |
|---|---|---|
| `object_instances(id, object_type_id, properties JSONB, created_by, created_at, updated_at)` — pure system-cols + JSONB | **Yes** (the D5 shape) | add `pkey`, `title`, `version`, `deleted_at`, split `properties` into `datasource ⊕ edits`, add generated typed columns |
| `link_instances` — one unified edge table (`link_type_id, source_object_id, target_object_id, properties`) | **Yes** (the D6 shape) | add tombstone + per-type partial-unique for cardinality; OF has **no** unique on the triple (dup edges allowed) and **no** type-match check (ONT-05, VERIFIED) |
| `properties.validation_rules JSONB` per property | **Concept yes** | OF stores it but **never reads it** (`type_system.rs`, VERIFIED) — we resolve it into a per-type `CHECK` so the DB enforces it |
| `link_types.cardinality TEXT DEFAULT 'many_to_many'` | name only | OF **never enforces** it (no constraint, VERIFIED) — we back `one_to_*` with a partial unique index |
| Everything `ON DELETE CASCADE`, **no** `version`, **no** `deleted_at`, **no** audit/edit table | **No** | hard delete + cascade erases history (A6); we use tombstones + an append-only `edit_event` log |

OpenFoundry has **no** `value_type` table, **no** `edit_event`/audit on the write path, **no** version column, **no** tombstone — confirmed by `rg` (VERIFIED). Our schema adds all of them.

---

## 1. Extensions & config (the ontology as data)

Declare extensions **first** — the blueprint's §4 failed because `gin_trgm_ops` had no `create extension` (audit A2). On Supabase these are enabled in the dashboard or via migration.

```sql
create extension if not exists pg_trgm;        -- fuzzy/title search
create extension if not exists pg_jsonschema;  -- Supabase: JSON Schema in CHECK (see §3). Vanilla PG: use a plain CHECK.
-- gen_random_uuid() is core since PG13 — no extension needed.

-- value_type BEFORE property_def (audit A1 was a forward-reference that wouldn't run)
create table value_type (
  id          text primary key,                 -- 'sla_status', 'email'
  base_type   text not null,                    -- enum|text|integer|decimal|boolean|date|timestamp
  constraint_ jsonb not null default '{}'       -- {"enum":[...]} | {"regex":"..."} | {"min":..,"max":..}
);

create table object_type (
  id          text primary key,                 -- 'carrier'
  title       text not null,                     -- 'Carrier'
  primary_key text not null,                     -- property id used as the business key
  title_prop  text                               -- property shown as the object's label
);

create table property_def (
  object_type text not null references object_type(id),
  id          text not null,                      -- 'account_manager'
  base_type   text not null,                      -- resolved from value_type if value-typed (fixes audit A4)
  value_type  text references value_type(id),
  required    boolean not null default false,
  hot         boolean not null default false,     -- if true, loader promotes it to a generated column (§4)
  primary key (object_type, id)
);

create table link_type (
  id          text primary key,
  from_type   text references object_type(id),
  to_type     text references object_type(id),
  -- OF's type_system.rs allows 4 (incl many_to_one, VERIFIED); we keep 3 and model
  -- many_to_one as one_to_many declared from the other side. Add it here if you'd rather not flip.
  cardinality text not null check (cardinality in ('one_to_one','one_to_many','many_to_many')),
  from_name   text, to_name text
);

create table action_type (                        -- mirrors OF's action_types: input_schema + config split
  id          text primary key,
  object_type text references object_type(id),
  spec        jsonb not null                      -- {parameters, submission_criteria(CEL), rules}
);
```

> **Loader job the blueprint never described (audit A4):** when a property is value-typed (`{value_type: sla_status}` with no `base_type`), the loader **resolves** `base_type` from `value_type.base_type` before insert. `[verified]` in the repro (§2 of the harness).

---

## 2. Objects — hybrid, two-layer, versioned, soft-deletable

The crux. We keep OpenFoundry's "system columns + JSONB" idea but make types **data** *and* recover real DB typing — and we split the blob into the **datasource ⊕ edit** layers (brainstorm §1, the B2 resolution).

```sql
create table objects (
  id          uuid primary key default gen_random_uuid(),
  object_type text not null references object_type(id),
  pkey        text not null,                         -- business PK; mandatory on create (fixes A3)
  title       text,                                  -- denormalized title_prop (executor keeps in sync)
  datasource  jsonb not null default '{}',           -- INGEST layer (M4 writes here)
  edits       jsonb not null default '{}',           -- EDIT layer (the action executor writes here)
  properties  jsonb generated always as (datasource || edits) stored,  -- effective read view; edits WIN
  version     integer not null default 1,            -- optimistic-concurrency guard (fixes B3 lost-update)
  deleted_at  timestamptz,                           -- tombstone; never hard-delete (fixes A6)
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  unique (object_type, pkey)
);
```

Why this beats both the blueprint and OpenFoundry:

- **`properties` is a *stored generated column*** `datasource || edits`. Postgres `||` is right-wins, so an edited property overrides the datasource value while unedited properties keep flowing from ingestion — the per-property merge Foundry-proper documents, and **lineage-per-value for free** (you can always see whether a value came from `datasource` or `edits`). `[verified]`.
- **Hot fields → real typed, indexable generated columns.** The audit (V4/C3) proved a GIN on `properties` serves `@>` containment but *not* range/sort. So promote filterable/sortable fields:

```sql
-- generated DIRECTLY from the merge (a generated col may not reference another generated col)
alter table objects add column sla_status text
  generated always as ((datasource || edits)->>'sla_status') stored;
alter table objects add column annual_spend numeric
  generated always as (((datasource || edits)->>'annual_spend')::numeric) stored;

create index on objects (object_type, sla_status) where deleted_at is null;   -- equality + sort
create index on objects (object_type, annual_spend) where deleted_at is null; -- range + ORDER BY
create index on objects using gin (properties);                              -- containment on the cold tail
create index on objects using gin (title gin_trgm_ops);                      -- fuzzy title search (needs pg_trgm)
```

- **The DB enforces JSONB shape on *write*** (fixes audit A5, where the blueprint accepted `annual_spend:"not-a-number"` and broke the *read* view for everyone). On Supabase use `pg_jsonschema`; the portable form is a plain `CHECK`:

```sql
alter table objects add constraint carrier_spend_numeric check (
  object_type <> 'carrier'
  or not ((datasource || edits) ? 'annual_spend')
  or jsonb_typeof((datasource || edits)->'annual_spend') = 'number');

alter table objects add constraint carrier_sla_enum check (
  object_type <> 'carrier'
  or not ((datasource || edits) ? 'sla_status')
  or (datasource || edits)->>'sla_status' in ('green','amber','red'));
-- Supabase pg_jsonschema equivalent:
--   check ( json_matches_schema('{"type":"object","properties":{...}}', datasource || edits) )
```

`[verified]`: the repro inserts `annual_spend:"not-a-number"` and `sla_status:"purple"` and the DB **rejects both at write time**, while valid rows insert.

---

## 3. Links — one edge table, cardinality actually enforced

```sql
create table links (
  link_type  text not null references link_type(id),
  from_id    uuid not null references objects(id),
  to_id      uuid not null references objects(id),
  properties jsonb not null default '{}',
  deleted_at timestamptz,                          -- unlink is an event, not a DELETE
  created_at timestamptz not null default now(),
  primary key (link_type, from_id, to_id)          -- OF allows duplicate edges (ONT-05); we don't
);
create index on links (to_id, link_type) where deleted_at is null;  -- reverse traversal

-- cardinality the brainstorm/blueprint way: a per-constrained-type partial unique index.
-- one_to_many (a circuit has many escalations, each escalation belongs to one circuit):
create unique index esc_card_ix on links (link_type, to_id)
  where link_type = 'circuit_has_escalation' and deleted_at is null;
```

> **Honest note (audit C5 / V7):** a *global* `unique(link_type, to_id)` would wrongly block legitimate many-to-many. So each constrained link type gets its **own** partial index at load — i.e. cardinality enforcement **is** per-type DDL. We state that plainly rather than claim "zero schema change per link type." The loader emits one such index per `one_to_*` link type in the config (`01` declares **4**); the repro proves the representative `circuit_has_escalation` case. OpenFoundry enforces cardinality *not at all* (VERIFIED), so even one partial index puts us ahead.

---

## 4. Edit log — append-only audit **and** version history (the thing OpenFoundry never wired)

This is the single biggest gap in OpenFoundry: `rg -n 'audit|emit|edit_event' services/ontology-service/src` → **nothing** (VERIFIED, by me and by the skeptic). Its `execute_action` mutates objects and records no who/what/before→after. We make the edit log the spine.

```sql
create table edit_event (
  id          bigserial primary key,
  -- optional tamper-evidence harvested from OF's AuditEvent FIELD shape (audit_event.rs L78-101) --
  -- but done RIGHT: a real digest, unlike OF's format-string "chain" (immutable_log.rs, see 05_ANTIPATTERNS)
  seq         bigint,
  prev_hash   text,
  entry_hash  text,                                -- = encode(sha256(prev_hash || canonical(row)), 'hex')
  -- the event --
  action_id   text,                                -- which action type
  action_run  uuid not null,                       -- one run = one atomic transaction (D14)
  object_id   uuid references objects(id),         -- FK is SAFE: we tombstone, never hard-delete (fixes A6)
  link_key    text,                                -- for link/unlink events (audit C5: links don't fit object_id)
  op          text not null check (op in ('create','update','delete','link','unlink')),
  property    text, before jsonb, after jsonb,
  actor       text not null,                       -- SERVER-derived from the session (B5); never client-supplied
  status      text not null default 'success'      -- success|failure|denied (harvested from OF AuditEventStatus)
                check (status in ('success','failure','denied')),
  at          timestamptz not null default now()
);
create index on edit_event (object_id, at);
create index on edit_event (action_run);
```

- **`object_id` FK is now safe** precisely because objects are tombstoned, never removed — the exact circularity that made `op='delete'` unimplementable in the blueprint (audit A6) is dissolved. `[verified]`: the repro tombstones a carrier and its `edit_event` history survives.
- **Point-in-time** = replay `edit_event` for an object up to `at`. Per audit C4, add a per-object snapshot every N events when history grows (brainstorm §5); not needed at Bailey's scale.
- **`actor` is server-derived** (see §6), closing B5.
- The optional `seq/prev_hash/entry_hash` give *real* tamper-evidence with `sha256(prev || row)` — do **not** copy OpenFoundry's `chain_hash` (it's a format string, not a digest; see `05_ANTIPATTERNS`).

The append-only guarantee on Supabase: revoke `update`/`delete` on `edit_event` from the app role (OpenFoundry's "append-only" is only `CHECK(sequence>0)` — UPDATE/DELETE are *not* revoked, VERIFIED).

---

## 5. Provenance (the lineage MUST, audit D-ii)

```sql
create table dataset_load (
  id uuid primary key default gen_random_uuid(),
  source text not null, loaded_by text not null, loaded_at timestamptz not null default now(),
  row_count integer
);
alter table objects add column source_load uuid references dataset_load(id);  -- which load produced/updated this
```

This closes the lineage chain's first hop, which the blueprint left dangling (`dataset_load` was referenced but never DDL'd). Combined with the `datasource`/`edits` split, every value is traceable to *either* a load *or* a decision.

---

## 6. Access — RBAC + row policies compiled into the read WHERE (security travels with reads)

OpenFoundry's read-side security is **unbuilt**: `optimizer_rules.rs` is a 5-line "Future" TODO, the `RlsContext.org_filter` helper is **never called by any service**, and the ABAC `row_filter` is *returned to the caller* rather than applied (B6-*, VERIFIED). We do the opposite — compile the policy into the query, with **Supabase RLS as a real in-DB backstop**.

```sql
create table role_def    ( id text primary key, operations text[] not null );  -- e.g. {object:read:carrier, action:open_escalation}
create table user_role   ( user_id text, role_id text references role_def(id), primary key (user_id, role_id) );
create table object_policy ( object_type text, role_id text, predicate jsonb ); -- predicate authored in CEL/JSON
```

Two enforcement layers:

1. **App layer (primary, Hasura-style).** The read API compiles a row policy's CEL predicate into a parameterized `WHERE` fragment and appends it to every object-set/traversal query, so a viewer literally cannot `SELECT` forbidden rows. `[verified]`: the repro compiles `region == actor.region` to `properties->>'region' = $1` and a west viewer sees only the west carrier. **Always parameterize** — never string-interpolate the value (OpenFoundry's `format!("{col} = '{org}'")` and its `{{token}}` `row_filter` are injection-shaped; see `05_ANTIPATTERNS`).

2. **DB layer (backstop).** Supabase RLS on `objects`, keyed off the JWT, so even a direct PostgREST call is filtered:

```sql
alter table objects enable row level security;
create policy carrier_mgr_read on objects for select
  using ( deleted_at is null and (
    (auth.jwt() ->> 'role') = 'admin'
    or properties->>'account_manager' = (auth.jwt() ->> 'email') ) );
```

`actor` for the audit log is derived **server-side** from `auth.uid()` / the verified JWT (`claims.sub` in OpenFoundry's `claims.rs`, VERIFIED) — never from a request body. This is the concrete shape behind B5: Bailey's identity → `actor` → `edit_event`.

---

## 7. Reproduction

`Harvest/repro/wedge_schema_repro.mjs` builds this schema verbatim on PostgreSQL 18 (PGlite) and asserts each fix:

```
1. Schema runs clean top-to-bottom ................. PASS  (A1 forward-ref, A2 extension)
   + hot fields as generated typed cols (range/sort) PASS  (C3)
2. value-typed property resolves base_type ......... PASS  (A4)
3. DB rejects bad number / bad enum on write ....... PASS  (A5)
4. datasource ⊕ edits merge; edits win; ds intact .. PASS  (B2 resolution + lineage)
5. action-created object carries a pkey; 1st-class link  PASS  (A3 + audit E)
6. stale version update affects 0 rows ............. PASS  (B3 lost-update)
7. tombstone hides object; edit_event survives ..... PASS  (A6)
8. compiled WHERE filters a viewer's rows .......... PASS  (B6 resolution)
```
> 8 reproduced defects (A1, A2, A3, A4, A5, A6, C3, B3) + the B2/B6 design resolutions.

Run: `cd Foundry/Harvest/repro && npm install && node wedge_schema_repro.mjs`.

---

## Provenance

- OpenFoundry, **VERIFIED** (read in full): `services/ontology-service/migrations/20260419100004_initial_ontology.sql` (L3–71), `.../20260423113000_action_types.sql`, `.../src/domain/type_system.rs`, `.../src/handlers/actions.rs` (L73–99, L993–1202), `services/audit-service/src/models/audit_event.rs` (L78–101), `services/audit-service/src/domain/immutable_log.rs`, `libs/auth-middleware/src/{row_level_security.rs,claims.rs}`, `libs/query-engine/src/optimizer_rules.rs`.
- Our chain: `SPEC_Foundry-Clone_Build-Blueprint.md` §4, `SPEC_Foundry-Clone_Spec-Audit.md` (the 8 reproduced defects), `SPEC_Foundry-Clone_Prior-Art-Brainstorm.md` §§1,3,4,5,6,7.
- `[verified]` marks: `Harvest/repro/` on PostgreSQL 18 (PGlite) + cel-js, this machine, 2026-06-14.
