# Foundry Clone — Prior Art & Brainstorm

> **Purpose:** I went looking at how other people solve the exact problems the audit (`SPEC_Foundry-Clone_Spec-Audit.md`) flagged — Palantir's own docs, the Airtable-clones, the authorization and expression-language ecosystems, and two ontology-native databases. This maps each finding onto real prior art, lays out the options, and gives a **leaning to argue about** (not a decision). Two of the ideas I proved in our own stack (Postgres 18.4 + Node) before writing them down; those are marked **[verified]**.
> **Status:** Draft 1 · 2026-06-14 · Research input for resolving the six pre-M0 blockers.

---

## The headline: research moved two "blockers" and confirmed one bug

1. **Blocker B2 (ingestion vs. edits-only) mostly dissolves** once you see how Foundry actually does it: Actions are *not* the only writer. Ingestion and user-edits both write, into **separate layers**, merged per-property. We mis-stated our own invariant.
2. **Blocker B1 (the rules language) is off-the-shelf.** Google's **CEL** is purpose-built for "safe expressions embedded in declarative config," has mature TypeScript libraries, and evaluated our `onlyManagersMayEscalate` criterion verbatim. We don't invent a language; we adopt one.
3. **Defect A3 (create needs a primary key) is confirmed by Foundry**, which *requires* you to specify the PK on object creation. Our pkey-less `create` rule is a real bug, and Foundry tells us the fix.

Everything else below is options + leanings.

---

## 1. Restate the core invariant: "edits via Actions" ≠ "all writes via Actions" — dissolves B2

The audit's sharpest contradiction was M4 ingestion writing `objects` while §5 declared the executor the *only* writer. **Foundry doesn't have that contradiction because it never makes that claim.** From Palantir's "how user edits are applied" doc: an object "receives data from **both** the input datasource **and** user edits, [which] must be transparently resolved with a *conflict resolution strategy*," and by default "the final state of an object is always determined by the **user edits** applied to it, regardless of any future datasource updates for edited properties." The merge is **per-property**: an unedited property keeps taking datasource refreshes; an edited property ignores them.

So the real invariant is: **decisions (user edits) happen only through Actions; bulk data arrives through ingestion; reads merge the two with edits winning.** Two writers, two layers, one merged read.

**What this changes in our model.** `objects.properties` shouldn't be a single blob that both ingestion and actions fight over. Cleanest shapes to debate:

- **(a) Two-layer column:** `properties` = datasource layer; `edits` = a second JSONB (or the `edit_event` log itself) overlaid at read time. Read = `datasource ⊕ edits`.
- **(b) Per-property provenance:** materialize current-state but tag each property with its source (`ingest` | `edit`) so a refresh only overwrites `ingest`-sourced values.

Either way we get two things the audit said were missing: ingestion stops violating the invariant, **and** lineage-per-value (D-ii) falls out for free — you can always say whether a value came from a load or a decision. This is the single biggest revision to the blueprint, and it's not extra complexity — it's the complexity Foundry already found necessary.

---

## 2. The rules/expression language (B1, D10, D12) — adopt CEL, don't build a DSL

The audit's #1 gap was that §6's config invents an expression language (`$circuit.circuit_id`, `$actor`, predicates) it never specifies. The ecosystem has already solved this twice over:

| Option | What it is | Fit |
|---|---|---|
| **CEL** (Common Expression Language, Google) | Non-Turing-complete, sandbox-safe expression language **explicitly designed "for extending declarative configurations"**; used for validation, filtering, and authorization rules. TS libs: `cel-js`, `@marcbachmann/cel-js` (full spec, ~22× faster). | **Strong.** One language for submission criteria, row policies, *and* value-type constraints. |
| **JSONLogic** | Tiny, deterministic, read-only ("one rule → one decision, no side effects"); rules are JSON, not a string grammar. | Good for the simplest predicates; less ergonomic for anything nested. |
| **Function-backed (TS)** | Arbitrary TypeScript for complex/multi-object logic. | The escape hatch — exactly Foundry's "if a function rule is present, no other rule may be configured." |

