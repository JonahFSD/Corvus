---
**Artifact:** Deep-research output — technical reconstruction of Foundry's Ontology *dynamic layer* (Scenarios, models / simulation / optimization, the temporal axis, and live behavior). Completes the Ontology trilogy after the *semantic* (what exists) and *kinetic* (what can happen) layers.
**Produced:** 2026-06-13, by a deep-research agent run on `DEEP-RESEARCH-PROMPT_Ontology-Dynamic-Layer.md`.
**Independent spot-check (by Claude, 2026-06-13):** Every load-bearing, falsifiable claim checked **confirmed verbatim** against primary docs (`palantir.com/docs`); none contradicted. Specifically:
- **Scenario = delta-only fork** and **immutable** — verbatim at `workshop/scenarios-concepts`: "The fork contains only the edits or changes from the base Ontology including modified Object properties, created Objects, deleted Objects, created link types, and deleted link types" and "A Scenario is immutable once created."
- **Hard caps** — verbatim at `workshop/scenarios-concepts`: "A single Scenario cannot make more than 30,000 edits to the Ontology"; "cannot contain more than 50 Actions"; "you cannot load more than 10,000 objects."
- **Commit = transactional Action replay; model results not written back** — verbatim at `workshop/scenarios-apply`: Actions "applied to the Ontology transactionally, such that either all of the Actions will be applied or none of them will be applied if there is a validation failure," and "Model results in a Scenario will not be applied to the Ontology."
- **Live deployments = serverless REST** — confirmed at `manage-models/create-a-model-deployment` & `live-deployment-reference`: "serverless REST API endpoint," "highly available," CI/CD without downtime, autoscale at 75% capacity, scale down after 30 minutes idle, scale-from-zero, endpoint `…/foundry-ml-live/api/inference/transform/ri.foundry-ml-live.<RID>/v2`.
- **Functions-on-models limits** — confirmed at `functions/functions-on-models`: 50 MB I/O, 30 s total execution.
- **NVIDIA cuOpt collaboration** — confirmed: announced **Oct 28, 2025**, GTC Washington D.C., **Lowe's** launch customer (NVIDIA newsroom / GlobeNewswire press release).
- **Patent 12,282,997** ("Generating simulation scenarios and digital media using digital twins") — the report's **negative finding is correct**: assignee is **Duality Robotics, Inc. / Duality AI**, inventors Apurva Shah & Thomas Henry — **not Palantir** (Justia; Duality AI's own announcement). Do not attribute it to Palantir.

**Read with care — caveated / unresolved (land in the report's `[Speculative]` / gaps register, exactly as predicted):** the scenario **overlay internals** (read-time merge vs. materialized store), the **scenario RID prefix**, any **named scenario backend service**, an **OSDK create/read-scenario** API, and a **general "as-of" / bitemporal Ontology read** — no primary doc resolves any of these; treat the report's hypotheses as design starting points, not facts. Minor naming nuance: the report cites "Nemotron"; NVIDIA's release also foregrounds "NeMo Retriever" open models — the *substance* of the collaboration (cuOpt for dynamic supply-chain optimization, Lowe's) is confirmed regardless. The numeric caps (30k/50/10k, 50 MB/30 s, 75%/30 min) are Palantir-scale artifacts, not requirements for our clone.
---

# The Dynamic Layer of Palantir Foundry's Ontology: A Technical Reconstruction for Cloners

## TL;DR

- Foundry's dynamic layer is built on four interlocking primitives: **Scenarios** (immutable, delta-only forks of the Ontology produced by replaying Actions and evaluating Models), **Models + Modeling Objectives** (a governed train→evaluate→release→deploy→monitor lifecycle), **Functions on Models / Live deployments** (serverless REST inference wrapped as callable Functions), and a **temporal/time-series + streaming-liveness substrate** — composed by **Vertex** (graph/scenario) and **Quiver** (time-series) into a simulatable digital twin.
- The single most important mechanic for a faithful clone: a Scenario stores **only the diff** (modified properties, created/deleted objects, created/deleted links) over the base Ontology, is **immutable once created**, is capped at **30,000 edits / 50 Actions / 10,000 objects loaded**, and is **committed by replaying its staged Actions transactionally (all-or-nothing)** — model outputs in a scenario are NOT written back.
- The deepest unknowns (not in public docs): the Scenario RID prefix, the named scenario backend service, whether the overlay is resolved at read time vs. materialized, and any OSDK create/read-scenario API. These must be reconstructed by inference; best-supported hypotheses are given and flagged [Speculative].

