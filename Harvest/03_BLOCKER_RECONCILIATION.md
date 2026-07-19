# 03 — Blocker Reconciliation

> For each pre-M0 blocker (`SPEC_Foundry-Clone_Spec-Audit.md`) and the related defects: **what OpenFoundry actually does** (path:line, VERIFIED = I/we read the code, REPORTED = only docs say so), whether it **confirms / improves-on / contradicts / does-not-help** our brainstorm leaning, and the **final lean answer** for the wedge.
>
> **The through-line, stated up front (the inversion):** on the six hard blockers OpenFoundry is **not ahead of us**. It *punts* (B1, B7), *shares our gap* (B3), or is *actively worse* (A6, and the un-wired + faked audit). The genuine harvest is narrow and concrete — schema *shapes* and the identity→actor wiring — not blocker solutions. Every negative below was put to an adversarial skeptic that tried to refute it by searching the whole repo; **all six held (refuted = 0)**.

---

## B1 — Expression / rules language → **OpenFoundry has none; our CEL leaning stands**

**What OpenFoundry does (VERIFIED).** There is no embedded expression DSL anywhere. `rg -ilw 'cel|pratt|lexer|tokenizer|interpreter|ast'` over `services/ontology-service` + `libs` returns nothing (only false positives like "at least" in a doc comment). Action rules are a **fixed 5-variant enum + hardcoded Rust**: `actions.rs` `validate_action_definition` does `match operation_kind { … }` and deserializes `config` into fixed structs (`UpdateObjectActionConfig`, `CreateLinkActionConfig`); a mapping's value is a literal JSON `Value`, never an evaluated expression (`actions.rs` L455–528, VERIFIED). Pipeline "transforms" dispatch on a `transform_type` string to **run arbitrary SQL / Python (pyo3) / WASM (wasmtime)** (`pipeline-service/src/domain/engine/mod.rs` L93–217, VERIFIED) — full host runtimes invoked via JSON config, *not* a sandboxed expression language. Cargo.lock's `pest`/`nom` are transitive deps of `json5`/`config`, not a rule engine (VERIFIED).

**Reconciliation: confirms our leaning (it offers nothing to copy).** OpenFoundry punts exactly where we must decide; it neither helps nor refutes CEL.

**Final lean answer.** **Adopt CEL** for every boolean — submission criteria, row policies, value-type constraints — one language across the system. `[verified]`: `cel-js` evaluates `'carrier_manager' in actor.roles` → manager `true` / viewer `false`, `size(params.reason) > 0`, `circuit.status != 'red'` (`repro/cel_check.mjs`). Caveat: `cel-js` lacks the `exists` macro — use the `in` operator for enum checks, or `@marcbachmann/cel-js` for full-spec/faster. For one workflow even a handful of typed TS predicates would do; CEL is the lean choice that keeps "config is the product surface" true.

---

## B2 — Ingestion vs. edits-only → **OpenFoundry doesn't validate the two-layer model; it's a single blob, written two ungoverned ways**

**What OpenFoundry does (VERIFIED).** `object_instances.properties` is **one JSONB blob** (`initial_ontology.sql` L46–53). It is written by *two unrelated* paths, neither governed: (a) plain CRUD `create_object` inserts the raw `properties` with **zero validation** (`objects.rs` L34–60, VERIFIED), and (b) the action executor's `UpdateObject` merges the action's patch into the current properties **in memory** (`actions.rs` L1027–1031) then rewrites the **whole** column with `UPDATE … SET properties=$2` (L1033, VERIFIED). That in-memory patch-merge is *not* the thing we mean: there is **no datasource-vs-edit layer separation**, **no** per-source conflict-resolution strategy, and no `update_object` route at all (`main.rs` wires only POST/GET/GET/DELETE; VERIFIED via B7 skeptic). So OpenFoundry does **not** confirm our two-layer model; that idea comes from Foundry-proper's docs (brainstorm §1), not from this repo.

**Reconciliation: does-not-help (the idea is ours, not theirs).** Said plainly: OpenFoundry has the exact contradiction our audit feared (two writers into one blob) and simply doesn't notice it, because it doesn't claim "edits only via actions."

