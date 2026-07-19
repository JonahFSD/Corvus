# Foundry Clone — Build Blueprint: Adversarial Audit

> **Audits:** `Spec/SPEC_Foundry-Clone_Build-Blueprint.md` (Draft 1, 2026-06-14), against `Spec/SPEC_Foundry-Clone_Design-Constraints.md` and `Palantir-Foundry-Conceptual-Map.md`.
> **Question put to it:** *"Do we seriously have all our implementation details figured out?"*
> **Method:** read the full chain; then stood up a real PostgreSQL 18.4 instance, built the blueprint's schema **verbatim** from §4, and ran the blueprint's own worked example (§6) and index/concurrency claims against it. Eight defects below were *reproduced*, not reasoned. Repro appendix at the end.
> **Status:** Draft 1 · 2026-06-14 · Adversarial pass, not a redesign.

---

## Verdict

**No.** The blueprint resolves the *architecture-level* questions well — and that work is real (see "What holds" below). But "all implementation details figured out" is not where this is. Three things are true at once:

1. **The document does not run as written.** Its config DDL fails on a forward reference, its index DDL fails on a missing extension, and — most damning — **its flagship worked example (§6 `open_escalation`) cannot execute against its flagship schema (§4).** Two independent NOT-NULL violations and a type fiction. These are not nitpicks; the one end-to-end example the spec offers is broken in three places.
2. **Several mechanisms that M0–M5 depend on are named but unspecified** — above all the *expression/binding language* that the spec itself calls "the product surface for modeling" (line 27). The hardest, most product-defining decision is the one declared already made.
3. **Two headline promises are contradicted by the spec's own contents** — "Bailey's domain becomes a config file, not a code branch" (line 22) and "with no code written" (line 307).

The blueprint is a strong *decision record*. It is not yet a *buildable spec*. The gap between those two is this document.

---

## What holds (so the critique is calibrated)

Real strengths, kept brief because they're not the point of an audit:

- The **metadata-driven thesis** (ontology-as-data, engine-knows-nothing-about-carriers) is the correct spine and is argued cleanly.
- The **standardize-vs-adapt boundary table** (§7) is the right artifact to own, and the "if a right-column change forces a left-column change, the abstraction leaked" test is a genuinely good design discipline.
- The **authorization composition** (§5) reserving gate (2) for markings/CBAC so they slot in without touching callers is the right kind of seam.
- The **milestone decomposition** (M0–M5) is demonstrable and sequenced sanely.
- Choosing **one Postgres + one language** at this scale is the correct anti-over-engineering call.

None of that is in dispute. What follows is everything that is.

---

## Evidence table (reproduced on PostgreSQL 18.4)

| # | Spec claim / artifact | What actually happened | Where |
|---|---|---|---|
| V0 | §4.1 config DDL, as printed | `ERROR: relation "value_type" does not exist` — `property_def` (line 99-104) references `value_type` created later (line 106-110). **The DDL block does not run in document order.** | A1 |
| V1 | line 146 `... using gin (title gin_trgm_ops)` | `ERROR: operator class "gin_trgm_ops" does not exist` — needs `create extension pg_trgm` first, which the spec never issues. | A2 |
| V2 | D5 line 66 "typed views restore … constraints"; line 149 "the database enforces types" | Base table **accepted** `annual_spend: "not-a-number"`. Then `select … from v_carrier` → `ERROR: invalid input syntax for type numeric`. The view enforces **nothing** on write, and **one dirty row breaks the entire view for every reader.** | A5 |
| V3 | §4.4 `edit_event.op` includes `delete`; FK `object_id → objects(id)` | `delete from objects` → `ERROR: … violates foreign key constraint`. Hard delete is impossible; the only escape (`ON DELETE CASCADE`) would **erase the immutable audit trail.** `op='delete'` is unimplementable as drawn. | A6 |
| V4 | line 145 GIN on `properties` = "filter on any property" | With seqscan disabled: containment `@>` uses the GIN (Bitmap Index Scan); **range `>` and `ORDER BY` on a property both fall back to Seq Scan / Sort.** GIN cannot serve them. | C3 |
| V5 | §6 `open_escalation` `create` rule (no pkey given) vs §4.2 `pkey … not null` | `ERROR: null value in column "pkey" … violates not-null constraint`. **The worked example's create step fails.** | A3 |
| V6 | §6 `sla_status: { value_type: sla_status }` vs §4.1 `property_def.base_type not null` | `ERROR: null value in column "base_type" … violates not-null constraint`. **The worked config cannot be loaded into the worked schema.** | A4 |
| V7 | line 176/179 cardinality via partial index, "a new link type appears with zero schema change" | one_to_many requires a **per-type** partial unique index (works); a single *global* index **wrongly blocks legitimate many_to_many.** So every constrained link type needs its own DDL at load — **not** zero schema change. | C5 |
| V8 | §5 submission criteria = "server-enforced validation," step 4 | Two concurrent actions each passed a "max one open escalation" check under READ COMMITTED and both committed → **2 open escalations, no error** (write-skew). SERIALIZABLE correctly aborted one. **The spec never names an isolation level, so the validation it sells is not actually enforced.** | B3 |