---

## 1. Executive Summary & Key Findings

The Foundry Ontology is described by Palantir as a "digital twin of an organization," explicitly partitioned into **semantic** (objects, properties, links), **kinetic** (actions, functions, dynamic security), and what this report treats as the **dynamic** layer — the forward-looking, time-aware, simulatable dimension. The dynamic layer does not introduce a new storage primitive so much as it composes the kinetic layer (Actions, Functions) and model-serving infrastructure over a temporal/streaming data substrate, exposed through what-if Scenarios and the Vertex/Quiver analytical surfaces.

**Most important findings (for a cloning team):**

1. **A Scenario is a delta-only fork.** [Documented, High] "The fork contains only the edits or changes from the base Ontology including modified Object properties, created Objects, deleted Objects, created link types, and deleted link types." Build the overlay as a copy-on-write delta keyed on the base object/link identity, not a full copy.
2. **Scenarios are immutable.** [Documented, High] "A Scenario is immutable once created. To 'modify' a Scenario, create a new Scenario with a modified set of Actions or Models." Implement scenarios as append-only / versioned artifacts.
3. **Edits enter via Actions (current) and Function-backed Actions wrapping Models (current); legacy direct-model evaluation is deprecated.** [Documented, High]
4. **Commit = transactional Action replay.** [Documented, High] "Applying a Scenario applies the Actions associated with the Scenario to the Ontology. These Actions are applied transactionally, such that either all of the Actions will be applied or none of them will be applied if there is a validation failure on any of the actions." Model results are explicitly NOT applied.
5. **Hard limits:** 30,000 edits per scenario; ≤50 Actions; ≤10,000 objects loadable in a scenario context; attachment properties unsupported. [Documented, High]
6. **Models span ML, forecasting, optimization, physical models, business rules** — a single artifact abstraction "for inference." [Documented, High]
7. **Modeling Objectives provide the lifecycle** (submit→evaluate→release with Staging/Production tags→deploy) and a CI/CD layer with zero-downtime deployment. [Documented, High]
8. **Live deployments are serverless REST inference endpoints** with autoscaling (scale from zero; +1 replica at 75% capacity; scale-down after 30 min idle), wrapped as Functions on Models and consumable by Actions/Scenarios. [Documented, High]
9. **Temporal substrate:** time-series properties (TSP), geotemporal series (tracks), event object types, and immutable edit-history changelogs give the layer its time dimension; streaming-backed OSv2 object types + Workshop auto-refresh give liveness. [Documented, High]
10. **Vertex** (system-graph / scenario simulation, model chaining/"model mesh") and **Quiver** (time-series analysis + interactive forecasts) are the consumer surfaces. [Documented, High]

---

## 2. Scenarios (the most technical section)

### 2.1 What a Scenario IS

A Scenario is "essentially a 'fork' or 'branch' of the data in your Ontology generated by applying one or more actions, which can optionally leverage models through functions on models." [Documented, High — workshop/scenarios-overview]

The canonical concept definition: "A Scenario is fork of the data in the Ontology created by applying a set of Actions and evaluating a set of Models. The fork contains only the edits or changes from the base Ontology including modified Object properties, created Objects, deleted Objects, created link types, and deleted link types." [Documented, High — workshop/scenarios-concepts]

**Cloning implication:** the scenario store is a **diff/overlay** keyed to base-Ontology identity. The diff records: (a) property mutations on existing objects, (b) created objects, (c) deleted objects, (d) created links, (e) deleted links. It does NOT snapshot the whole object graph.

### 2.2 Edit kinds & how edits enter

| Edit entry path | Status | Mechanism |
|---|---|---|
| Action Types applied "to Scenario" | Current | Workshop "Apply to Scenario" toggle on a Button Group action; action writes to the scenario overlay, not base Ontology |
| Model via Function-backed Action | Current | Model wrapped in a Function on Model, invoked inside a Function-backed Action |
| Direct model evaluation in scenario (via Modeling Objective live deployment) | **Deprecated/legacy** | "It was previously possible to evaluate a model in a Scenario without wrapping it in an Action… This feature has been deprecated" |
| Manual edits (Workshop widgets) | Current | Edits in Scenario-aware widgets staged as proposed changes, not written to Ontology |

