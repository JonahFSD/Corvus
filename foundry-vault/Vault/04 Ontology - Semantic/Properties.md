---
aliases:
  - Property
  - Property Base Type
  - Value Type
  - Derived Property
  - Shared Property
  - Title Property
  - Advanced Property Types
  - Mandatory Control Property
layer: semantic
kind: domain
updated: 2026-06-13
---

# Properties

> The typed attributes of objects — base types, reusable value types, derived and shared properties, and property-level access controls.

## Property

> A typed attribute of an object type (a circuit's bandwidth, a carrier's account manager).

Has a [[Properties#Property Base Type|base type]] and optional [[Properties#Value Type|value type]] for validation, plus metadata (formatting, visibility, render hints). One property may be the [[Objects#Primary Key|Primary Key]] or [[Properties#Title Property|Title Property]].

**Related:** [[Properties#Property Base Type|Property Base Type]] · [[Properties#Value Type|Value Type]] · [[Objects#Primary Key|Primary Key]] · [[Properties#Title Property|Title Property]] · [[Properties#Derived Property|Derived Property]]

*clone: keep · kind: concept · layer: semantic · invariants: [[Semantic Model Over Data]] · source: Semantic reconstruction §2.2*
#clone/keep #kind/concept #layer/semantic

## Property Base Type

> The underlying datatype of a property (string, integer, date, boolean, geopoint, …).

Determines the operations available. A small core (text/number/date/boolean) covers most needs; advanced types add geo, time-series, media, struct, vector. See [[Properties#Advanced Property Types|Advanced Property Types]].

**Related:** [[Properties#Property|Property]] · [[Properties#Value Type|Value Type]] · [[Properties#Advanced Property Types|Advanced Property Types]]

**For our clone:** Keep a small core; defer advanced types (D7).

*clone: keep · kind: type · layer: semantic · invariants: [[Semantic Model Over Data]] · source: Semantic reconstruction §2.2*
#clone/keep #kind/type #layer/semantic

## Value Type

> A reusable semantic wrapper over a base type that adds constraints (email regex, enum, range).

Defined once, reused across object types and pipelines, versioned and permissioned — conceptually like RDF/OWL/XSD typing. The mechanism for [[Define-Once Reuse|define-once]] validation.

**Related:** [[Properties#Property Base Type|Property Base Type]] · [[Properties#Property|Property]] · [[Actions#Submission Criteria|Submission Criteria]]

**For our clone:** Keep — constrained/enumerated values are high-value at v1.

*clone: keep · kind: type · layer: semantic · invariants: [[Semantic Model Over Data]] · [[Governed Writeback]] · source: Semantic reconstruction §2.3*
#clone/keep #kind/type #layer/semantic

## Derived Property

> A property computed at runtime from other properties or linked objects (counts, sums, lookups).

Read-only; traverses up to a few link levels; cannot be a primary key or carry constraints. Useful for live rollups without storing redundant data.

**Related:** [[Properties#Property|Property]] · [[Links#Link Type|Link Type]] · [[Functions#Function|Function]]

*clone: keep · kind: mechanism · layer: semantic · invariants: [[Semantic Model Over Data]] · source: Semantic reconstruction §2.4*
#clone/keep #kind/mechanism #layer/semantic

## Shared Property

> A property reusable across multiple object types for consistent modeling and centralized metadata.

Can satisfy [[Ontology & Metadata#Interface (Ontology)|interface]] requirements. Another expression of [[Define-Once Reuse]] at the property level.

**Related:** [[Properties#Property|Property]] · [[Ontology & Metadata#Interface (Ontology)|Interface (Ontology)]]

*clone: keep · kind: concept · layer: semantic · invariants: [[Semantic Model Over Data]] · source: Semantic reconstruction §2.8*
#clone/keep #kind/concept #layer/semantic

## Title Property

> The human-readable display property shown for an object across applications.

e.g., a person's full name or a circuit's ID. A small but important piece of [[Define-Once Reuse]] — one display rule, everywhere.

**Related:** [[Objects#Object Type|Object Type]] · [[Properties#Property|Property]]

*clone: keep · kind: concept · layer: semantic · invariants: [[Semantic Model Over Data]] · source: Semantic reconstruction §2.1*
#clone/keep #kind/concept #layer/semantic

## Advanced Property Types

> The richer property types beyond the core: geospatial, time-series, media, attachment, struct, vector, marking.

Each needs special configuration (e.g., vector for semantic search, geotime for tracks, media reference for large files). Powerful but optional — implement on real need.

**Related:** [[Properties#Property Base Type|Property Base Type]] · [[Properties#Mandatory Control Property|Mandatory Control Property]]

**For our clone:** Defer most; add per real requirement (D7).

*clone: defer · kind: type · layer: semantic · invariants: [[Semantic Model Over Data]] · source: Semantic reconstruction §2.5*
#clone/defer #kind/type #layer/semantic

## Mandatory Control Property

> A property carrying markings/organizations/classifications that enforce access at the storage level.

An object violating its mandatory-control constraints fails to index; invalid edits are rejected at submit. The point where [[Security Travels With Data|security]] becomes part of the object itself.

**Related:** [[Mandatory Controls & Classification#Marking|Marking]] · [[Data-Level Security Policies#Object Security Policy|Object Security Policy]] · [[Properties#Property|Property]]

*clone: keep · kind: concept · layer: semantic · invariants: [[Security Travels With Data]] · [[Semantic Model Over Data]] · source: Semantic reconstruction §4.5*
#clone/keep #kind/concept #layer/semantic
