---
aliases:
  - Scenario
  - Scenario Overlay
  - Scenario Apply (Commit)
  - Scenario Comparison
  - State-Dependent Security
updated: 2026-06-13
---

# Scenarios

> Immutable, delta-only forks of the Ontology — copy-on-write what-if edits staged as Actions, read through an overlay, compared against a baseline, and applied transactionally by replay; plus the state-dependent security those staged edits can change.

## Scenario

> An immutable, delta-only fork of the Ontology — staged what-if edits that never touch reality until applied.

Created by applying [[Actions#Action Type|Actions]] and evaluating [[Models, Inference & Simulation#Model|Models]]; the fork stores **only the diff** from the base — modified properties, created/deleted objects, created/deleted links — keyed to base identity, not a snapshot. It is **immutable**: to 'modify' a Scenario you create a new one. Built on Actions infrastructure, so Action limits apply transitively. The projection half of the [[Digital Twin]].

**Related:** [[Scenarios#Scenario Overlay|Scenario Overlay]] · [[Scenarios#Scenario Apply (Commit)|Scenario Apply (Commit)]] · [[Scenarios#Scenario Comparison|Scenario Comparison]] · [[Actions#Action Type|Action Type]] · [[Functions#Function-Backed Action|Function-Backed Action]] · [[Models, Inference & Simulation#Model|Model]] · [[Digital Twin]]

**For our clone:** Defer — powerful but post-MVP. When built: a copy-on-write delta keyed to base identity, append-only/versioned, not a full copy.

*clone: defer · kind: concept · layer: dynamic · invariants: [[Governed Writeback]] · [[Versioned Data Foundation]] · source: Dynamic reconstruction §2.1–2.4*
#clone/defer #kind/concept #layer/dynamic

## Scenario Overlay

> The copy-on-write delta that holds a scenario's changes, merged over the base Ontology when a scenario context is supplied.

Records property mutations and created/deleted objects and links against base identity. Whether Foundry resolves it at read time or materializes a temporary store is **undocumented** ([Speculative]); the caps — 30,000 edits, 50 Actions, 10,000 objects loaded, no attachment properties — are consistent with a *bounded read-time merge*. Reads flow through the [[Object Storage#Object Set Service (OSS)|Object Set Service (OSS)]], and scenario state does not auto-propagate through object sets — consumers reference a scenario variable explicitly.

**Related:** [[Scenarios#Scenario|Scenario]] · [[Object Storage#Object Set Service (OSS)|Object Set Service (OSS)]] · [[Object Storage#Object Storage V2 (OSv2)|Object Storage V2 (OSv2)]] · [[Reactive State Model#Workshop Variable|Workshop Variable]]

**For our clone:** Defer — implement as a read-time overlay keyed to identity; validate the scale assumption against your own tests before trusting it.

*clone: defer · kind: mechanism · layer: dynamic · invariants: [[Versioned Data Foundation]] · source: Dynamic reconstruction §2.3, §2.8*
#clone/defer #kind/mechanism #layer/dynamic

## Scenario Apply (Commit)

> Committing a scenario by replaying its staged Actions transactionally — all-or-nothing — never by diff-merging a blob.

Either every Action applies or none does if any fails validation. **Model results are never written back** — they are expected outputs, not modifiable values. Permission to apply equals permission to run the configured apply [[Actions#Action Type|Action]]; an optional post-apply Action's validation gates it further.

**Related:** [[Scenarios#Scenario|Scenario]] · [[Actions#Action Type|Action Type]] · [[Actions#Action Atomicity|Action Atomicity]] · [[Actions#Submission Criteria|Submission Criteria]] · [[Models, Inference & Simulation#Model|Model]]

**For our clone:** Defer — but the rule is free once Actions are transactional: replay the staged Actions, and never persist model outputs.

*clone: defer · kind: mechanism · layer: dynamic · invariants: [[Governed Writeback]] · source: Dynamic reconstruction §2.6*
#clone/defer #kind/mechanism #layer/dynamic

## Scenario Comparison

> Reading scenario-vs-baseline and scenario-vs-scenario side by side to see what each what-if changes.

Scenario-aware widgets show values **only in columns that differ** and can layer many scenarios at once; in [[Analysis Surfaces#Vertex|Vertex]] a *baseline* runs the chosen [[Models, Inference & Simulation#Model|models]] with no overrides as the reference. A read-only surface over the [[Scenarios#Scenario Overlay|Scenario Overlay]].

**Related:** [[Scenarios#Scenario|Scenario]] · [[Scenarios#Scenario Overlay|Scenario Overlay]] · [[Analysis Surfaces#Vertex|Vertex]] · [[Reactive State Model#Workshop Variable|Workshop Variable]]

**For our clone:** Defer — a UI affordance over overlays; trivial once overlays and a baseline exist.

*clone: defer · kind: mechanism · layer: dynamic · invariants: [[Versioned Data Foundation]] · source: Dynamic reconstruction §2.5*
#clone/defer #kind/mechanism #layer/dynamic

## State-Dependent Security

> Access that changes as object state changes — editing a policy-referenced property can grant or revoke visibility.

The *dynamic* face of [[Security Travels With Data]]: because [[Data-Level Security Policies#Object Security Policy|policies]] and [[Properties#Mandatory Control Property|control properties]] are evaluated per query, an [[Actions#Action Type|Action]] (or a [[Scenarios#Scenario|Scenario]]-staged edit) that mutates a referenced property immediately changes who can see the object. Policy changes propagate near-instantly; group/attribute changes are cached briefly.

**Related:** [[Data-Level Security Policies#Object Security Policy|Object Security Policy]] · [[Properties#Mandatory Control Property|Mandatory Control Property]] · [[Data-Level Security Policies#Property Security Policy|Property Security Policy]] · [[Scenarios#Scenario|Scenario]]

**For our clone:** Simplify — falls out of per-query, data-driven security we already keep; no extra machinery needed.

*clone: simplify · kind: property · layer: dynamic · invariants: [[Security Travels With Data]] · [[Governed Writeback]] · source: Dynamic reconstruction §7.2*
#clone/simplify #kind/property #layer/dynamic
