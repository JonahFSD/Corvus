# 04 — Ignore List (platform-scale machinery we are deliberately not taking)

> Everything here is **real in the repo** (verified, not assumed) and **deliberately out of the wedge**. Each row: what it is (with a path that proves it's there), the one-line *why not now*, and *when we'd revisit*. The discipline: a wedge that clones **one** carrier-relations workflow on **one** managed Postgres needs none of this; adding it later must not require rework, so we note the revisit trigger.

## The fleet & its plumbing

| Machinery (VERIFIED location) | Why not now | Revisit when |
|---|---|---|
| **21 microservices** (`services/` — `ai, app-builder, audit, auth, code-repo, data-connector, dataset, fusion, gateway, geospatial, marketplace, ml, nexus, notebook, notification, ontology, pipeline, query, report, streaming, workflow`) | A single-workflow wedge is **one app + Supabase**, not a fleet | Product breadth genuinely needs independent deploy/scale per domain (likely never for the wedge) |
| **gRPC / tonic** (`tonic = { workspace = true }` in 10 service Cargo.tomls; root pins `tonic="0.12"` + `tonic-build`, VERIFIED) | Inter-service RPC is moot with one service; Supabase gives REST/RPC + typed client | We have ≥2 backend services with versioned contracts |
| **proto/ + buf codegen** (`proto/buf.gen.yaml` → prost/tonic + connect-es; 21 proto package dirs, VERIFIED) | IDL-driven codegen across 21 namespaces is heavyweight — *and it never ran* (output dirs absent, TC-6) | Polyglot service contracts must be version-controlled across teams |
| **NATS / JetStream event bus** (`libs/event-bus` wraps `async_nats::jetstream`; root pins `async-nats="0.38"`, VERIFIED) | One transactional Postgres gives read-your-writes for free; no broker needed | Cross-service async fan-out or true event sourcing is required |
| **Redis** (`Cargo.toml` L113 `redis="0.27"`, **declared but unused** — absent from Cargo.lock, no `redis::` in source, VERIFIED) | Not even linked in OpenFoundry; Postgres covers caching/sessions at this scale | A hot read path needs a dedicated cache |
| **MinIO / S3 storage abstraction** (`libs/storage-abstraction/src/s3.rs` uses `object_store::aws`; MinIO container in `infra/docker-compose.yml`, VERIFIED) | Supabase Storage + Postgres rows cover file/blob needs | Pluggable object-storage backends become a customer requirement |
| **WASM runtime (wasmtime 24)** + **Python runtime (pyo3)** (`pipeline-service/.../engine/mod.rs` imports `wasmtime::{Engine,Module,…}`; `pyo3` in pipeline + notebook services, VERIFIED) | The wedge needs a *constrained* rule language (CEL), not in-process arbitrary-code execution | We must run untrusted user transforms in multiple languages |
| **Multi-tenancy plumbing** (`org_id`/`tenant_id` in `auth-middleware` claims/RlsContext/tenant.rs — but only **2 of 21 services** reference it, VERIFIED PLAT-06) | A single-customer wedge needs no org isolation; Supabase RLS on one org covers it | Serving multiple isolated customer orgs from one deployment |
| **infra/ (Docker Compose ×3, K8s + Helm with HPA/KEDA, Terraform custom provider + CDN module)** (`infra/k8s/helm/open-foundry/templates/{hpa,scaledobject}.yaml`, `infra/terraform/providers/openfoundry/`, VERIFIED) | The wedge deploys to Vercel + Supabase with zero K8s/Terraform | Self-hosted multi-tenant scale + custom infra provisioning |

## The satellite services (someday, not now)

All present under `services/` (VERIFIED) but out of scope — and largely **0-byte scaffolding inside** (see `05_ANTIPATTERNS` F10):

| Service | Why not now | Revisit when |
|---|---|---|
| `vector-store` (lib) + `ml-service` + `ai-service` | No semantic search / ML / LLM in a carrier-relations wedge | An AIP-style layer is separately funded (keep the *execution-permission* seam from blueprint §9) |
| `geospatial-service` + `libs/geospatial-core` (H3/WKT/MVT) | No maps in the wedge | Circuit/site geography becomes a real workflow need |
| `nexus-service`, `marketplace-service`, `fusion-service` | Distribution/packaging/entity-resolution are platform features | Multi-product distribution matters |
| `notebook-service` (pyo3 kernels, CRDT) | No code notebooks in the wedge | Analysts need interactive compute |
| `streaming-service` (NATS topologies) | Bailey's data is batch/small | Real-time circuit telemetry ingestion |
| `pipeline-service` (DataFusion + SQL/Python/WASM transforms) | Transforms are SQL/views in one Postgres (D3) | Distributed multi-engine compute over big data |
| `code-repo-service` (git-backed) | No code authoring surface in the wedge | Function-backed actions need versioned authoring |

## What we keep from the same repo (so the boundary is explicit)

Not everything OpenFoundry built is rejected — we keep the **shapes** (see `00`/`01`/`02`): the objects-as-JSONB + unified-edge-table data model, the action `input_schema`/`config` split and validate→preview→execute contract, the `audit_event` *field shape*, and the JWT→`RlsContext`→`actor` identity wiring. We reject the **scale tactics** above. The line is exactly the blueprint's standardize-vs-adapt boundary (§7): keep the promises, drop the Fortune-500 tactics.

## License note (the one non-scale ignore)

OpenFoundry is Apache-2.0 (`Cargo.toml` L47, `package.json`, README badge/prose — all VERIFIED) which permits reuse with attribution. We still **reimplement clean** (Rust → TS/Postgres doesn't drop in anyway) and cite path:line for provenance. The empty `LICENSE` file (0 bytes, VERIFIED) is a real ambiguity — flagged in `05_ANTIPATTERNS`; resolve in writing before any verbatim copy (we have none).
