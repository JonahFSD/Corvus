# 00 — Harvest Digest

> What's worth stealing from OpenFoundry for Bailey's one-workflow wedge (TS + Supabase/Postgres), ranked by value — and, just as important, what *isn't there*. Every claim is cited and marked **VERIFIED** (read the code) / **REPORTED** (only docs say so). `[verified]` = we *ran* it on this machine (PostgreSQL 18 via PGlite, + cel-js). Full detail in `01`–`06`; reproductions in `Harvest/repro/`.

## The punchline

**OpenFoundry's value to us is its data-model *shapes* and its identity *wiring* — not its solutions to our hard problems, because it doesn't have them.** It is a fast, agent-built, breadth-first skeleton: a 5-table ontology and a real action-validation contract sit next to **322 zero-byte stub files** and a ROADMAP whose "✅ Done" markers are frequently untrue. Take the handful of concrete shapes below; build everything load-bearing yourself.

**The inversion (lead with this honesty).** On the six pre-M0 blockers, OpenFoundry is **behind or level with us**, never ahead:

- **It punts** where we must decide: no expression language at all (B1), and no story for changing the ontology once data exists (B7).
- **It shares our gap:** the action write path has **no transaction, no isolation, no version guard** (B3) — the exact write-skew our audit reproduced.
- **It is actively worse on the things that matter for a system of record:** the kinetic core **writes objects without recording any audit/edit event** (`rg audit services/ontology-service/src` → nothing, VERIFIED); it **hard-deletes with `ON DELETE CASCADE` everywhere** and keeps no tombstone (VERIFIED); and its advertised **"immutable hash-chained" audit is a `format!` string, not a hash** (VERIFIED). Read-side row security is a 5-line "Future" TODO (VERIFIED).

So our spec chain isn't behind a reference implementation — it's **ahead of one.** That's the most important finding.

## Top ideas to steal (ranked)

