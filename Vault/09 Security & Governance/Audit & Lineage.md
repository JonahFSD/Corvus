---
aliases:
  - Audit Log
  - Audit Schema
tags:
  - layer/security
  - kind/doc
  - clone/keep
layer: security
kind: doc
clone: keep
source: "09 Security & Governance (consolidated)"
updated: 2026-06-14
---

# Audit & Lineage

> The append-only record of who did what, when, and where — the queryable backbone of end-to-end lineage and accountability.

## Audit Log

> An append-only, platform-wide record of who did what, when, and where.

Complements object-level [[Audit & Writeback#Edit History|Edit History]] and [[Audit & Writeback#Action Log|action logs]] with system-wide accountability. A pillar of [[End-to-End Lineage]] and governance.

**Invariants:** [[End-to-End Lineage]] · [[Security Travels With Data]]

**Related:** [[Audit & Writeback#Edit History|Edit History]] · [[Audit & Writeback#Action Log|Action Log]] · [[Roles & Authorization#Role|Role]]

**For our clone:** Keep — append-only events table (D13).

*clone: keep · kind: mechanism · layer: security · invariants: [[End-to-End Lineage]] · [[Security Travels With Data]] · source: Kinetic §7 / Security*
#clone/keep #kind/mechanism #layer/security

## Audit Schema

> The audit-log format, migrating from audit.2 to the category-based, low-latency audit.3.

audit.3 logs every event under standardized categories with promoted `entities`/`origins`/`result` fields, ~15-minute latency, pollable by SIEMs via the audit API. The queryable backbone of [[End-to-End Lineage]] and [[Audit & Lineage#Audit Log|Audit Log]].

**Invariants:** [[End-to-End Lineage]] · [[Security Travels With Data]]

**Related:** [[Audit & Lineage#Audit Log|Audit Log]] · [[Audit & Writeback#Edit History|Edit History]]

**For our clone:** Keep the idea (an append-only events stream); our [[Audit & Lineage#Audit Log|Audit Log]] covers it.

*clone: keep · kind: mechanism · layer: security · invariants: [[End-to-End Lineage]] · [[Security Travels With Data]] · source: Security reconstruction §7*
#clone/keep #kind/mechanism #layer/security
