---
aliases:
  - Model
  - Modeling Objective
  - Live Deployment
  - Inference History
  - Functions on Models
  - Model Mesh
  - Optimization
  - Simulation
updated: 2026-06-13
---

# Models, Inference & Simulation

> The model stack and the motion that runs it: a uniform model artifact, its governed lifecycle and live/inference serving, the Functions that expose it to Actions and Scenarios, and simulation/optimization over the Ontology — mostly post-MVP.

## Model

> An artifact for inference spanning ML, forecasting, optimization, physical models, and business rules.

A uniform abstraction: model artifacts (weights/container) plus a Python **adapter** that lets the platform load, initialize, and run inference on any kind of model. Bound to the Ontology as model-backed properties and consumed by [[Models, Inference & Simulation#Functions on Models|Functions on Models]], [[Actions#Action Type|Actions]], and [[Scenarios#Scenario|Scenarios]].

**Related:** [[Models, Inference & Simulation#Modeling Objective|Modeling Objective]] · [[Models, Inference & Simulation#Functions on Models|Functions on Models]] · [[Models, Inference & Simulation#Live Deployment|Live Deployment]] · [[Models, Inference & Simulation#Simulation|Simulation]] · [[Properties#Derived Property|Derived Property]]

**For our clone:** Defer — model serving is post-MVP; the clone's [[Functions#Function|Function]] model already accommodates inference later.

*clone: defer · kind: concept · layer: dynamic · invariants: [[Semantic Model Over Data]] · source: Dynamic reconstruction §3.1*
#clone/defer #kind/concept #layer/dynamic

## Modeling Objective

> The 'mission control' lifecycle for one modeling problem: submit → evaluate → release → deploy → monitor.

A governance + automation + CI/CD layer: a submission is an immutable copy (like a pull request); a **release** is versioned and environment-tagged (Staging/Production); a deployment takes the latest tagged release with zero-downtime cutover. Spans problems classic ML-Ops tools miss — simulation and optimization.

**Related:** [[Models, Inference & Simulation#Model|Model]] · [[Models, Inference & Simulation#Live Deployment|Live Deployment]] · [[Models, Inference & Simulation#Inference History|Inference History]] · [[Models, Inference & Simulation#Functions on Models|Functions on Models]]

**For our clone:** Defer — replicate the *contract* (versioned, tagged, governed releases) cheaply once models arrive.

*clone: defer · kind: service · layer: dynamic · invariants: [[Governed Writeback]] · [[End-to-End Lineage]] · source: Dynamic reconstruction §3.2*
#clone/defer #kind/service #layer/dynamic

## Live Deployment

> A serverless, autoscaling REST endpoint that serves a model for low-latency interactive inference.

Independently permissioned, highly available (updated via CI/CD without downtime), scales from zero, adds a replica at 75% capacity, and scales down after 30 minutes idle; queried at `…/foundry-ml-live/.../v2`. Contrast the **batch deployment** — pipeline inference on an input→output dataset. Feeds [[Scenarios#Scenario|scenarios]] and [[Models, Inference & Simulation#Simulation|Simulation]].

**Related:** [[Models, Inference & Simulation#Model|Model]] · [[Models, Inference & Simulation#Functions on Models|Functions on Models]] · [[Models, Inference & Simulation#Modeling Objective|Modeling Objective]] · [[Models, Inference & Simulation#Simulation|Simulation]] · [[Compute Backends & Economics|Compute-Seconds]]

**For our clone:** Defer — one small inference service replaces the autoscaling tier; the numbers (75%/30 min) are Palantir-scale artifacts.

*clone: defer · kind: service · layer: dynamic · invariants: [[Governed Writeback]] · source: Dynamic reconstruction §4.2*
#clone/defer #kind/service #layer/dynamic

## Inference History

> A dataset ledger capturing the inputs and outputs of every request to a live deployment.

The model-side audit trail — enabling drift detection, continuous retraining, and performance evaluation; gated by an edit-inference-ledger permission and co-located with its objective because the I/O is sensitive. The temporal record that ties model behavior into [[End-to-End Lineage]] (not all I/O is guaranteed to appear).

**Related:** [[Models, Inference & Simulation#Model|Model]] · [[Models, Inference & Simulation#Modeling Objective|Modeling Objective]] · [[Models, Inference & Simulation#Live Deployment|Live Deployment]] · [[Audit & Writeback#Edit History|Edit History]]

**For our clone:** Defer — an append-only inference log mirrors our [[Audit & Writeback#Edit History|Edit History]] pattern.

*clone: defer · kind: mechanism · layer: dynamic · invariants: [[End-to-End Lineage]] · source: Dynamic reconstruction §3.3*
#clone/defer #kind/mechanism #layer/dynamic

## Functions on Models

> Auto-generated Function wrappers around a live model deployment, callable from Actions, Scenarios, and derived properties.

They mirror the model's API in [[Functions#Function|Function]]-supported types and **defer all logic to the underlying deployment** — one function per branch, and a new model version auto-versions the function. The seam by which model output becomes object or scenario state; capped at 50 MB I/O and 30 s execution.

**Related:** [[Functions#Function|Function]] · [[Models, Inference & Simulation#Model|Model]] · [[Models, Inference & Simulation#Live Deployment|Live Deployment]] · [[Functions#Function-Backed Action|Function-Backed Action]] · [[Scenarios#Scenario|Scenario]]

**For our clone:** Defer — wrap inference as an ordinary [[Functions#Function|Function]] so the rest of the system stays model-agnostic.

*clone: defer · kind: mechanism · layer: dynamic · invariants: [[Governed Writeback]] · source: Dynamic reconstruction §4.1*
#clone/defer #kind/mechanism #layer/dynamic

## Model Mesh

> Vertex's chained-model ('simulation mesh') infrastructure that forwards one model's outputs into another's inputs.

Enabled continuous evaluation by flowing real-time sensor and configuration data through a graph of models. **Sunsetting** in Foundry — the supported path is plain [[Models, Inference & Simulation#Functions on Models|Functions on Models]] composed inside [[Functions#Function-Backed Action|function-backed Actions]].

**Related:** [[Analysis Surfaces#Vertex|Vertex]] · [[Models, Inference & Simulation#Simulation|Simulation]] · [[Models, Inference & Simulation#Functions on Models|Functions on Models]] · [[Models, Inference & Simulation#Model|Model]]

**For our clone:** Drop — sunset feature; chain models via functions instead.

*clone: drop · kind: mechanism · layer: dynamic · invariants: [[Semantic Model Over Data]] · source: Dynamic reconstruction §5.1*
#clone/drop #kind/mechanism #layer/dynamic

## Optimization

> A model type that solves for a best decision (routing, allocation, scheduling) rather than predicting a value.

Treated as a [[Models, Inference & Simulation#Model|Model]] wrapping a solver (LP/MILP/VRP) — Foundry integrates **NVIDIA cuOpt** (GPU decision optimization; the Oct 2025 collaboration, Lowe's as launch customer) for dynamic supply-chain use. Optimizer results are staged as [[Scenarios#Scenario|scenario]] edits via a [[Functions#Function-Backed Action|Function-Backed Action]] for comparison before transactional apply.

**Related:** [[Models, Inference & Simulation#Model|Model]] · [[Models, Inference & Simulation#Simulation|Simulation]] · [[Scenarios#Scenario|Scenario]] · [[Functions#Function-Backed Action|Function-Backed Action]]

**For our clone:** Defer — a solver is just another model behind a [[Functions#Function|Function]]; GPU acceleration is post-MVP.

*clone: defer · kind: concept · layer: dynamic · invariants: [[Governed Writeback]] · source: Dynamic reconstruction §5.2*
#clone/defer #kind/concept #layer/dynamic

## Simulation

> Running models over the Ontology inside a scenario to project outcomes, then comparing to a baseline.

Function-backed Actions invoke [[Models, Inference & Simulation#Model|models]] against a [[Scenarios#Scenario Overlay|Scenario Overlay]]; in [[Analysis Surfaces#Vertex|Vertex]] a scenario 'evaluates actions along with one or more modeled inputs and computes the output to reflect the real-world interactions of your digital twin.' Time-series inputs can be overridden with simulated values. The motion that makes the [[Digital Twin]] *projectable*.

**Related:** [[Scenarios#Scenario|Scenario]] · [[Scenarios#Scenario Overlay|Scenario Overlay]] · [[Models, Inference & Simulation#Model|Model]] · [[Models, Inference & Simulation#Optimization|Optimization]] · [[Analysis Surfaces#Vertex|Vertex]] · [[Temporal & Streaming Substrate#Time-Series Property|Time-Series Property]] · [[Digital Twin]]

**For our clone:** Defer — emerges for free once scenarios and model functions exist.

*clone: defer · kind: pattern · layer: dynamic · invariants: [[Semantic Model Over Data]] · source: Dynamic reconstruction §5.1, §5.3*
#clone/defer #kind/pattern #layer/dynamic
