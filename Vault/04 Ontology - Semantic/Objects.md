---
aliases:
  - Object Type
  - Object
  - Primary Key
  - Object Backing
  - Object Set
layer: semantic
kind: domain
updated: 2026-06-13
---

# Objects

> The object model — the nouns of the semantic layer: the kinds of real-world entities, their instances, identity, and how they are materialized from data.

## Object Type

> The schema definition of a kind of real-world entity or event (a Carrier, a Circuit, a Contract).

Has a [[Objects#Primary Key|Primary Key]], a [[Properties#Title Property|Title Property]], and typed [[Properties#Property|properties]]; its instances are [[Objects#Object|objects]]. Materialized from a backing dataset (see [[Objects#Object Backing|Object Backing]]). The nouns of the [[Semantic Model Over Data|model]].

**Related:** [[Objects#Object|Object]] · [[Properties#Property|Property]] · [[Links#Link Type|Link Type]] · [[Objects#Primary Key|Primary Key]] · [[Properties#Title Property|Title Property]] · [[Objects#Object Backing|Object Backing]]

**For our clone:** Keep (core). One DB table per type, or a generic store — see [[Design Decisions|D5]].

*clone: keep · kind: concept · layer: semantic · invariants: [[Semantic Model Over Data]] · source: Semantic reconstruction §2.1*
#clone/keep #kind/concept #layer/semantic

## Object

> A single instance of an object type — one set of primary-key + property values.

Analogous to a row, but a first-class thing users search, view, and act on. Carries a [[RID]] and [[Objects#Primary Key|primary key]]; addressable, traversable via [[Links#Link Type|links]], and editable only through [[Actions#Action Type|actions]].

**Related:** [[Objects#Object Type|Object Type]] · [[Properties#Property|Property]] · [[Objects#Primary Key|Primary Key]] · [[Objects#Object Set|Object Set]]

*clone: keep · kind: concept · layer: semantic · invariants: [[Semantic Model Over Data]] · source: Semantic reconstruction §2.1*
#clone/keep #kind/concept #layer/semantic

## Primary Key

> The property uniquely identifying each object instance; should be deterministic.

Must be unique in the backing dataset; cannot be edited by an [[Actions#Action Type|action]] (that would be delete + create). Certain types (geo, arrays, real numbers) can't be primary keys.

**Related:** [[Objects#Object Type|Object Type]] · [[Objects#Object|Object]] · [[Objects#Object Backing|Object Backing]]

*clone: keep · kind: concept · layer: semantic · invariants: [[Semantic Model Over Data]] · source: Semantic reconstruction §2.1*
#clone/keep #kind/concept #layer/semantic

## Object Backing

> The handoff where a curated dataset materializes an object type: rows → objects, columns → properties.

The seam between the [[Data Integration & Pipeline Layer|data layer]] and the [[Ontology — Semantic Layer|semantic layer]]. The semantic layer is a *view of meaning* over the [[Versioned Data Foundation|versioned store]], not a separate source of truth.

**Related:** [[Dataset & Transactions|Dataset]] · [[Objects#Object Type|Object Type]] · [[Properties#Property|Property]] · [[Materialization]]

**For our clone:** Keep — the data→object handoff must be first-class.

*clone: keep · kind: mechanism · layer: semantic · invariants: [[Semantic Model Over Data]] · [[Versioned Data Foundation]] · [[End-to-End Lineage]] · source: Semantic reconstruction §3.1*
#clone/keep #kind/mechanism #layer/semantic

## Object Set

> A saved or temporary query over objects (static list or dynamic filter), served by the Object Set Service.

The unit of 'show me all circuits with degraded SLA this quarter'. Composable, shareable, and permissioned; the read surface over the [[Objects#Object Type|object model]].

**Related:** [[Object Storage#Object Set Service (OSS)|Object Set Service (OSS)]] · [[Objects#Object|Object]] · [[Objects#Object Type|Object Type]]

**For our clone:** Keep (core) — saved filters over objects.

*clone: keep · kind: concept · layer: semantic · invariants: [[Semantic Model Over Data]] · source: Semantic reconstruction §5.1*
#clone/keep #kind/concept #layer/semantic
