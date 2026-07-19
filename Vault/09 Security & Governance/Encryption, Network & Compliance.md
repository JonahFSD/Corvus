---
aliases:
  - Encryption at Rest & in Transit
  - Cipher
  - Egress Policy
  - Compliance Accreditation
tags:
  - layer/security
  - kind/doc
  - clone/keep
layer: security
kind: doc
clone: keep
source: "09 Security & Governance (consolidated)"
updated: 2026-06-14
---

# Encryption, Network & Compliance

> Confidentiality and containment beneath the access model — encryption at rest and in transit, field-level ciphers, outbound egress control, and the certifications that drive it all.

## Encryption at Rest & in Transit

> TLS 1.2+ in transit; application-level encryption at rest; AES-256-GCM for modern connector credentials.

Legacy agents use AES-128-GCM with keys on the host. The baseline confidentiality guarantee underneath every layer; [[Encryption, Network & Compliance#Cipher|Cipher]] adds field-level encryption on top.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Encryption, Network & Compliance#Cipher|Cipher]] · [[Encryption, Network & Compliance#Egress Policy|Egress Policy]] · [[Data Connection (Magritte)|Foundry Worker]]

**For our clone:** Keep the baseline (TLS + at-rest); use the platform/DB defaults.

*clone: keep · kind: property · layer: security · invariants: [[Security Travels With Data]] · source: Security reconstruction §8*
#clone/keep #kind/property #layer/security

## Cipher

> In-platform field-level encryption: Channels define algorithms/keys; Licenses govern who can encrypt/decrypt.

Value- or column-level encryption/hashing (AES-GCM-SIV, AES-SIV, salted SHA), rate-limited and cell-level auditable. For data so sensitive that even authorized viewers shouldn't see plaintext.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Encryption, Network & Compliance#Encryption at Rest & in Transit|Encryption at Rest & in Transit]] · [[Data-Level Security Policies#Property Security Policy|Property Security Policy]]

**For our clone:** Defer — niche field-level encryption.

*clone: defer · kind: service · layer: security · invariants: [[Security Travels With Data]] · source: Security reconstruction §8*
#clone/defer #kind/service #layer/security

## Egress Policy

> Controls on outbound network access from Foundry (direct-connection vs agent-proxy), enforced by Cilium/eBPF.

Set by the Information Security Officer by domain/IP/CIDR; destinations immutable once created. Compute defaults to zero-trust (no external network until a source is attached). How the platform contains data exfiltration.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Data Connection (Magritte)|Foundry Worker]] · [[Data Connection (Magritte)|Agent-Proxy vs Agent Worker]] · [[Data Connection (Magritte)|Data Connection]]

**For our clone:** Defer — relevant only once we have external integrations.

*clone: defer · kind: mechanism · layer: security · invariants: [[Security Travels With Data]] · source: Security reconstruction §8*
#clone/defer #kind/mechanism #layer/security

## Compliance Accreditation

> The government/enterprise certifications the platform holds: FedRAMP High, DoD IL5/IL6, CMMC Level 2, SOC 2, ISO 27001.

FedRAMP High (Dec 2024) covers Foundry/AIP/Apollo/Gotham; CMMC L2 (Sep 2025) via C3PAO. Deployed/audited through [[Platform & Ecosystem Layer|Apollo]]. Context for *why* the security model is so elaborate — almost all of it is droppable for an internal tool.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Platform & Ecosystem Layer]] · [[Audit & Lineage#Audit Schema|Audit Schema]]

**For our clone:** Drop — irrelevant unless we ever pursue accreditation.

*clone: drop · kind: reference · layer: security · invariants: [[Security Travels With Data]] · source: Security reconstruction §9 (verified dates)*
#clone/drop #kind/reference #layer/security
