---
aliases:
  - "Dataset"
  - "Transaction Model"
  - "Dataset Branch"
  - "Dataset Projection"
  - "View (virtual dataset)"
tags:
  - layer/data
  - kind/concept
  - clone/keep
layer: data
kind: concept
clone: keep
invariants:
  - "[[Versioned Data Foundation]]"
source: "Data reconstruction §3–3.6"
updated: 2026-06-13
---

# Dataset & Transactions

> The versioned-storage core: a dataset is a versioned wrapper around files, advanced by an append-only transaction log, with branches, views, and projections layered on the same model.

**Dataset.** The fundamental unit of data storage — a versioned wrapper around files in a backing file system (commonly S3, usually Parquet), with [[Schema & Inference|schema]] stored as metadata. Versioned by transactions, identified by a [[RID]]. The substrate that [[Objects#Object Backing|backs object types]]. *Clone: keep — likely rows/tables in one DB rather than files on S3 (D1).*

**Transaction Model.** A dataset is a linear sequence of atomic commits; the current view is computed by replaying them. Four types — **SNAPSHOT** (replace the view), **APPEND** (add files), **UPDATE** (add/replace files), **DELETE** (remove references) — replayed forward from the latest SNAPSHOT. This single mechanism underlies versioning, incrementality, branching, and retention ([[Git for Data]]). *Clone: keep — a DB transaction + history/change-log is likely enough (D2).*

**Dataset Branch.** A named pointer to the most recent transaction on a linear sequence; supports dev→prod separation. Each branch is an independent transaction sequence (root is usually `master`); unlike Git there is **no merge**. Builds use branch fallbacks (e.g. develop → master). Pairs with [[Roles & Authorization#Project|Project]]-based flow. *Clone: simplify.*

**View (virtual dataset).** A file-less resource that is the deduplicated union of backing datasets, computed at read time — builds near-instantly, can be a transform input but not an output, and can stop [[Mandatory Controls & Classification#Marking|marking]] propagation. (Distinct from the point-in-time *view* produced by replaying transactions.) *Clone: simplify.*

**Dataset Projection.** An independently-stored, compacted query representation that reorganizes data as volume grows; readers transparently combine projection + canonical data. *Clone: drop — a small-file scale artifact.*

**Invariants:** [[Versioned Data Foundation]]

**Related:** [[Schema & Inference]] · [[RID]] · [[Transforms & Build]] · [[Objects#Object Backing|Object Backing]]

**For our clone:** Keep the core (dataset + transactions); branches and views simplify; projections drop.

*Source: Data reconstruction §3–3.6*
