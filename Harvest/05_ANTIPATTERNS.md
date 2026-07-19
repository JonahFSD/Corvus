# 05 — Antipatterns (things in OpenFoundry *not* to copy)

> This repo was built fast and largely by agents. README/ROADMAP routinely overstate the code. Every item below is **VERIFIED against code**, with the `rg`/read that proves it. Read this as "the traps," and as the honest counterweight to the harvest: where OpenFoundry looks finished but isn't.

---

## A1 — The empty `LICENSE` (the legal/provenance trap)

`LICENSE` is **0 bytes** (`wc -c LICENSE` → `0`, VERIFIED) while Apache-2.0 is asserted in `Cargo.toml` L47 (`license = "Apache-2.0"`), root `package.json` L6, and README L10 (badge) + L493 (prose). So the canonical grant text is **missing**: "stated Apache-2.0 but no LICENSE body" is a genuine ambiguity. **Don't** treat the badge as the grant. We reimplement clean (stack-fit) and cite for provenance, so we never rely on it — but resolve this in writing before any verbatim copy. *And for our own repo: ship an actual LICENSE file.*

## A2 — 0-byte stub files masquerading as features (322 of them)

`find . -type f -size 0 -not -path './.git/*' | wc -l` → **322** (VERIFIED). ~120 are `.rs`. The empties cluster in the **most-advertised** capabilities:

- **Ontology:** `models/{constraint,interface}.rs`, `domain/{graph,indexer,sync,time_series}.rs`, `domain/search/{fulltext,semantic,mod}.rs`, `handlers/{search,bulk}.rs` — **all 0 bytes**, and **not even declared** in their `mod.rs` (`domain/mod.rs` exports only `type_system`; VERIFIED). So search, graph traversal, indexing, interfaces, value-type constraints, bulk, time-series are *dead, uncompiled placeholders*.
- **Connectors:** `data-connector/.../{snowflake,bigquery,salesforce,kafka,oracle}.rs` — 0 bytes.
- **ML / pipeline:** `ml-service/.../feature_store/*`, `serving/*`, `training/*`; `pipeline-service/.../engine/{datafusion_rt,polars_rt,python_rt,wasm_sandbox}.rs` — 0 bytes.

**Trap:** never assume a capability exists because a file/dir is named for it. `wc -c` first.

## A3 — ROADMAP claims contradicted by code (treat ROADMAP as marketing)

- **"Ontology ✅ Done … type validation"** (ROADMAP L42/L50/L99) vs. `create_object` inserts the raw `properties` blob with **zero validation** (`objects.rs` L34–60, VERIFIED); the type system is only invoked inside the action path, and even there checks **base type only**, never `validation_rules` (`type_system.rs`, VERIFIED).
- **"Code search — Tantivy-indexed full-text"** (ROADMAP L273) vs. **no `tantivy` dependency anywhere** (`rg -l tantivy --type toml` → nothing); the real impl is a lowercased `String::contains` substring scan (`code-repo-service/.../git/files.rs` L38–53, VERIFIED). `.env.example` wires Meilisearch + Qdrant but **no service imports them**.
- **"Protobuf generation — buf pipeline generating Rust + TS clients ✅"** (ROADMAP L81) vs. both codegen output dirs (`libs/proto-gen/src`, `apps/web/src/lib/api/gen`) are **missing**, **38 of 53** `.proto` files are 0 bytes (only 15 non-empty), and **no `build.rs` exists** — codegen never ran (TC-6, VERIFIED). The Rust models are the de-facto source of truth, not proto.

## A4 — The action write path writes **without auditing** (the headline gap)

`rg -n 'audit|emit|AuditEvent|edit_event|EditEvent' services/ontology-service/src` → **zero matches** (VERIFIED, by me and the adversarial skeptic). `execute_action` mutates `object_instances`/`link_instances` and records **no** who/what/before→after. `ontology-service`'s `Cargo.toml` *depends on* `event-bus` and `auth-middleware`, yet `rg 'event_bus|publish|nats|emit' services/ontology-service/src` → nothing — the deps are unused on the write path. For a system whose whole pitch is a trustworthy operational record, the kinetic core keeps no history. **Our `edit_event` design is ahead of theirs; do not copy this silence.**

## A5 — The audit "hash chain" is a **label, not a hash** (faked tamper-evidence)

The `audit_event` *field shape* is good and harvestable (actor/action/resource/status/severity/metadata — `audit_event.rs` L78–101, VERIFIED). But the integrity mechanism is fake. `immutable_log.rs` (VERIFIED):

