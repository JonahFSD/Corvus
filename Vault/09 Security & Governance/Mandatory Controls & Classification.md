---
aliases:
  - Mandatory Control
  - Marking
  - Organization
  - Classification-Based Access Control (CBAC)
  - CBAC
  - Purpose-Based Access Control
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

# Mandatory Controls & Classification

> The all-or-nothing controls that override roles — markings a user must fully hold, organizational tenancy, and the classification and purpose models layered on top.

## Mandatory Control

> The all-or-nothing access requirements that override roles: Markings, Organizations, and CBAC classifications.

A user must hold ALL applied [[Mandatory Controls & Classification#Marking|markings]], belong to ≥1 applied [[Mandatory Controls & Classification#Organization|Organization]], and (if CBAC) be classified ≥ the resource's max. They propagate down hierarchy and lineage and cannot be overridden by a [[Roles & Authorization#Role|Role]]. The teeth of [[Security Travels With Data]].

**Invariants:** [[Security Travels With Data]]

**Related:** [[Mandatory Controls & Classification#Marking|Marking]] · [[Mandatory Controls & Classification#Organization|Organization]] · [[Mandatory Controls & Classification#Classification-Based Access Control (CBAC)|Classification-Based Access Control (CBAC)]] · [[Roles & Authorization#Authorization Decision|Authorization Decision]] · [[Properties#Mandatory Control Property|Mandatory Control Property]]

**For our clone:** Replicate Markings + a simple tenant/Org; drop CBAC at v1.

*clone: keep · kind: concept · layer: security · invariants: [[Security Travels With Data]] · source: Security reconstruction §4*
#clone/keep #kind/concept #layer/security

## Marking

> A mandatory, all-or-nothing access control tag; a user must hold all of a resource's markings.

Propagates downstream through [[Transforms & Build|transforms]] automatically, so derived data inherits restrictions. The blunt, powerful instrument of [[Security Travels With Data]].

**Invariants:** [[Security Travels With Data]]

**Related:** [[Data-Level Security Policies#Restricted View|Restricted View]] · [[Properties#Mandatory Control Property|Mandatory Control Property]] · [[Mandatory Controls & Classification#Classification-Based Access Control (CBAC)|Classification-Based Access Control (CBAC)]] · [[Roles & Authorization#Project|Project]]

**For our clone:** Simplify — roles + optional row rules at v1 (D15).

*clone: simplify · kind: concept · layer: security · invariants: [[Security Travels With Data]] · source: Security / Semantic §4.5*
#clone/simplify #kind/concept #layer/security

## Organization

> A top-level tenancy/marking grouping that scopes who can see a space's resources.

An object/space can be private to one organization or shared across several. Coarse, mandatory partitioning above markings.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Mandatory Controls & Classification#Marking|Marking]] · [[Roles & Authorization#Project|Project]]

**For our clone:** Drop or reduce to a single tenant at v1.

*clone: drop · kind: concept · layer: security · invariants: [[Security Travels With Data]] · source: Semantic §7.4 / Security*
#clone/drop #kind/concept #layer/security

## Classification-Based Access Control (CBAC)

> Access granted by data classification level (and max-classification constraints on objects).

A government/enterprise-grade control layered on [[Mandatory Controls & Classification#Marking|markings]] and [[Mandatory Controls & Classification#Organization|organizations]]. Likely overkill for our v1.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Mandatory Controls & Classification#Marking|Marking]] · [[Mandatory Controls & Classification#Purpose-Based Access Control|Purpose-Based Access Control]] · [[Mandatory Controls & Classification#Organization|Organization]]

**For our clone:** Drop at v1.

*clone: drop · kind: concept · layer: security · invariants: [[Security Travels With Data]] · source: Security*
#clone/drop #kind/concept #layer/security

## Purpose-Based Access Control

> Access granted based on the declared *purpose* for which a user is accessing data.

Ties usage to an approved purpose, not just identity — strong governance, but heavy. Part of Palantir's compliance posture.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Mandatory Controls & Classification#Classification-Based Access Control (CBAC)|Classification-Based Access Control (CBAC)]] · [[Mandatory Controls & Classification#Marking|Marking]]

**For our clone:** Drop at v1.

*clone: drop · kind: concept · layer: security · invariants: [[Security Travels With Data]] · source: Security*
#clone/drop #kind/concept #layer/security
