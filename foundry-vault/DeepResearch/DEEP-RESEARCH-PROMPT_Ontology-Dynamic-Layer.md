# Deep Research Prompt — Reverse-Engineering Foundry's Ontology *Dynamic Layer*

**What this is:** the eighth prompt, completing the Ontology trilogy. After the **semantic** layer (*what exists*) and the **kinetic** layer (*what can happen*), this targets the **dynamic** layer — the Ontology's forward-looking, simulatable, time-aware dimension that makes it a *living, projectable* digital twin rather than a static record.

**How to use it:** paste everything below the line into any deep-research tool. Tool-agnostic. The **Confirmed starting leads** give real entry points. Keep role, scope, question bank, methodology, and output spec; trim the seed list if input is tight.

**Scope note:** the *dynamic* dimension only — Scenarios, models/simulation/optimization, the temporal axis, and live behavior. The semantic and kinetic layers are reconstructed separately and are out of scope except where the dynamic layer *builds on* them (scenarios apply actions; models back properties).

---

# ▼▼▼ PASTE FROM HERE ▼▼▼

## Role

You are a senior platform-architecture researcher and reverse-engineer specializing in simulation engines, model-serving/MLOps systems, temporal/bitemporal data, and "digital twin" architectures. You are rigorous, source-driven, and allergic to marketing language. Your task is to reconstruct the internal design of the **dynamic layer of Palantir Foundry's Ontology** — the mechanisms by which the Ontology supports hypothetical futures (**Scenarios**), model-driven projection (**simulation, optimization, forecasting**), a **temporal** view of state over time, and **real-time** liveness.

## Objective

Produce an **exhaustive, citation-backed technical reconstruction** of how Foundry turns a static object model into a *living, simulatable* one: how Scenarios fork the Ontology and stage uncommitted edits, how models are integrated and served to drive simulation/optimization, how time-series and temporal state are represented and projected, and how the digital twin stays live — detailed enough that a competent team could use it as the functional-and-architectural reference to build a faithful (appropriately simplified) clone of this layer. **Prioritize concrete mechanics** (the scenario fork/overlay model and its edit semantics, model-integration and live-deployment mechanics, the temporal/time-series representation, commit/compare behavior, limits) over conceptual or promotional description.

## Precise scope

