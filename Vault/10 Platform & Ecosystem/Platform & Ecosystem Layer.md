---
tags:
  - hub
  - layer/platform
---

# Platform & Ecosystem Layer

> How the engine is deployed, upgraded, packaged, and distributed: Apollo (continuous delivery), Marketplace, Rubix (the Kubernetes substrate), and the Gotham→Foundry lineage. Mostly droppable for an internal clone.

## Documents in this layer

The 22 concepts are consolidated into five subdomain documents. Each link jumps straight to the concept's section.

### [[Apollo & the Delivery Engine]]

The continuous-delivery control plane — constraint-based, pull-model, with no target state — plus its hub-and-spoke topology and the plans it issues to keep thousands of services compatible.

[[Apollo & the Delivery Engine#Apollo|Apollo]] · [[Apollo & the Delivery Engine#Apollo Constraint|Apollo Constraint]] · [[Apollo & the Delivery Engine#Apollo Plan|Apollo Plan]] · [[Apollo & the Delivery Engine#Orchestration Engine|Orchestration Engine]] · [[Apollo & the Delivery Engine#Hub-and-Spoke|Hub-and-Spoke]] · [[Apollo & the Delivery Engine#Spoke Control Plane|Spoke Control Plane]]

### [[Releases, Channels & Promotion]]

What Apollo deploys and how it flows — versioned products and releases, the channels environments subscribe to, and the health-gated promotion, rollback, and zero-downtime mechanics that move them safely.

[[Releases, Channels & Promotion#Apollo Product|Apollo Product]] · [[Releases, Channels & Promotion#Release & Version|Release & Version]] · [[Releases, Channels & Promotion#Release Channel|Release Channel]] · [[Releases, Channels & Promotion#Entity & Environment|Entity & Environment]] · [[Releases, Channels & Promotion#Promotion Pipeline|Promotion Pipeline]] · [[Releases, Channels & Promotion#Recall & Roll-off|Recall & Roll-off]] · [[Releases, Channels & Promotion#Zero-Downtime Upgrade|Zero-Downtime Upgrade]]

### [[Marketplace & Packaging]]

The packaging and distribution layer above Apollo — portable bundles of Foundry resources, their upstream→downstream links, the storefront that installs them, and the DevOps app that promotes resources between environments.

[[Marketplace & Packaging#Marketplace|Marketplace]] · [[Marketplace & Packaging#Marketplace Product|Marketplace Product]] · [[Marketplace & Packaging#Linked Products|Linked Products]] · [[Marketplace & Packaging#Foundry DevOps|Foundry DevOps]]

### [[Infrastructure Substrate]]

The physical floor under the stack — the hardened, autoscaling Kubernetes substrate and the 300+ microservice, zero-trust mesh that Foundry and AIP actually run as.

[[Infrastructure Substrate#Rubix|Rubix]] · [[Infrastructure Substrate#Compute Mesh|Compute Mesh]]

### [[Ecosystem & Lineage]]

The bigger picture — the AIP + Foundry + Apollo "enterprise operating system" framing, the Gotham lineage that birthed the dynamic ontology, and the enrollment tenancy boundary a deployment lives in.

[[Ecosystem & Lineage#Enterprise Operating System|Enterprise Operating System]] · [[Ecosystem & Lineage#Gotham|Gotham]] · [[Ecosystem & Lineage#Enrollment|Enrollment]]

---

**Invariants this layer serves:** [[Semantic Model Over Data]] · [[Versioned Data Foundation]] · [[Governed Writeback]] · [[Security Travels With Data]] · [[End-to-End Lineage]]

[[Foundry — Home (MOC)|← Home]]
