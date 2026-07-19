---
aliases:
  - Authorization Decision
  - Operation
  - Role
  - Role Set
  - Project
  - Space
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

# Roles & Authorization

> How an access request is decided — the default-deny composition rule, operations and the roles that bundle them, and the project/space resource hierarchy that roles inherit through.

## Authorization Decision

> The composition rule: access is granted only if ALL mandatory controls pass AND a role grants the operation AND any granular policy passes — default-deny.

Four gates in order: valid session → [[Mandatory Controls & Classification#Mandatory Control|mandatory controls]] (all-or-nothing, override roles) → a [[Roles & Authorization#Role|Role]] granting the [[Roles & Authorization#Operation|Operation]] → a [[Data-Level Security Policies#Granular Policy|Granular Policy]]/[[Data-Level Security Policies#Object Security Policy|Object Security Policy]] at row/cell level. Miss any gate and access is denied. The single most important rule to replicate.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Mandatory Controls & Classification#Mandatory Control|Mandatory Control]] · [[Roles & Authorization#Role|Role]] · [[Roles & Authorization#Operation|Operation]] · [[Data-Level Security Policies#Granular Policy|Granular Policy]] · [[Mandatory Controls & Classification#Marking|Marking]]

**For our clone:** Replicate exactly: default-deny; mandatory controls beat roles.

*clone: keep · kind: pattern · layer: security · invariants: [[Security Travels With Data]] · source: Security reconstruction §3 (composition; [Inferred] order)*
#clone/keep #kind/pattern #layer/security

## Operation

> An atomic, namespaced permission an app checks before allowing an action (e.g. compass:read-resource).

Namespaces map to subsystems (`compass:`, `stemma:`, `s3-proxy:`, `marketplace:`, `audit-export:`). [[Roles & Authorization#Role|Roles]] are just sets of operations; the [[Roles & Authorization#Authorization Decision|Authorization Decision]] checks for the specific operation.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Roles & Authorization#Role|Role]] · [[Roles & Authorization#Role Set|Role Set]] · [[Roles & Authorization#Authorization Decision|Authorization Decision]]

*clone: simplify · kind: concept · layer: security · invariants: [[Security Travels With Data]] · source: Security reconstruction §3*
#clone/simplify #kind/concept #layer/security

## Role

> A named set of operations (Owner, Editor, Viewer, Discoverer, …) granted on a resource.

Each role can grant equal-or-lesser roles; roles inherit to child resources. The backbone of who-can-do-what.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Roles & Authorization#Project|Project]] · [[Audit & Lineage#Audit Log|Audit Log]]

**For our clone:** Keep — role-based access is the v1 baseline (D15).

*clone: keep · kind: concept · layer: security · invariants: [[Security Travels With Data]] · source: Data §7.3*
#clone/keep #kind/concept #layer/security

## Role Set

> A context-scoped group of roles (Project, Ontology, or Marketplace Installation contexts).

Customizing default [[Roles & Authorization#Role|roles]] means copying a role set; roles can 'Include' others to inherit [[Roles & Authorization#Operation|operations]]. How role definitions are versioned and namespaced.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Roles & Authorization#Role|Role]] · [[Roles & Authorization#Operation|Operation]]

**For our clone:** Defer — start with fixed roles; add custom role sets later.

*clone: defer · kind: concept · layer: security · invariants: [[Security Travels With Data]] · source: Security reconstruction §3*
#clone/defer #kind/concept #layer/security

## Project

> The primary security boundary: a container of resources with roles that inherit to children.

Access is granted at the project level and flows down. Datasets, object types, sources, and apps live in projects; dev→prod separation is organized here.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Roles & Authorization#Role|Role]] · [[Mandatory Controls & Classification#Marking|Marking]] · [[Dataset & Transactions|Dataset Branch]]

**For our clone:** Simplify to a basic workspace/role scheme.

*clone: simplify · kind: concept · layer: security · invariants: [[Security Travels With Data]] · source: Data §7.3*
#clone/simplify #kind/concept #layer/security

## Space

> A high-level container of Projects sharing one Ontology, restricted by an Organization or set of Organizations.

The first path element (`space/project/...`); a multi-org space enables cross-org collaboration. Sits above the [[Roles & Authorization#Project|Project]] in the resource hierarchy.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Roles & Authorization#Project|Project]] · [[Mandatory Controls & Classification#Organization|Organization]] · [[Ontology & Metadata#Ontology|Ontology]]

**For our clone:** Simplify — a single workspace at v1.

*clone: simplify · kind: concept · layer: security · invariants: [[Security Travels With Data]] · source: Security reconstruction §6*
#clone/simplify #kind/concept #layer/security