---

## A. Won't run as written — the document contradicts itself mechanically

These are not "underspecified." They are wrong. Each was reproduced.

*In fairness:* §4 hedges that "DDL below is illustrative … trimmed for clarity" (line 82), which legitimately covers **A1** and **A2** — formatting-level slips with one-line fixes. It does **not** cover **A3–A6**: those are not the DDL being trimmed, they are the spec's *config* (§6) and its *schema* (§4) disagreeing with each other, and a typing claim that is false regardless of trimming. A3–A6 survive the hedge.

**A1 — Config DDL is in the wrong order.** `property_def` (§4.1, line 99) has `value_type text references value_type(id)`, but `value_type` is created seven lines below it (line 106). Run top-to-bottom → `relation "value_type" does not exist`. *Fix:* trivial reorder. *Why it matters anyway:* it's the first sign that the DDL was written to read well, not to execute — and the rest of the section was never run.

**A2 — The title index needs an extension the spec never creates.** Line 146 uses `gin_trgm_ops`, which only exists after `create extension pg_trgm`. As printed it errors. *Fix:* one line. *Tell:* same as A1 — illustrative, not executed.

**A3 — The flagship action creates an object with no primary key.** §6 `open_escalation` does `create: { object_type: escalation, properties: {...} }` with no `pkey`. But §4.2 declares `pkey text not null` with `unique(object_type, pkey)`. Reproduced: `null value in column "pkey" … violates not-null constraint`. **This is the central question.** Either the executor mints surrogate keys for action-created objects (then *what* — a UUID? a sequence? and how does re-running an idempotent action avoid duplicates without a natural key?), or every `create` rule must compute a `pkey` expression. The spec specifies neither. The one example it ships does not run.

**A4 — A value-typed property can't be loaded into the property table.** §6 writes `sla_status: { value_type: sla_status }` — no base type. §4.1 declares `base_type text not null`. Reproduced: NOT NULL violation. So the loader must *resolve* a property's `base_type` from its `value_type.base_type` before insert — a resolution step that is the loader's core job and is never described. As written, config and schema disagree about whether `base_type` is required.

**A5 — "Typed views" are a fiction; they enforce nothing and are fragile.** D5's selling point is that generated views "restore SQL ergonomics **and constraints**" (line 66) and that "the database enforces types" (line 149). Reproduced: the base table cheerfully stored `annual_spend: "not-a-number"`; the view's `(properties->>'annual_spend')::numeric` cast then threw **at read time**, taking down the whole-view query for every consumer. Two facts follow, both contra the spec: (a) the view is a **read projection** — it constrains no write; **all** typing lives in the app executor, and the DB is a bystander. (b) Because the cast runs per row at read time, a single bad row (from a bug, a migration, a direct write) **breaks the view for everyone** until manually repaired. The honest description is: "JSONB validated only by application code; views are convenience projections that fail closed on dirty data." That is a very different value proposition than "the database enforces types."

**A6 — `op='delete'` is unimplementable under the schema as drawn.** `edit_event.object_id` and `links.from_id/to_id` are `NOT NULL` FKs to `objects(id)`. Deleting an object is therefore blocked by its own history and its links (reproduced: FK violation). The only way to permit delete is `ON DELETE CASCADE`, which **destroys the immutable audit trail** the system exists to keep — violating MUST #2/#5 of the constraints. The spec lists `delete` as an op (line 190) but the data model makes object deletion mutually exclusive with keeping history. **Decision forced:** objects are *soft-deleted* (a `deleted_at` / tombstone, never physically removed), every read path filters tombstones, and links to tombstoned objects are handled explicitly. None of this is in the spec, and it ripples into the read API, traversal, and the §6 examples.