| # | What OpenFoundry does (cited) | Why it's good | Lean wedge version (TS + Supabase) |
|---|---|---|---|
| 1 | **Objects = system columns + one `JSONB` blob**, types-as-data, no per-type tables (`object_instances`, `initial_ontology.sql` L46-53, **VERIFIED**) | Lets new object types appear with no DDL — the metadata-driven core | Keep it, but split into **`datasource ⊕ edits`** + generated typed columns for hot fields + per-type `CHECK` (`02` §2). `[verified]` |
| 2 | **One unified `link_instances` edge table** for all relationships (`initial_ontology.sql` L55-63, **VERIFIED**) | One mechanism covers every relationship; new link types need no schema | Keep it; **add** the unique-on-triple and per-type partial index for cardinality OF lacks (`02` §3) |
| 3 | **Action = `input_schema` (params) + `config` (operation) split**, with a **validate → preview(dry-run) → execute** contract returning `{valid, errors[], preview}` (`action_types.sql`; `actions.rs` `validate_action`/`plan_action` L959/L534, **VERIFIED**) | Exactly the submission-criteria + dry-run UX we want; clean config vocabulary | Mirror in `action_type.spec` JSON; criteria are **CEL** (`01`). The contract is the harvest; the write path is not |
| 4 | **`audit_event` field shape**: `actor/action/resource_type/resource_id/status(success\|failure\|denied)/severity/classification/metadata/occurred_at` (`audit_event.rs` L78-101, **VERIFIED**) | A well-shaped, governance-grade audit row; `denied` status is a nice touch | One append-only `edit_event` table with this shape (`02` §4). Do **not** copy its fake hash chain (#below) |
| 5 | **JWT → `Claims` → `RlsContext` → `actor`** server-derived identity (`claims.rs`, `row_level_security.rs`, **VERIFIED**) | The right provenance pattern: actor comes from the verified token, not the client | Map onto **Supabase Auth**: `actor ← auth.uid()`/JWT `sub`; roles/permissions/org as claims (`02` §6, `03` B5) |
| 6 | **Concrete enum vocabularies** — 9 property types, 4 cardinalities, 5 operation kinds (`type_system.rs` L3/L42 + `action_type.rs`, **VERIFIED**) | Saves us bikeshedding; battle-named values | Adopt the operation-kind + cardinality sets; alias scalars for Postgres (`text`←`string`, etc.) in `01` |
| 7 | **`ObjectType`/`Property`/`LinkType` proto naming** (`proto/ontology/ontology.proto`, **VERIFIED**) | Consistent vocabulary for the YAML config surface | Borrow field names (`primary_key_property`, `display_name`, `default_value`, `validation_rules`) |
| 8 | **`tenant.rs` derives tier/quota from JWT attributes** (`tenant.rs` L54-114, **VERIFIED**) | Clean claim-driven scoping pattern (if we ever multi-tenant) | Defer; if needed, a plan/quota table keyed off the JWT (the wedge is single-org) |
| 9 | **Typed front-end client pattern** — a `fetch` wrapper with Bearer auth + per-feature API modules (`apps/web/src/lib/api/client.ts`, SvelteKit, **VERIFIED**) | Proof a thin typed client over the ontology is feasible | Reference only; we'll likely use Supabase's generated types + React/Next |
| 10 | **`.env.example` as a "what NOT to carry" list** (Postgres+Redis+NATS+S3+Meili+Qdrant, **VERIFIED**) | Names the heavy stack explicitly | Collapse all six to **one Supabase** (`04`) |

## Where OpenFoundry is *behind* us (do not copy — build it right)

- **Un-wired audit** — action writes record nothing (`rg audit services/ontology-service/src` → ∅, **VERIFIED**). Our transactional `edit_event` is a genuine differentiator. (`05` A4)
- **Faked tamper-evidence** — `chain_hash` is `format!("AUD-{seq}-{8 chars of prev}-{8 chars of service-action}")`; no sha2, no `verify_chain`, "append-only" = `CHECK(sequence>0)` only (`immutable_log.rs`, **VERIFIED**). Use real `sha256(prev‖row)` + revoked UPDATE/DELETE. (`05` A5)
- **No version guard / no transaction** in `execute_action` (**VERIFIED**) → lost updates. Use SERIALIZABLE + `version` (`02` §2/§4). `[verified]`
- **Hard delete + cascade**, no tombstone (**VERIFIED**) → history erased. Use `deleted_at` + delete-is-an-event (`02`). `[verified]`
- **Read-side security unbuilt** — optimizer RLS is a TODO comment; the `org_filter` helper is dead code; ABAC `row_filter` is returned to callers, not applied; all SQL built by string interpolation (**VERIFIED**). Compile to **parameterized** WHERE + Supabase RLS. (`03` B6) `[verified]`

## Where OpenFoundry simply doesn't help (the blockers stay ours)

- **B1 (expression language)** — none exists; CEL stands on its own (**VERIFIED**). `[verified]`
- **B7 (ontology change once data exists)** — no version table, `validation_rules` is dead data, property defs can't even be edited via the API (**VERIFIED**). The deepest hole, still ours; the two-layer model eases it.
- **B2 (ingestion vs edits)** — OpenFoundry doesn't model it (one blob, two ungoverned writers); the two-layer merge is *our* idea from Foundry-proper, not validated here.

## What we proved, not just asserted

- The **wedge schema runs clean on PostgreSQL 18 and fixes the audit's 8 reproduced defects** the blueprint's §4 failed — A1, A2, A3, A4, A5, A6, C3, B3 — **and additionally implements the B2/B6 design resolutions** (`repro/wedge_schema_repro.mjs`, *ALL CHECKS PASSED*, exit 0).
- **CEL evaluates every criterion the config actually ships** — 17 assertions on the macro-complete `@marcbachmann/cel-js` (`repro/cel_check.mjs`, exit 0; the script fails nonzero on any miss). Value-type regex/range constraints compile to SQL `CHECK`, not runtime CEL.
- **All 6 load-bearing negatives survived an adversarial skeptic** that tried to refute each by searching the whole repo (refuted = 0).

## Read next
`01` (the config to build from) · `02` (the proven schema) · `03` (blocker-by-blocker) · `04` (what to ignore) · `05` (traps) · `06` (which files to read).

*Sourcing: OpenFoundry is Apache-2.0 (`Cargo.toml` L47, **VERIFIED**) — reuse is permitted with attribution, but we reimplement clean (Rust→TS won't drop in) and cite path:line for provenance. The empty `LICENSE` (0 bytes, **VERIFIED**) is flagged in `05` A1.*
