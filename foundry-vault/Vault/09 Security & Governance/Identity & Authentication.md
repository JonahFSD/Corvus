---
aliases:
  - Multipass
  - Identity Provider (SSO)
  - SSO
  - Authentication & Session
  - Scoped Session
  - Service User & Tokens
  - User Attribute
  - Group
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

# Identity & Authentication

> Who you are and how the platform proves it — the identity backbone, federated login, sessions, machine credentials, and the user/group attributes that policies read.

## Multipass

> Foundry's internal identity backbone: users, groups, key-value attributes, and tokens.

External [[Identity & Authentication#Identity Provider (SSO)|IdPs]] feed it; the `multipass:` attribute prefix is reserved internally; Org RIDs are `ri.multipass..organization`. Every [[Roles & Authorization#Authorization Decision|Authorization Decision]] starts from a Multipass identity.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Identity & Authentication#Identity Provider (SSO)|Identity Provider (SSO)]] · [[Identity & Authentication#User Attribute|User Attribute]] · [[Identity & Authentication#Group|Group]] · [[Identity & Authentication#Authentication & Session|Authentication & Session]] · [[Mandatory Controls & Classification#Organization|Organization]]

**For our clone:** Becomes our user/identity store — far simpler (a users/groups/attrs schema).

*clone: keep · kind: service · layer: security · invariants: [[Security Travels With Data]] · source: Security reconstruction §2*
#clone/keep #kind/service #layer/security

## Identity Provider (SSO)

> An external authentication source (SAML 2.0 / OIDC) that validates users and supplies attributes and groups.

Foundry is the Service Provider; email-domain rules route logins; [[Identity & Authentication#User Attribute|attributes]] and provider [[Identity & Authentication#Group|groups]] are mapped in on login. The federation seam — Foundry rarely owns credentials itself.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Identity & Authentication#Multipass|Multipass]] · [[Identity & Authentication#Authentication & Session|Authentication & Session]] · [[Identity & Authentication#User Attribute|User Attribute]] · [[Identity & Authentication#Group|Group]]

**For our clone:** Defer SSO; start with local auth, design for an IdP later.

*clone: defer · kind: mechanism · layer: security · invariants: [[Security Travels With Data]] · source: Security reconstruction §2*
#clone/defer #kind/mechanism #layer/security

## Authentication & Session

> MFA-backed login producing a short-lived session token (PALANTIR_TOKEN, ~16h default).

MFA is mandatory; sessions are intentionally short to force re-auth; idle accounts deactivate after 30 days. The gate-zero of every [[Roles & Authorization#Authorization Decision|Authorization Decision]].

**Invariants:** [[Security Travels With Data]]

**Related:** [[Identity & Authentication#Multipass|Multipass]] · [[Identity & Authentication#Identity Provider (SSO)|Identity Provider (SSO)]] · [[Identity & Authentication#Service User & Tokens|Service User & Tokens]] · [[Roles & Authorization#Authorization Decision|Authorization Decision]]

*clone: simplify · kind: mechanism · layer: security · invariants: [[Security Travels With Data]] · source: Security reconstruction §2*
#clone/simplify #kind/mechanism #layer/security

## Scoped Session

> A session deliberately limited to a chosen subset of a user's Markings.

Lets a user operate at reduced privilege for a task; 'authorized group IDs' from the scope feed [[Data-Level Security Policies#Granular Policy|policies]]. A least-privilege refinement of [[Identity & Authentication#Authentication & Session|Authentication & Session]].

**Invariants:** [[Security Travels With Data]]

**Related:** [[Identity & Authentication#Authentication & Session|Authentication & Session]] · [[Mandatory Controls & Classification#Marking|Marking]] · [[Data-Level Security Policies#Granular Policy|Granular Policy]]

**For our clone:** Defer.

*clone: defer · kind: mechanism · layer: security · invariants: [[Security Travels With Data]] · source: Security reconstruction §2/§5*
#clone/defer #kind/mechanism #layer/security

## Service User & Tokens

> Non-human identities and API credentials: personal access tokens (PATs) and OAuth2 (auth-code / client-credentials).

A PAT carries the creating user's permissions; client-credentials creates a service user with NO access by default. Effective access = intersection of identity permissions ∩ app scope ∩ requested scope. The programmatic on-ramp.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Identity & Authentication#Authentication & Session|Authentication & Session]] · [[Identity & Authentication#Multipass|Multipass]] · [[Roles & Authorization#Role|Role]]

**For our clone:** Keep — API keys/service accounts scoped by role.

*clone: keep · kind: mechanism · layer: security · invariants: [[Security Travels With Data]] · source: Security reconstruction §2*
#clone/keep #kind/mechanism #layer/security

## User Attribute

> A key-value, multi-valued property on a user (or group) used by policies and services.

Populated by the [[Identity & Authentication#Identity Provider (SSO)|IdP]] or admins; the `multipass:` namespace is reserved. The raw material [[Data-Level Security Policies#Granular Policy|granular policies]] compare against. Attribute-based access control (ABAC) lives here.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Identity & Authentication#Multipass|Multipass]] · [[Identity & Authentication#Group|Group]] · [[Data-Level Security Policies#Granular Policy|Granular Policy]]

*clone: simplify · kind: concept · layer: security · invariants: [[Security Travels With Data]] · source: Security reconstruction §2*
#clone/simplify #kind/concept #layer/security

## Group

> A named collection of users (direct + inherited members; provider groups mirror the IdP).

The usual grant target — assign [[Roles & Authorization#Role|roles]] and [[Mandatory Controls & Classification#Marking|markings]] to groups, not individuals. Membership (direct and inherited) drives policy evaluation.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Identity & Authentication#Multipass|Multipass]] · [[Roles & Authorization#Role|Role]] · [[Identity & Authentication#User Attribute|User Attribute]] · [[Roles & Authorization#Project|Project]]

*clone: simplify · kind: concept · layer: security · invariants: [[Security Travels With Data]] · source: Security reconstruction §2*
#clone/simplify #kind/concept #layer/security