---

## B. Load-bearing for v1, named but unspecified

Not deferred — these sit inside M0–M5 and block them.

**B1 — The expression/binding language is undefined, and it is the product.** The spec calls the config format "the product surface for modeling" (line 27) and then, in §6, quietly invents an expression language it never specifies: `$circuit` (param ref), `$circuit.circuit_id` (property access on a resolved object), `$reason`, `$actor` (a reserved identity variable?), and rule verbs `update: { object:…, set:{…} }`, `create: { object_type:…, properties:{…} }`. What is the grammar? How are `$`-bindings scoped and resolved? What's the type discipline (is `$circuit.circuit_id` type-checked against `property_def` at load or at run?)? Null handling? Can a `set:` value be an expression, or only a literal? Can rules reference each other's outputs (the `create`d escalation's id, to then link it)? **This is the single largest gap.** It is also why the spec's claim that "D11 is the one call left to make" (§10) is false: **D10 and D12 — the rule/criteria/expression language — are the unresolved, hardest decisions**, and they're punted to "code-first, config sugar later." You cannot build M0 (the loader that validates this config) without specifying it, because the loader's whole job is to parse and type-check exactly this language.

**B2 — Ingestion (M4) directly contradicts the edits-only-via-actions invariant.** §5 is emphatic: the executor is "the **only** code path [that] writes to `objects`, `links`, or `edit_event`," enforced structurally because "the application service holds the only DB role with write access to those tables." Then M4 ingests CSVs/APIs **into object types** — i.e., writes `objects`. These cannot both be true. Either (a) ingestion *is* actions — then a 100k-row upload is 100k action runs, 100k+ `edit_event` rows, and you owe an answer on bulk atomicity, validation-per-row failure policy (reject row / reject load / quarantine), and audit-volume; or (b) ingestion is a **second privileged write path**, in which case the headline invariant ("edits only via actions") is already false in v1 and the "only DB role" enforcement story is wrong. The spec picks neither. This is the collision between the Data layer's "objects backed by data" MUST and the Kinetic layer's "edits only via actions" MUST, and resolving it is a real design decision, not a detail.

**B3 — No concurrency or isolation model; server-side validation isn't actually enforced.** Reproduced (V8): under READ COMMITTED (Postgres default), two concurrent `open_escalation` actions each evaluated a "max one open escalation per circuit" submission criterion, each saw zero, each inserted, both committed → invariant violated, **no error**. This is textbook write-skew, and it guts the central promise that submission criteria are "server-enforced." Any criterion that *reads* state to decide whether a write is allowed (most of them) is unsafe under the default isolation the spec implicitly assumes. Compounding it: `objects.version` exists (line 139) and is described as "bumped on each action," but **nothing ever checks it** — there is no optimistic-concurrency guard (`where version = $expected`), so two actions on the *same* object lost-update each other silently. **Decisions forced, none made:** isolation level (SERIALIZABLE with retry? explicit `SELECT … FOR UPDATE`? advisory locks per object?), and whether `version` is load-bearing for optimistic locking or just decoration.

**B4 — Object sets are a MUST and have no implementation.** The constraints list "object sets / saved queries — define, **name**, filter, and **reuse**" as a semantic-layer MUST. M1's demo covers ad-hoc filter/traverse, but the **saved/named/reusable** half — a table to persist a set definition, an API to name and recall it, whether a set is stored as a predicate or a materialized id list — appears nowhere. The read-API shape generally (REST? GraphQL? a filter DSL? — note this is *yet another* expression language, and it should share grammar with B1) is undefined.

**B5 — Identity and authentication are absent; the audit's trust root is undefined.** Authorization gate (1) is "session valid" and the audit's `actor` is `not null` — but **where does a session come from, and how is `actor` established and trusted?** There is no auth story: no login, no session store, no token, no mapping from request → `actor`. For a system whose entire value proposition is a trustworthy audit trail ("who did what"), the provenance of "who" is foundational and entirely missing. It can be thin for v1, but it must be *named* — and `actor` must be server-derived from an authenticated session, never client-supplied (the spec never says so, and the §6 `opened_by: $actor` makes it look like a config-level value).

**B6 — "Security travels with data" is wired into writes but not reads.** Invariant #4 (and Foundry's whole model) is row/object-level visibility enforced **everywhere data is read**. The spec's authorization decision (§5) gates **actions**; gate (4) checks `object_policy` for the object an action touches. But object sets, searches, and link traversals (M1, M5) must **also** filter every returned object through `object_policy` — and that read-path enforcement is never described. Worse, `object_policy.predicate jsonb` (line 206) is undefined: what's the predicate language (a third expression grammar?), and is it compiled into the SQL `WHERE` (fast, safe) or evaluated per-row in app code (N+1, and easy to forget on a new read path)? As written, security travels with *writes*, not with *data*. That's a different, weaker guarantee than the one promised.

**B7 — There is no story for changing the ontology once data exists — which undercuts the entire thesis.** The load-bearing promise is "standardize the engine now, adapt the config later" (everywhere, esp. §1, §7). But "adapt the config later" assumes config changes are safe and online. Once Bailey has data, they are not: tighten `sla_status`'s enum, retype `annual_spend`, or remove a property, and you must answer — what happens to **existing `objects.properties`** that now violate the new constraint (nothing validates data already at rest)? to the **generated view** whose cast now throws on historical rows (see A5)? to **`edit_event`** rows referencing a now-deleted property/type? The spec has no ontology-migration/versioning mechanism, no "validate existing data against new config" pass, no view-regeneration-with-dirty-data handling. This is the deepest hole, because the freedom to adapt config later — the reason Phase 1.5 exists as a thing you can finish now — is exactly what's unsupported the moment there's data to migrate.

**B8 — The function runtime is a black box, and "the edits API" is named but never defined.** §7 lists "the function runtime + **the edits API**" as fixed platform. §5 says complex logic is "a function in the one runtime" returning "either edits or a validation error." But: how is a function **registered** (config references `fn: onlyManagersMayEscalate` by string — what maps that string to code)? **Loaded** (in-process modules? hot-reloaded on config change across app instances?)? What is the **edit object's shape** a function returns (`{op, object_type, pkey?, properties}`?) — i.e., the "edits API" the spec promises and never draws? Does a function get a **transaction handle** so its reads are consistent with the write (essential for B3)? Is it **sandboxed / time-limited** (a function-backed action runs arbitrary TS in the backend process — author of functions == author of arbitrary backend code; trust model unstated)? M2 cannot be built on "a function in the one runtime."

---

## C. Challenged decisions and overstated claims

Where the verdict may even stand, but the stated reasoning is wrong or the claim oversells.

**C1 — "A config file, not a code branch" / "with no code written" is contradicted by the spec itself.** The thesis (line 22) and the §6 payoff ("Load that … with **no code written**", line 307) describe a world where Phase 2 is pure declarative config. But the very example uses `submission_criteria: [{ fn: onlyManagersMayEscalate }]` — a hand-written TypeScript function — and §7's right-hand "adapt later" column **itself lists** "the validation functions for complex criteria" (line 323) as a per-deployment deliverable. So Phase 2 is **config + TypeScript**, and any non-trivial action (anything past single-object literal sets) requires code. That's fine — but it means the boundary "leaks" by the spec's own §7 test the moment you need real validation, and the marketing line should be retired in favor of "config for the common case, typed functions for the rest" (which D10/D12 actually say — the headline just contradicts the body).

**C2 — D5's core justification is partly self-defeating.** Table-per-type is rejected because it "demand[s] a migration on every model change — fatal to a config-driven platform" (line 162). But the chosen design **also** requires the loader to run DDL on every model change: `CREATE OR REPLACE VIEW` per type (§4.2), a partial unique index **per constrained link type** (V7/C5), and — because GIN can't serve ranges/sort (V4/C3) — a **btree expression index per hot filterable/sortable property**. So "no per-type DDL" is not actually what's purchased. The real trade is narrower and worth stating honestly: **(a)** `ALTER TABLE ADD COLUMN` vs `CREATE VIEW` (both are loader-run DDL; neither is "no schema change"), and **(b)** where validation lives (app code, either way, since JSONB constrains nothing — A5). Given that, the spec should at least consider a middle design it dismisses: let the loader **promote a handful of hot properties to real typed columns** (real constraints, real range/sort indexes, real `NOT NULL`) while leaving the long tail in JSONB. That keeps "types as data" for the cold tail and recovers actual DB-enforced typing + fast queries for the few fields that need them — which is closer to what Foundry's object store actually does than an all-JSONB table is.

**C3 — "Filter on any property" overstates the GIN, and the search story (D8) is thin.** Reproduced (V4): the GIN on `properties` accelerates **equality/containment** (`@>`) only; range predicates and `ORDER BY` on a property fall back to sequential scan + sort. So "filter on any property" (line 145) is true for `status = 'red'` and false for `annual_spend > 1000` or `order by renewal_date` — the bread-and-butter of an operational tool. Each such field needs its own expression index (per-property DDL, see C2). Separately, D8 promises "full-text (`tsvector`/`pg_trgm`)" but the schema only trigram-indexes `title`; there is **no `tsvector` column, no full-text index over property content, no language/ranking choice.** Searching the *content* of objects (a reason, a note, a description) is unbuilt.

**C4 — D2's dual-use log is elegant but its reconstruction story is naïve, and delete breaks it.** Making `edit_event` simultaneously audit and version history is nice. But "what did this look like on March 1 = replay its edits to that timestamp" is **O(history)** per object and, for "the ontology as of March 1," O(all history) — with no snapshotting strategy, history-table partitioning, or retention. At "low-millions of objects" with frequent edits, `edit_event` becomes the largest table and reconstruction the slowest path, and the spec treats both as free. And per A6, the FK design makes object deletion incompatible with keeping that history at all. The idea is right; the operational design behind it is missing.

**C5 — D6's "zero schema change per link type" is false (reproduced), and link events don't fit the audit schema.** V7: a single global `unique(link_type, to_id)` wrongly forbids legitimate many-to-many, so cardinality **must** be a per-constrained-type partial index created at load — i.e., per-link-type DDL, contradicting line 179. Secondary problem: `edit_event` has a single `object_id` and `before/after jsonb`, but a `link`/`unlink` event is about a *triple* (`link_type, from_id, to_id`) with no natural single `object_id` or property diff. The audit schema can't cleanly represent the link operations it lists as ops (line 190).

---

## D. Deferred — but the seam is thinner than the spec claims

The spec's discipline is "everything deferred must be addable without rework." These have a seam, but it's narrower than advertised.

- **D-i Outbox is named, not designed.** §5 invokes "a small outbox table polled by a worker" for side effects. No schema, no delivery semantics (at-least-once ⇒ consumers must be idempotent — unstated), no retry/backoff, ordering, or dead-letter. If it's in the M2 write path (post-commit side effects), the table belongs in §4.
- **D-ii The lineage pointer is missing, so a MUST isn't reconstructable.** "Source → dataset → object → action → audit" is a MUST. But `objects` carries **no reference to the `dataset_load` that produced/updated it**, and `dataset_load` is referenced (line 199) yet **never DDL'd**. As drawn, you cannot trace an object back to its load — the lineage chain is broken at its first hop.
- **D-iii Audit growth has no plan.** One row per property change, unbounded, unpartitioned, no retention. See C4.
- **D-iv Config-load is the most privileged operation and has no authorization model.** Loading config can define an action that does anything; it is the keys to the kingdom. Yet the §5 authorization decision governs *running* actions, not *changing the ontology*. There is no "modeler/admin" role, no auth on the loader. The most dangerous operation in the system is ungoverned.
- **D-v Multi-instance realities are unaddressed.** If the app runs more than one process: the in-process function registry and any cached ontology must be invalidated across nodes on config reload (unspecified). And "the app holds the only **write** DB role" (§5) is in tension with that same role needing **DDL** rights (`CREATE VIEW`/`INDEX`) to load config — a privilege split the spec doesn't acknowledge.

---

## E. Smaller, still-real

- **`objects.title` denormalization drifts.** It mirrors `properties->>title_prop` (line 138) for fast display, but nothing keeps it in sync when that property changes via an action. The executor must resync it on every relevant write; unstated.
- **Operation taxonomy is undefined and unscoped.** `role_def.operations` shows `object:read` and `action:open_escalation`, but `object:read` is **global** — no way to grant read on carriers but not contracts. Real RBAC needs type scoping (`object:read:carrier`). The full operation vocabulary (create? link? delete? ingest? load-config?) is never enumerated.
- **Value-type constraint vocabulary is undefined.** Only `regex` and `enum` appear. Numbers need `min`/`max`, strings `length`, dates ranges. The constraint kinds the validator must support aren't listed.
- **`enum` is conflated.** It's both a `base_type` value and a `value_type` constraint shape. A bare `{type: enum}` has nowhere to carry its members. Pick one representation.
- **The escalation example contradicts "links are first-class."** §6 stores `circuit_id` as a bare property on the escalation rather than creating a `circuit → escalation` link — and no such link type is even defined. The flagship example models a relationship as a denormalized foreign value, the exact anti-pattern the semantic layer exists to replace.
- **UUIDv4 random PKs** as the clustered key invite index write-amplification under insert-heavy ingest at "low-millions"; consider UUIDv7/ULID. Minor.
- **No acceptance criteria or performance targets per milestone** ("fast enough" is asserted; no p95, no concrete row/throughput numbers). And M5's "thin UI" hides real work: auto-generated action forms need a param-type → control mapping, and object-typed params (line 292) need a searchable object-picker over the object set. "Thin" is doing a lot of lifting.

---

## The minimum to resolve before M0 starts

Most of the above can be sequenced into the milestones. Six cannot — they are prerequisites because M0/M1/M2 are defined in terms of them:

1. **The config expression/binding + rules language (B1)** — M0's loader is precisely the thing that parses and type-checks it. Specify grammar, scoping, type discipline, and how `create` rules mint `pkey` (A3) and link their outputs (E/escalation).
2. **Ingestion's relationship to the edits-only invariant (B2)** — decide whether ingestion is actions or a sanctioned second write path, before the invariant is baked into M2's enforcement.
3. **Isolation & concurrency model (B3)** — pick SERIALIZABLE-with-retry or explicit locking, and decide whether `version` is a real optimistic-lock; submission criteria are not "server-enforced" until this exists.
4. **Soft-delete + audit reconciliation (A6)** — tombstones, read-path filtering, link handling. Touches the schema and every read.
5. **Identity → `actor` (B5)** — even a thin, server-derived session, named now, because the audit trail's meaning depends on it.
6. **Ontology-change-with-data (B7)** — at least a stated policy (e.g., "config changes are validated against data at rest; incompatible changes require a migration action"), or the central "adapt later" thesis is unfunded.

Everything in C, D, and E can be resolved inside the milestones. Items in A are one-line fixes *except* A3, A5, and A6, which are design decisions wearing the costume of typos.

---

## Repro appendix

- **Environment:** PostgreSQL 18.4 (aarch64), userspace install via conda-forge, default `postgresql.conf` (so READ COMMITTED is the default isolation, as any vanilla deployment would be).
- **Schema:** built **verbatim** from blueprint §4.1–§4.5 and the §4.2 generated view; the only deviation was reordering `value_type` before `property_def` so the script would run at all (that reorder *is* finding A1).
- **Procedure:** loaded the schema; issued line 146's index as printed (V1); inserted via the §6 worked example's own shapes (V5, V6); inserted a dirty JSONB value and read the typed view (V2); attempted object deletion with history+links present (V3); seeded 5,000 rows and read `EXPLAIN` plans with `enable_seqscan=off` to isolate index capability (V4); tested cardinality with global vs per-type partial indexes (V7); and ran two concurrent transactions through a read-then-write submission criterion under READ COMMITTED and again under SERIALIZABLE (V8).
- Every `ERROR:` and `QUERY PLAN` quoted in the evidence table is a literal server response, not a paraphrase.

---

## Sources & cross-references

- `Spec/SPEC_Foundry-Clone_Build-Blueprint.md` — the document audited (line numbers cited throughout).
- `Spec/SPEC_Foundry-Clone_Design-Constraints.md` — the MUST/DROP/OPEN constraints and D1–D15 register the blueprint resolves; the invariants this audit checks the blueprint against.
- `Palantir-Foundry-Conceptual-Map.md` — §4 (the Ontology), §8 (the irreducible core): the promises the implementation must keep.
