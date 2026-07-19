---
aliases:
  - Granular Policy
  - Restricted View
  - Object Security Policy
  - Property Security Policy
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

# Data-Level Security Policies

> Row- and cell-level visibility computed at request time — the granular-policy engine and the object/property security policies that make security a property of the data itself.

## Granular Policy

> A rule set comparing user attributes, columns, and values to decide row visibility at request time.

Template-based, converted to queries on access. The engine under [[Data-Level Security Policies#Restricted View|restricted views]] and [[Data-Level Security Policies#Object Security Policy|object security policies]].

**Invariants:** [[Security Travels With Data]]

**Related:** [[Data-Level Security Policies#Restricted View|Restricted View]] · [[Data-Level Security Policies#Object Security Policy|Object Security Policy]]

*clone: simplify · kind: mechanism · layer: security · invariants: [[Security Travels With Data]] · source: Security §6.3*
#clone/simplify #kind/mechanism #layer/security

## Restricted View

> Row-level security: a policy limits a dataset/object to only the rows a user may see.

Powered by [[Data-Level Security Policies#Granular Policy|granular policies]]; can back object types for row-level object security. The mechanism behind 'security travels with the row'.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Data-Level Security Policies#Granular Policy|Granular Policy]] · [[Data-Level Security Policies#Object Security Policy|Object Security Policy]] · [[Mandatory Controls & Classification#Marking|Marking]]

*clone: simplify · kind: mechanism · layer: security · invariants: [[Security Travels With Data]] · source: Security / Data §7.2*
#clone/simplify #kind/mechanism #layer/security

## Object Security Policy

> Row-level visibility configured directly on an object type, independent of backing-dataset permissions.

Compares user attributes/properties to gate which object instances a user sees. With a [[Data-Level Security Policies#Property Security Policy|Property Security Policy]], gives cell-level security.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Data-Level Security Policies#Property Security Policy|Property Security Policy]] · [[Data-Level Security Policies#Granular Policy|Granular Policy]] · [[Properties#Mandatory Control Property|Mandatory Control Property]]

*clone: simplify · kind: mechanism · layer: security · invariants: [[Security Travels With Data]] · source: Kinetic / Security §6.2*
#clone/simplify #kind/mechanism #layer/security

## Property Security Policy

> Column-level security on an object type — hides specific properties (e.g., PII) from some users.

Requires an [[Data-Level Security Policies#Object Security Policy|Object Security Policy]] first; a primary key can't be in a property policy. Together they make security a property of the [[Objects#Object|object]] itself.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Data-Level Security Policies#Object Security Policy|Object Security Policy]] · [[Properties#Mandatory Control Property|Mandatory Control Property]]

*clone: simplify · kind: mechanism · layer: security · invariants: [[Security Travels With Data]] · source: Kinetic / Security §6.2*
#clone/simplify #kind/mechanism #layer/security