**[verified]** `cel-js` installed from npm and evaluated, in Node:
`'carrier_manager' in actor.roles` → `true`; `size(params.reason) > 0` → `true`; `circuit.status != 'red'` → `true`; and the viewer case → `false`. That first expression *is* `onlyManagersMayEscalate`, with no hand-written function at all.

Foundry's own structure backs the split: declarative **Rules** ("transform the parameters into Ontology edits") + **Submission Criteria** (templated predicates) + function-backed for the rest. **Leaning:** CEL for every boolean in the system (criteria, policies §7, value-type constraints §3), a small declarative edit-rule schema (`create`/`update`/`link` whose values may be CEL), and TS functions for genuinely complex actions. This makes "the config is the product surface" (blueprint line 27) *true*, and collapses D10/D12 from "unresolved" to "pick CEL." It also means D11's "one call left" is real but trivial — CEL has first-class TypeScript support, so the stack stays TS end-to-end.

---

## 3. Object storage shape (D5, C2) — real columns are the prior-art norm, and JSONB *can* be constrained

The audit challenged D5's "typed views enforce types" (they don't) and "no per-type DDL" (false — views, partial indexes, and range-query indexes are all per-type DDL). Prior art is clarifying on both halves:

**How the Airtable-clones actually store dynamic fields:** they use **real Postgres tables and columns**, generated at runtime. Teable: "every table you see in Teable corresponds to a **physical table in Postgres**." Directus and NocoBase model real schema (tables, columns, constraints, relationships) too. They *accept* loader-run DDL on every field change — the very thing the blueprint tried to avoid and, per the audit, failed to avoid anyway.