Supported diff kinds: modified object properties, created objects, deleted objects, created links, deleted links. **Attachment properties are not supported** "since uploaded files will not be registered to the referencing objects." [Documented, High]

### 2.3 Storage / overlay model

**[Documented]** The scenario stores only the delta and is built on Actions infrastructure: "Since Scenarios infrastructure is built on top of Actions, any limits applied by Actions also apply to the Actions in your Scenario." A confirmed read constraint: "When loading object data from an object set in the context of a Scenario, you cannot load more than 10,000 objects."

**[Known unknown]** Public docs do NOT state whether the overlay is resolved at read time (overlay merged onto base reads on the fly) or materialized into a temporary store, nor do they name a dedicated scenario backend service, nor expose a scenario RID prefix. The public Load Object Set API exposes only `branch` and `transaction` context parameters — no `scenarioRid`/`scenario` parameter. A Palantir staff forum statement confirms scenarios do not propagate through object sets: scenario state must be referenced explicitly via a Workshop "scenario variable" — "there's no way for an object set itself to carry scenario metadata and make downstream consumers automatically scenario-aware."

**[Speculative, Med] Best-supported hypothesis on overlay internals:** Because Scenarios are "built on top of Actions," and Actions apply user edits into object databases (Object Storage V2 via the Actions service, with Funnel orchestrating durable writes), the most likely implementation is that a scenario is an **in-memory / session-scoped edit batch** (a named set of staged Action edits) that the Object Set Service overlays at read time when a scenario identifier is supplied as query context — analogous to, but distinct from, Foundry Global Branching. The 10,000-object read cap and 30,000-edit write cap are consistent with a read-time merge that must hold the delta in bounded memory rather than a fully materialized branch. This is unverified and should be treated as a design starting point, not fact.

### 2.4 Immutability

"A Scenario is immutable once created. To 'modify' a Scenario, create a new Scenario with a modified set of Actions or Models. You can also duplicate a Scenario along with its existing Actions and parameters." [Documented, High]

**Why this design (inferred):** Immutability makes scenarios safely shareable and comparable artifacts, gives deterministic reproducibility (re-running the same staged Actions/Models yields the same fork), and sidesteps concurrent-mutation conflicts. [Inferred, Med]

### 2.5 Comparison: scenario vs. baseline and scenario vs. scenario

Workshop's Scenario-aware widgets (Object Table, Chart XY) support **an arbitrary number of scenarios** displayed side-by-side; the Object Table shows scenario values "only in columns that differ," and the Chart XY places different scenarios "in different layers." [Documented, High — workshop/scenarios-getting-started] Dedicated widgets: **Scenario Manager**, **Scenario Selector**, **Scenario Summary**.

In **Vertex**, an optional **baseline scenario** runs "the models you have chosen without any actions or overrides, providing you with a baseline against which to compare." Override values "show the newly calculated outputs for comparison to the baseline scenario." [Documented, High — vertex/scenarios-options, vertex/scenarios-getting-started]

### 2.6 Committing / merging a scenario back

"Applying a Scenario applies the Actions associated with the Scenario to the Ontology. These Actions are applied transactionally, such that either all of the Actions will be applied or none of them will be applied if there is a validation failure on any of the actions. Note that Model results in a Scenario will not be applied to the Ontology as these represent expected results rather than explicitly modifiable values." [Documented, High — workshop/scenarios-apply]

**Mechanism:** commit is a **replay of staged Actions**, not a blob-diff writeback. **Permissions:** "the user must be able to run the configured apply Action in order to be able to apply a Scenario"; an optional post-apply Action's validation logic gates apply permissions. **Saved-scenario binding:** the type class `scenarios:scenario-object-locator` on an apply Action's object parameter auto-populates with the object backing the saved scenario. [Documented, High]

### 2.7 Scenario-backed object sets & layering

A Workshop Object Table with "scenario comparison" enabled, fed a Scenario array variable from the Scenario Manager, "will cause the data in the table to reflect any modifications to Scenarios in the Manager rather than the raw Ontology." [Documented, High] In Vertex graph widgets, "Load data from scenario" toggles the resource to load via a scenario instead of the base Ontology, with "Regenerate graph after applying scenario." Multiple scenarios can be layered in a single widget. [Documented, High]

### 2.8 Limits & performance (verbatim)

