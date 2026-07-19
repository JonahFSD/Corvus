# Prompt — OpenFoundry Fork-or-Harvest Teardown

> **How to use:** paste everything below the line into a capable coding agent (one with shell + filesystem + web access) running in a fresh clone of OpenFoundry. If our `Foundry/Spec/` chain is mounted, point the agent at it; if not, the prompt carries enough context to stand alone. The agent's job is an exhaustive, *verified* map of OpenFoundry plus a fork-vs-harvest-vs-build recommendation — written so we can answer any later question without re-reading the repo.
>
> **Read this first (why the prompt is framed as a decision, not a doc):** a 20-minute recon already established that OpenFoundry is **not** the lean TS/Node + single-Postgres engine our blueprint describes. It is **~42 Go microservices** + 33 Go libs + a React/Vite/TS console + Protobuf/gRPC contracts, backed by **Postgres, Cassandra, Kafka, Iceberg, Vespa, Temporal, and Ceph S3**, deployed via **Helm/ArgoCD/Terraform/Kubernetes**, under the **AGPL-3.0-only** license, with ~1,033 commits compressed into ~3.5 weeks (Apr 19–May 13 2026) by 6 authors and "originated as a port of a Rust workspace" — i.e. very young and heavily agent-built. So "just fork it and adapt it down to what we need" is a real, non-obvious decision, and the prompt is built to make that decision with evidence.

---

You are a staff-level engineer performing **acquisition due diligence** on the open-source project **OpenFoundry** (`github.com/openfoundry/openfoundry-go`, mirror `github.com/Shamdon/openfoundry`). We are considering forking it as the basis for our own product. Your output must let a skeptical reader decide **fork wholesale / harvest parts / build our own using it only as a design oracle**, and must be detailed enough to answer arbitrary follow-up questions later. **Trust nothing you cannot confirm in the code or by running it.** READMEs, `CLAUDE.md`, `ARCHITECTURE.md`, and status tables ("✅ Available") are claims to verify, not facts — this repo was built fast and largely by agents, so treat capability claims as hypotheses.

## 1. What WE are building (the yardstick to judge everything against)

Our project ("Foundry for Unity Fiber") is a **deliberately lean, metadata-driven operational platform** for carrier-relations management. Our resolved design (see `Foundry/Spec/SPEC_Foundry-Clone_Build-Blueprint.md` and `_Design-Constraints.md` if mounted) intentionally **drops every Palantir-scale tactic**: target stack is **one PostgreSQL + one application service + one language (TypeScript/Node), no microservice mesh, no Spark, no separate search cluster, no message queue.** The engine is a dynamic ontology read from config; the domain is loaded as data, not code.

The five invariants we must keep: (1) a semantic object/link model over the data; (2) versioned/historied data with point-in-time reads; (3) governed writeback — all change flows through validated, audited Actions; (4) security that travels with the data (row/object-level, on by default); (5) end-to-end lineage (source→object→action→audit).

Our six unresolved "pre-M0 blockers" (judge whether OpenFoundry solves each, and how): **B1** a config expression/rules language; **B2** how ingestion coexists with edits-only-via-actions; **B3** concurrency/isolation for server-side validation; **B4/A6** soft-delete reconciled with an immutable audit log; **B5** identity → actor; **B7** changing the ontology once data exists. Our prior-art brainstorm leans toward: CEL for the expression language, a two-layer (datasource ⊕ user-edit) merged store, SERIALIZABLE + version guard, tombstones, and compiling row-policies into SQL `WHERE`. **For every OpenFoundry capability, the question is not "is it impressive" but "does it advance our lean engine, and at what cost in complexity, language, and license."**

## 2. Known starting facts (verify or correct each — do not assume)

