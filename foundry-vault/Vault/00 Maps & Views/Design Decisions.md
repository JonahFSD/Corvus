---
tags:
  - hub
  - decisions
---

# Design Decisions

> **Resolved.** All 15 forks were committed in the Build-Blueprint (`Spec/SPEC_Foundry-Clone_Build-Blueprint.md` §3). The leanings below are the historical pre-decision state; see the Blueprint for the resolved engine choice on each.

| # | Decision | Leaning |
|---|---|---|
| D1 | Storage substrate (Postgres / file store / DuckDB…) | A single relational DB |
| D2 | How literal the transaction/version model is | Versioned rows + change log |
| D3 | Separate compute step vs. in-database transforms | In-DB / SQL where possible |
| D4 | Lineage granularity (dataset vs. column) | Dataset-level to start |
| D5 | Object storage shape (table-per-type vs. generic store) | Resolved: hybrid `objects` table + JSONB + generated typed views |
| D6 | Link implementation (FK + join tables vs. unified edge table) | Follow Foundry (FK / join) |
| D7 | Property/value-type richness at v1 | Small core + constrained values |
| D8 | Search (DB queries vs. search index) | DB queries + full-text |
| D9 | Object liveness (sync reads vs. async indexing) | Synchronous |
| D10 | Action definition format (declarative vs. code) | Likely both, code-first |
| D11 | Function language/runtime | One; same as backend |
| D12 | Validation-rule expression (DSL vs. functions) | Functions to start |
| D13 | Audit log shape & queryability | Append-only events table |
| D14 | Atomicity scope | One DB transaction per action |
| D15 | Access-control richness at v1 | Roles + optional row rules |

[[Minimum Viable Foundry]] · [[Foundry — Home (MOC)|← Home]]