| Limit | Value (verbatim) |
|---|---|
| Edits per scenario | "A single Scenario cannot make more than 30,000 edits to the Ontology." |
| Actions per scenario | "Your Scenario cannot contain more than 50 Actions." |
| Object load in scenario context | "you cannot load more than 10,000 objects. Attempting to load more than 10,000 objects will result in an error." |
| Function-backed Action | "subject to the limitations that exist on Foundry Functions" |
| Action limits | inherited transitively ("any limits applied by Actions also apply") |
| Attachments | "Attachment properties are not supported in Scenarios" |

No published latency SLAs; the caps are framed "For performance reasons." [Documented, High]

### 2.9 Permissions / sharing / lifecycle

Saved scenarios are persisted as Ontology objects implementing the **Scenario trait** (type classes `scenarios:versioned-scenario-rid` on the ID/primary-key property and `scenarios:scenario-name` on the title). Saving requires the Editor role. Scenarios are loaded by converting an object set of Scenario-trait objects into a Scenario array variable ("Scenario loaded from object set"), enabling search-around/filtering and sharing. [Documented, High — workshop/scenarios-save, scenarios-load]

---

## 3. Models & Modeling Objectives

### 3.1 The model artifact

"In Foundry, a model is an artifact for inference that contains machine learning, forecasting, optimization, physical models, or business rules." A Model resource comprises **model artifacts** (weights/container) plus an **adapter** "published as part of a Python library… It enables the platform to load, initialize, and run inference on any kind of model." [Documented, High]

| Model type | Representation |
|---|---|
| Machine learning | Trained weights/container + adapter |
| Forecasting | Same artifact abstraction |
| Optimization | Container encapsulating solver logic (e.g., cuOpt LP/MILP/VRP) |
| Physical models | Container encapsulating equations |
| Business rules | Containerized executable logic (Foundry Rules) |

### 3.2 Modeling Objective lifecycle

Modeling Objectives are the "mission control" providing a governance/permissions layer, an automation layer (uniform evaluation), and a CI/CD layer for "continuous and downtime-free deployment." [Documented, High]

Lifecycle: **Submit** (immutable copy, "akin to a code Pull Request") → **Evaluate** (MetricSets via evaluation libraries on evaluation datasets) → **Release** (versioned, packaged, production-ready, with environment tags such as "Staging"/"Production" + version number + release note) → **Deploy** (batch or live; "a deployment with a 'Production' environment will take the latest tagged 'Production' release"). Objectives "enable the complete model lifecycle for any modeling problem… including those not traditionally addressed by ML Ops tools, such as simulation and optimization." [Documented, High]

### 3.3 Model-backed properties & inference history

The **model inference history** is "a dataset in Foundry that captures all inference requests (inputs) and inference results (outputs) that are sent to a Modeling Objective live deployment." It requires the gatekeeper permission `foundry-ml-live:edit-inference-ledger` (typically the "owner" role), must be saved to the same project as the parent objective (sensitive I/O), and supports drift detection, continuous retraining, and performance evaluation. "Not all inputs and outputs are guaranteed to appear in the inference history." [Documented, High]

---

## 4. Functions on Models & Live Deployments

### 4.1 Functions on Models

"Model functions are automatically generated wrappers around live model deployments that can be imported into a functions repository and called from your code." They mirror the model's API using Function-supported types and "are simple wrappers that defer all logic to the underlying live deployment." Publishable from (a) direct model deployments or (b) Modeling Objective live deployments; one function per branch. A new model version on the branch auto-creates a new function version; API changes require manual republish of consumers. Supported in TS v1, TS v2, and Python. [Documented, High]

**Limits:** "When calling live deployments, model input and output data is sent through the network with an upper limit of 50 MB… the total execution time of the function cannot exceed 30 seconds." [Documented, High]

### 4.2 Live deployments (serverless REST inference)

"For low-latency or interactive settings, models can be served via Live deployments, which provide a serverless REST API endpoint that can be interactively queried. Live endpoints can be independently permissioned, and executed with configured replication and resources. They are also highly available, meaning models can be updated via CI/CD without incurring endpoint downtime." [Documented, High]