- License **AGPL-3.0-only** (`LICENSE`). Confirm, and analyze obligations for (a) internal-only operational use and (b) any future network-exposed or external offering.
- **~42 Go services** under `services/`, **~33 libs** under `libs/`, React 19/Vite/TS in `apps/web/`, Protobuf in `proto/` (generated to `libs/proto-gen/` via `buf`), SDKs in `sdks/` (TS/Python/Java).
- Storage per `ARCHITECTURE.md`: Postgres (CNPG+PgBouncer), Cassandra, Kafka (Strimzi+MM2), Iceberg (Lakekeeper), Vespa (search+RAG), Temporal (workflow), Ceph S3. **Verify which are actually required to run the ontology core vs. optional.**
- Infra: Helm + ArgoCD + Terraform; local `docker compose` via `compose.yaml` → `infra/docker-compose.yml`. Key tooling: `buf`, `sqlc` (`sqlc.yaml`), `pgx`, `gocql`, `kafka-go`, `chi`, gRPC, `testcontainers`.
- Ontology core appears to be: `services/object-database-service`, `ontology-definition-service`, `ontology-actions-service`, `ontology-query-service`, `ontology-indexer`, `ontology-exploratory-analysis-service`, plus `libs/ontology-kernel`, `libs/core-models`, `libs/pipeline-expression` (likely the expression language), `libs/authz-cedar-go` (Cedar policies), `libs/outbox`, `libs/saga`, `libs/idempotency`, `libs/audit-trail`. **Confirm the real boundaries.**
- Activity: ~1,033 commits, 6 authors, Apr 19–May 13 2026, then quiet (~1 month). Confirm latest activity, open/closed issues & PRs, release tags, and whether the burst pattern suggests momentum or abandonment.

## 3. Method and ground rules

1. **Clone and inventory.** Full tree; per-service and per-lib one-line purpose; LOC; languages; direct dependencies; the DB tables/migrations it owns; the `.proto` it defines; the endpoints it exposes; the tests it ships.
2. **Reconstruct architecture from code, not prose.** Build the real runtime topology and the request/data-flow graph (who calls whom, over gRPC/Kafka/HTTP), the storage each service uses, and which paths are synchronous vs. asynchronous. Where docs and code disagree, code wins; note the disagreement.
3. **Actually build and run it.** Capture exact commands, prereqs, and versions. Try: `docker compose up` (core stack), `make gen`/`make` (or `justfile`), and the smoke/integration tests under `smoke/`, `tests/`, `benchmarks/`. **Stand up the minimum subset that runs the ontology**, then exercise the closed loop end-to-end: define an object type, create an object, run an action that edits it, read it back, and inspect the audit/version/lineage. Record what worked, what didn't, and what it depends on.
4. **Probe the "reducibility" question hard.** Our entire thesis is lean. Determine empirically whether the ontology core can run against **just Postgres**, or whether it hard-depends on Kafka/Cassandra/Temporal/Vespa to do basic object+action+audit. This single answer largely decides fork-vs-harvest.
5. **Use git history as evidence.** Churn hotspots, bus factor, "TODO/FIXME/panic/unimplemented" density, how much is generated vs. hand-written, whether tests accompany features or trail them.
6. **Separate VERIFIED from REPORTED.** Every claim gets either a `file:line` / command-output citation (VERIFIED) or an explicit "unconfirmed — README says X" tag (REPORTED). Quantify wherever possible.
7. If a repo-documentation skill (e.g. `legacy-repo-docs`) is available, you may use it for the inventory pass — but the deliverables below are the spec.

## 4. Deliverables (write each as a separate Markdown file under `openfoundry-teardown/`)

