---
aliases:
  - Enterprise Operating System
  - Gotham
  - Enrollment
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

# Ecosystem & Lineage

> The bigger picture — the AIP + Foundry + Apollo 'enterprise operating system' framing, the Gotham lineage that birthed the dynamic ontology, and the enrollment tenancy boundary a deployment lives in.

## Enterprise Operating System

> Palantir's framing of AIP + Foundry + Apollo as one integrated operating system for an organization.

Data ([[Data Integration & Pipeline Layer|Foundry]]) + meaning ([[Ontology & Metadata#Ontology|Ontology]]) + AI ([[AIP Layer]]) + delivery ([[Apollo & the Delivery Engine#Apollo|Apollo]]) as a single stack. The whole that all eight reconstructed layers compose into.

**Invariants:** [[End-to-End Lineage]]

**Related:** [[Apollo & the Delivery Engine#Apollo|Apollo]] · [[Infrastructure Substrate#Compute Mesh|Compute Mesh]] · [[Ecosystem & Lineage#Gotham|Gotham]] · [[The Closed Loop]]

*clone: drop · kind: concept · layer: platform · invariants: [[End-to-End Lineage]] · source: Platform reconstruction §9.1*
#clone/drop #kind/concept #layer/platform

## Gotham

> Palantir's original (2008) defense/intelligence platform — the birthplace of the 'dynamic ontology'.

Pioneered mapping heterogeneous data into objects/properties/links for analysts; Foundry generalized that into the commercial [[Ontology & Metadata#Ontology|Ontology]]. Today Gotham integrates atop the Foundry-managed Ontology via type mapping (querying through the [[Object Storage#Object Set Service (OSS)|Object Set Service (OSS)]]).

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[Ontology & Metadata#Ontology|Ontology]] · [[Object Storage#Object Set Service (OSS)|Object Set Service (OSS)]] · [[Ecosystem & Lineage#Enterprise Operating System|Enterprise Operating System]]

*clone: drop · kind: concept · layer: platform · invariants: [[Semantic Model Over Data]] · source: Platform reconstruction §9.2*
#clone/drop #kind/concept #layer/platform

## Enrollment

> An Organization's primary Foundry identity — the tenancy/account boundary for a deployment.

Scopes resource limits, cloud identities, network policy, and which [[Marketplace & Packaging#Marketplace Product|products]] are enabled. The top of the practical hierarchy above [[Roles & Authorization#Space|spaces]] and [[Roles & Authorization#Project|projects]].

**Invariants:** [[Security Travels With Data]]

**Related:** [[Mandatory Controls & Classification#Organization|Organization]] · [[Roles & Authorization#Space|Space]] · [[Roles & Authorization#Project|Project]]

*clone: drop · kind: concept · layer: platform · invariants: [[Security Travels With Data]] · source: Platform reconstruction §8/§10*
#clone/drop #kind/concept #layer/platform
