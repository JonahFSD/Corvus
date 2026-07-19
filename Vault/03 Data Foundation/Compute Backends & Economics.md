---
aliases:
  - "Lightweight Transform"
  - "Faster Pipelines"
  - "Spark Profile"
  - "Compute-Seconds"
tags:
  - layer/data
  - kind/concept
  - clone/drop
layer: data
kind: concept
clone: drop
invariants:
  - "[[Versioned Data Foundation]]"
source: "Data reconstruction §4.2–4.3, §8"
updated: 2026-06-13
---

# Compute Backends & Economics

> The pluggable compute engines under transforms, how they're sized, and how they're billed — mostly Palantir-scale tuning we don't need.

**Lightweight Transform.** Runs on a single node without Spark (Polars/pandas) for small-to-medium data; faster and cheaper than Spark for suitable jobs, with bring-your-own-container support. Evidence that distributed compute is optional for modest volumes.

**Faster Pipelines.** A pipeline-acceleration backend powered by **DataFusion** (open-source, Rust) that speeds small-to-medium batch/incremental pipelines vs Spark (no LLM/geo/media operations). A reminder we likely need no distributed engine at all.

**Spark Profile.** A configuration of distributed compute resources (driver/executor cores, memory, executor count) selecting how a Spark transform is resourced; metered in compute-seconds. *Drop — scale tuning.*

**Compute-Seconds.** Foundry's metered compute unit: max(vCPU, GiB/7.5) × seconds, summed across driver + executors. A billing/scale artifact. *Drop entirely.*

**Invariants:** [[Versioned Data Foundation]]

**Related:** [[Transforms & Build]]

**For our clone:** Drop the whole cluster — a single relational DB / in-process compute is enough (D1, D3). Keep only as a reminder of why we skip distributed compute.

*Source: Data reconstruction §4.2–4.3, §8*
