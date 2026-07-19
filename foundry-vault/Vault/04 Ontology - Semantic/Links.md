---
aliases:
  - Link Type
  - Link Cardinality
  - Object-Backed Link
layer: semantic
kind: domain
updated: 2026-06-13
---

# Links

> First-class, traversable relationships between object types — their cardinality and link-carrying object types.

## Link Type

> A first-class, named, traversable relationship between two object types.

Supports the three [[Links#Link Cardinality|cardinalities]] (1:1, 1:N, N:M). Implemented via foreign keys, join-table datasets, or an [[Links#Object-Backed Link|Object-Backed Link]]. The edges of the [[Semantic Model Over Data|model]] ('show me this carrier's circuits').

**Related:** [[Links#Link Cardinality|Link Cardinality]] · [[Links#Object-Backed Link|Object-Backed Link]] · [[Objects#Object Type|Object Type]]

**For our clone:** Keep (core). FK for 1:N, join table for N:M, or a unified edge table — see [[Design Decisions|D6]].

*clone: keep · kind: concept · layer: semantic · invariants: [[Semantic Model Over Data]] · source: Semantic reconstruction §9 / Kinetic §9*
#clone/keep #kind/concept #layer/semantic

## Link Cardinality

> The multiplicity of a relationship: one-to-one, one-to-many, or many-to-many.

1:1 and many:1 use a foreign-key property; N:M uses a join-table dataset (or an [[Links#Object-Backed Link|Object-Backed Link]] when the link itself needs properties).

**Related:** [[Links#Link Type|Link Type]] · [[Links#Object-Backed Link|Object-Backed Link]]

*clone: keep · kind: concept · layer: semantic · invariants: [[Semantic Model Over Data]] · source: Kinetic reconstruction §9.1*
#clone/keep #kind/concept #layer/semantic

## Object-Backed Link

> A link type that carries its own object type, so the relationship can hold properties.

Extends many-to-one with first-class storage and metadata (e.g., a Flight Manifest linking Pilot and Aircraft). Adds link-level attributes at the cost of an extra object type.

**Related:** [[Links#Link Type|Link Type]] · [[Links#Link Cardinality|Link Cardinality]] · [[Objects#Object Type|Object Type]]

*clone: keep · kind: mechanism · layer: semantic · invariants: [[Semantic Model Over Data]] · source: Kinetic reconstruction §9.1*
#clone/keep #kind/mechanism #layer/semantic
