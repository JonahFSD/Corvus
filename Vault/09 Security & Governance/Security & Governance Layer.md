---
tags:
  - hub
  - layer/security
---

# Security & Governance Layer

> Cross-cutting access control, audit, and lineage that thread through every other layer.

## Documents in this layer

The 28 concepts are consolidated into six subdomain documents. Each link jumps straight to the concept's section.

### [[Identity & Authentication]]

Who you are and how the platform proves it — the identity backbone, federated login, sessions, machine credentials, and policy-readable attributes.

[[Identity & Authentication#Multipass|Multipass]] · [[Identity & Authentication#Identity Provider (SSO)|Identity Provider (SSO)]] · [[Identity & Authentication#Authentication & Session|Authentication & Session]] · [[Identity & Authentication#Scoped Session|Scoped Session]] · [[Identity & Authentication#Service User & Tokens|Service User & Tokens]] · [[Identity & Authentication#User Attribute|User Attribute]] · [[Identity & Authentication#Group|Group]]

### [[Roles & Authorization]]

How an access request is decided — the default-deny composition rule, operations and roles, and the project/space hierarchy roles inherit through.

[[Roles & Authorization#Authorization Decision|Authorization Decision]] · [[Roles & Authorization#Operation|Operation]] · [[Roles & Authorization#Role|Role]] · [[Roles & Authorization#Role Set|Role Set]] · [[Roles & Authorization#Project|Project]] · [[Roles & Authorization#Space|Space]]

### [[Mandatory Controls & Classification]]

The all-or-nothing controls that override roles — markings, organizational tenancy, and the classification/purpose models on top.

[[Mandatory Controls & Classification#Mandatory Control|Mandatory Control]] · [[Mandatory Controls & Classification#Marking|Marking]] · [[Mandatory Controls & Classification#Organization|Organization]] · [[Mandatory Controls & Classification#Classification-Based Access Control (CBAC)|Classification-Based Access Control (CBAC)]] · [[Mandatory Controls & Classification#Purpose-Based Access Control|Purpose-Based Access Control]]

### [[Data-Level Security Policies]]

Row- and cell-level visibility computed at request time — the granular-policy engine and object/property security policies.

[[Data-Level Security Policies#Granular Policy|Granular Policy]] · [[Data-Level Security Policies#Restricted View|Restricted View]] · [[Data-Level Security Policies#Object Security Policy|Object Security Policy]] · [[Data-Level Security Policies#Property Security Policy|Property Security Policy]]

### [[Audit & Lineage]]

The append-only record of who did what, when, and where — the backbone of end-to-end lineage.

[[Audit & Lineage#Audit Log|Audit Log]] · [[Audit & Lineage#Audit Schema|Audit Schema]]

### [[Encryption, Network & Compliance]]

Confidentiality and containment beneath the access model — encryption, field-level ciphers, egress control, and certifications.

[[Encryption, Network & Compliance#Encryption at Rest & in Transit|Encryption at Rest & in Transit]] · [[Encryption, Network & Compliance#Cipher|Cipher]] · [[Encryption, Network & Compliance#Egress Policy|Egress Policy]] · [[Encryption, Network & Compliance#Compliance Accreditation|Compliance Accreditation]]

---

**Invariants this layer serves:** [[Semantic Model Over Data]] · [[Versioned Data Foundation]] · [[Governed Writeback]] · [[Security Travels With Data]] · [[End-to-End Lineage]]

[[Foundry — Home (MOC)|← Home]]
