---
aliases:
  - Action Type
  - Action Parameter
  - Action Rule
  - Side Effect
  - Submission Criteria
  - Action Atomicity
  - Inline Edit
  - Edits-Only-via-Actions
updated: 2026-06-13
---

# Actions

> The governed, transactional change model: action types and their parameters, rules, side effects, submission criteria, and atomicity — the only sanctioned way to edit the Ontology.

## Action Type

> A governed, transactional definition of a set of edits to objects/links, plus side effects.

Bundles [[Actions#Action Parameter|parameters]] (typed inputs), [[Actions#Action Rule|rules]] (the edits), and [[Actions#Submission Criteria|submission criteria]] (validation). The *only* sanctioned way to change the [[Ontology & Metadata#Ontology|Ontology]] — the heart of [[Actions#Edits-Only-via-Actions|Edits-Only-via-Actions]].

**Related:** [[Actions#Action Parameter|Action Parameter]] · [[Actions#Action Rule|Action Rule]] · [[Actions#Submission Criteria|Submission Criteria]] · [[Actions#Action Atomicity|Action Atomicity]] · [[Actions#Edits-Only-via-Actions|Edits-Only-via-Actions]] · [[Functions#Function-Backed Action|Function-Backed Action]]

**For our clone:** Keep (the heart). Definition format: declarative vs code — see [[Design Decisions|D10]].

*clone: keep · kind: concept · layer: kinetic · invariants: [[Governed Writeback]] · source: Kinetic reconstruction §2*
#clone/keep #kind/concept #layer/kinetic

## Action Parameter

> A typed input to an action — the interface between the form/caller and the rules.

Can be a primitive, object/object-set reference, attachment, etc.; supports defaults, validation, conditional visibility, and reading an object's *current* value before the edit. Binds to apps (Workshop, Object Views).

**Related:** [[Actions#Action Type|Action Type]] · [[Actions#Action Rule|Action Rule]] · [[Actions#Submission Criteria|Submission Criteria]]

*clone: keep · kind: concept · layer: kinetic · invariants: [[Governed Writeback]] · source: Kinetic reconstruction §3*
#clone/keep #kind/concept #layer/kinetic

## Action Rule

> The logic of an action: an Ontology edit (create/modify/delete object, add/remove link) or a side effect.

Multiple rules compile to a single edit per object (last-writer-wins per property). A [[Functions#Function-Backed Action|function rule]] is exclusive — when present, no other rule may be configured. See also [[Actions#Side Effect|Side Effect]].

**Related:** [[Actions#Action Type|Action Type]] · [[Functions#Function-Backed Action|Function-Backed Action]] · [[Actions#Side Effect|Side Effect]]

*clone: keep · kind: concept · layer: kinetic · invariants: [[Governed Writeback]] · source: Kinetic reconstruction §4*
#clone/keep #kind/concept #layer/kinetic

## Side Effect

> A non-edit action outcome: notify someone, call a webhook, trigger a build.

Runs around the edit with defined ordering/failure semantics (a failed notification doesn't roll back edits; a failed writeback webhook does). The 'and then…' of an [[Actions#Action Type|action]].

**Related:** [[Actions#Action Rule|Action Rule]] · [[Integration & Automation#Webhook|Webhook]]

*clone: keep · kind: concept · layer: kinetic · invariants: [[Governed Writeback]] · source: Kinetic reconstruction §4*
#clone/keep #kind/concept #layer/kinetic

## Submission Criteria

> Server-enforced conditions (formerly 'validations') determining whether an action can be submitted.

Encode business rules using object, link, and user attributes ('only a manager can escalate'). Enforced on the server, never trusting the client. The governance gate of [[Governed Writeback]].

**Related:** [[Actions#Action Type|Action Type]] · [[Actions#Action Parameter|Action Parameter]] · [[Properties#Value Type|Value Type]]

**For our clone:** Keep (core). Expressed as a small DSL or as functions — see [[Design Decisions|D12]].

*clone: keep · kind: mechanism · layer: kinetic · invariants: [[Governed Writeback]] · source: Kinetic reconstruction §5*
#clone/keep #kind/mechanism #layer/kinetic

## Action Atomicity

> All edits an action computes succeed together or not at all — one transaction.

A function that throws produces no edits (whole-function-must-succeed). Cross-system writes (e.g., a [[Integration & Automation#Webhook|Webhook]]) are *not* transactional and must be handled explicitly. A DB transaction gives us this directly.

**Related:** [[Actions#Action Type|Action Type]] · [[Functions#Function-Backed Action|Function-Backed Action]] · [[Audit & Writeback#Writeback Path|Writeback Path]] · [[Integration & Automation#Webhook|Webhook]]

**For our clone:** Keep — one DB transaction per action (D14).

*clone: keep · kind: property · layer: kinetic · invariants: [[Governed Writeback]] · source: Kinetic reconstruction §6*
#clone/keep #kind/property #layer/kinetic

## Inline Edit

> A cell-level edit bound to a single object via an action type.

A convenience surface for quick edits that still flows through the [[Actions#Action Type|action]] machinery — preserving [[Actions#Edits-Only-via-Actions|Edits-Only-via-Actions]] guarantees.

**Related:** [[Actions#Action Type|Action Type]] · [[Actions#Edits-Only-via-Actions|Edits-Only-via-Actions]]

*clone: keep · kind: mechanism · layer: kinetic · invariants: [[Governed Writeback]] · source: Kinetic reconstruction §2*
#clone/keep #kind/mechanism #layer/kinetic

## Edits-Only-via-Actions

> The governance pattern: objects change ONLY through defined, validated, audited actions.

What makes the platform *operational* rather than a database with a UI. A user may even create objects they can't view. This pattern + a [[Versioned Data Foundation|versioned store]] = end-to-end provenance.

**Related:** [[Actions#Action Type|Action Type]] · [[Actions#Submission Criteria|Submission Criteria]] · [[Audit & Writeback#Edit History|Edit History]] · [[Operational Application]]

**For our clone:** Keep — the single most important pattern to replicate.

*clone: keep · kind: pattern · layer: kinetic · invariants: [[Governed Writeback]] · [[Security Travels With Data]] · source: Kinetic reconstruction §11*
#clone/keep #kind/pattern #layer/kinetic
