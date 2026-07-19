# Deep Research Prompt — Reverse-Engineering Foundry's *Platform & Ecosystem* Layer

**What this is:** the seventh and final prompt in the set. Its single job is to reconstruct, as exhaustively as the public record allows, the **platform & ecosystem** beneath and around Foundry: **Apollo** (continuous delivery), **Marketplace** (packaging/distribution), the **infrastructure** (Rubix/Kubernetes, the compute mesh), deployment models, and the **Gotham→Foundry** platform lineage.

**How to use it:** paste everything below the line into any deep-research tool. Tool-agnostic. Keep role, scope, question bank, methodology, and output spec; trim the seed list if input is tight.

**Scope note:** the *platform/ops/ecosystem* layer — how Foundry is packaged, deployed, upgraded, distributed, and situated in Palantir's product family. The data/ontology/app/AIP/security layers are covered separately; Apollo *deploys* them but their internals are out of scope here.

---

# ▼▼▼ PASTE FROM HERE ▼▼▼

## Role

You are a senior platform/DevOps/SRE architect and reverse-engineer specializing in continuous delivery, Kubernetes-based infrastructure, multi-environment release management, and software-distribution/marketplace systems. You are rigorous, source-driven, and allergic to marketing language. Your task is to reconstruct the internal design of **Palantir's platform & ecosystem layer**: **Apollo** (the continuous-delivery system), **Marketplace** (product packaging/distribution), the underlying **infrastructure** (Rubix/Kubernetes, the compute mesh), the **deployment models** (cloud/on-prem/air-gapped), and how **Gotham, Foundry, AIP, and Apollo** relate as an "Enterprise Operating System."

## Objective

