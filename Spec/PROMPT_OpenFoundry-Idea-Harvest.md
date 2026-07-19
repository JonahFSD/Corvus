# Prompt — OpenFoundry Idea Harvest (for the lean one-workflow wedge)

> **How to use:** run this in a Cowork (or any capable coding-agent) session whose mounted folder can see **both** (a) this Foundry workspace — our spec chain under `Foundry/` and `Foundry/Spec/` — and (b) the **OpenFoundry repo cloned on disk**. Paste everything below the line as the task. The agent reads our decisions first, then mines OpenFoundry for *ideas, schemas, and patterns* we can reuse, and writes durable artifacts under `Foundry/Harvest/`.
>
> **Spirit:** magpie, not mover. We are **not** forking OpenFoundry (it's ~42 Go microservices on Kubernetes under AGPL — the opposite of what we're building). We are stealing the *thinking*: its ontology data model, its action/edit/audit schema, its naming, its design choices — and translating each into a **lean TypeScript + single managed Postgres** proof of concept. Steal the design, reimplement clean; never paste its Go/SQL verbatim into our code.

---

You are a senior engineer helping a **solo developer** build a **proof of concept over one summer**: clone **one real workflow for one real user** (a carrier-relations manager at Unity Fiber — "Bailey": carriers, circuits, contracts, escalations, SLAs). The PoC runs on a **managed Postgres backend** — assume **Supabase** (Postgres + auth + row-level security + auto-generated API) or a **low-code Postgres layer** (Directus / NocoBase) — with a **thin TypeScript front end**. The goal is a working wedge that proves demand, not a platform. A larger internal Foundry clone may come *later*, separately funded; it must not distort this PoC.

Your job: **mine OpenFoundry for everything worth borrowing for that wedge, and nothing that isn't.** Output directly usable artifacts (a proposed ontology config, a Supabase schema, a blocker-by-blocker plan), each grounded in real OpenFoundry files and reconciled against our own spec chain.

## 0. License & sourcing discipline (read first)

OpenFoundry is **AGPL-3.0-only**. Harvesting *ideas, schema shapes, vocabulary, and design decisions* is fine; copying its **source code or SQL verbatim** into our codebase would impose AGPL on us. So: describe what you find **in our own words**, reimplement schemas **clean-room** in our chosen stack, and **never paste OpenFoundry source** into our deliverables or our repo. When you cite, cite to show provenance (`path:line`), not to copy.

## 1. Read our decisions first (the lens)

Before touching OpenFoundry, read our chain in this workspace and hold it as the lens — we have already done the reasoning and run experiments; your harvest must *reconcile against* it, not relitigate it:

- `Foundry/Palantir-Foundry-Conceptual-Map.md` — what Foundry is (the five invariants, the closed loop).
- `Foundry/Spec/SPEC_Foundry-Clone_Design-Constraints.md` — MUST-replicate vs CAN-drop, and the D1–D15 register.
- `Foundry/Spec/SPEC_Foundry-Clone_Build-Blueprint.md` — our resolved lean engine (one Postgres, TS/Node, JSONB-hybrid, action executor, edit log, §6 config format).
- `Foundry/Spec/SPEC_Foundry-Clone_Spec-Audit.md` — the audit that found the blueprint's defects and the **six pre-M0 blockers** (B1 expression/rules language; B2 ingestion vs edits-only; B3 concurrency/isolation; B5 identity→actor; B7 ontology-change-once-data-exists; A6 soft-delete vs audit).
- `Foundry/Spec/SPEC_Foundry-Clone_Prior-Art-Brainstorm.md` — our leanings: two-layer datasource⊕edit merge (edits win), CEL for the expression language, per-type CHECK/pg_jsonschema, generated columns for hot fields, SERIALIZABLE + version guard, tombstones, compile policies into the `WHERE` clause.

Summarize, in 5 bullets, what we have already decided — so your harvest is additive, not redundant.

## 2. The wedge filter (apply ruthlessly to every candidate)

For each thing you find in OpenFoundry, ask: **"Does this help us clone Bailey's one workflow on a managed Postgres backend faster or better?"**

