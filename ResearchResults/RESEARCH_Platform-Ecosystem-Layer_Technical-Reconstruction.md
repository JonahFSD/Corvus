---
**Artifact:** Deep-research output — technical reconstruction of Foundry's *platform & ecosystem* layer (Apollo, Marketplace, Rubix, the platform family).
**Produced:** 2026-06-13, by a deep-research agent run on `DEEP-RESEARCH-PROMPT_Platform-Ecosystem-Layer.md`.
**Independent spot-check (by Claude, 2026-06-13):** Confirmed — the three **Spoke Control Plane** services (`helm-chart-operator`, `apollo-auth-broker`, `expected-state-k8s`), Apollo's **constraint-gated** install model, and **Rubix's "nodes cannot live longer than 48 hours"** ephemerality (anti-APT). High-confidence.
**Read with care (flagged conflicts):** 48h *node* vs 72h *container* cycle; `service.v1` product type status; Apollo launch year (2020 disclosure vs 2022 GA); "Central Observability" thinly sourced. The 300+ microservices figure is from the Architecture Center overview.
**The clone takeaway:** this is the **most droppable layer for us.** Apollo's Hub-and-Spoke + air-gap + constraint-satisfaction machinery earns its complexity only when shipping to *many heterogeneous, intermittently-connected, separately-accredited* environments. For one internal tool, ordinary deployment (a desired-state GitOps tool + a simple packaging step) suffices. Keep the *ideas* (versioned/auditable deploys, env separation); drop the apparatus.
---

# Palantir's Platform & Ecosystem Layer: A Technical Reconstruction of Apollo, Marketplace, Rubix, and the "Enterprise Operating System"

*Architectural reference for the operational/deployment story. Compiled June 13, 2026. Claims tagged [Documented] / [Inferred] / [Speculative].*

## TL;DR