- **`00_EXEC_SUMMARY.md`** — the recommendation up front: **fork wholesale / harvest core / build-our-own-as-oracle**, with the 5–7 decision-determining facts, and an honest effort estimate (person-weeks) for each path *including* the cost of adapting it to our lean TS/Postgres target (or the cost of switching our target to Go/microservices). State plainly if forking is slower than building per our blueprint.
- **`01_REPO_MAP.md`** — the full inventory from §3.1: every service and lib with purpose, LOC, deps, owned tables, proto, endpoints, tests, and a maturity tag (working / partial / stub).
- **`02_ARCHITECTURE.md`** — the reconstructed runtime topology and data-flow graph; storage per service; the end-to-end **write path** (request → validation → edit → persistence → index → audit); sync vs. async boundaries; the dependency DAG between services.
- **`03_ONTOLOGY_DEEP_DIVE.md`** — the part we actually care about. For `object-database-service`, the four `ontology-*` services, `ontology-indexer`, and `libs/ontology-kernel`/`core-models`/`pipeline-expression`/`authz-cedar-go`, answer: **how are object types / properties / links / value-types stored** (table-per-type? JSONB? EAV? generated columns?); **how do Actions/edits work** and is there a function/edit API; **how are audit, versioning, and point-in-time done**; **what is the expression/rules language** (`pipeline-expression`) and is it CEL/JSONLogic/custom; **object liveness** (synchronous reads vs. the async indexer/reindex-coordinator); **how ingestion and user-edits interact** (is there a per-property datasource⊕edit merge like Palantir's?); **how authorization works** (Cedar policies, row/object-level, how enforced on reads). Map each answer to our blueprint's D1–D15 and the six blockers.
- **`04_MAPPING_TO_OUR_SPEC.md`** — a table: each of our **five invariants**, our **MUST-replicate** items, and our **six blockers** → how OpenFoundry implements it (with citation) → **keep / adapt / drop** for us → effort. This is the crosswalk that makes the decision concrete.
- **`05_FORK_VIABILITY.md`** — **AGPL-3.0 analysis** (obligations for internal operational use vs. network-exposed/external use; what must be released and when; compatibility with any proprietary plans — flag that this warrants legal review, don't give legal advice); maintenance health & bus factor; **code quality & coherence** given the rapid agent-built, Rust→Go-ported history; test coverage reality; build reproducibility; and "what breaks if upstream dies."
- **`06_HARVEST_LIST.md`** — even if we don't fork: the specific files/dirs worth porting or studying, ranked, with why — e.g. the `.proto` contracts, the ontology data model & migrations, the action/edit model, `libs/outbox`/`saga`/`idempotency`/`state-machine`, the Cedar policy setup, and `docs_original_palantir_foundry/`. For each, note language-portability to TS/Node.
- **`07_QUESTION_BANK.md`** — every question in §5 answered with evidence.
- **`08_RUNBOOK.md`** — the exact, verified commands to clone/build/generate/run/test, with prereqs/versions and a log of what failed and how you worked around it. Someone should be able to reproduce your run from this file alone.

## 5. Question bank (answer every one, with VERIFIED/REPORTED tags and citations)

**Strategic / fit**
1. Language & runtime: backend is Go — quantify the cost of either (a) adopting Go or (b) reimplementing the parts we want in TS/Node. Is the React console reusable independently of the Go backend?
2. Architecture fit: it's 42 microservices + Kafka/Cassandra/Temporal/Vespa; our target is one service + one Postgres. **Can the ontology core run standalone on just Postgres?** Exactly which services and infra are mandatory for "define object type → create object → run action → read with audit"? List the irreducible subset and its footprint.
3. Is forking and stripping it down genuinely faster/safer than building our lean engine per the blueprint? Give a defensible person-week estimate for each path.
4. License: what does AGPL-3.0-only require of us for (a) an internal Unity Fiber tool and (b) any future external/SaaS exposure? Any CLA or contributor terms? (Flag for counsel.)

**Ontology core (map to D1–D15 + blockers)**
5. Object storage shape (D5): table-per-type, JSONB, EAV, or hybrid? Show the schema/migrations.
6. Links (D6): edge table or FKs? How is cardinality enforced?
7. Actions/edits (the kinetic core): how is an action defined, validated, and applied atomically? Is there a function-backed-action equivalent and an explicit "edits API"? How is "edits-only-via-actions" enforced — and does ingestion bypass it or merge with it (B2)?
8. Expression/rules language (B1): what is `libs/pipeline-expression`? Grammar, safety, is it CEL/JSONLogic/custom, and could we adopt it standalone?
9. Audit/versioning/point-in-time (D2/D13/B7): event log, temporal tables, or other? Can it answer "what did this object look like on date T"? How are deletes handled vs. the audit (A6)?
10. Concurrency/isolation (B3): what isolation level / locking / optimistic-version strategy guards server-side validation?
11. Authorization (D15/B6): Cedar? Row/object-level? Enforced on **reads** (object sets/traversals) or only writes? How are policies expressed and evaluated?
12. Identity (B5): how is the acting user authenticated and propagated to `actor` in the audit?
13. Lineage (invariant 5): is source→object→action→audit actually reconstructable? Show it.
14. Multi-tenancy: the `tenancy-organizations-service` suggests multi-tenant — does that help or complicate a single-deployment carrier tool?

**Reality check**
15. Maturity: which "✅ Available" capabilities actually work when run? Which are stubs/scaffolding? Cite tests and runs.
16. Test coverage: real numbers; do integration tests pass locally?
17. Build reproducibility: does it build and run from a clean checkout following its own docs? What's missing?
18. Upstream health: latest commit, cadence, issues/PRs, releases, single-vendor risk.
19. Security-critical zones the maintainers flag (`SECURITY.md`, `CLAUDE.md`) — and whether they're sound.

## 6. Output discipline

Lead with the recommendation. Every nontrivial claim carries a citation (`path:line` or the command + output). Keep VERIFIED and REPORTED strictly separate, and call out anywhere the project's own docs overstate what the code does. You are explicitly permitted — encouraged — to conclude "**don't fork**" if the evidence says so; an honest "harvest these six things and build lean" is a successful outcome. End with the three or four facts that, if any one changed, would flip your recommendation.