**Final lean answer.** Keep the **two-layer `datasource ⊕ edits` merge** (edits win, per-property) from the brainstorm — it dissolves B2, makes ingestion a sanctioned layer rather than an invariant violation, and yields lineage-per-value for free. `[verified]`: in `02`'s schema, `properties` is a generated column `datasource || edits`; an action edit flips `status` to red while `datasource.status` stays `amber` for future refreshes (`repro` §4).

---

## B3 — Concurrency / isolation → **OpenFoundry shares our gap exactly, and offers no fix**

**What OpenFoundry does (VERIFIED, plus adversarial skeptic).** `execute_action` runs each write as a **bare auto-commit statement on the pool** — `rg 'begin|transaction|FOR UPDATE|advisory|SERIALIZABLE|version' actions.rs` → nothing. `UpdateObject` is a textbook lost-update: `plan_action` `SELECT`s the target unlocked (`actions.rs` L550), then `execute_action` rewrites the whole properties column with `UPDATE … SET properties=$2 WHERE id=$1` — **no `WHERE version=…`, no `xmin` guard, no transaction** (L1033–1043). `object_instances` has **no `version` column** (`initial_ontology.sql`, VERIFIED). Tellingly, the codebase *knows* how to use transactions — `app-builder/.../publish.rs:46` and `auth-service/.../role_mgmt.rs:256` use `state.db.begin()` — but the action path deliberately doesn't (skeptic, VERIFIED). Multi-statement `InvokeFunction` (patch + link + delete) is therefore also non-atomic.

**Reconciliation: confirms the gap (shares it; worse, since it lacks even a `version` column).** Our audit reproduced this exact write-skew on PG 18.4 under READ COMMITTED.

**Final lean answer.** Run each action in **one transaction at SERIALIZABLE with a bounded retry** on `40001` (3–5 attempts), **plus** an optimistic `version` guard (`UPDATE … WHERE id=? AND version=?`). At Bailey's scale retry cost is negligible. `[verified]`: in `02`'s schema a stale `version` update affects **0 rows** (`repro` §6); SERIALIZABLE handles cross-row write-skew (already reproduced in the audit). This is the difference between submission criteria being *enforced* vs. merely *advisory*.

---

## B5 — Identity → actor → **OpenFoundry hands us the field shape and the JWT wiring; provenance is thin but the pattern is right**