**JSONB is not doomed to be a free-for-all.** A per-type `CHECK` constraint (or the `pg_jsonschema` extension's `json_matches_schema()` in a CHECK) makes Postgres enforce shape on write. **[verified]** a CHECK on the carrier type **rejected the exact `annual_spend:"not-a-number"` value that broke the audit's view**, and rejected a bad `sla_status` enum, while accepting valid rows. So A5's "the DB enforces nothing" is fixable without leaving JSONB — the loader generates a CHECK (or pg_jsonschema doc) per object type alongside the view.

Options to weigh:

| Shape | Typing/constraints | Range & sort | Per-type DDL | App duplication |
|---|---|---|---|---|
| All-JSONB + per-type CHECK + GIN | DB-enforced shape; no native types | needs expression index per hot field | CHECK + indexes | none |
| **JSONB + generated columns** for hot fields | real typed column, DB-checked | native btree, fast | `ALTER … ADD GENERATED` | none (column derives from JSONB) |
| Real column per property (Teable/Directus) | full native typing | native | `ALTER` per field | none |
| Blueprint as-is (JSONB + read-only view) | **none** (app-only) | none (audit V4) | view + indexes anyway | view restates every field |

**Leaning:** drop the "no per-type DDL" promise (it was never true), keep system columns + a JSONB cold tail, and **promote hot/filterable/sortable properties to Postgres *generated columns*** — e.g. `annual_spend numeric generated always as ((properties->>'annual_spend')::numeric) stored`. That yields a real, indexable, type-checked column with **zero app-side duplication**, derived from the same JSONB. It's the middle path the audit gestured at (C2), and it's cheap to prototype next.

---

## 4. Concurrency & isolation (B3) — version guard + SERIALIZABLE, both with retry

The audit proved submission criteria aren't enforced under Postgres's default READ COMMITTED (write-skew → two "max one" escalations) and that `objects.version` is never checked. Prior art is unanimous and boring in a good way: **optimistic version columns** catch lost updates on a single row; **SERIALIZABLE (SSI)** or explicit `SELECT … FOR UPDATE` catch read-then-write anomalies; **both require an app-level retry loop.** Our audit already showed SERIALIZABLE makes the offending transaction abort cleanly.

**Leaning:** run each action transaction at **SERIALIZABLE** with a bounded retry (3–5 attempts on `40001`), and use `objects.version` as a real optimistic guard (`UPDATE … WHERE id=? AND version=?`) so concurrent edits to the same object fail fast instead of silently clobbering. At Bailey's scale (few concurrent writers) the retry cost is negligible, and it's the difference between submission criteria being *enforced* and merely *advisory*. Note even Foundry's OSv2 relaxed this ("does not guarantee that objects read outside of edit generation have not changed during the course of an Action") — so we should be explicit where we land.

---

## 5. Audit & point-in-time (D2, D13, C4) — event log + snapshots, and the edit layer *is* the log

The audit flagged that reconstruct-by-replay is O(history) with no snapshot story, and that the FK design makes deletes incompatible with keeping history. Prior art:

- **Event sourcing + periodic snapshots** is the standard answer to replay cost: "aggregates with thousands of events benefit from periodic snapshots; load the latest snapshot then apply subsequent events." Our `edit_event` table already *is* the event log.
- **Temporal tables** (a main table + a history table kept by triggers) are the lighter alternative if we only want audit + time-travel and not event-driven workflows — Postgres has no built-in temporal tables, but the trigger pattern is well-trodden.

**Leaning:** keep `edit_event` as the event log (it doubles as the §1 edit layer — nice convergence), add **per-object snapshots** on a cadence or every N events for fast point-in-time, and stop treating "replay the whole ontology as of date T" as free. Pair with soft-delete (next) so history survives deletion.

---

## 6. Soft-delete (A6) — tombstones, and a delete is an event

The audit proved you can't `DELETE` an object that has history or links (FK violation), and cascading would erase the audit. Foundry's model resolves it: "**Deletions are not considered an edit.** Once a deletion is applied, the object is no longer visible regardless of datasource state," and "there is **no mechanism to directly undo a single user edit** … other than to make additional user edits." **Leaning:** never physically delete; set a `deleted_at` tombstone, record the deletion as an event, and filter tombstones on every read path (object sets, traversals, views). This is forced once §1 and §5 are in place; it just needs to be written down.

---

## 7. Row-level security / authorization (B6, D15) — compile predicates into the WHERE clause

The audit's B6: security is wired into the *write* path but reads (object sets, traversals) never filter by `object_policy`, whose predicate language is undefined anyway. The cleanest prior art is **Hasura**: it stores row permissions as **boolean expressions and compiles them directly into the SQL `WHERE` clause** of the generated query — "Hasura generates a SQL query, which includes the row/column-level constraints from the access control rules." That's how you make security travel with *reads* without N+1 per-row checks in app code.

| Approach | Shape | Fit for us |
|---|---|---|
| **Predicate → WHERE (Hasura-style)** | author policy as a boolean (CEL/JSON), compile to SQL `WHERE`, inject into every read | **Best fit** — reuses the §2 CEL, enforces on reads, no per-row app loop |
| Postgres **RLS** | `CREATE POLICY` in the DB | Real but "difficult to enforce and maintain"; role-explosion; defense-in-depth later |
| **Oso/Polar** | expressive policy language, evaluated locally, no data centralization | Powerful, heavier than our scale needs |
| **OpenFGA / SpiceDB** (Zanzibar) | relationship-based, centralizes all authz data | Built for Google-scale ReBAC; overkill |

**Leaning:** app-layer authorization, policies authored in the **same CEL** as everything else, **compiled into the read query's `WHERE`** so a viewer literally cannot select rows a policy forbids. Keep Postgres RLS in reserve as a belt-and-suspenders layer once the model stabilizes. This closes the read-side hole and unifies the third "expression language" the audit worried about into the one CEL.

---

## 8. The edits API & function model (B8) — copy Foundry's shape exactly

Foundry's TypeScript edit functions are a ready-made spec for the "edits API" our blueprint named but never drew:

- Decorators `@OntologyEditFunction()` + `@Edits([Type])`, **`void` return**; "the true return type of the function is a **list of Ontology edits**," and "edits are collapsed intelligently."
- Operations: property assignment (`employee.lastName = x`); links `supervisor.set(...)/.clear()`, `reports.add(...)/.remove(...)`; create `Objects.create().ticket(ticketId)` — **"you have to specify a value for its primary key"**; delete `ticket.delete()`.
- Governance: "**Ontology edit functions must be configured as an Action**; running an edit function outside of an Action will not actually modify any object data."

That last line is our "edits-only-via-Actions" invariant enforced at the API layer, and the create-needs-a-PK line independently confirms audit defect **A3**. **Leaning:** define our edits API as either a recording proxy over a typed object graph (mutations captured, returned as an edit list) or an explicit returned edit list; the executor applies the collected edits in one SERIALIZABLE transaction (§4) and writes `edit_event`. **PK on create is mandatory** — closes A3, and the loader/config must specify how each `create` rule computes its key.

---

## 9. Build vs. borrow the substrate — a provocation worth 30 minutes

We are hand-rolling an ontology engine (schema-as-data, versioning, traversal, validation, point-in-time) on raw Postgres. Two kinds of prior art could shortcut large parts of it — not necessarily to adopt, but to *measure ourselves against* before committing months:

- **OpenFoundry** (`github.com/Shamdon/openfoundry`) — an open-source Palantir Foundry alternative with "object types, actions, functions, object views, lineage," **Protobuf as the source of truth → generated TypeScript/Python/Java SDKs.** Even if we don't use it, its object/action schema is a free design review of ours.
- **Ontology-native databases.** **TypeDB** is schema-first and strongly typed — "all writes and reads are validated against the schema," with rule inference; that's our `property_def`/`value_type` validation *as a database feature*. **TerminusDB** is git-like and **versions structured data at the field level**, with semantic diff and queries across history — that's our D2/D13/point-in-time *as a database feature*.

**Honest read:** the blueprint's instinct to keep ops simple (one Postgres, one language) is right, and these substrates add something new to learn and operate. But the audit showed how much engine we're building by hand — and TypeDB hands us schema-as-data + write/read validation, while TerminusDB hands us versioning + time-travel. A **half-day spike** on each (model carriers/circuits/escalations, run the open-escalation action, ask "what did this look like on March 1") is cheap insurance against hand-coding six months of what a database might already do. Recommendation is *look*, not *switch*.

---

## What this changes about the blueprint (the short list)

- **B2 dissolves** → restate the invariant as "edits via Actions"; add a datasource layer + per-property merge (§1). Biggest single revision; also yields lineage (D-ii).
- **B1 resolved** → adopt **CEL**; "config is the product surface" becomes true; D10/D12 collapse to "pick CEL"; D11 stays TS (§2).
- **A5 softened** → per-type `CHECK`/`pg_jsonschema` makes the DB enforce JSONB shape **[verified]**; views stop being fiction (§3).
- **A3 confirmed + fixed** → PK required on `create` (Foundry does this); config must say how each `create` mints its key (§8).
- **B3 resolved** → SERIALIZABLE + retry + a real `version` guard (§4).
- **A6 resolved** → tombstones; a delete is an event (§6).
- **B6 resolved** → compile policy predicates into the read `WHERE`; one CEL for criteria, policies, and constraints (§7).
- **New decision surfaced** → build-vs-borrow the substrate (Postgres vs TypeDB/TerminusDB); at least spike it (§9).

Net: of the six pre-M0 blockers, research clears or de-risks **B1, B2, B3, B6** and the A3/A5/A6 defects. The two left standing are genuinely ours to decide — **identity → `actor` (B5)** and **ontology-change-once-data-exists (B7)** — and even B7 gets easier under the two-layer model (a config change re-validates the edit layer against new constraints; incompatible datasource values are quarantined, not silently broken).

---

## Sources

**Palantir Foundry (how the real system does it)**
- [Object edits & materializations — how user edits are applied](https://www.palantir.com/docs/foundry/object-edits/how-edits-applied) — conflict resolution, edits-win, index vs. persistent store, consistency.
- [Object backend / Ontology architecture](https://www.palantir.com/docs/foundry/object-backend/overview) — Funnel, Actions service, OSS roles.
- [Functions — TypeScript ontology edits API](https://www.palantir.com/docs/foundry/functions/api-ontology-edits) — `@Edits`, operations, PK-on-create, edits-as-list, must-be-an-Action.
- [Action types: Rules](https://www.palantir.com/docs/foundry/action-types/rules) · [Submission criteria](https://www.palantir.com/docs/foundry/action-types/submission-criteria) · [Parameters](https://www.palantir.com/docs/foundry/action-types/parameter-overview).

**Expression / rules languages (B1)**
- [CEL overview](https://cel.dev/overview/cel-overview) · [cel.dev](https://cel.dev/) — safe, non-Turing-complete, for declarative config.
- [cel-js (npm)](https://www.npmjs.com/package/cel-js) · [@marcbachmann/cel-js](https://www.npmjs.com/package/@marcbachmann/cel-js) — full-spec, ~22× faster TS implementation.
- [JSONLogic](https://jsonlogic.com/) — read-only, deterministic, JSON-native predicates.

**Dynamic-schema storage (D5/C2)**
- [Teable — Postgres-Airtable fusion](https://blog.teable.io/blog/data-reimagined-postgres-airtable-fusion) · [Teable repo](https://github.com/teableio/teable) — every table is a physical Postgres table.
- [pg_jsonschema (Supabase)](https://supabase.com/blog/pg-jsonschema-a-postgres-extension-for-json-validation) · [postgres-json-schema](https://github.com/gavinwahl/postgres-json-schema) — JSON Schema validation via CHECK.
- [Zod](https://zod.dev/) — TS-first app-side validation (complementary to DB-side).

**Audit / versioning / concurrency (D2/D13/B3)**
- [Temporal tables vs event sourcing (event-driven.io)](https://event-driven.io/en/temporal_tables_and_event_sourcing/) · [postgresql-event-sourcing reference impl](https://github.com/eugene-khyst/postgresql-event-sourcing) — snapshots for replay cost.
- [PostgreSQL anti-patterns: read-modify-write (EDB)](https://www.enterprisedb.com/blog/postgresql-anti-patterns-read-modify-write-cycles) — optimistic version columns vs SERIALIZABLE.

**Authorization (B6/D15)**
- [Row-level security with Postgres via Hasura](https://hasura.io/blog/row-level-security-with-postgres-via-hasura-authz) · [Hasura row permissions](https://hasura.io/docs/2.0/auth/authorization/permissions/row-level-permissions/) — predicates compiled into the SQL WHERE.
- [Postgres RLS limitations & alternatives (Bytebase)](https://www.bytebase.com/blog/postgres-row-level-security-limitations-and-alternatives/) · [Authorization infra compared](https://inferadb.com/dispatch/authorization-infrastructure-compared/) — RLS vs Oso vs OpenFGA/SpiceDB.

**Reference implementations / ontology-native DBs (§9)**
- [OpenFoundry](https://github.com/Shamdon/openfoundry) — open-source Foundry alternative; Protobuf source-of-truth, generated SDKs.
- [TypeDB](https://typedb.com/) ([repo](https://github.com/typedb/typedb)) — schema-first, strongly typed, validates all reads/writes.
- [TerminusDB](https://github.com/terminusdb/terminusdb) — git-like, field-level versioning, semantic diff, history queries.
