---
tags:
  - hub
  - layer/data
---

# Data Integration & Pipeline Layer

> The data foundation: how source data is ingested, versioned, transformed, and kept fresh as Ontology-ready datasets.

## Concepts in this layer

- [[Data Connection (Magritte)]] — sources, connectors, agents, workers
- [[Virtual Table & Export]] — boundary in/out
- [[Dataset & Transactions]] — versioned storage core
- [[Schema & Inference]] — typing
- [[RID]] — addressing
- [[Transforms & Build]] — authoring → orchestration
- [[Compute Backends & Economics]] — engines & billing (mostly dropped)
- [[Data Health & Lineage]] — quality & dependency graph
- [[Materialization]] — the writeback seam

> [!note] Consolidated 2026-06-13 — 30 atomic notes merged into these 9. Old titles (e.g. `[[Dataset & Transactions|Dataset]]`, `[[Dataset & Transactions|Transaction Model]]`, `[[Data Connection (Magritte)|Magritte]]`) live on as aliases, so existing links still resolve.

---

**Invariants this layer serves:** [[Semantic Model Over Data]] · [[Versioned Data Foundation]] · [[Governed Writeback]] · [[Security Travels With Data]] · [[End-to-End Lineage]]

[[Foundry — Home (MOC)|← Home]]
