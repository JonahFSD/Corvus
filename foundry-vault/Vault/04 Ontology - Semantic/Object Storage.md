---
aliases:
  - Object Storage Backend (OSv2)
  - Object Storage V2 (OSv2)
  - OSv2
  - Object Set Service (OSS)
  - OSS
  - Object Data Funnel
  - Object Indexing
  - Phonograph (OSv1)
  - OSv1
layer: semantic
kind: service
clone: drop
invariants:
  - "[[Semantic Model Over Data]]"
  - "[[Governed Writeback]]"
  - "[[Versioned Data Foundation]]"
source: "Semantic reconstruction §4.1, §4.2, §5.2 / Kinetic §7"
updated: 2026-06-13
---

# Object Storage

> Foundry's object-storage plumbing — the services that index, write, and serve objects. We replace all of it with an ordinary database; kept here for completeness, not as clone targets.

## Object Storage V2 (OSv2)

> The next-gen backend that indexes/serves objects across multiple storage backends in parallel.

Replaces [[#Phonograph (OSv1)|Phonograph]]; separates indexing from querying for scale (tens of billions of objects/type). Comprises the [[#Object Data Funnel|Object Data Funnel]], [[#Object Set Service (OSS)|Object Set Service]], and [[Ontology & Metadata#Ontology Metadata Service (OMS)|Ontology Metadata Service (OMS)]].

**For our clone:** Drop the decomposition — objects live in our DB.

## Object Data Funnel

> The OSv2 microservice that orchestrates writes into the Ontology and indexing of datasources + edits.

Receives modification instructions from the [[Actions#Action Type|Actions]] service into an offset-tracked queue, applies them to the live index immediately, and flushes periodically to a durable [[Materialization|merged dataset]]. Enables [[Read-Your-Writes]] at scale.

**Related:** [[Audit & Writeback#Writeback Path|Writeback Path]] · [[Materialization]] · [[Read-Your-Writes]]

**For our clone:** Drop — a DB commit is our write; no queue needed.

## Object Indexing

> Turning dataset rows and user edits into searchable, queryable objects in an object database.

Incremental in OSv2; the index is ephemeral (durability comes from datasources + [[Materialization|merged datasets]]). The 'live' feeling of objects comes from here.

**For our clone:** Drop a separate index tier — DB indexes suffice (D8).

## Object Set Service (OSS)

> The OSv2 service that serves reads — searching, filtering, aggregating, loading objects.

Determines which compute engine runs a query and produces [[Objects#Object Set|object sets]]. For our scale, ordinary database queries cover this.

**For our clone:** Drop — DB queries replace it.

## Phonograph (OSv1)

> The legacy object backend (Elasticsearch-based); end-of-life after June 30, 2026.

Foundry's original object database for indexing, edits, and writeback. Superseded by OSv2 (above). Historical context, not a clone target.

**For our clone:** Drop (legacy).
