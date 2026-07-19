---
aliases:
  - Vertex
  - Quiver
updated: 2026-06-13
---

# Analysis Surfaces

> The interactive what-if applications — Vertex (graph + scenario) and Quiver (time-series + scenario): Palantir's own surfaces for visualizing and quantifying cause and effect across the digital twin.

## Vertex

> The graph + scenario surface: visualize and quantify cause and effect across the digital twin.

Object-backed system diagrams with [[Scenarios#Scenario|Scenario]] creation (Actions + modeled inputs + overrides), [[Scenarios#Scenario Comparison|baseline comparison]], and (sunsetting) [[Models, Inference & Simulation#Model Mesh|model chaining]]; embeddable in [[Workshop, Modules & Views#Workshop|Workshop]] with 'load data from scenario.' The interactive what-if surface of the [[Digital Twin]].

**Related:** [[Scenarios#Scenario|Scenario]] · [[Models, Inference & Simulation#Simulation|Simulation]] · [[Models, Inference & Simulation#Model Mesh|Model Mesh]] · [[Analysis Surfaces#Quiver|Quiver]] · [[Digital Twin]] · [[Workshop, Modules & Views#Workshop|Workshop]]

**For our clone:** Defer — build a minimal what-if graph UI later; Vertex itself is a Palantir application.

*clone: defer · kind: service · layer: dynamic · invariants: [[Semantic Model Over Data]] · source: Dynamic reconstruction §8.2*
#clone/defer #kind/service #layer/dynamic

## Quiver

> The time-series + scenario analysis surface: point-and-click analysis over object and time-series data.

An analysis is a graph of interdependent **cards**, offering interactive forecasts (constant/linear/formula, fit with RMSE/MAE), [[Temporal & Streaming Substrate#Derived Series|derived-series]] transforms, [[Temporal & Streaming Substrate#Event Object Type|event]] analytics, streaming rolling windows, and writeback to the Ontology via [[Actions#Action Type|Actions]]. The temporal counterpart to [[Analysis Surfaces#Vertex|Vertex]].

**Related:** [[Temporal & Streaming Substrate#Time-Series Property|Time-Series Property]] · [[Temporal & Streaming Substrate#Derived Series|Derived Series]] · [[Temporal & Streaming Substrate#Event Object Type|Event Object Type]] · [[Analysis Surfaces#Vertex|Vertex]]

**For our clone:** Defer — a charting/forecast UI over time series; post-MVP, and a Palantir application itself.

*clone: defer · kind: service · layer: dynamic · invariants: [[Versioned Data Foundation]] · source: Dynamic reconstruction §8.3*
#clone/defer #kind/service #layer/dynamic