**What OpenFoundry does (VERIFIED).** Identity flows JWT → `Claims { sub: Uuid, email, name, roles, permissions, org_id, attributes, … }` (`claims.rs` L7–41) → `RlsContext { user_id, org_id, roles, permissions, attributes }` via `From<&Claims>` (`row_level_security.rs` L9–27). JWT is **HS256, single shared secret** (`jwt.rs`, VERIFIED). The audit record (`audit_event.rs` L78–101) is a genuinely good *field shape*: `actor: String`, `action`, `resource_type/resource_id`, `status` (success/failure/**denied**), `severity`, `classification`, `metadata`, `occurred_at`. **But** the only wired emitter is the gateway, which stamps `actor = "system:gateway"` — *not* the JWT user — fire-and-forget over NATS, dropped if NATS is down (`gateway/.../audit.rs` L63–114, VERIFIED); and `ontology-service` emits **no** audit at all. So "who did what" is, in practice, "the gateway forwarded a POST."

**Reconciliation: confirms our B5 direction and hands us a concrete field shape — while showing the anti-pattern to avoid** (anonymous, async, best-effort provenance).

**Final lean answer.** Map onto **Supabase Auth**: `actor`/`opened_by` ← `auth.uid()` / verified JWT `claims.sub`, **server-derived, never client-supplied**. Borrow the `audit_event` field shape verbatim (actor/action/resource/status/severity/metadata; keep the `denied` status — auditing refused attempts is valuable). Write the audit row **in the same transaction** as the domain write (an RPC or trigger), not via best-effort async. Supabase's asymmetric JWKS + `auth.uid()` is strictly better than OpenFoundry's single HS256 secret.

---

## B6 — Security travels with data → **aspired-to but UNBUILT in OpenFoundry; Supabase RLS is materially ahead**

**What OpenFoundry does (VERIFIED, three ways).** (1) The query-engine RLS hook is a **5-line "Future" comment** with no code (`query-engine/src/optimizer_rules.rs`, VERIFIED — I read all 5 lines). (2) The `RlsContext.org_filter`/`owner_or_org_filter` SQL-fragment helpers are **never called by any service** — the only repo-wide reference is the `pub mod` declaration (B6-rls-helper-unused, VERIFIED). (3) There *is* a working ABAC evaluator (`auth-service/.../abac.rs`) that renders a `row_filter` by `{{subject.x}}` token-substitution — but `policy_mgmt.rs` `evaluate_policy` just **returns it to the API caller as JSON**; it is *never compiled into a data query's WHERE* (VERIFIED). Both the helper and the ABAC renderer build SQL by **string interpolation** (`format!("{col} = '{org}'")`, `{{token}}` replace) — injection-shaped, mitigated only by UUID typing. ROADMAP L126 marks "RBAC — row-level security" done; the code contradicts it.

**Reconciliation: confirms our leaning — our "compile predicates into WHERE" is the right idea, and OpenFoundry proves it's hard precisely by leaving it unbuilt.** Our brainstorm's Hasura-style leaning is unrefuted; OpenFoundry neither helps nor refutes the mechanism, but it does warn us off string-templated SQL.

**Final lean answer.** **Compile row policies (CEL/JSON) into a parameterized `WHERE`** on every read path (object sets, traversals), **and** enable **Supabase RLS** as an in-DB backstop keyed off the JWT — real, always-enforced, no N+1. Always parameterize; never interpolate values. `[verified]`: `02`'s repro compiles `region == actor.region` to `properties->>'region' = $1` and a west viewer sees only the west carrier.

---

## B7 — Ontology change once data exists → **OpenFoundry has no answer; this remains the deepest hole, and ours**

**What OpenFoundry does (VERIFIED, adversarial skeptic).** Nothing. Schema is `CREATE TABLE IF NOT EXISTS` with **no version/revision columns** on `object_types`/`properties`/`object_instances`, and **no ontology-version table** (`initial_ontology.sql`, VERIFIED). `validation_rules` is **dead data** — referenced only in the migration and three struct fields, never read by any validator (`type_system.rs` checks base type only; VERIFIED). Worse, property definitions can't even be *changed* via the API: `CreatePropertyRequest`/`UpdatePropertyRequest` exist but are wired to **no route** (skeptic, VERIFIED). Version/history tables exist for *other* domains (`dataset_versions`, `app_versions`, `ml_model_versions`) but never for the ontology. No re-validation job, no trigger, no `of.ontology` event consumer.

**Reconciliation: does-not-help (it punts).** OpenFoundry gives no answer; B7 stays ours.

**Final lean answer.** B7 is genuinely ours to design, but the **two-layer model makes it easier** (brainstorm §145): on a config change, re-validate the **edit** layer against the new constraint; datasource values that now violate it are **quarantined** (flagged, not silently broken), not erased. Minimum policy for the wedge: config changes are validated against data at rest; incompatible changes require an explicit migration action; the generated `CHECK`/columns are rebuilt with a dirty-row report. At Bailey's scale this is small; it must just be *named* before M0.

---

## A3 — Create needs a primary key → **OpenFoundry confirms it (and can't create objects via actions at all)**

**What OpenFoundry does (VERIFIED).** Object creation requires no governed key because **actions can't create objects** — `ActionPlan` has variants `UpdateObject, CreateLink, DeleteObject, InvokeFunction, InvokeWebhook` and **no `CreateObject`** (`actions.rs` L73–99, VERIFIED). Plain `create_object` mints a `Uuid::now_v7()` id and stores a raw blob with no business PK (`objects.rs`, VERIFIED). Foundry-proper, by contrast, *requires* a PK on create (brainstorm §8).

**Reconciliation: confirms the defect and the fix.** Our pkey-less `create` rule (blueprint §6) was a real bug; PK-on-create is mandatory.

**Final lean answer.** Every `create` rule computes a `pkey` (e.g. `'ESC-' + uuid()`), enforced by `unique(object_type, pkey)`. `[verified]`: `repro` §5 mints `ESC-…` and links the escalation to its circuit as a first-class link.

---

## A5 — "Typed views enforce types" → **OpenFoundry confirms the fiction; we make the DB enforce shape on write**

**What OpenFoundry does (VERIFIED).** `object_instances.properties` is unconstrained JSONB; `create_object` writes it with no validation; `property_type` is free `TEXT` with no `CHECK`; `validation_rules` is never read (VERIFIED). So OpenFoundry's "typed ontology" (ROADMAP "type validation ✅") is, at the instance level, a JSONB bag — exactly the A5 fiction the audit exposed in our blueprint's read-only views.

**Reconciliation: confirms by counterexample.** Both the blueprint's views and OpenFoundry's JSONB enforce nothing on write.

**Final lean answer.** Per-type **`CHECK` (or `pg_jsonschema` on Supabase) so the DB rejects bad shape on write**, plus generated typed columns for hot fields. `[verified]`: `repro` §3 rejects `annual_spend:"not-a-number"` and `sla_status:"purple"` at write time.

---

## A6 — Soft-delete vs. audit → **OpenFoundry is actively worse; it hard-deletes and cascades, erasing everything**

**What OpenFoundry does (VERIFIED, adversarial skeptic).** Two hard-delete sites — `DeleteObject` runs `DELETE FROM object_instances WHERE id=$1` (`actions.rs` L1095), and `InvokeFunction` can hard-delete based on an **external HTTP response** (L1175) — plus the plain `delete_object` handler (`objects.rs` L118). **Every FK is `ON DELETE CASCADE`** (`initial_ontology.sql`, VERIFIED), so deleting an object wipes its links, and deleting an object_type wipes all its instances. **No `deleted_at`/tombstone anywhere** in the repo (skeptic swept Rust/SQL/proto, VERIFIED). No edit history to lose because none is kept (A6 + the un-wired audit compound).

**Reconciliation: confirms by counterexample — OpenFoundry does the exact thing our audit warned against.** Our tombstone design is validated as the right call.

**Final lean answer.** **Never physically delete.** `deleted_at` tombstone; a delete is an `edit_event`; every read filters tombstones; links to tombstoned objects handled explicitly. The `edit_event.object_id` FK is then **safe** (objects always exist), dissolving the blueprint's circular A6 problem. `[verified]`: `repro` §7 tombstones a carrier — it vanishes from reads while its `edit_event` history survives.

---

## Scorecard

| Blocker | OpenFoundry's posture | Our position relative to it |
|---|---|---|
| B1 expression language | **Punts** (none; hardcoded Rust) | Ahead — adopt CEL `[verified]` |
| B2 ingestion vs edits | **Doesn't model it** (one blob, 2 writers) | Ahead — two-layer merge `[verified]` |
| B3 concurrency | **Shares the gap** (no txn/version) | Ahead — SERIALIZABLE + version `[verified]` |
| B5 identity→actor | **Right shape, thin wiring** | Confirmed — map to Supabase Auth; borrow field shape |
| B6 read-side security | **Aspired-to, UNBUILT** (×3) | Ahead — compile WHERE + Supabase RLS `[verified]` |
| B7 ontology change | **Punts** (no version, dead `validation_rules`) | Ours — two-layer eases it; must be named |
| A3 PK on create | **Confirms** (can't create via actions at all) | Fixed `[verified]` |
| A5 typed-shape enforcement | **Confirms the fiction** (unvalidated JSONB) | Fixed — CHECK/pg_jsonschema `[verified]` |
| A6 soft-delete | **Actively worse** (hard delete + cascade) | Fixed — tombstones `[verified]` |

**Net:** OpenFoundry validates our *direction* on every blocker and *solves* none of them. Lead with that honesty.
