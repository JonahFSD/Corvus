---
aliases:
  - Edit History
  - Action Log
  - Writeback Path
updated: 2026-06-13
---

# Audit & Writeback

> How edits are recorded and persisted: the immutable per-object edit history, the action-level log, and the end-to-end writeback path from action to durable store.

## Edit History

> An immutable audit trail of every object change: who, what, when, previous → new values.

Cannot be altered by end users even if edits are reverted. Rides directly on the [[Versioned Data Foundation|versioned store]]. Non-negotiable for an operational system.

**Related:** [[Audit & Writeback#Action Log|Action Log]] · [[Audit & Lineage#Audit Log|Audit Log]] · [[Audit & Writeback#Writeback Path|Writeback Path]]

**For our clone:** Keep — an append-only events table capturing the diff (D13).

*clone: keep · kind: mechanism · layer: kinetic · invariants: [[Governed Writeback]] · [[End-to-End Lineage]] · source: Kinetic reconstruction §7*
#clone/keep #kind/mechanism #layer/kinetic

## Action Log

> A `[LOG]` object type that records each action submission, linked to all objects it edited.

Captures edited objects, an optional summary, and contextual properties — a queryable record of *which action* did *what*. Complements property-level [[Audit & Writeback#Edit History|Edit History]].

**Related:** [[Audit & Writeback#Edit History|Edit History]] · [[Actions#Action Type|Action Type]] · [[Audit & Lineage#Audit Log|Audit Log]]

*clone: keep · kind: mechanism · layer: kinetic · invariants: [[End-to-End Lineage]] · [[Governed Writeback]] · source: Kinetic reconstruction §7*
#clone/keep #kind/mechanism #layer/kinetic

## Writeback Path

> The end-to-end route of an edit: Action → Actions service → Object Data Funnel → index + materialization.

Index-first, persist-later: applied to the live index immediately, flushed to a durable [[Materialization|merged dataset]] periodically. Gives [[Read-Your-Writes]] at scale. With a single DB, a committed transaction *is* the write.

**Related:** [[Object Storage#Object Data Funnel|Object Data Funnel]] · [[Materialization]] · [[Actions#Action Atomicity|Action Atomicity]] · [[Read-Your-Writes]]

**For our clone:** Drop the machinery — a DB commit replaces the whole path.

*clone: drop · kind: mechanism · layer: kinetic · invariants: [[Governed Writeback]] · [[Versioned Data Foundation]] · source: Kinetic reconstruction §7*
#clone/drop #kind/mechanism #layer/kinetic