- **Apollo is a constraint-based, pull-model continuous-delivery control plane on a Hub-and-Spoke architecture**: Hub Environments run an Orchestration Engine that issues "Plans" (units of work); Spoke Environments are Kubernetes clusters running a "Spoke Control Plane" of agents that poll for Plans, execute them, and report telemetry back. Apollo has **no single target state** — it proposes the latest Release that satisfies all configured constraints. [Documented]
- **Marketplace + Foundry DevOps is the packaging/distribution layer on top of Apollo**: Foundry resources (pipelines, ontology types, Workshop apps, functions, models) are packaged into self-contained "Products" with auto-resolved dependency metadata and input mappings, published to "Stores," and installed/upgraded via Apollo. This makes Apollo "natively aware" of Foundry's object model — deployments are versioned operational logic, not just code bundles. [Documented]
- **The whole stack runs on Rubix** (Palantir's hardened, autoscaling Kubernetes) as an integrated "Enterprise Operating System" of AIP + Foundry + Apollo. "AIP and Foundry collectively consist of 300+ microservices and assets, all running in a highly available and autoscaling compute mesh, atop zero-trust security infrastructure… (for instance, aggressive node cycling to guard against advanced persistent threats)" — deployable identically across AWS, Azure, GCP, OCI, on-prem, and air-gapped/edge. [Documented]

## Key Findings

1. **Apollo inverts the traditional CI/CD "push" model into a "pull" model.** Developers register Products + constraints/SLAs/promotion criteria; environment operators subscribe to Release Channels; Apollo autonomously computes and issues Plans that satisfy all constraints. There is explicitly "no single target state" — a contrast to GitOps tools like ArgoCD that reconcile to a declared desired state. [Documented]
2. **The Hub-and-Spoke split is the make-or-break design.** The Hub holds the brain (Orchestration Engine, Product catalog, Environment settings, promotion logic); the Spoke holds a thin control plane (4 named services). All Agent→Hub communication is **encrypted, unidirectional, outbound**, authenticated with a per-Environment key signed by the Hub at registration — enabling air-gapped operation. [Documented]
3. **Apollo's data model is small and precise:** Products (Maven-coordinate-identified deployable software) → Releases (a version + immutable metadata) → Versions (strictly ordered); deployed into Environments (one K8s cluster) as Entities (one installed Product in one Environment). [Documented]
4. **Promotion is health-gated and time-gated ("soak").** Releases move RELEASE→CANARY→STABLE-type channels automatically only after meeting health criteria over a soak duration; failed health triggers automatic recall and roll-off. Zero-downtime via blue/green on Rubix. [Documented]
5. **Marketplace dependency resolution is automatic and lineage-driven.** DevOps inspects packaged resources, surfaces upstream dependencies as "inputs," and links products whose outputs satisfy those inputs. [Documented]
6. **Rubix enforces aggressive ephemerality** — "nodes in Rubix environments cannot live longer than 48 hours," for HA and as an anti-APT control. (Doc inconsistency: a 72-hour *container* cycle is also stated; see Caveats.) [Documented]
7. **The four products form a deliberate lineage:** Gotham (2008, defense, dynamic-ontology heritage) → Foundry (commercial, generalized ontology) → AIP (2023, generative-AI layer) → Apollo (continuous delivery, conceived alongside Foundry). Gotham is now integrated atop the Foundry-managed Ontology. [Documented]

## 2. Apollo Architecture (Hub-and-Spoke, Control Planes, Orchestration Engine, Plans)

### 2.1 Hub-and-Spoke topology

Two Environment types:
- **Hub Environments** "receive information and telemetry about Spoke Environments and issue Plans to make changes. Hubs can manage multiple Spoke Environments, and can also be set up to self-manage."
- **Spoke Environments** "each run a Spoke Control Plane which reports information and telemetry back to the managing Hub and executes Plans issued by the Hub."

A Spoke is a Kubernetes cluster (CNCF-certified for production). A Hub can itself be a Spoke of another Hub ("a hierarchy of Hubs and Spokes"). Environments are disjoint; they may be "disconnected" during unmanaged periods (e.g., "running on vehicles"). The "Main Apollo Hub is the SaaS hub" in Palantir's hosted configuration.

### 2.2 The Orchestration Engine

Each Hub contains an **Orchestration Engine**: "Services running in each Hub that determine which Plans to issue to the Spoke Environment from all possible Plans, after ensuring all constraints are satisfied." Two jobs:
1. **Issue Plans** — "Continuously evaluates all the possible Plans for each Spoke. Evaluates all the constraints… Issues Plans, whose constraints are satisfied, to the Spoke's agents."
2. **Drive Release promotion** — "continuously evaluates whether a release already passed or failed the health promotion criteria using the information coming from the Reported State… the release will be added to the next Release Channel… In cases where the evaluation fails… the Orchestration Engine will automatically recall the release."

**Critical: no target state.** "Apollo does not have a specific target state for Environments or Entities. Instead, Apollo proposes Plans which satisfy the configured constraints… an Entity is defined with a Product and a Release Channel but not a specific version." Inputs: the **Product catalog**, **Environment settings**, and the **Reported State**. "The Orchestration Engine can only propose changes that do not violate any of the constraints."

### 2.3 Plans and Constraints

**Plans** are "how Apollo delivers instructions from the Hub to agents… Each Plan is a unit of work… only sent to an agent for execution when all relevant constraints have been satisfied." Types: install a new Entity; modify config overrides; modify version + config (in lockstep); uninstall; create/edit/delete secrets.

**Plan-based vs control loops:** "Rather than directly carrying out actions in the background without a human noticing, Apollo generates a Plan, and once all constraints are satisfied, the Plan is sent to an agent for execution," surfaced in the Activity/Plans tabs.

**Prioritization/failure:** roll-off of a recalled release and break-glass commands are prioritized; on Plan failure Apollo "will automatically create an Entity-level suppression window," permitting an automatic rollback Plan but always respecting human suppression windows. Apollo requests a new Plan when reported state, entity settings, config/secrets, or release-channel membership change, or when a Plan has been blocked > 4 hours.

**Constraints** are "preconditions which Plans must satisfy." Categories: cross-service **Product dependencies** (version ranges `[1.2.3, 2.0.0)`), **Product incompatibilities** (bidirectional), **schema-version dependencies**, **maintenance windows**, **suppression windows**, health/SLO criteria.

### 2.4 Spoke Control Plane — the named services

Four named components (verified):

| Service | Role |
|---|---|
| `helm-chart-operator` | Manages `helm-chart` entities (install, config changes); also manages all the other Spoke Control Plane services (first service installed); optional mutating admission webhook rewrites image registries + injects pull secrets. |
| `apollo-auth-broker` | "Brokering authentication material on behalf of Apollo Agents between the Apollo Hub, the Spoke Environment, and any Artifact Registries." |
| `expected-state-k8s` | Converts the K8s object model into the Apollo object model and sends it back to the Hub; collects health from managed Entities and forwards it. |
| Apollo Agent (generic) | "Any agent… responsible for executing Plans provided by the Apollo Hub and reporting back the Reported State." |

The Spoke Control Plane "module" is selected at registration (Dev vs Standard accreditation determines installed services).

### 2.5 Agents & connectivity (incl. air-gapped)

Agents "Continuously poll the orchestration engine for new Plans and report back the state… Execute the change(s)… Report whether Plans succeeded or failed." They talk to the **Apollo Hub** (Plans) and **Artifact Registries** (Helm charts, container images).

**Security:** "During the Environment registration process, a cryptographic key is generated that is unique to that specific Environment. This certificate is signed by the Apollo Hub and is leveraged by the Apollo Agent for all communications back to the Hub… preventing impersonation." Communication is "encrypted, unidirectional outbound requests from the Environment."

**Air-gapped:** pull-based + outbound-only means Spokes can be disconnected when unmanaged. Apollo "supports all major cloud, on-premises, and disconnected (air-gapped) environments" via "autonomous deployment," with controls for FedRAMP, IL5, IL6. All artifacts cryptographically signed and auditable end-to-end.

## 3. Apollo Product/Release Model

| Concept | Definition | Identity |
|---|---|---|
| **Product** | "The software components that are deployable in Apollo." Types: Helm charts and Assets. | Maven `group:artifactId` = ProductId |
| **Release** | "A versioned code artifact that is published to the Product catalog" — code + metadata Apollo uses to manage it. | Maven `group:artifactId:version` |
| **Version** | Strictly orderable string (`1.0.0`, snapshot, rc); ordering lets Apollo reason about migrations/compatibility. | each component ≤ 2³¹−1 |
| **Environment** | "A grouping of Entities deployed into the same infrastructure… microservices running in a single Kubernetes cluster." | per-env config |
| **Entity** | "An installation of a Product in an Environment." | belongs to exactly one Environment |
| **Product catalog** | "An inventory of all Products… published to an Apollo Hub" incl. dependencies, recall info, Release Channels. | per-Hub |

**Apollo Product Specification (packaging contract):** an Apollo Product Definition conforms to the spec, is versioned alongside a release, and is immutable for that Release; components are "packaged into a compressed tarball." **`manifest.yml` [Required]** declares immutable intrinsic properties (`product-type`, `product-group`, `product-name`, `product-version`) + extensions (dependencies, incompatibilities, health). Product types: `asset.v1` (arbitrary files); `helm.v1` (Helm Charts). **Traits** describe behavior/requirements (memory, ports, TLS certs); implementation deferred to the Spoke Control Plane.

**"Natively aware" of Foundry's object model:** as Foundry's delivery layer, "deployments aren't just bundles of code—they're versioned, interlinked operational logic" — it versions object types, actions, logic flows, policy rules, UI definitions. [Documented at the seam; third-party for framing]

## 4. Release & Promotion

**Release Channels & the pull model:** "Apollo orchestrates product upgrades based on subscriptions to Release Channels; for example… RELEASE, CANARY, and STABLE. Developers define the criteria and the order for promotion… Environment operators subscribe to the Release Channel appropriate for their environment."

**Promotion pipeline:** to promote, a Release must pass **health criteria** (Apollo computes Healthy/Unhealthy duration; weekends excluded), satisfy **label requirements**, promote within the **maintenance window**, and soak ≥ a configured duration (0s–13d) across N entities. **Timeouts:** canary soak cancels at 2× soak duration; canary-reachability cancels after 7 days. **Recall when unhealthy:** auto-recall above an unhealthy-entity threshold.

**Recalls & roll-off:** recalls (manual, automatic, or API-triggered, e.g. CVE scans) communicate a bad Release. Roll-off: **roll forward** (default), **allow downgrade** (to a min good version), **freeze** (stay put, block roll-outs), **per-environment** (test fix first). "Apollo will ignore an Entity's no-downtime maintenance window when rolling off a recalled Release" — safety overrides zero-downtime during a recall.

**Zero-downtime:** "every software service is deployed in a multi-node configuration… designed for 'blue/green' rollout… builds a parallel green environment… if the green environment operates successfully for a specified period, traffic is gradually redirected… and the blue nodes are simply destroyed." Apollo orchestrates "thousands of zero-downtime upgrades across hundreds of services and assets every day," leveraging "Rubix's opinionated API layer."

## 5. Marketplace (Packaging & Distribution)

**Products as self-contained bundles:** "Products are collections of Foundry resources that a product builder has made available to install." A **Foundry product** is "portable across enrollments… includes enhanced capabilities for cross-environment deployment and Apollo-based management." Properties: environment portability ("deployed across different Foundry enrollments without modification"), self-contained packaging ("all necessary components and dependency metadata are bundled"), Apollo-managed lifecycle, version control/rollback. Two install modes: **Managed** (delivered from Palantir, managed in Apollo) vs **Artifact** (delivers only the Marketplace product; install via Marketplace without Apollo overhead).

**Content/inputs/resources:** **Content** = resources installed once inputs are mapped; **Inputs** = dependencies that must be mapped. "The vast majority of Foundry resource types can be included as outputs" — datasets/transformations, object & link types, action types, functions (incl. OSDK-backed), automations, Workshop modules, models (static ≤8 GiB or with producer), Developer Console apps. **Objects themselves cannot be packaged** (only datasets + object types that create objects post-install).

**Dependency resolution & linked products:** DevOps "automatically identifies resource dependencies, so you should add the furthest downstream resources first." **Linked products** are "one-way connections that allow downstream products… to link to upstream products"; DevOps inspects packaged source entities to determine links (a pipeline's clean datasets auto-map to an Ontology product's inputs). Breaking changes require major-version increments.

**Stores:** "a store is a collection of products." **Foundry Store** (all customers); **Local stores** (in a Project/folder, inherit permissions); **Remote stores** (cross-enrollment, Palantir-created only). Governed by `marketplace:*` permissions; can require approval before publishing (approver ≠ author).

**Install/upgrade/versioning:** guided flow — name + location → choose Ontology → **map inputs** (column mappings; "Prefix ontology entities" to namespace e.g. `[DEV]`) → review Content → (Production) Release Channels + maintenance windows. **Modes:** Production (auto-upgrades, channel-tracked) vs Bootstrap (auto-upgrades off). Automatic upgrades (beta) run within a maintenance window (cause downtime); manual edits to installed content are overwritten on upgrade; uninstall deletes all resources across versions.

**Marketplace ↔ Apollo:** Marketplace/DevOps is the packaging + storefront UX; Apollo is the orchestration engine that executes installs/upgrades/rollbacks.

## 6. Foundry DevOps & Resource Promotion

**Release management = environment separation.** "Spaces are a flexible primitive… that allow for environment separation." Recommended: one Space per environment (Dev/Test/Prod); package from dev into products, install into Test, then Production. **Recommended product split:** Datasource product + Ontology product + Use-case product(s); 1:1 Project-to-product. Environment-specific differences configurable (data scope, behavior, approvals).

**Two complementary mechanisms:** **DevOps + Marketplace** (cross-environment release management) and **Foundry/Global Branching** (in-environment iteration — "available for Pipeline Builder, the Ontology, Workshop, datasets in Code Repositories, and running Actions on a branch"). "Complementary solutions to different problems."

## 7. Infrastructure — Rubix & the Compute Mesh

### 7.1 Rubix

"AIP, Foundry, and Apollo all operate within a hardened, autoscaling, highly available implementation of Kubernetes known as Palantir Rubix." History: the 2017 decision to migrate to Kubernetes (vs YARN/Mesos), to "guarantee execution time with lower variance" for Spark, with two goals — "streamlining and scaling the deployment of our software platforms and strengthening our security posture."

**Core features:**
- **Ephemerality:** "nodes in Rubix environments cannot live longer than 48 hours" — for HA (designed-for-disruption) and anti-APT ("Compromising a single node is insufficient for an attacker to gain persistent access").
- **Zero-trust:** "Every workload is securely isolated… every interaction between workloads must be authenticated, authorized, and logged in accordance with immutable configurations." Accreditations: FedRAMP High, IL-5/IL-6, CMMC.
- **Networking:** Cilium/eBPF container network policy; Hubble (eBPF) observability; forward-proxy egress migrated **Squid → Envoy** (L4/L7), moving egress control into the platform for self-service. Rubix is the egress substrate for Foundry's data-connection egress + published "Foundry Rubix IPs."
- **Autoscaling:** "dynamic and intelligent autoscaling," demand-sensing, continuous cost optimization; extends to customer workloads via **Compute Modules** (BYO containers into the Apollo-managed mesh).

### 7.2 The compute mesh / 300+ microservices

"AIP and Foundry collectively consist of 300+ microservices and assets, all running in a highly available and autoscaling compute mesh, atop zero-trust security infrastructure… (aggressive node cycling to guard against advanced persistent threats)." Maps into nine capability sets × six mesh-wide components (Storage, Compute, Networking, Security, Governance, Workspace) — "All… powered by Apollo." **Open compute/data plane (MMDP):** Apache Iceberg primary table format; autoscaling Spark (batch), Flink (streaming), single-node DuckDB/Polars; pushdown to Databricks/Snowflake; Compute Modules for BYO containers. The **Ontology backend** is itself microservices (OSv2; Object Set Service; Object Data Funnel; legacy Phonograph deprecating after June 30, 2026).

## 8. Deployment Models

| Model | Mechanics |
|---|---|
| Public cloud SaaS | Managed/accredited; AWS/Azure/GCP/OCI; dedicated URL; multi-AZ HA + auto DR; autoscaling |
| Gov/classified cloud | GCC (AWS, FedRAMP Mod), Gov Cloud (AWS, IL5) |
| On-premises | "Foundry On-Premises"; DirectConnect; agent-based connectivity |
| Air-gapped / disconnected / edge | Apollo pull-model + signed artifacts; "humvee… submarine"; drones, vehicles |
| Multi-cloud / hybrid / Private SaaS | Apollo runs "at the application layer, above the infrastructure layer" |

**Provisioning:** "Palantir Foundry and AIP is not self-deployable" — provisioned with account teams. Rubix gives "identical operational characteristics" across clouds/on-prem. **Cloud nuance:** despite the 2024 Palantir–Oracle OCI partnership, *The Register* reported the UK NHS Federated Data Platform deploys Foundry on AWS + Azure — cloud footprint is per-deal, not monolithic.

## 9. The Platform Family & Lineage

| Platform | What | Year | Role |
|---|---|---|---|
| **Gotham** | Defense/intel "AI-ready OS"; entity resolution, link analysis, geospatial | 2008 | Now integrated atop the Foundry-managed Ontology |
| **Foundry** | Data operations platform — integration, ontology, analytics, apps | ~2016 | The data/ontology core |
| **AIP** | Generative-AI platform — k-LLM, agents, Evals | 2023 | The AI layer on the shared mesh |
| **Apollo** | Continuous delivery / Day-2 ops | ~2020 | "Manages the infrastructure that hosts Foundry and AIP" |

"The standard Palantir architecture consists of three integrated platforms: AIP, Foundry, and Apollo… designed to function as an Enterprise Operating System."

**Ontology lineage (Gotham → Foundry):** Gotham pioneered the "dynamic ontology" (objects/properties/links for analysts); Foundry generalizes it with three layers — Semantic (objects/links/properties), Kinetic (actions/functions), Dynamic (AI/simulation). **Live interoperation:** Ontology Manager supports **type mapping** to Gotham ("create new Gotham types based on existing Foundry object types… which remain synchronized"); Gotham queries Foundry object data via the **Object Set Service**; irreversible once enabled.

## 10. Admin/Ops, APIs & Internal Architecture

**Control Panel** = "Foundry's full suite of governance and administration." **Resource Management:** compute in **Foundry compute-seconds**; Resource Transparency per Project/Ontology; Usage accounts; Budgets; Resource queues (FIFO, vCPU/vGPU) gating compute groups; AIP TPM/RPM limits. **Observability:** Data Health (alerts via PagerDuty/Slack/webhooks); Workflow Lineage (7-day history, distributed tracing); 30-day metrics; Apollo monitors compatible with DataDog/Prometheus.

**APIs:** Apollo API is **GraphQL** (in-Hub API Explorer); **Apollo CLI** (`apollo-cli`) verbs: changerequest, cve, entity, environment, helm-chart, module, product, product-release, profile, release-channel, terminal. **No open public REST reference** for Apollo. Foundry API is separate. **Named Hub services:** the **Orchestration Engine** is the only distinctly named Hub-side service published; a "Central Observability" name appears once but is not elaborated.

## 11. History & Evolution

- **2008** — Gotham launches (USIC; on-prem, infrequent manual upgrades).
- **~2016** — Foundry launches commercially.
- **Conceived alongside Foundry** — Apollo "initially built as the automation and delivery infrastructure for our public-cloud SaaS."
- **Sept 2020** — Apollo publicly detailed ("Powering SaaS where no SaaS has gone before").
- **2022** — Apollo technical white paper; productized for external customers; Control Panel unified.
- **2023** — AIP launches.
- **2024** — Palantir–Oracle OCI partnership; cloud-identities cap.
- **2025/26** — AIP + Foundry + Apollo formalized as "Enterprise Operating System"; OSv1 (Phonograph) deprecation set for June 30, 2026.

## 12. Glossary

- **Hub / Spoke** — managing Environment (runs Orchestration Engine) / managed Environment (a K8s cluster).
- **Spoke Control Plane** — `helm-chart-operator`, `apollo-auth-broker`, `expected-state-k8s`, + generic Apollo Agent.
- **Orchestration Engine** — Hub services that compute/issue Plans and drive promotion.
- **Plan** — a unit of work issued to an Agent once constraints pass.
- **Constraint** — precondition a Plan must satisfy.
- **Product / Release / Version** — deployable software / published versioned artifact + metadata / orderable version.
- **Entity / Environment** — one installed Product in one Environment / a grouping of Entities in one cluster.
- **Release Channel** — named promotion tier Environments subscribe to.
- **Recall** — signal that a Release is bad; triggers roll-off.
- **Marketplace Product / Store / Linked products** — bundle of Foundry resources / collection of products / one-way upstream→downstream links.
- **Foundry DevOps** — the packaging/release-management app feeding Marketplace.
- **Rubix** — Palantir's hardened, autoscaling Kubernetes substrate.
- **Compute mesh** — the 300+ microservice, zero-trust, autoscaling fabric.
- **Enrollment** — an Organization's primary Foundry identity.

## 13. Recommendations for a clone

**Stage 1 — control-plane core first:** a central Hub (Product catalog + Environment settings + an Orchestration Engine) and a thin Spoke agent that *polls* and reports outbound-only. Adopt the **no-target-state, constraint-satisfaction** model rather than desired-state GitOps — the single most distinctive choice, decoupling "what releases exist" from "what each environment may run." Per-Environment signed certs from day one.
**Stage 2 — model Products/Releases/Versions/Entities/Environments** with Maven coordinates, orderable versions, immutable manifests, declarative dependency/incompatibility extensions.
**Stage 3 — promotion + recall:** Release Channels, health/soak-gated pipelines (2× soak timeout, 7-day canary defaults), automatic recall/roll-off; multi-node blue/green for zero-downtime.
**Stage 4 — packaging/marketplace last:** auto-resolve dependencies into "inputs," support linked products, delegate all execution to the orchestrator.
**Threshold that changes the plan:** if your targets are all connected single-tenant public-cloud SaaS, the full Hub-and-Spoke + air-gap machinery is over-engineering — a desired-state GitOps tool + a packaging layer suffices. Apollo's model earns its complexity only for *many heterogeneous, intermittently-connected, independently-accredited* environments. **(This is us: drop it.)**

## 14. Caveats & Gaps Register

**High-confidence [Documented]:** Hub-and-Spoke; Orchestration Engine; Plan/Constraint mechanics; Product/Release/Version/Entity/Environment; Maven coordinates; promotion soak/health/timeouts; recall/roll-off; blue/green; Marketplace packaging/inputs/linked products/stores; DevOps; Rubix features; 300+ microservices; cloud footprint; Gotham↔Foundry type mapping; the four Spoke Control Plane services.

**Known unknowns / conflicts:** exact count of Hub-side microservices [Gap]; "Central Observability" thinly sourced [Speculative]; Rubix internal scheduler internals [Gap]; `service.v1` current vs legacy [Conflict]; `configuration.yml` (beta/legacy) [Conflict]; **48h node vs 72h container cycle** [Conflict — likely node vs container, unreconciled]; Apollo launch year 2020 vs 2022 [Conflict]; third-party framing used for corroboration only.

## 15. Source Bibliography (by tier; accessed June 13, 2026)

**Tier 1 — Apollo docs:** /docs/apollo/core/{overview, how-apollo-works, environments, agents, spoke-control-plane, plans-and-constraints, release-channels, products-releases-versions, entities}; /apollo-getting-started/{welcome, introduction-promotion, introduction-recall, glossary, introduction-install}; /apollo-product-specification/{spec, manifest, product-types, product-versions, product-dependencies, product-incompatibilities, health}; /managing-release-channels/configure-promotion-pipeline; /managing-products/tracking-product-releases; /recalling-releases/*; /apollo-cli; /managing-environments/{connect-new-environment, spoke-environment-prerequisites}.
**Tier 1 — Foundry docs:** /architecture-center/{overview, platforms, rubix, multimodal-data-plane, aip-architecture}; /marketplace/{overview, foundry-products, browse-products, linked-products, install-product}; /foundry-devops/{overview, supported-resources}; /devops-release-management/*; /object-link-types/enable-gotham-integration; /resource-management/*; /object-backend/overview.
**Tier 2 — Palantir blog/whitepapers:** "Palantir Apollo: Powering SaaS where no SaaS has gone before" (2020); "Introducing Rubix: Kubernetes at Palantir"; "The Benefits of Running Kubernetes on Ephemeral Compute"; "Using Envoy for Egress Traffic"; "Hardening Palantir's Kubernetes Infrastructure with Cilium"; Apollo Technical White Paper (2022); palantir.com/rubix.
**Tier 3 — Partner/cloud & trade press:** Oracle "Run Palantir Foundry and AIP on OCI"; The Register (Palantir–Oracle, 2024); System Soft Technologies; engineering blogs — corroboration only.