- **Harvest** if it's about: the ontology *data model* (object/property/link/value-type), the *action/edit/audit* model, value-type *constraints*, *submission-criteria* / rules shape, lineage, the object-set/query shape, how a single use-case is modeled end-to-end, naming/vocabulary, or a Postgres schema pattern we can drop into Supabase.
- **Reject (note as "platform-era, not now")** anything that is scale machinery: the 42-service decomposition itself, Kafka/NATS, Cassandra, Iceberg/lakehouse, Vespa, Temporal, Spark, Helm/ArgoCD/Terraform/Kubernetes, SDK generation, multi-tenancy, the observability stack, agent/AI runtime. These are real but they are *someday*; they must not enter the PoC.

When in doubt, prefer the lean version. We can always add later; we cannot un-spend the summer.

## 3. Start here (verified high-value landmarks — confirm and expand)

These were located in a quick recon; verify each exists in the on-disk clone and follow the threads:

**Ontology data model (the schema gold)**
- `services/ontology-definition-service/internal/repo/migrations/0001_ontology_schema_consolidated.sql` — the live, consolidated ontology schema (object types, properties, links, value types). *This is the single most valuable file.*
- `docs/architecture/legacy-migrations/ontology-definition-service/*.sql` — granular history (`initial_ontology`, `ontology_projects`, `ontology_funnel`, governance) showing how the model evolved and what each table is for.
- `libs/ontology-kernel/models/` (`link_type.go`, `function_authoring.go`, `interface.go`, `search.go`) and `libs/ontology-kernel/stores/pg.go`, `stores/object_set_materializations.go` — the domain types and the Postgres store; how object sets are materialized.
- `libs/core-models/dataset/transaction.go` (their dataset transaction/version model — compare to our D2), `libs/core-models/ids/typed_id.go`, `libs/core-models/security/`.

**Action / edit / audit model (the kinetic core)**
- `docs/architecture/legacy-migrations/ontology-actions-service/` — especially `20260423113000_action_types.sql`, `20260503000000_action_log.sql`, `20260504000000_action_executions_revert.sql`, `20260506000000_action_execution_side_effects.sql`, `20260426001500_action_type_policies_and_what_if.sql`. These show how action types, the audit/action log, undo/revert, side-effects, policies, and "what-if" scenarios are modeled in Postgres — directly relevant to B2, A6, audit, side-effects, and even scenario-overlays.
- The live action service code under `services/ontology-actions-service/` — how an action is validated, applied atomically, and logged. Find what expression mechanism actions use for **rules and submission criteria** (this may be *different* from the pipeline DSL below — establish which, for B1).

**Expression language (B1)**
- `libs/pipeline-expression/` — a **custom, hand-rolled Pratt-parser DSL** with a type lattice and nine transforms, built for *Pipeline Builder* data transforms (not necessarily action rules). Read `doc.go`. Treat as a *reference point* for "what a typed embedded expression language looks like," but contrast with our leaning to adopt **CEL** off-the-shelf rather than hand-roll. Determine whether actions reuse this DSL or have their own predicate mechanism.

**Authorization (B6 / security-travels-with-data)**
- `libs/authz-cedar-go/` (`cedar_schema.cedarschema`, `engine.go`, `audit.go`) and per-service policies like `services/identity-federation-service/policies/identity_admin.cedar`, `services/media-sets-service/internal/cedarauthz/media_sets.cedar`. They chose **AWS Cedar** as the policy language. Harvest the *idea* (declarative, auditable policies; a schema for principals/resources/actions) and compare it to our two real options for the wedge: **Supabase Row-Level Security** (simplest, enforced in-DB on reads) vs **compile-policy-into-WHERE**. Decide which fits a solo PoC.

**Side-effects / workflow patterns (harvest the concept, not the infra)**
- `libs/outbox/`, `libs/saga/`, `libs/idempotency/`, `libs/state-machine/` — the *transactional outbox* concept matters for our post-commit side effects (our brainstorm already flagged it); the rest are mostly platform-era. Extract the pattern, ignore the plumbing.

**Their own single-use-case PoC (a template for ours)**
- `docs/poc-online-retail/`, `docs/ontology-building/`, `docs/use-case-development/`, `docs/architecture-center/`, and `docs_original_palantir_foundry/` — read how *they* model one use-case end-to-end and how they describe the ontology to builders. This is a free worked example of the exact thing we're doing.

