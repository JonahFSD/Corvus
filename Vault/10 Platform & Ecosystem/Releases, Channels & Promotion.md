---
aliases:
  - Apollo Product
  - Release & Version
  - Release Channel
  - Entity & Environment
  - Promotion Pipeline
  - Recall & Roll-off
  - Zero-Downtime Upgrade
tags:
  - layer/platform
  - kind/doc
  - clone/drop
layer: platform
kind: doc
clone: drop
source: "10 Platform & Ecosystem (consolidated)"
updated: 2026-06-14
---

# Releases, Channels & Promotion

> What Apollo deploys and how it flows — versioned products and releases, the channels environments subscribe to, and the health-gated promotion, rollback, and zero-downtime mechanics that move them safely.

## Apollo Product

> A deployable software component (Helm chart or asset) identified by Maven coordinates, with an immutable manifest.

Packaged as a tarball with declarative dependency/incompatibility/health extensions; published to the per-Hub Product catalog. The deployment counterpart to a [[Marketplace & Packaging#Marketplace Product|Marketplace Product]].

**Invariants:** [[End-to-End Lineage]]

**Related:** [[Releases, Channels & Promotion#Release & Version|Release & Version]] · [[Apollo & the Delivery Engine#Apollo|Apollo]] · [[Marketplace & Packaging#Marketplace Product|Marketplace Product]]

*clone: drop · kind: concept · layer: platform · invariants: [[End-to-End Lineage]] · source: Platform reconstruction §3*
#clone/drop #kind/concept #layer/platform

## Release & Version

> A published, versioned artifact + immutable metadata; versions are strictly orderable so Apollo can reason about upgrades.

Identified by `group:artifactId:version`. Ordering lets the engine compute forward/backward migrations and compatibility ranges. The unit that flows through [[Releases, Channels & Promotion#Release Channel|channels]].

**Invariants:** [[End-to-End Lineage]] · [[Versioned Data Foundation]]

**Related:** [[Releases, Channels & Promotion#Apollo Product|Apollo Product]] · [[Releases, Channels & Promotion#Release Channel|Release Channel]] · [[Releases, Channels & Promotion#Recall & Roll-off|Recall & Roll-off]]

*clone: drop · kind: concept · layer: platform · invariants: [[End-to-End Lineage]] · [[Versioned Data Foundation]] · source: Platform reconstruction §3.1*
#clone/drop #kind/concept #layer/platform

## Release Channel

> A named promotion tier (e.g. RELEASE → CANARY → STABLE) that environments subscribe to by stability need.

The pull-model dial: operators choose a channel; the [[Releases, Channels & Promotion#Promotion Pipeline|Promotion Pipeline]] moves releases between channels by health and soak. Decouples 'what exists' from 'what each env runs'.

**Invariants:** [[End-to-End Lineage]]

**Related:** [[Releases, Channels & Promotion#Promotion Pipeline|Promotion Pipeline]] · [[Releases, Channels & Promotion#Release & Version|Release & Version]] · [[Releases, Channels & Promotion#Entity & Environment|Entity & Environment]]

*clone: drop · kind: mechanism · layer: platform · invariants: [[End-to-End Lineage]] · source: Platform reconstruction §4*
#clone/drop #kind/mechanism #layer/platform

## Entity & Environment

> An Entity is one installed Product in one Environment; an Environment is a grouping of Entities in one cluster.

Environments are disjoint and may be disconnected when unmanaged. An Entity is defined by a Product + [[Releases, Channels & Promotion#Release Channel|Release Channel]] (not a fixed version) — Apollo keeps it at the latest allowed state.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Releases, Channels & Promotion#Apollo Product|Apollo Product]] · [[Releases, Channels & Promotion#Release Channel|Release Channel]] · [[Apollo & the Delivery Engine#Hub-and-Spoke|Hub-and-Spoke]]

*clone: drop · kind: concept · layer: platform · invariants: [[Security Travels With Data]] · source: Platform reconstruction §3.1*
#clone/drop #kind/concept #layer/platform

## Promotion Pipeline

> Health- and time-gated automatic promotion of a release between channels (soak duration + criteria).

Promotes only after a release stays healthy across N entities for a soak window; cancels on timeout (2× soak; 7-day canary reachability); can auto-[[Releases, Channels & Promotion#Recall & Roll-off|recall]] when unhealthy. The safety automation of delivery.

**Invariants:** [[End-to-End Lineage]]

**Related:** [[Releases, Channels & Promotion#Release Channel|Release Channel]] · [[Releases, Channels & Promotion#Recall & Roll-off|Recall & Roll-off]] · [[Releases, Channels & Promotion#Zero-Downtime Upgrade|Zero-Downtime Upgrade]] · [[Apollo & the Delivery Engine#Orchestration Engine|Orchestration Engine]]

*clone: drop · kind: mechanism · layer: platform · invariants: [[End-to-End Lineage]] · source: Platform reconstruction §4.2*
#clone/drop #kind/mechanism #layer/platform

## Recall & Roll-off

> Marking a release bad and reverting: roll forward, allow downgrade, freeze, or per-environment.

Triggered manually, automatically (unstable promotion), or via API (e.g. CVE scans). Safety can override the no-downtime window during a recall. The rollback story.

**Invariants:** [[End-to-End Lineage]]

**Related:** [[Releases, Channels & Promotion#Release & Version|Release & Version]] · [[Releases, Channels & Promotion#Promotion Pipeline|Promotion Pipeline]] · [[Apollo & the Delivery Engine#Apollo|Apollo]]

*clone: drop · kind: mechanism · layer: platform · invariants: [[End-to-End Lineage]] · source: Platform reconstruction §4.3*
#clone/drop #kind/mechanism #layer/platform

## Zero-Downtime Upgrade

> Blue/green rollout on multi-node services: build a parallel 'green', shift traffic, destroy 'blue'.

Required of every service claiming zero-downtime; leverages [[Infrastructure Substrate#Rubix|Rubix]]'s opinionated API layer. How Apollo runs thousands of upgrades a day without outage.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Releases, Channels & Promotion#Promotion Pipeline|Promotion Pipeline]] · [[Infrastructure Substrate#Rubix|Rubix]] · [[Apollo & the Delivery Engine#Apollo|Apollo]]

*clone: drop · kind: mechanism · layer: platform · invariants: [[Security Travels With Data]] · source: Platform reconstruction §4.4*
#clone/drop #kind/mechanism #layer/platform
