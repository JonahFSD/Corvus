---
aliases:
  - Marketplace
  - Marketplace Product
  - Linked Products
  - Foundry DevOps
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

# Marketplace & Packaging

> The packaging and distribution layer above Apollo — portable bundles of Foundry resources, their upstream→downstream links, the storefront that installs them, and the DevOps app that promotes resources between environments.

## Marketplace

> The packaging + storefront layer over Apollo: install/upgrade self-contained Products from Stores.

Products are collections of Foundry resources with bundled dependency metadata, published to Stores (Foundry / local / remote) and installed via [[Apollo & the Delivery Engine#Apollo|Apollo]] orchestration. The distribution UX; Apollo does the execution.

**Invariants:** [[End-to-End Lineage]]

**Related:** [[Marketplace & Packaging#Marketplace Product|Marketplace Product]] · [[Marketplace & Packaging#Linked Products|Linked Products]] · [[Marketplace & Packaging#Foundry DevOps|Foundry DevOps]] · [[Apollo & the Delivery Engine#Apollo|Apollo]]

**For our clone:** Drop — a simple export/import step covers our needs.

*clone: drop · kind: service · layer: platform · invariants: [[End-to-End Lineage]] · source: Platform reconstruction §5*
#clone/drop #kind/service #layer/platform

## Marketplace Product

> A self-contained, portable bundle of Foundry resources with dependency metadata and mappable inputs.

Content (installed resources) + inputs (dependencies to map). Most resource types can be packaged — [[Objects#Object Type|object types]], [[Actions#Action Type|actions]], [[Functions#Function|functions]], [[Workshop, Modules & Views#Workshop Module|modules]], models — but **objects themselves cannot**. Versioned for consistent installs/rollbacks.

**Invariants:** [[End-to-End Lineage]]

**Related:** [[Marketplace & Packaging#Marketplace|Marketplace]] · [[Marketplace & Packaging#Linked Products|Linked Products]] · [[Releases, Channels & Promotion#Apollo Product|Apollo Product]] · [[Objects#Object Type|Object Type]]

*clone: drop · kind: concept · layer: platform · invariants: [[End-to-End Lineage]] · source: Platform reconstruction §5.1*
#clone/drop #kind/concept #layer/platform

## Linked Products

> One-way upstream→downstream connections that auto-map one product's outputs to another's inputs.

DevOps inspects packaged entities to derive links (a pipeline's clean datasets feed an Ontology product's inputs). Modularizes workflows; breaking changes force major-version bumps. Lineage-driven packaging.

**Invariants:** [[End-to-End Lineage]]

**Related:** [[Marketplace & Packaging#Marketplace Product|Marketplace Product]] · [[Marketplace & Packaging#Foundry DevOps|Foundry DevOps]] · [[Data Health & Lineage|Data Lineage Graph]]

*clone: drop · kind: mechanism · layer: platform · invariants: [[End-to-End Lineage]] · source: Platform reconstruction §5.3*
#clone/drop #kind/mechanism #layer/platform

## Foundry DevOps

> The release-management app that packages resources from one environment and promotes them to the next.

Pairs with [[Roles & Authorization#Space|Spaces]] for environment separation (Dev/Test/Prod) and with [[Marketplace & Packaging#Marketplace|Marketplace]] for distribution; complementary to [[Dataset & Transactions|branching]] (in-environment iteration vs cross-environment promotion).

**Invariants:** [[End-to-End Lineage]]

**Related:** [[Marketplace & Packaging#Marketplace|Marketplace]] · [[Roles & Authorization#Space|Space]] · [[Dataset & Transactions|Dataset Branch]] · [[Marketplace & Packaging#Marketplace Product|Marketplace Product]]

**For our clone:** Simplify to a basic dev→prod promotion step.

*clone: simplify · kind: service · layer: platform · invariants: [[End-to-End Lineage]] · source: Platform reconstruction §6*
#clone/simplify #kind/service #layer/platform
