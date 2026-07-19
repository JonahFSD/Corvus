---
aliases:
  - Rubix
  - Compute Mesh
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

# Infrastructure Substrate

> The physical floor under the stack — Palantir's hardened, autoscaling Kubernetes substrate and the 300+ microservice, zero-trust mesh that Foundry and AIP actually run as.

## Rubix

> Palantir's hardened, autoscaling Kubernetes substrate running the whole stack, with nodes that live ≤48 hours.

Aggressive node cycling guards against persistent threats; Cilium/eBPF egress, Envoy proxy, zero-trust isolation, FedRAMP/IL accreditation. The infrastructure floor under [[Apollo & the Delivery Engine#Apollo|Apollo]], Foundry, and AIP.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Infrastructure Substrate#Compute Mesh|Compute Mesh]] · [[Apollo & the Delivery Engine#Apollo|Apollo]] · [[Releases, Channels & Promotion#Zero-Downtime Upgrade|Zero-Downtime Upgrade]] · [[Encryption, Network & Compliance#Egress Policy|Egress Policy]]

**For our clone:** Drop — use ordinary managed infrastructure (a container host or a single VM).

*clone: drop · kind: service · layer: platform · invariants: [[Security Travels With Data]] · source: Platform reconstruction §7.1 (verified 48h)*
#clone/drop #kind/service #layer/platform

## Compute Mesh

> The 300+ microservice, zero-trust, autoscaling fabric that is Foundry + AIP, all powered by Apollo.

Maps into nine capability sets over six mesh-wide components (storage/compute/networking/security/governance/workspace). The 'Enterprise Operating System' in physical form. Its scale is exactly what we DON'T replicate.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Infrastructure Substrate#Rubix|Rubix]] · [[Ecosystem & Lineage#Enterprise Operating System|Enterprise Operating System]] · [[Apollo & the Delivery Engine#Apollo|Apollo]]

**For our clone:** Drop — our clone is a handful of services, not 300.

*clone: drop · kind: concept · layer: platform · invariants: [[Security Travels With Data]] · source: Platform reconstruction §7.2*
#clone/drop #kind/concept #layer/platform
