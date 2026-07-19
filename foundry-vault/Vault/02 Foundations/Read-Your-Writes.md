---
aliases: []
tags:
  - layer/crosscutting
  - kind/property
  - clone/core
layer: crosscutting
kind: property
clone: core
invariants:
  - "[[Governed Writeback]]"
source: "Kinetic reconstruction"
updated: 2026-06-13
---

# Read-Your-Writes

> After a change is committed, reads promptly reflect it — users trust that what they just did is what they now see.

In Foundry this is guaranteed at the index: once an [[Actions#Action Type|action]]'s edit is sent to the [[Object Storage#Object Data Funnel|Object Data Funnel]], subsequent object reads include it. For a small clone, an ordinary database transaction gives this for free.

**Invariants:** [[Governed Writeback]]

**Related:** [[Audit & Writeback#Writeback Path|Writeback Path]] · [[Object Storage#Object Data Funnel|Object Data Funnel]] · [[Actions#Action Atomicity|Action Atomicity]]

*Source: Kinetic reconstruction*
