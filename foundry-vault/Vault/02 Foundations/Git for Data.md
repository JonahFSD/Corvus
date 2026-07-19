---
aliases: []
tags:
  - layer/crosscutting
  - kind/concept
  - clone/core
layer: crosscutting
kind: concept
clone: core
invariants:
  - "[[Versioned Data Foundation]]"
source: "Data reconstruction"
updated: 2026-06-13
---

# Git for Data

> The data foundation behaves like version control: immutable, historied, branchable commits.

Every [[Dataset & Transactions|Dataset]] is a linear sequence of [[Dataset & Transactions|transactions]] (commits) per [[Dataset & Transactions|branch]]; the current state is a replay. Versioning, [[Transforms & Build|incrementality]], branching, and retention all derive from this one idea.

**Invariants:** [[Versioned Data Foundation]]

**Related:** [[Dataset & Transactions|Dataset]] · [[Dataset & Transactions|Transaction Model]] · [[Dataset & Transactions|Dataset Branch]] · [[End-to-End Lineage]]

*Source: Data reconstruction*
