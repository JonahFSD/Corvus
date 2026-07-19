---
aliases: []
tags:
  - layer/data
  - kind/mechanism
  - clone/simplify
layer: data
kind: mechanism
clone: simplify
invariants:
  - "[[Versioned Data Foundation]]"
  - "[[End-to-End Lineage]]"
source: "Kinetic reconstruction §7"
updated: 2026-06-13
---

# Materialization

> An optional dataset (OSv2) reflecting object/writeback state — formerly the 'writeback dataset'.

Persists Ontology object state back to a dataset; carries `__`-prefixed metadata columns. Propagates backing [[Mandatory Controls & Classification#Marking|markings]]. The seam where [[Governed Writeback|kinetic edits]] re-enter the [[Versioned Data Foundation|data foundation]].

**Invariants:** [[Versioned Data Foundation]] · [[End-to-End Lineage]]

**Related:** [[Audit & Writeback#Writeback Path|Writeback Path]] · [[Objects#Object Backing|Object Backing]] · [[Mandatory Controls & Classification#Marking|Marking]]

*Source: Kinetic reconstruction §7*