| Property | Detail (verbatim/near-verbatim) |
|---|---|
| Endpoint shape | `<ENV_URL>/foundry-ml-live/api/inference/transform/ri.foundry-ml-live.<LIVE_DEPLOYMENT_RID>/v2` |
| v2 vs v1 | Multi I/O ("v2") endpoint preferred; Single I/O ("v1") sunset |
| Auth | `Authorization: Bearer <BEARER_TOKEN>`; `Content-Type: application/json` |
| Autoscaling | "When the deployment reaches 75% capacity, it will create an additional replica until it reaches the maximum replica count"; "scale down after 30 minutes without a live request"; "scale from zero" |
| Resources | Configurable replica count + CPU/GPU counts |
| Backing | Direct model deployments "backed by compute modules… support automatic horizontal scaling"; live deployments now ship with JDK + local Spark |
| Errors | "503: The service or deployment is unavailable… Retry with backoff." |
| Batch alternative | Batch deployments run models within a pipeline on an input dataset → output dataset, via build schedules |

Live deployments feed scenarios: "You can also integrate models into scenario analyses and simulations." [Documented, High]

---

## 5. Simulation & Optimization

### 5.1 Simulation over the Ontology

In Workshop, simulation = applying Function-backed Actions (which may invoke models) to a scenario overlay and comparing. In Vertex, "a scenario evaluates actions along with one or more modeled inputs and computes the output value to reflect the real-world interactions of your digital twin." Vertex chains models — "automatically chain these together to forward the outputs of one model as the inputs to another" — described elsewhere as Vertex's **"model mesh"** / **"simulation mesh"** infrastructure that "allows for continuous evaluation of the expected behavior of the asset by flowing through real-time sensor and asset configuration data." (Model chaining is in the **sunset** phase; the recommended path is functions + function-backed Actions.) [Documented, High; chaining sunset noted]

Vertex inputs/overrides: a scenario specifies a time window; supports time-series smoothing over minute periods; inputs can be overridden by editing values in the scenario table; outputs compared to baseline. [Documented, High]

### 5.2 Optimization & the NVIDIA cuOpt collaboration

Optimization is treated as a model type. The **NVIDIA cuOpt** collaboration integrates GPU-accelerated decision optimization into Foundry/AIP. Per NVIDIA's product page, cuOpt is "an open source, GPU-accelerated engine for decision optimization, excelling in mixed-integer programming (MIP), linear programming (LP), vehicle routing problems (VRPs), and quadratic programming (QP)."

The Palantir–NVIDIA collaboration was announced **October 28, 2025 at GTC Washington, D.C.** Per the NVIDIA newsroom: "NVIDIA today announced a collaboration with Palantir Technologies Inc. to build a first-of-its-kind integrated technology stack for operational AI." NVIDIA CEO Jensen Huang: "We're creating a next-generation engine to fuel AI-specialized applications and agents that run the world's most complex industrial and operational pipelines." The release states "NVIDIA cuOpt decision optimization software, will enable enterprises to use AI for dynamic supply-chain management," integrated alongside "NVIDIA CUDA-X libraries and open-source NVIDIA Nemotron models into [Palantir's] Ontology framework at the core of the Palantir AI Platform."

The reference launch customer is **Lowe's**. Per Lowe's EVP and chief digital and information officer Seemantini Godbole (Oct 28, 2025 release): "Even small shifts in demand can create ripple effects across the global network. By combining Palantir technologies with NVIDIA AI, Lowe's is reimagining retail logistics, enabling us to serve customers better every day." Palantir's blog frames the shift as moving "from optimizing individual nodes once a week to continuous, dynamic optimization at a global level." Use cases: inventory rebalancing, vehicle routing, dynamic re-routing on disruptions. [Documented, High]

**How optimizer results land as scenario edits (inferred):** an optimization model wrapped as a Function on Model, invoked in a Function-backed Action, stages its recommended changes (e.g., new routes/allocations) as scenario edits for comparison before transactional apply. [Inferred, Med]

### 5.3 Simulated time-series overrides vs. actuals

Vertex emphasizes shaping measured values "as time series in order to configure these as inputs to your model which will generate calculated time series outputs for comparison… monitor your current state, view historic trends, and predict future changes with simulated overrides to modeled conditions." [Documented, High]

---

## 6. Temporal / Time Dimension

### 6.1 Time-series properties (TSP)

"A time series property is a specific type of object property. While a conventional object property contains a single value… a time series property stores a history of timestamped values." Backed by **time series syncs** (datasets or streams) keyed by `seriesId`; "When Foundry resolves a time series property on a given object… the seriesId contained in the property's value will be searched for within that property's data sources." Requires time-series services (incl. a proprietary time-series compute database). **Derived series** are computed-on-the-fly TSPs stored via Codex template RIDs. [Documented, High]

