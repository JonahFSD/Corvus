---
aliases:
  - "Virtual Table"
  - "Export"
tags:
  - layer/data
  - kind/mechanism
  - clone/simplify
layer: data
kind: mechanism
clone: simplify
invariants:
  - "[[Versioned Data Foundation]]"
  - "[[Security Travels With Data]]"
  - "[[End-to-End Lineage]]"
source: "Data reconstruction §2.4–2.5"
updated: 2026-06-13
---

# Virtual Table & Export

> The boundary edges of the data foundation: querying external tables without ingesting them, and pushing Foundry data back out.

**Virtual Table.** A pointer to an external table (Delta/Iceberg/BigQuery/Snowflake/…) queried without ingesting it — no-copy federation: always-current, no storage cost, optional compute pushdown. But reads depend on the source and lack Foundry's full [[Dataset & Transactions|transactional]] guarantees.

**Export.** Pushing Foundry data back out to an external system (file, table, streaming). Governed by [[Mandatory Controls & Classification#Marking|markings]] — exporting is treated as removing markings and requires permission. One way [[The Closed Loop|the loop]] reaches external systems of record (cf. [[Integration & Automation#Webhook|Webhook]]).

**Invariants:** [[Versioned Data Foundation]] · [[Security Travels With Data]] · [[End-to-End Lineage]]

**Related:** [[Data Connection (Magritte)]] · [[Mandatory Controls & Classification#Marking|Marking]] · [[Integration & Automation#Webhook|Webhook]]

**For our clone:** Simplify — a manual CSV/table export plus a single inbound API; skip federation unless a live external table is genuinely required.

*Source: Data reconstruction §2.4–2.5*
