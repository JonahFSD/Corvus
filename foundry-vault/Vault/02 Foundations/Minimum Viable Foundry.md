---
aliases: []
tags:
  - layer/crosscutting
  - kind/pattern
  - clone/core
layer: crosscutting
kind: pattern
clone: core
invariants:
  - "[[Governed Writeback]]"
  - "[[Semantic Model Over Data]]"
  - "[[Versioned Data Foundation]]"
source: "Design Constraints spec"
updated: 2026-06-13
---

# Minimum Viable Foundry

> The smallest system still recognizably Foundry-like: versioned store + semantic model + governed actions + audit + roles.

The v1 target for our clone. In: a [[Versioned Data Foundation|versioned store]], [[Objects#Object Type|object]]/[[Links#Link Type|link]] model, [[Objects#Object Set|object sets]], [[Actions#Action Type|governed actions]] with [[Actions#Submission Criteria|validation]], an [[Audit & Lineage#Audit Log|Audit Log]], and [[Roles & Authorization#Role|roles]]. Out (deferrable without rework): distributed compute, the connector tier, [[AIP Layer|AIP]], [[Platform & Ecosystem Layer|Apollo]]. See [[Design Decisions]].

**Invariants:** [[Governed Writeback]] · [[Semantic Model Over Data]] · [[Versioned Data Foundation]]

**Related:** [[Design Decisions]] · [[The Closed Loop]]

*Source: Design Constraints spec*