### 6.2 Geotemporal series (tracks)

"Geotemporal series data is used to track the geographic position of entities over time… conceptually similar to time series except they include a geospatial component." Components: a **geotemporal series object type** + a **geotemporal series sync (GTSS)** referenced via a **geotemporal series reference (GTSR)** property; identified by a **series ID**; individual points are **observations**. Properties are "live" by default or markable "static." Storage options: **live streaming** (real-time, 14-day default retention) or **dataset archive** (persistent historical). Currently **beta**. [Documented, High]

### 6.3 Events & change-over-time

"Events are object types configured in the Ontology that include temporal information—minimally, two timestamps that indicate the start and end of the event." Quiver provides event statistics, comparison plots, and filtering. [Documented, High]

### 6.4 Edit history as a temporal record & as-of reads

**Edit history** (OSv2): "Track user edit history" yields an immutable changelog — "Changelog records are designed for auditing purposes and cannot be deleted or modified by end users, even if the corresponding ontology edits are reverted." Users with access to current state can access full history; disabling permanently deletes history. The complementary **Action Log** models each action submission as an object type (`[LOG]` prefix), linking to all edited objects with userID + timestamp. [Documented, High]

**As-of reads:** The public Load Object Set API exposes an **experimental** `transaction` parameter ("The ID of an Ontology transaction to read from. Transactions are an experimental feature") and a `branch` parameter, plus a `snapshotConsistency` paging flag for consistent views. There is **no documented general-purpose "query Ontology state as of past time T" API**; the temporal record is reconstructable via edit-history/action-log changelogs and time-series history, not a first-class bitemporal read. [Documented for params, High; absence of as-of read, Med]

---

## 7. Real-Time Liveness & Dynamic Security

### 7.1 Ontology-level liveness

OSv2 "supports low-latency streaming data indexing into the Ontology by using Foundry streams as input datasources… on the order of seconds or minutes." Streaming uses a "most recent update wins" changelog strategy with exactly-once (default) or at-least-once (lower-latency) consistency. Constraints: record size ≤1MB, ≤250 properties, MDOs unsupported on streaming object types. **Workshop auto-refresh** (OSv2-only) watches registered object sets and refreshes on Action edits, upstream integration edits, or new streaming records — "all data in the current module will automatically refresh without user interaction." Outside Workshop, "no other Foundry frontend application supports live data refresh." [Documented, High]

**"Always current" guarantee (interpretation):** liveness is per-surface — streaming-backed OSv2 objects index continuously, but UI freshness depends on Workshop auto-refresh (with documented filter-type and on-screen-visibility caveats). It is not a global push-to-every-consumer guarantee. [Inferred, High]

### 7.2 Dynamic security

The Ontology's security is "woven into data, logic, and actions" and reconciled "at the time of interaction." **Mandatory control properties** (OSv2) let an object's property value gate visibility of other properties in the same datasource (markings, organizations, classifications). **Object/property security policies** + **granular policies** deliver row/column/cell-level security evaluated per query. Critically, security is **data-driven and changes with object state**: "Access to an ontology object can be affected by user edits, since it is possible to edit a property that is referenced in the object's security" — e.g., changing an Assignee property can revoke/grant access. Object/property security policies offer "near-instantaneous policy updates" vs. restricted views which need pipeline rebuilds. [Documented, High]

**How dynamic, really:** access genuinely changes with object state and time (e.g., an Action that mutates a policy-referenced property immediately changes who can see the object), and policy changes propagate near-instantly — but group-membership/user-attribute changes are cached briefly. [Documented, High]

---

## 8. Digital-Twin Synthesis & Consumer Surfaces

### 8.1 The end-to-end story

Palantir markets the composition explicitly: "MULTI-MODAL, SEMANTIC DATA → AI/ML-BASED TWINS → TWIN-BASED SIMULATIONS → … SIMULATIONS & SCENARIOS ACROSS YOUR TWIN." The dynamic twin = live/streaming data (liveness) + time-series/geotemporal history (temporal) + models bound to the Ontology (logic) + Scenarios (projection) + transactional Actions (commit). [Documented, High]

### 8.2 Vertex

"Vertex allows you to visualize and quantify cause and effect across the digital twin." It exposes: object-backed **system graphs/diagrams**; **scenario** creation (Actions + model inputs + overrides); **baseline** comparison; model chaining ("model mesh," sunsetting); embeddability in Workshop via the Vertex Graph widget with "Load data from scenario." Dynamic-layer role: interactive what-if simulation across a network of objects/processes. [Documented, High]

