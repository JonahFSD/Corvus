---
aliases:
  - Function
  - Function Runtime
  - Functions on Objects (FOO)
  - FOO
  - Ontology Edits API
  - Function-Backed Action
  - External Function
updated: 2026-06-13
---

# Functions

> Reusable server-side logic that reads objects and computes results or edits — the compute substrate behind validation, derived data, function-backed writeback, and external integration.

## Function

> Reusable server-side business logic that reads objects and computes results (TypeScript / Python).

The substrate for complex validation, [[Properties#Derived Property|derived data]], [[Functions#Function-Backed Action|function-backed writeback]], and (later) AI tools. Authored once, reused on every surface — [[Define-Once Reuse]].

**Related:** [[Functions#Function-Backed Action|Function-Backed Action]] · [[Functions#Functions on Objects (FOO)|Functions on Objects (FOO)]] · [[Functions#Function Runtime|Function Runtime]] · [[Functions#Ontology Edits API|Ontology Edits API]]

**For our clone:** Keep; pick one runtime/language — see [[Design Decisions|D11]].

*clone: keep · kind: concept · layer: kinetic · invariants: [[Governed Writeback]] · [[Define-Once Reuse]] · source: Kinetic reconstruction §8*
#clone/keep #kind/concept #layer/kinetic

## Function Runtime

> The sandboxed environment functions run in (TypeScript v1/v2, Python), with limits and metering.

Default 60-second elapsed limit (TS v1: 30s CPU / 128 MB); serverless vs deployed modes; metered in compute-seconds. Scale/runtime detail Palantir needs that we can radically simplify.

**Related:** [[Functions#Function|Function]] · [[Compute Backends & Economics|Compute-Seconds]]

**For our clone:** Pick one runtime, likely the app backend's own language (D11).

*clone: keep · kind: concept · layer: kinetic · invariants: [[Governed Writeback]] · source: Kinetic reconstruction §8.2*
#clone/keep #kind/concept #layer/kinetic

## Functions on Objects (FOO)

> Functions exposed on object types for object-aware logic and computed/derived columns.

Consumed in Workshop/Quiver/Map; the read-side counterpart to edit functions. Each execution carries a small compute-second overhead.

**Related:** [[Functions#Function|Function]] · [[Properties#Derived Property|Derived Property]] · [[Objects#Object Type|Object Type]]

*clone: keep · kind: mechanism · layer: kinetic · invariants: [[Semantic Model Over Data]] · [[Define-Once Reuse]] · source: Kinetic reconstruction §8.1*
#clone/keep #kind/mechanism #layer/kinetic

## Ontology Edits API

> The in-function API for create/update/delete object and link edits (verified surface).

TS v2 builds an edit batch (`createEditBatch` → `getEdits()`); Python uses `client.ontology.edits()` → `get_edits()`; TS v1 captures edits implicitly. Edits are collapsed to the minimal set and applied as one transaction.

**Related:** [[Functions#Function|Function]] · [[Functions#Function-Backed Action|Function-Backed Action]] · [[Actions#Action Atomicity|Action Atomicity]] · [[Audit & Writeback#Writeback Path|Writeback Path]]

**For our clone:** Design our own edit API; the *contract* (atomic batched edits) is what matters.

*clone: keep · kind: mechanism · layer: kinetic · invariants: [[Governed Writeback]] · source: Kinetic reconstruction §6*
#clone/keep #kind/mechanism #layer/kinetic

## Function-Backed Action

> An action whose edits are computed by a function via the Ontology Edits API — for complex writeback.

The function's inputs derive from action parameters; it returns a batch of edits applied atomically. When this rule is present, no other rule may coexist. Enables multi-object, conditional writeback.

**Related:** [[Functions#Function|Function]] · [[Actions#Action Type|Action Type]] · [[Functions#Ontology Edits API|Ontology Edits API]] · [[Actions#Action Atomicity|Action Atomicity]]

*clone: keep · kind: mechanism · layer: kinetic · invariants: [[Governed Writeback]] · source: Kinetic reconstruction §6*
#clone/keep #kind/mechanism #layer/kinetic

## External Function

> A function permitted to call an external API, gated through a Data Connection source.

By default functions cannot call out; a configured source enables egress. Lets governed logic integrate with outside systems without leaving the [[Governed Writeback|action]] model.

**Related:** [[Functions#Function|Function]] · [[Integration & Automation#Webhook|Webhook]] · [[Data Connection (Magritte)|Data Connection]]

*clone: keep · kind: mechanism · layer: kinetic · invariants: [[Governed Writeback]] · [[Security Travels With Data]] · source: Kinetic reconstruction §9*
#clone/keep #kind/mechanism #layer/kinetic