## 4. Reconcile against our six blockers (the core of the harvest)

For **each** blocker, write: *what OpenFoundry does* (with `path:line`), *whether it confirms, improves on, or contradicts our brainstorm leaning*, and *the final lean answer for the wedge*:

- **B1 — expression/rules language:** their pipeline DSL vs what actions actually use vs our CEL leaning. Recommendation for the PoC (likely: CEL for criteria/policies, or even simpler for one workflow).
- **B2 — ingestion vs edits-only:** does `object-database` / ingestion layer datasource data *under* user edits (the per-property merge), or overwrite? Does the action log confirm "edits win"? Map to our two-layer model.
- **B3 — concurrency:** what isolation/locking/versioning guards action validation? (Look for `version`, `SELECT … FOR UPDATE`, serializable, optimistic columns.)
- **B5 — identity→actor:** how is the acting principal authenticated and stamped into the audit/action log? (For us, Supabase Auth likely supplies this — confirm the shape they store.)
- **B7 — ontology change once data exists:** do their migrations/versioning handle schema/value-type changes against existing object data? Any "ontology versioning" or migration story to copy.
- **A6 — soft-delete vs audit:** tombstones or hard delete? How does the action-log/revert model treat deletion? Confirm our tombstone-and-delete-is-an-event plan.

## 5. Deliverables (write each as Markdown under `Foundry/Harvest/`)

1. **`00_HARVEST_DIGEST.md`** — the top ~10 ideas worth stealing, ranked by value to the wedge. Each: *what OpenFoundry does* (cited), *why it's good*, and *the lean wedge version* (TS + Supabase/Postgres). One screen if possible.
2. **`01_WEDGE_ONTOLOGY_CONFIG.md`** — a concrete, ready-to-use **ontology config** (JSON/YAML) for Bailey's domain (carrier, circuit, contract, escalation, SLA; their links; 2–3 real actions like *open escalation* / *flag for renegotiation* with parameters, rules, and submission criteria), synthesized from OpenFoundry's model + our blueprint §6 + the brainstorm. This is the artifact the PoC is built from.
3. **`02_WEDGE_DB_SCHEMA.md`** — a concrete **Supabase/Postgres schema** for the wedge: objects (hybrid JSONB + a few typed/generated columns), links, an edit/audit log, a datasource⊕edit layering, value-type CHECK constraints, and **example RLS policies** for "security travels with data." Reconcile OpenFoundry's real migrations with our brainstorm (CHECK/pg_jsonschema, generated columns, tombstones, two-layer merge). Pure Postgres, clean-room.
4. **`03_BLOCKER_RECONCILIATION.md`** — §4 above, written out.
5. **`04_IGNORE_LIST.md`** — the platform-scale machinery we are deliberately not taking, each with a one-line *why* and *when we'd revisit*.
6. **`05_ANTIPATTERNS.md`** — things in OpenFoundry **not** to copy: over-engineering for our scale, immature/agent-built rough edges, anything the code does that contradicts its own docs. (This repo was built very fast and largely by agents — be a skeptical reader; verify claims against code.)
7. **`06_READING_LIST.md`** — a curated, ordered list of the exact OpenFoundry files worth a human read, with a one-line "what you'll learn" each, so the developer can go look without re-deriving.

## 6. Method & output discipline

- Read **our chain first**, then OpenFoundry; every harvest item must be reconciled against what we already decided.
- Every nontrivial claim about OpenFoundry carries a `path:line` citation; mark **VERIFIED** (read the code) vs **REPORTED** (only docs say so). Flag where their docs overstate the code.
- Apply the **wedge filter** to everything; prefer the lean version; push scale ideas to the ignore list, don't smuggle them in.
- **Never** recommend adopting Go, microservices, Kafka/Cassandra/Temporal/etc., or forking the repo. Translate every good idea into **TypeScript + one managed Postgres**.
- Respect the **license discipline** in §0: describe and reimplement, don't copy.
- Lead the digest with the punchline: the handful of ideas that will most accelerate Bailey's workflow — and name anything that says "our brainstorm was wrong, OpenFoundry does it better."