### 8.3 Quiver

"Quiver provides a point-and-click interface to perform data analysis on object and time series data," optimized for time series with "a specific time series library with sensor and signal processing functions… backed by a proprietary time series database." Dynamic-layer capabilities: **interactive/visual forecasts** (constant, linear, formula/sinusoidal, with training-time-range fitting and RMSE/MAE metrics), time-series transforms saved as **derived series**, event analytics, analysis-wide **streaming** (rolling windows), and writeback to the Ontology via Actions. An analysis is "a number of cards that can depend on each other, forming an analysis graph." [Documented, High]

---

## 9. APIs / SDK & Internal Architecture

### 9.1 Scenario APIs / RIDs / OSDK

| Item | Finding |
|---|---|
| Scenario RID prefix | **No primary source.** Not documented. (Do not fabricate.) |
| `scenarioRid`/`scenario` param on Load Object Set | **Absent.** API exposes only `branch` + `transaction` context params |
| OSDK create/read scenario | **No documented method.** Scenarios are a Workshop-variable construct; no OSDK `createScenario`/`applyScenario` |
| Saved-scenario persistence | Ontology objects implementing the Scenario trait (`scenarios:versioned-scenario-rid`, `scenarios:scenario-name`) |
| Apply-action binding | type class `scenarios:scenario-object-locator` |
| "No context travel" | Per Palantir staff: scenarios don't propagate through object sets; consumers must reference a scenario variable explicitly |

### 9.2 Model deployment APIs

Live inference: `POST <ENV_URL>/foundry-ml-live/api/inference/transform/ri.foundry-ml-live.<RID>/v2` with JSON body matching the model API; 200 → JSON inference response; 503 → retry with backoff. OSDK consumption is via generated model-function query methods (e.g., `client.ontology.queries.flight_model_deployment(...)`). [Documented, High]

### 9.3 Ontology backend (the substrate scenarios build on)

| Service | Role (verbatim/near) |
|---|---|
| Ontology Metadata Service (OMS) | "defines the set of ontological entities that exist" |
| Object Set Service (OSS) | "responsible for serving reads from the Ontology… searching, filtering, aggregating, and loading of objects" |
| Actions service | "responsible for applying user edits to object databases" |
| Object Data Funnel ("Funnel") | "orchestrating data writes into the Ontology" (OSv2) |
| Object Storage V2 | "next-generation canonical data store"; OSv1/Phonograph deprecated (unavailable after June 30, 2026) |

**No named scenario-specific service** appears in public docs. [Documented for general backend, High; scenario service unknown]

---

## 10. History & Patents

- **Models/Modeling Objectives** are the long-standing MLOps spine; the legacy direct-model-in-scenario evaluation predates the current Function-backed-Action pattern and is deprecated. [Documented, High]
- **Action Log** was introduced **October 26, 2022**, per the Palantir Foundry announcement "Introducing Action Log: Turn decisions into data": "With the Action Log in Foundry, you can now store the state of the world when decisions are made, allowing you to track not just what is changing, but why." [Documented, High]
- **Vertex model chaining** and the legacy Vertex model selector are in **sunset**; functions + function-backed Actions are the supported path. [Documented, High]
- **Geotemporal series** are **beta** (as of the current docs). [Documented, High]
- **NVIDIA cuOpt collaboration** announced **October 28, 2025 at GTC Washington, D.C.**, with Lowe's as a launch customer. [Documented, High]
- **OSv1 (Phonograph)** deprecation: "unavailable after June 30, 2026." [Documented, High]
- **Patents:** The USPTO patent No. 12,282,997, "Generating simulation scenarios and digital media using digital twins" (issued Apr 22, 2025; filed Apr 13, 2023), is **NOT** assigned to Palantir — per USPTO/Justia records its "Assignee: DUALITY ROBOTICS, INC. (San Mateo, CA)," inventors Apurva Shah and Thomas Henry. No Palantir-assigned scenario/simulation/digital-twin patent was confirmed in this research. Do not attribute any simulation/digital-twin patent to Palantir without a verified assignee search. [Documented (negative finding), High]

---

## 11. Glossary