```rust
pub fn chain_hash(sequence, previous_hash, source_service, action) -> String {
  format!("AUD-{sequence:08x}-{}-{}", normalize(previous_hash), normalize(&format!("{source_service}-{action}")))
}
fn normalize(v) -> String { v.chars().filter(|c| c.is_ascii_alphanumeric()).take(8).collect().to_uppercase() }
```

It is a **format string**: no `sha2`/`hmac`, it covers only `sequence + 8 chars of prev + 8 chars of "service-action"` — **not** actor, resource, status, metadata, or timestamps. There is **no `verify_chain`** anywhere. "Append-only" is only `CHECK (sequence > 0)` (`audit_foundation.sql`); UPDATE/DELETE are **not** revoked, so rows stay mutable. The genesis row literally reads `AUD-00000001-GENESIS-GATEWAYR`. **Trap:** do not advertise this as security. If you want tamper-evidence, use a real `sha256(prev_hash || canonical(row))` (we do, optionally, in `02` §4) — and on Supabase revoke UPDATE/DELETE on the audit table.

## A6 — Only the gateway emits audit, and it stamps `actor = "system:gateway"`

The single wired emitter (`gateway/.../audit.rs` L63–114, VERIFIED) publishes one event per proxied request with `actor: "system:gateway"` (**not** the JWT user), `subject_id: None`, fire-and-forget over NATS, **silently dropped if `NATS_URL` is unset**. So an object edit appears, at best, as a generic `POST /api/v1/ontology 200` with no object id, no diff, no real actor. **Trap:** anonymous + async + best-effort provenance is not provenance. Derive `actor` server-side from `auth.uid()` and write the audit row in the *same transaction* as the write.

## A7 — Hard delete + `ON DELETE CASCADE` everywhere (history-erasing by construction)

**Every** FK in `initial_ontology.sql` is `ON DELETE CASCADE` (VERIFIED): deleting an object_type cascades to its properties, link_types, action_types, and instances; deleting an object cascades to its links. Deletes are unconditional `DELETE FROM object_instances` at **two** sites (`actions.rs` L1095 direct; L1175 driven by an **external HTTP response**) plus the plain handler. No `deleted_at`/tombstone exists anywhere (skeptic swept Rust/SQL/proto, VERIFIED). An accidental object_type delete irreversibly wipes all instances and edges. **Trap:** combined with A4, deletion erases data *and* leaves no trace. Use tombstones (we do, `02` §2).

## A8 — Cardinality stored but unenforced; links untyped and dup-able

`link_types.cardinality` is plain `TEXT DEFAULT 'many_to_many'` with **no CHECK** (`initial_ontology.sql`, VERIFIED); `validate_cardinality` only checks the *label* string is valid, never that instances obey it (`type_system.rs`, VERIFIED). `link_instances` has **no unique** on `(link_type_id, source, target)` → duplicate edges allowed, and source/target are **not** constrained to match the link_type's declared `source_type_id`/`target_type_id` (no trigger) → type-mismatched edges are possible at the DB level (ONT-05, VERIFIED). **Trap:** "we have cardinality" is a column, not a guarantee. Back `one_to_*` with a partial unique index (we do, `02` §3).

## A9 — Security helpers that are dead, and SQL built by string interpolation

Two compounding traps in `auth-middleware`/`auth-service` (VERIFIED):

- The `RlsContext.org_filter`/`owner_or_org_filter` helpers and the query-engine RLS optimizer are **never used** — `optimizer_rules.rs` is a 5-line "Future" TODO, and the only repo-wide reference to the RLS helpers is their `pub mod` line. Read-side security is *unbuilt* despite ROADMAP "✅".
- Where row-filtering logic *does* exist (the ABAC `row_filter`), it is built by **string interpolation** — `format!("{column} = '{org}'")` and `{{subject.x}}` token replacement — an injection-shaped pattern, mitigated only by UUID typing, and the result is *returned to the caller*, never applied. **Trap:** never build SQL predicates by string concatenation; compile to **parameterized** WHERE (we do, `02` §6) and lean on Supabase RLS.

## A10 — The "ontology" can't actually be evolved through its own API

`object_instances` has no `update_object` route (`main.rs` wires only POST/GET/GET/DELETE), and `CreatePropertyRequest`/`UpdatePropertyRequest` are wired to **no route** (skeptic, VERIFIED). So you can create an object but not edit it via CRUD, and you can't change a property definition at all. **Trap:** a "dynamic ontology" that can't be changed once running isn't dynamic — and it means B7 (change-with-data) was never even reachable here.

---

### How to read OpenFoundry going forward
1. `wc -c` before trusting any named file. 2. `rg` the claim against `src`, not the README. 3. Check whether a `mod.rs` even declares the module. 4. For any "✅ Done" in ROADMAP, find the executing call site or assume it's aspirational. The harvest in `00`–`03` survived exactly this scrutiny; these ten did not.
