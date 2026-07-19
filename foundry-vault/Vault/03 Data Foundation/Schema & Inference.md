---
aliases:
  - "Schema"
  - "Schema Inference"
tags:
  - layer/data
  - kind/concept
  - clone/simplify
layer: data
kind: concept
clone: simplify
invariants:
  - "[[Versioned Data Foundation]]"
source: "Data reconstruction §3.4"
updated: 2026-06-13
---

# Schema & Inference

> Metadata defining how a dataset's files are interpreted — column names and types — applied manually or detected automatically.

**Schema.** Metadata on a dataset view defining column names and types (internally the `foundry-metadata` service). Schema-evolution rules constrain incremental outputs — same-named columns must keep their type.

**Schema Inference.** Automatic detection of column names and types from data (CSV/JSON, semi-structured), often the first step of a pipeline on raw data (internally `foundry-schema-inference`). Turns untyped bytes into a typed schema the rest of the pipeline and the [[Objects#Object Type|object model]] can rely on.

**Invariants:** [[Versioned Data Foundation]]

**Related:** [[Dataset & Transactions]] · [[Transforms & Build]]

**For our clone:** Simplify — infer types on upload; enforce type-stability on refresh.

*Source: Data reconstruction §3.4*