- **Scenario** — immutable, delta-only fork of Ontology data created by replaying Actions and evaluating Models.
- **Domain** — "the valid set over which [a] Model can be evaluated," defined as a set of Objects; model results over a Domain must be independent.
- **Modeling Objective** — project/"mission control" centralizing data, metrics, model submissions, releases, and deployments for one operational problem.
- **Model** — "an artifact for inference that contains machine learning, forecasting, optimization, physical models, or business rules."
- **Function on Model** — auto-generated wrapper around a live deployment, callable from Functions/Actions.
- **Live deployment** — serverless, autoscaling REST inference endpoint.
- **Batch deployment** — pipeline inference on input→output datasets.
- **Inference history** — dataset ledger of live-deployment inputs/outputs.
- **TSP / time-series sync / seriesId** — time-series property, its backing sync, and series key.
- **GTSS / GTSR / observation** — geotemporal series sync, reference property, and individual point.
- **Edit history / Action Log** — immutable changelog and per-action object record.
- **Vertex / Quiver** — graph-scenario and time-series consumer surfaces.
- **Model mesh / simulation mesh** — Vertex's chained-model infrastructure (sunsetting).

---

## 12. Confidence & Gaps Register

| Claim | Confidence | Resolving source |
|---|---|---|
| Scenario = delta-only fork | High | scenarios-concepts (resolved) |
| Immutable; modify = new scenario | High | scenarios-concepts (resolved) |
| Commit = transactional Action replay; models not applied | High | scenarios-apply (resolved) |
| 30k edits / 50 Actions / 10k objects / no attachments | High | scenarios-concepts (resolved) |
| Live deployment autoscaling specifics | High | create-a-model-deployment (resolved) |
| Functions-on-models 50MB / 30s limits | High | functions-on-models (resolved) |
| **Scenario RID prefix** | Unknown | Would need API reference / internal docs |
| **Read-time overlay vs. materialized** | Unknown | Would need architecture doc / engineering source |
| **Named scenario backend service** | Unknown | Would need object-backend internals |
| **OSDK scenario create/read** | Unknown (likely absent) | OSDK reference |
| **General as-of/bitemporal read** | Likely absent | Ontology API reference |
| **Palantir simulation/digital-twin patent** | Resolved negative | USPTO/Justia (12,282,997 is Duality Robotics, not Palantir) |

---

## 13. Caveats

- Marketing-sourced claims (digital-twin page, NVIDIA press) are flagged; treat capability sequencing as promotional framing, not architecture.
- Several mechanics (overlay resolution, scenario RID, scenario backend service) are genuine known-unknowns; the [Speculative] hypotheses are design starting points, not verified facts. Do NOT ship a clone assuming the overlay is read-time-merged without validating against your own scale tests.
- Multiple features are explicitly **beta** (geotemporal series) or **sunset** (Vertex model chaining/selector, OSv1, Single I/O endpoints); a clone should target the current Function-backed-Action + Live-deployment + OSv2 path.
- The frequently-cited "simulation scenarios… digital twins" patent (USPTO 12,282,997) belongs to **Duality Robotics, Inc.**, not Palantir; do not attribute it to Palantir.

---

### Minimum viable clone — architectural checklist (synthesis)

1. **Base store:** an object/link store with stable identity (analogue of OSv2) and an Actions service that applies validated, typed edits transactionally.
2. **Scenario overlay:** a named, immutable edit-batch keyed to base identity, storing only the diff (property mutations, created/deleted objects, created/deleted links). Resolve reads by merging the overlay over the base when a scenario context is supplied. Enforce caps (≈30k edits, ≈50 actions, ≈10k objects loaded) to bound the merge.
3. **Commit:** replay the scenario's staged Actions against the base transactionally (all-or-nothing); never write model outputs.
4. **Model serving:** a serverless REST inference tier (autoscale from zero, +1 replica at ~75% load, scale down after idle), with versioned releases gated by environment tags and zero-downtime cutover; wrap each deployment as a typed Function callable from Actions and scenarios.
5. **Temporal substrate:** time-series + geotemporal series stores keyed by seriesId, event object types, and an immutable edit-history changelog.
6. **Liveness & security:** streaming ingest with most-recent-wins changelog semantics; per-query, data-driven row/column/cell security that re-evaluates on every read so state changes (and the edits scenarios stage) immediately affect visibility.
7. **Surfaces:** a graph/scenario simulation UI (Vertex-like, with baseline comparison and model chaining) and a time-series analysis UI (Quiver-like, with interactive forecasts and derived-series writeback).
