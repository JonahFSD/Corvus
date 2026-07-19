---
tags:
  - layer/app
aliases:
  - Workshop
  - Workshop Module
  - Module Interface
  - Embedded Module
  - Object View
  - App vs Data Permissions
updated: 2026-06-13
---

# Workshop, Modules & Views

> The structural core of operational apps: Workshop's module unit (header → pages → sections → widgets), the variable-mapping interface that is a module's API, module embedding and reuse, the per-object detail view (itself now a module), and how app access decouples from data access.

## Workshop

> Foundry's modern no-code builder for operational apps, bound tightly to the Ontology.

Apps are [[Workshop, Modules & Views#Workshop Module|modules]] of [[Widgets, Binding & Writeback#Widget|widgets]] driven by a reactive [[Reactive State Model#Workshop Variable|variable]] graph; writeback happens through [[Widgets, Binding & Writeback#Action Form|action forms]]. The recommended path over [[Slate (Legacy Builder)#Slate|Slate]].

**Invariants:** [[Semantic Model Over Data]] · [[Governed Writeback]]

**Related:** [[Workshop, Modules & Views#Workshop Module|Workshop Module]] · [[Widgets, Binding & Writeback#Widget|Widget]] · [[Reactive State Model#Workshop Variable|Workshop Variable]] · [[Widgets, Binding & Writeback#Action Form|Action Form]] · [[Slate (Legacy Builder)#Slate|Slate]] · [[Operational Application]]

**For our clone:** Keep the model; an ordinary reactive front-end framework covers it at our scale.

*clone: keep · kind: service · layer: app · source: App-Building reconstruction §2*
#clone/keep #kind/service #layer/app

## Workshop Module

> The unit Workshop app: header → pages → sections → widgets, identified by an RID.

Only the header persists across pages. Exposes a [[Workshop, Modules & Views#Module Interface|Module Interface]] (its 'API') and can be reused via [[Workshop, Modules & Views#Embedded Module|embedding]]. Inherits its parent project's permissions.

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[Workshop, Modules & Views#Workshop|Workshop]] · [[Widgets, Binding & Writeback#Widget|Widget]] · [[Workshop, Modules & Views#Module Interface|Module Interface]] · [[Workshop, Modules & Views#Embedded Module|Embedded Module]] · [[Workshop, Modules & Views#App vs Data Permissions|App vs Data Permissions]]

*clone: simplify · kind: concept · layer: app · source: App-Building reconstruction §2*
#clone/simplify #kind/concept #layer/app

## Module Interface

> The set of a module's externally-mappable variables — effectively the module's API.

Lets a parent map variables into an [[Workshop, Modules & Views#Embedded Module|embedded child]] and lets the URL initialize state (`?externalId=value`) for deep-linking. Another expression of [[Define-Once Reuse]].

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[Workshop, Modules & Views#Workshop Module|Workshop Module]] · [[Workshop, Modules & Views#Embedded Module|Embedded Module]] · [[Workshop, Modules & Views#Object View|Object View]]

*clone: simplify · kind: concept · layer: app · source: App-Building reconstruction §2*
#clone/simplify #kind/concept #layer/app

## Embedded Module

> Reusing one module inside another (via a loop layout or embed widget), each with its own variable scope.

Parent↔child communication is via the [[Workshop, Modules & Views#Module Interface|Module Interface]]. Module-level config (routing, auto-refresh) is not inherited; children are separately permissioned. The composition unit for maintainable apps.

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[Workshop, Modules & Views#Workshop Module|Workshop Module]] · [[Workshop, Modules & Views#Module Interface|Module Interface]]

*clone: simplify · kind: mechanism · layer: app · source: App-Building reconstruction §2*
#clone/simplify #kind/mechanism #layer/app

## Object View

> The per-object detail surface — now itself a Workshop module (full), with legacy YAML views still supported.

Auto-created standard views show prominent properties + links; configured views use the full widget set in tabs. Permissions sync with the object type. Maps app variables onto the view via the [[Workshop, Modules & Views#Module Interface|Module Interface]].

**Invariants:** [[Semantic Model Over Data]] · [[Security Travels With Data]]

**Related:** [[Workshop, Modules & Views#Workshop Module|Workshop Module]] · [[Workshop, Modules & Views#Module Interface|Module Interface]] · [[Objects#Object Type|Object Type]] · [[Workshop, Modules & Views#App vs Data Permissions|App vs Data Permissions]]

*clone: simplify · kind: concept · layer: app · source: App-Building reconstruction §7*
#clone/simplify #kind/concept #layer/app

## App vs Data Permissions

> Module access is decoupled from access to the data, actions, and functions the module uses.

A user can open an app but be blocked from its objects/actions (widgets show permission errors). Security lives on the data, not the app — a direct consequence of [[Security Travels With Data]].

**Invariants:** [[Security Travels With Data]]

**Related:** [[Workshop, Modules & Views#Workshop Module|Workshop Module]] · [[Roles & Authorization#Role|Role]] · [[Workshop, Modules & Views#Object View|Object View]] · [[Actions#Edits-Only-via-Actions|Edits-Only-via-Actions]]

**For our clone:** Keep — enforce on the data/action, never trust the app surface.

*clone: keep · kind: pattern · layer: app · source: App-Building reconstruction §9*
#clone/keep #kind/pattern #layer/app
