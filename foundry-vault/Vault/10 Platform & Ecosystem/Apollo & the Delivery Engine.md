---
aliases:
  - Apollo
  - Apollo Constraint
  - Apollo Plan
  - Orchestration Engine
  - Hub-and-Spoke
  - Spoke Control Plane
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

# Apollo & the Delivery Engine

> Palantir's continuous-delivery control plane — a constraint-based, pull-model engine with no target state, its hub-and-spoke topology, and the plans it issues to keep thousands of services compatible during rolling upgrades.

## Apollo

> Palantir's continuous-delivery control plane: a constraint-based, pull-model system with NO single target state.

Developers register [[Releases, Channels & Promotion#Apollo Product|products]] + constraints; environments subscribe to [[Releases, Channels & Promotion#Release Channel|channels]]; the [[Apollo & the Delivery Engine#Orchestration Engine|Orchestration Engine]] proposes [[Apollo & the Delivery Engine#Apollo Plan|Plans]] that satisfy all constraints. Deployments are versioned operational logic, not code bundles. Hosts Foundry + AIP on [[Infrastructure Substrate#Rubix|Rubix]].

**Invariants:** [[End-to-End Lineage]]

**Related:** [[Apollo & the Delivery Engine#Hub-and-Spoke|Hub-and-Spoke]] · [[Apollo & the Delivery Engine#Orchestration Engine|Orchestration Engine]] · [[Apollo & the Delivery Engine#Apollo Plan|Apollo Plan]] · [[Releases, Channels & Promotion#Apollo Product|Apollo Product]] · [[Releases, Channels & Promotion#Release Channel|Release Channel]] · [[Infrastructure Substrate#Rubix|Rubix]]

**For our clone:** Drop for an internal tool — ordinary deployment suffices; keep only the idea of versioned, auditable releases.

*clone: drop · kind: service · layer: platform · invariants: [[End-to-End Lineage]] · source: Platform reconstruction §2*
#clone/drop #kind/service #layer/platform

## Apollo Constraint

> A precondition a Plan must satisfy: dependencies, incompatibilities, schema versions, maintenance/suppression windows, health.

The engine can only propose changes that violate no constraint — how Apollo keeps thousands of services compatible during rolling upgrades.

**Invariants:** [[Security Travels With Data]] · [[End-to-End Lineage]]

**Related:** [[Apollo & the Delivery Engine#Apollo Plan|Apollo Plan]] · [[Apollo & the Delivery Engine#Orchestration Engine|Orchestration Engine]] · [[Releases, Channels & Promotion#Apollo Product|Apollo Product]]

*clone: drop · kind: concept · layer: platform · invariants: [[Security Travels With Data]] · [[End-to-End Lineage]] · source: Platform reconstruction §2.3*
#clone/drop #kind/concept #layer/platform

## Apollo Plan

> A unit of deployment work (install / config / upgrade / uninstall / secret) issued to an agent only once all constraints pass.

Apollo surfaces Plans for transparency rather than acting silently like a control loop. Roll-off and break-glass Plans are prioritized. The atom of change in [[Apollo & the Delivery Engine#Apollo|Apollo]].

**Invariants:** [[End-to-End Lineage]]

**Related:** [[Apollo & the Delivery Engine#Orchestration Engine|Orchestration Engine]] · [[Apollo & the Delivery Engine#Apollo Constraint|Apollo Constraint]] · [[Apollo & the Delivery Engine#Spoke Control Plane|Spoke Control Plane]]

*clone: drop · kind: concept · layer: platform · invariants: [[End-to-End Lineage]] · source: Platform reconstruction §2.3*
#clone/drop #kind/concept #layer/platform

## Orchestration Engine

> Hub services that continuously evaluate all possible Plans against constraints and issue the satisfied ones.

Also drives [[Releases, Channels & Promotion#Promotion Pipeline|release promotion]] using reported health. The embodiment of 'no target state' — it proposes the latest [[Releases, Channels & Promotion#Release & Version|release]] allowed by [[Apollo & the Delivery Engine#Apollo Constraint|constraints]], not a declared desired state.

**Invariants:** [[End-to-End Lineage]]

**Related:** [[Apollo & the Delivery Engine#Apollo|Apollo]] · [[Apollo & the Delivery Engine#Apollo Plan|Apollo Plan]] · [[Apollo & the Delivery Engine#Apollo Constraint|Apollo Constraint]] · [[Releases, Channels & Promotion#Promotion Pipeline|Promotion Pipeline]]

*clone: drop · kind: service · layer: platform · invariants: [[End-to-End Lineage]] · source: Platform reconstruction §2.2*
#clone/drop #kind/service #layer/platform

## Hub-and-Spoke

> Apollo's topology: a Hub holds the brain (catalog, settings, Orchestration Engine); Spokes are K8s clusters running a thin control plane.

All Agent→Hub traffic is encrypted, unidirectional, and outbound, authenticated by a per-Environment key signed at registration. This is what makes air-gapped/disconnected operation possible.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Apollo & the Delivery Engine#Apollo|Apollo]] · [[Apollo & the Delivery Engine#Spoke Control Plane|Spoke Control Plane]] · [[Apollo & the Delivery Engine#Orchestration Engine|Orchestration Engine]]

**For our clone:** Drop — over-engineering unless shipping to many disconnected environments.

*clone: drop · kind: mechanism · layer: platform · invariants: [[Security Travels With Data]] · source: Platform reconstruction §2.1*
#clone/drop #kind/mechanism #layer/platform

## Spoke Control Plane

> The thin set of Spoke-side services that execute Plans and report state: helm-chart-operator, apollo-auth-broker, expected-state-k8s, + the Agent.

`helm-chart-operator` runs lifecycle actions and manages the others; `apollo-auth-broker` brokers auth to registries; `expected-state-k8s` reports state/health to the Hub. The Spoke's whole footprint.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Apollo & the Delivery Engine#Hub-and-Spoke|Hub-and-Spoke]] · [[Apollo & the Delivery Engine#Apollo Plan|Apollo Plan]] · [[Infrastructure Substrate#Rubix|Rubix]]

*clone: drop · kind: service · layer: platform · invariants: [[Security Travels With Data]] · source: Platform reconstruction §2.4 (verified)*
#clone/drop #kind/service #layer/platform
