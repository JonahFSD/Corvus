---
aliases:
  - Ontology
  - Ontology Metadata Service (OMS)
  - OMS
  - Interface (Ontology)
  - Ontology Branching & Proposals
layer: semantic
kind: domain
updated: 2026-06-13
---

# Ontology & Metadata

> The ontology as a whole, and the services and constructs that define and govern the structure of the model.

## Ontology

> Foundry's semantic + kinetic model of the business — the operational layer over integrated data.

Simultaneously a database, an API, a permission system, and a workflow engine. Its semantic half ([[Objects#Object Type|objects]], [[Properties#Property|properties]], [[Links#Link Type|links]]) says what exists; its [[Ontology — Kinetic Layer|kinetic]] half ([[Actions#Action Type|actions]], [[Functions#Function|functions]]) says what can happen. The [[Digital Twin]] of the organization.

**Related:** [[Objects#Object Type|Object Type]] · [[Links#Link Type|Link Type]] · [[Actions#Action Type|Action Type]] · [[Functions#Function|Function]] · [[Digital Twin]]

*clone: keep · kind: concept · layer: semantic · invariants: [[Semantic Model Over Data]] · source: Semantic reconstruction*
#clone/keep #kind/concept #layer/semantic

## Ontology Metadata Service (OMS)

> The service that defines the set of ontological entities — object, link, and action types.

The source of truth for the *structure* of the [[Ontology & Metadata#Ontology|Ontology]] (vs the data). Records definition changes; tracks legacy usage during migration.

**Related:** [[Ontology & Metadata#Ontology|Ontology]] · [[Objects#Object Type|Object Type]] · [[Links#Link Type|Link Type]] · [[Actions#Action Type|Action Type]]

**For our clone:** Becomes our schema/metadata store (could be plain DB tables).

*clone: keep · kind: service · layer: semantic · invariants: [[Semantic Model Over Data]] · source: Semantic reconstruction §7.1*
#clone/keep #kind/service #layer/semantic

## Interface (Ontology)

> An abstract shape (shared properties + link constraints) that object types implement — polymorphism.

Cannot be instantiated directly; object types map local properties onto required interface properties. Enables searching/acting across many types uniformly. An enterprise-modeling feature.

**Related:** [[Objects#Object Type|Object Type]] · [[Properties#Shared Property|Shared Property]] · [[Properties#Property|Property]]

**For our clone:** Defer — add when multiple types need a shared contract.

*clone: defer · kind: concept · layer: semantic · invariants: [[Semantic Model Over Data]] · source: Semantic reconstruction §2.7*
#clone/defer #kind/concept #layer/semantic

## Ontology Branching & Proposals

> PR-style review of model changes: a proposal groups ontology edits for approval before merge.

Integrates with Global Branching; reviewers approve per-resource changes. Valuable when many people build the model; heavier than a small team needs initially.

**Related:** [[Dataset & Transactions|Dataset Branch]] · [[Ontology & Metadata#Ontology Metadata Service (OMS)|Ontology Metadata Service (OMS)]]

**For our clone:** Defer — simpler change management at v1.

*clone: defer · kind: mechanism · layer: semantic · invariants: [[Governed Writeback]] · source: Semantic reconstruction §7.2*
#clone/defer #kind/mechanism #layer/semantic