**In scope:**
- **Scenarios** — the core. A Scenario as a **fork/branch of the Ontology**: a sandboxed overlay containing only the *changes* from the base (modified/created/deleted objects, created/deleted links). How edits enter a scenario via **Action Types** and via **models (Functions on Models)**; scenario **immutability** (modify = new scenario); **comparison** (scenario vs. baseline, scenario vs. scenario); **committing/merging** a scenario back to reality; **scenario-backed object sets** and how apps read "in" a scenario; storage model (overlay, not a copy); permissions/sharing; documented **limits** (e.g., the ~30,000-edit cap) and performance.
- **Models & Modeling Objectives** — the model artifact (ML, forecasting, **optimization**, physical models, business rules); the **Modeling Objective** lifecycle (train → evaluate → release → deploy → monitor); model integration into the Ontology; **model-backed object properties**; **inference history**/governance.
- **Functions on Models & Live deployments** — exposing a model as a **Function** consumable by actions, scenarios, and derived properties; **Live deployments** (low-latency serverless REST inference) vs. batch inference; how a model's output becomes object/scenario state.
- **Simulation & optimization** — running models/solvers over the Ontology to project outcomes; **optimization** (e.g., route/inventory solvers) and Monte-Carlo-style simulation; chaining model outputs as scenario inputs; **simulated overrides** to time-series inputs.
- **Temporal / time dimension** — **time-series properties** (as model inputs/outputs), **geotemporal series** (tracks), **event** object types, object **edit history** as a temporal record; current vs. historic vs. predicted state; any "as-of"/versioned/temporal read semantics.
- **Real-time liveness** — streaming-backed object liveness and **auto-refresh** at the Ontology level; the always-current digital twin (touch the seam to the data/app layers, don't re-derive them).
- **Dynamic security** — access that varies with object state/time (e.g., mandatory-control properties driven by data values), insofar as it's a *dynamic* behavior.
- **Consumer surfaces & synthesis** — **Vertex** (graph + scenario analysis) and **Quiver** (time-series + scenario/simulation analysis) as the apps where the dynamic layer is used; how scenarios + models + time compose into the "digital twin."
- **APIs/SDK & internals** — scenario RIDs/APIs, model-deployment APIs, OSDK scenario support, and the named internal services (verify).

**Out of scope** (touch only at the seam): the static semantic model and the base action/function mechanics (already reconstructed — but scenarios *use* actions and models, so that seam is in scope); the data-pipeline streaming plumbing (covered — cover only the Ontology-level live behavior); AIP agents (covered — only the models-as-tools seam); app-widget construction (covered — scenario/Quiver/Vertex widgets are the consumer surface, not the focus).

## Research question bank

Answer every question you can substantiate; record the rest as known unknowns.

**A. Scenarios — anatomy & edit semantics**
1. What *is* a Scenario, precisely? Substantiate the "**fork/branch of the Ontology**" model and that it stores **only the diff** (modified/created/deleted objects + links) over the base.
2. How do edits enter a scenario — via **Action Types**, via **models/Functions on Models**, via manual edits? What edit kinds are supported?
3. The **storage/overlay** model: is a scenario a lightweight overlay computed at read time, or a materialized copy? How are reads resolved "within a scenario"?
4. **Immutability**: substantiate that a scenario is immutable once created and that "modifying" means creating a new one. Why this design?

**B. Scenarios — compare, commit, lifecycle, limits**
5. **Comparison**: scenario vs. baseline and scenario vs. scenario — what's compared and how is it surfaced?
6. **Committing/merging** a scenario back to the real Ontology — the mechanism (does it replay the staged actions? apply the diff via writeback?), permissions, and validation.
7. **Scenario-backed object sets**: how an app/query reads objects "as of" a scenario; layering multiple scenarios.
8. **Limits & performance**: the documented edit cap (~30,000), scaling behavior, and any latency characteristics.
9. **Permissions/sharing/lifecycle** of scenarios (who can create/see/commit; expiry).

**C. Models & Modeling Objectives**
10. The **model** artifact: the documented span (ML, **forecasting**, **optimization**, **physical models**, **business rules**) and how each is represented.
11. The **Modeling Objective** lifecycle: train → evaluate → release → deploy → monitor; versioning; release/staging.
12. **Model-backed object properties** and **inference history** (what's recorded, governance).

**D. Functions on Models & Live deployments**
13. **Functions on Models**: how a model is wrapped as a Function and consumed by actions, scenarios, and derived properties.
14. **Live deployments**: the serverless REST inference endpoint, latency profile, autoscaling, and how interactive inference feeds scenarios; batch vs. live.

**E. Simulation & optimization**
15. How **simulation** is run over the Ontology (models applied to objects, outputs staged as a scenario); Monte-Carlo / probabilistic patterns.
16. **Optimization**: solver integration (e.g., route/inventory optimization), inputs/outputs, and how results land as scenario edits.
17. **Simulated overrides** to time-series and how projected/calculated time-series outputs are compared to actuals.

**F. Temporal / time dimension**
18. **Time-series properties** and **geotemporal series** (tracks): representation, as model inputs/outputs, and querying.
19. **Event** object types and the modeling of change-over-time; **edit history** as a temporal record.
20. Any **temporal / "as-of" / versioned** read semantics — can you query the Ontology's state at a past time?

**G. Real-time liveness & dynamic security**
21. **Ontology-level liveness**: streaming-backed objects + **auto-refresh**; what "always current" means and its guarantees.
22. **Dynamic security**: access that changes with object state/time (data-driven mandatory controls); how dynamic this actually is.

**H. The digital-twin synthesis & consumer surfaces**
23. How **Scenarios + models + time + live data** compose into the documented "**digital twin**" — the end-to-end story.
24. **Vertex** (graph/scenario analysis) and **Quiver** (time-series/simulation analysis): what dynamic-layer capabilities each exposes.

**I. APIs/SDK, internals & history**
25. **Scenario APIs/RIDs**, **model-deployment APIs**, and **OSDK** scenario/inference support — request/response shapes where available.
26. The named **internal services/architecture** behind scenarios and model serving (verify).
27. **History/evolution** of Scenarios, model integration, and live deployments; any **patents** touching scenario/simulation/digital-twin methods.

## Source strategy (prioritized)

1. **Primary — official docs:** `palantir.com/docs/foundry/**`, especially `workshop/scenarios-*`, `vertex/scenarios-*`, `quiver/**`, `model-integration/**` (overview, objectives, models), `manage-models/**` (objectives, live deployments, inference history), `functions/functions-on-models`, `time-series/**`, `geotemporal-series/**`, and the `api` reference for scenarios/models.
2. **Primary — blog & talks:** `blog.palantir.com`; Palantir Developers / AIPCon (scenarios, simulation, digital-twin, optimization demos); the NVIDIA cuOpt collaboration.
3. **Primary — source & API refs:** `github.com/palantir`; the API/OSDK reference.
4. **Primary — patents & training:** Google Patents / USPTO (simulation / scenario / digital-twin methods); `learn.palantir.com`.
5. **Secondary/Tertiary:** credible third-party deep-dives; community — leads/corroboration only.

Prefer primary, recent, version-stamped sources; capture URL + access date.

## Reverse-engineering methodology & rigor

- **Triangulate** non-trivial claims across ≥2 sources where possible.
- **Tag every claim** — **[Documented]** / **[Inferred]** / **[Speculative]** — with **confidence** (High/Med/Low) and an inline citation.
- **Separate current from legacy**; date-stamp version-specific facts; flag in-development features.
- **Flag contradictions** explicitly.
- **Never fabricate** scenario semantics, model-serving mechanics, limits, or service names. Where the record is silent (e.g., the scenario overlay's storage internals, the live-deployment runtime), say so and give one best-supported hypothesis labeled **[Speculative]**.
- **Chase named mechanisms** to source: **Scenario** (fork/branch, sandboxed edits, immutability, ~30k-edit cap, commit), **Modeling Objective**, **Model**, **Functions on Models**, **Live deployment**, **time-series property**, **geotemporal series**, **Vertex**, **Quiver**.

## Required output structure

1. **Executive summary** (≈1 page) + the 5–10 most important findings.
2. **Scenarios** *(most technical)* — the fork/overlay model, edit semantics, compare/commit, limits.
3. **Models & Modeling Objectives** — the artifact span + lifecycle.
4. **Functions on Models & Live deployments** — model serving into the Ontology.
5. **Simulation & optimization** — projecting outcomes over the Ontology.
6. **Temporal / time dimension** — time-series, geotemporal, events, as-of reads.
7. **Real-time liveness & dynamic security.**
8. **The digital-twin synthesis & consumer surfaces** (Vertex, Quiver).
9. **APIs / SDK & internal architecture.**
10. **History & patents.**
11. **Glossary.**
12. **Confidence & gaps register** — claims + confidence, plus a known-unknowns list and the source that would resolve each.
13. **Source bibliography** — URLs + access dates, by tier.

Use **tables** for enumerations (scenario edit kinds, model types, limits, API endpoints). Favor precise mechanics over prose. Quote exact limits/semantics **verbatim** where they exist.

## Exhaustiveness bar

Do **not** stop at the overview. Drill until each mechanism is concretely described with a primary citation or recorded as a known unknown with a best-supported hypothesis. Pay special attention to the **scenario fork/overlay + commit semantics**, **how models feed scenario state**, and the **temporal read model** — the make-or-break details for a clone. Aim for a detailed technical white paper; cite extensively; neutral tone.

## Confirmed starting leads (verified — begin here, then expand)

- **Scenarios:** `palantir.com/docs/foundry/workshop/scenarios-overview`, `…/workshop/scenarios-concepts`, `…/vertex/scenarios-overview` — a Scenario is a **fork/branch** of the Ontology generated by applying **actions** (optionally leveraging **models via Functions on Models**); the fork contains **only the edits** (modified/created/deleted objects + links); simulated outputs are **staged as ontology scenarios** in a **sandboxed subset**; a Scenario is **immutable once created**; **a single Scenario cannot make more than 30,000 edits**.
- **Models & Modeling Objectives:** `…/model-integration/overview`, `…/model-integration/objectives`, `…/model-integration/models` (a model = "an artifact for inference that contains machine learning, forecasting, optimization, physical models, or business rules"); `…/manage-models/create-a-modeling-objective`, `…/manage-models/model-inference-history`. **Objectives** "enable the complete model lifecycle … including simulation and optimization."
- **Functions on Models & Live deployments:** `…/functions/functions-on-models`; **Live deployments** = a "serverless REST API endpoint that can be interactively queried," integrable into scenario analyses/simulations.
- **Temporal:** `…/time-series/*`, `…/geotemporal-series/data-modeling`; events modeled as object types; objects persist through time (edit history captures change).
- **Optimization partner thread:** the NVIDIA **cuOpt** collaboration (from the AIP reconstruction).

**Named mechanisms to chase:** **Scenario** (fork/branch · sandboxed edits · immutable · 30k-edit cap · compare · commit · scenario-backed object set) · **Modeling Objective** · **Model** (ML/forecasting/optimization/physical/rules) · **Functions on Models** · **Live deployment** (serverless REST inference) · model-backed property · **inference history** · **time-series property** · **geotemporal series** · **Vertex** · **Quiver** · *(verify)* scenario **storage/overlay** internals · *(verify)* scenario **RID** + commit mechanism · *(verify)* temporal/"as-of" read support · *(find)* simulation/digital-twin **patents**.

# ▲▲▲ PASTE TO HERE ▲▲▲