Produce an **exhaustive, citation-backed technical reconstruction** of how Foundry (and AIP) are deployed, upgraded with zero downtime, packaged into shareable products, and run across environments — detailed enough that a competent team could use it as the architectural reference for the operational/deployment story of a clone (appropriately simplified). **Prioritize concrete mechanics** (Apollo's Hub-and-Spoke model and product/release/entity/environment concepts, the promotion pipeline, Marketplace packaging and dependency resolution, the infrastructure topology) over conceptual or promotional description.

## Precise scope

**In scope:**
- **Apollo (continuous delivery)** — the **Hub-and-Spoke** architecture (**Hub** environments issue **Plans**; **Spoke** environments are Kubernetes clusters running a **Spoke Control Plane**); the **Orchestration Engine**; the core model — **Products**, **Releases**, **Versions**, **Entities** (an installation of a product in an environment), **Environments**; **Release Channels** and **promotion pipelines** with promotion criteria; zero-downtime upgrades; agents and connectivity; self-managed hubs.
- **Marketplace (packaging & distribution)** — **Products** as self-contained collections of Foundry resources with **dependency metadata**; **Stores** (e.g., the Foundry Store); installation/upgrade via Apollo orchestration; **linked products**; versioning and input mapping on install.
- **Foundry DevOps & resource promotion** — promoting Foundry **resources** (pipelines, ontology, apps) across environments; supported resource types; the relationship to Apollo and Marketplace.
- **Infrastructure** — **Rubix** (Palantir's Kubernetes-based infrastructure), the autoscaling **compute mesh** / microservice fabric (the documented "300+ microservices"), zero-trust infra, cloud-provider footprint (AWS/Azure/GCP/OCI), and on-prem.
- **Deployment models** — cloud, on-prem, **air-gapped/sovereign**, multi-environment (dev/test/prod), and how isolation is maintained.
- **The platform family & lineage** — **Gotham**, **Foundry**, **AIP**, **Apollo** as an integrated "Enterprise Operating System"; the **Gotham→Foundry** ontology lineage and how the products differ/overlap.
- **Admin/ops & APIs** — platform admin (Control Panel), monitoring/telemetry, **resource management** (compute usage), and the Apollo/Marketplace APIs; named internal services (verify).

**Out of scope** (touch only at the seam): the internal mechanics of the data/ontology/app/AIP/security layers — referenced only as the *things* Apollo deploys and Marketplace packages.

## Research question bank

Answer every question you can substantiate; record the rest as known unknowns.

**A. Apollo architecture**
1. The **Hub-and-Spoke** model: what a **Hub** does (receives telemetry, issues **Plans**) vs a **Spoke** (a Kubernetes cluster running a **Spoke Control Plane** that reports telemetry and executes Plans); multi-spoke management; self-managed hubs.
2. The **Orchestration Engine** — its role in release promotion and issuing Plans; how Plans are computed and executed.
3. Agents/connectivity between Hub and Spokes; how cloud-disconnected/air-gapped spokes are managed.

**B. Apollo product/release model**
4. **Products** (deployable software components), **Releases** (a version + metadata), **Versions** — the data model and how a release is built.
5. **Entities** (an installation of a product in an environment) and **Environments** (a grouping of entities in one infrastructure/cluster) — lifecycle, monitoring, upgrade.
6. How Apollo is **"natively aware" of Foundry's object model** — deployments as versioned operational logic, not just code bundles.

**C. Release & promotion**
7. **Release Channels** and **promotion pipelines** — how releases promote from channel to channel and the **criteria/gates** at each stage.
8. **Zero-downtime upgrades** — how thousands of upgrades roll out without downtime or human intervention; rollback.

**D. Marketplace (packaging & distribution)**
9. **Products** as self-contained bundles of Foundry **resources** + **dependency metadata**; what resource types can be packaged; how dependencies are resolved.
10. **Stores** (Foundry Store and custom stores); browsing/installing; **input mapping** and versioning on install; **linked products**; upgrades.
11. The relationship between Marketplace packaging and **Apollo** orchestration.

**E. Foundry DevOps & resource promotion**
12. Promoting Foundry **resources** across environments (dev→test→prod); supported resource types; how this relates to Apollo/Marketplace and to dataset/ontology branching.

**F. Infrastructure**
13. **Rubix** — Palantir's Kubernetes-based infrastructure: what it is and its role (e.g., agent-proxy egress requires Rubix).
14. The **compute mesh** / microservice fabric — the documented scale ("300+ microservices"), autoscaling, high availability, zero-trust.
15. **Cloud footprint** (AWS/Azure/GCP/OCI) and on-prem; how a Foundry enrollment is provisioned.

**G. Deployment models**
16. **Cloud vs on-prem vs air-gapped/sovereign**; multi-environment topologies; tenancy/isolation between environments and customers.

**H. The platform family & lineage**
17. **Gotham vs Foundry vs AIP vs Apollo** — what each is, how they differ/overlap, and how they integrate as one "Enterprise Operating System."
18. The **Gotham→Foundry ontology lineage** — the shared "dynamic ontology" heritage and what carried over.

**I. Admin/ops, APIs & history**
19. Platform **admin** (Control Panel), **monitoring/telemetry**, and **resource management** (compute usage/metering at the platform level).
20. The **Apollo/Marketplace APIs** and the named **internal services** (verify).
21. **History/evolution** of Apollo, Marketplace, and the platform family.

## Source strategy (prioritized)

1. **Primary — official docs:** `palantir.com/docs/apollo/**` (core/how-apollo-works, environments, products-releases-versions, overview; getting-started/promotion), `palantir.com/docs/foundry/marketplace/**` (overview, foundry-products, browse-products, linked-products), `…/foundry/foundry-devops/**`, `…/foundry/architecture-center/**` (AIP/Foundry/Apollo).
2. **Primary — blog, whitepapers & filings:** `blog.palantir.com` (the Apollo "SaaS where no SaaS has gone before" post), the **Apollo technical white paper**, SEC filings, `palantir.com/platforms`.
3. **Primary — partner/cloud docs:** e.g., Oracle/AWS/Azure "run Foundry on …" references for infra topology.
4. **Primary — source & API refs:** `github.com/palantir`; Apollo/Marketplace API references.
5. **Secondary/Tertiary:** credible third-party (e.g., System Soft "real-time deployment with Apollo"); community — leads/corroboration only.

Prefer primary, recent, version-stamped sources; capture URL + access date.

## Reverse-engineering methodology & rigor

- **Triangulate** non-trivial claims across ≥2 sources where possible.
- **Tag every claim** — **[Documented]** / **[Inferred]** / **[Speculative]** — with **confidence** and citation.
- **Separate current from legacy**; date-stamp facts; flag in-development features.
- **Flag contradictions** explicitly.
- **Never fabricate** Apollo concepts, infra/service names, or scale figures. Where the record is silent (e.g., Rubix internals or the exact microservice count), say so and give one best-supported hypothesis labeled **[Speculative]**.
- **Chase named mechanisms** to source: **Hub/Spoke**, **Spoke Control Plane**, **Orchestration Engine**, **Plans**, **Products/Releases/Versions/Entities/Environments**, **Release Channels**, **promotion pipeline**, Marketplace **Products/Stores/linked products**, **Foundry DevOps**, **Rubix**, the **compute mesh**.

## Required output structure

1. **Executive summary** (≈1 page) + the 5–10 most important findings.
2. **Apollo architecture** *(most technical)* — Hub-and-Spoke, control planes, Orchestration Engine, Plans.
3. **Apollo product/release model** — Products/Releases/Versions/Entities/Environments.
4. **Release & promotion** — channels, pipelines, gates, zero-downtime upgrades.
5. **Marketplace** — packaging, dependencies, stores, install/upgrade, linked products.
6. **Foundry DevOps & resource promotion.**
7. **Infrastructure** — Rubix, the compute mesh, cloud/on-prem.
8. **Deployment models** — cloud/on-prem/air-gapped, multi-environment, isolation.
9. **The platform family & lineage** — Gotham/Foundry/AIP/Apollo; the ontology heritage.
10. **Admin/ops, APIs & internal architecture.**
11. **History & evolution.**
12. **Glossary.**
13. **Confidence & gaps register** — claims + confidence, known-unknowns + resolving source.
14. **Source bibliography** — URLs + access dates, by tier.

Use **tables** for the Apollo concept model, deployment models, and the platform-family comparison. Favor precise mechanics over prose; quote exact semantics verbatim.

## Exhaustiveness bar

Do **not** stop at the overview. Drill until each mechanism is concretely described with a primary citation or recorded as a known unknown with a best-supported hypothesis. Pay special attention to the **Hub-and-Spoke + Product/Release/Entity/Environment model** and the **Marketplace packaging/dependency model** — the make-or-break details for understanding how Foundry ships and is distributed. Aim for a detailed technical white paper; cite extensively; neutral tone.

## Confirmed starting leads (verified — begin here, then expand)

- **Apollo:** `palantir.com/docs/apollo/core/how-apollo-works` (Hub-and-Spoke; **Hub** environments issue **Plans**, **Spoke** environments are Kubernetes clusters running a **Spoke Control Plane**), `…/apollo/core/products-releases-versions` (**Products**, **Releases**, **Versions**), `…/apollo/core/environments` (**Entities** = a product installed in an environment; **Environment** = entities in one K8s cluster), `…/apollo/apollo-getting-started/introduction-promotion` (**Release Channels** + promotion pipeline + the **Orchestration Engine**). The **Apollo technical white paper** (palantir.com asset).
- **Marketplace:** `…/foundry/marketplace/overview`, `…/marketplace/foundry-products` (**Products** = collections of Foundry resources; self-contained packaging + dependency metadata; install/upgrade via **Apollo**), `…/marketplace/browse-products`, `…/marketplace/linked-products`; `…/foundry/foundry-devops/supported-resources`.
- **Platform family:** `palantir.com/platforms`; `…/foundry/architecture-center/*` (AIP + Foundry + Apollo as an "Enterprise Operating System"); **Gotham** (AI-ready OS with traceable lineage).
- **Infra:** **Rubix** (Palantir's Kubernetes-based infrastructure — surfaced in Data Connection docs re: agent-proxy egress); cloud "run Foundry on OCI/AWS/Azure" references.

**Named mechanisms to chase:** **Hub / Spoke** · **Spoke Control Plane** · **Orchestration Engine** · **Plans** · **Products / Releases / Versions** · **Entities / Environments** · **Release Channels** / promotion pipeline · zero-downtime upgrades · Marketplace **Products / Stores / linked products** · **Foundry DevOps** · **Rubix** · the **compute mesh** ("300+ microservices") · **Gotham** ↔ **Foundry** ontology lineage · *(verify)* Rubix internals · *(verify)* the exact microservice count.

# ▲▲▲ PASTE TO HERE ▲▲▲
