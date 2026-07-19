---
aliases:
  - Time-Series Property
  - Derived Series
  - Geotemporal Series
  - Event Object Type
  - As-Of Read
updated: 2026-06-13
---

# Temporal & Streaming Substrate

> The time dimension: time-series, derived and geotemporal series, event object types, and the (absent) as-of read — the timestamped raw material the dynamic layer projects forward.

## Time-Series Property

> An object property that stores a history of timestamped values rather than a single value.

Backed by **time-series syncs** (datasets or streams) keyed by a `seriesId` that Foundry resolves against the property's data sources; requires a proprietary time-series compute database. The raw material for forecasts, simulated overrides, and [[Analysis Surfaces#Quiver|Quiver]] analysis.

**Related:** [[Temporal & Streaming Substrate#Derived Series|Derived Series]] · [[Temporal & Streaming Substrate#Geotemporal Series|Geotemporal Series]] · [[Analysis Surfaces#Quiver|Quiver]] · [[Objects#Object Type|Object Type]]

**For our clone:** Defer — a timestamped-values table covers it; the dedicated time-series engine is a scale artifact.

*clone: defer · kind: type · layer: dynamic · invariants: [[Versioned Data Foundation]] · source: Dynamic reconstruction §6.1*
#clone/defer #kind/type #layer/dynamic

## Derived Series

> A time series computed on the fly from other series, stored as a template rather than materialized.

The time-series analogue of a [[Properties#Derived Property|Derived Property]] — transforms saved in [[Analysis Surfaces#Quiver|Quiver]] (smoothing, formulas) become reusable series without writing data, resolved at read time via template RIDs.

**Related:** [[Temporal & Streaming Substrate#Time-Series Property|Time-Series Property]] · [[Properties#Derived Property|Derived Property]] · [[Analysis Surfaces#Quiver|Quiver]]

**For our clone:** Defer — compute-on-read series; add alongside the time-series feature.

*clone: defer · kind: mechanism · layer: dynamic · invariants: [[Versioned Data Foundation]] · source: Dynamic reconstruction §6.1*
#clone/defer #kind/mechanism #layer/dynamic

## Geotemporal Series

> Time series with a geospatial component — the path of an entity over time ('tracks').

A geotemporal series object type plus a series sync (GTSS) referenced by a GTSR property; individual points are **observations**, stored as live streaming (real-time, ~14-day retention) or a persistent dataset archive. Currently **beta**.

**Related:** [[Temporal & Streaming Substrate#Time-Series Property|Time-Series Property]] · [[Temporal & Streaming Substrate#Event Object Type|Event Object Type]] · [[Objects#Object Type|Object Type]]

**For our clone:** Defer — niche; add only if the use case is spatial.

*clone: defer · kind: type · layer: dynamic · invariants: [[Versioned Data Foundation]] · source: Dynamic reconstruction §6.2*
#clone/defer #kind/type #layer/dynamic

## Event Object Type

> An object type carrying temporal information — minimally a start and end timestamp.

Makes change-over-time first-class: [[Analysis Surfaces#Quiver|Quiver]] computes event statistics, comparison plots, and filtering over them. The discrete-interval complement to continuous [[Temporal & Streaming Substrate#Time-Series Property|time series]].

**Related:** [[Objects#Object Type|Object Type]] · [[Temporal & Streaming Substrate#Time-Series Property|Time-Series Property]] · [[Analysis Surfaces#Quiver|Quiver]]

**For our clone:** Defer — an object type with two timestamps; nothing special to build early.

*clone: defer · kind: type · layer: dynamic · invariants: [[Semantic Model Over Data]] · [[Versioned Data Foundation]] · source: Dynamic reconstruction §6.3*
#clone/defer #kind/type #layer/dynamic

## As-Of Read

> Querying Ontology state as it was at a past time — a capability Foundry does NOT expose as a first-class API.

There is an experimental `transaction` parameter and a `branch` parameter, but **no general bitemporal 'as of time T' read**. The temporal record is reconstructable from the immutable [[Audit & Writeback#Edit History|Edit History]] / [[Audit & Writeback#Action Log|Action Log]] changelogs and time-series history, not a first-class query. A genuine gap — flagged so a clone is not tempted to assume it.

**Related:** [[Audit & Writeback#Edit History|Edit History]] · [[Audit & Writeback#Action Log|Action Log]] · [[Dataset & Transactions|Transaction Model]] · [[Temporal & Streaming Substrate#Time-Series Property|Time-Series Property]]

**For our clone:** Defer — reconstruct from the changelog we already keep; Foundry has no first-class as-of read either.

*clone: defer · kind: concept · layer: dynamic · invariants: [[Versioned Data Foundation]] · [[End-to-End Lineage]] · source: Dynamic reconstruction §6.4*
#clone/defer #kind/concept #layer/dynamic
