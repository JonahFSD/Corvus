---
aliases:
  - "Data Health & Expectations"
  - "Data Lineage Graph"
tags:
  - layer/data
  - kind/service
  - clone/keep
layer: data
kind: service
clone: keep
invariants:
  - "[[Versioned Data Foundation]]"
  - "[[End-to-End Lineage]]"
source: "Data reconstruction §6.1–6.2"
updated: 2026-06-13
---

# Data Health & Lineage

> The trust layer over builds: quality checks that guard integrity, and the dependency graph that traces everything end to end.

**Data Health & Expectations.** Two quality mechanisms — post-build **health checks** (warn/alert on freshness, row counts, schema, uniqueness) and in-build **data expectations** that fail a build if violated (e.g. primary-key uniqueness, row-count bounds). Guards the integrity feeding the [[Objects#Object Type|object model]]. *Clone: simplify.*

**Data Lineage Graph.** The branch-aware, inspectable dependency graph tracing source → dataset → transform → object → app. It computes out-of-date datasets, powers the health checks above, and structures the propagation of security. The backbone of [[End-to-End Lineage]]. *Clone: keep, simplified to dataset-level 'produced by' (D4).*

**Invariants:** [[Versioned Data Foundation]] · [[End-to-End Lineage]]

**Related:** [[Transforms & Build]] · [[Dataset & Transactions]] · [[Objects#Object Backing|Object Backing]]

**For our clone:** Keep lineage at dataset granularity; simplify health to a few checks on refresh.

*Source: Data reconstruction §6.1–6.2*
