---
tags:
  - layer/app
aliases:
  - Widget
  - Object Set Binding
  - Object Set Filter
  - Action Form
  - Auto-Refresh
  - AIP Agent Widget
updated: 2026-06-13
---

# Widgets, Binding & Writeback

> How apps consume the Ontology and write back to it: the widget catalog, object-set binding and filtering, the action form as the governed writeback surface, module-level live refresh, and the AIP agent widget.

## Widget

> A UI building block that declares a configuration shape: input/output variables, display options, and attached actions.

The catalog spans display (Object Table/List), filtering (Filter List), visualization (charts/Map), input, and AIP widgets. Inputs are [[Objects#Object Set|object sets]]/[[Reactive State Model#Workshop Variable|variables]]; selection flows back as output variables.

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[Reactive State Model#Workshop Variable|Workshop Variable]] · [[Widgets, Binding & Writeback#Object Set Binding|Object Set Binding]] · [[Objects#Object Set|Object Set]] · [[Widgets, Binding & Writeback#Action Form|Action Form]] · [[Widgets, Binding & Writeback#AIP Agent Widget|AIP Agent Widget]]

*clone: simplify · kind: concept · layer: app · source: App-Building reconstruction §3*
#clone/simplify #kind/concept #layer/app

## Object Set Binding

> How apps consume the Ontology: object sets feed widgets, and selection flows back as output object sets.

A widget reads an [[Objects#Object Set|Object Set]] variable; the user's selection produces an active/selected output set; [[Widgets, Binding & Writeback#Object Set Filter|filters]] narrow other sets (the canonical Filter List → Object Table pattern). The read side of the app↔ontology contract.

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[Objects#Object Set|Object Set]] · [[Widgets, Binding & Writeback#Object Set Filter|Object Set Filter]] · [[Widgets, Binding & Writeback#Widget|Widget]] · [[Functions#Functions on Objects (FOO)|Functions on Objects (FOO)]]

*clone: simplify · kind: mechanism · layer: app · source: App-Building reconstruction §5*
#clone/simplify #kind/mechanism #layer/app

## Object Set Filter

> A reusable variable of property/value pairs applied to object set variables to narrow them.

Output by Filter List, charts, and pivot tables; applied to a *separate* object-set variable so the base set isn't limited. The app-layer expression of querying the [[Objects#Object Set|object model]].

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[Objects#Object Set|Object Set]] · [[Widgets, Binding & Writeback#Object Set Binding|Object Set Binding]] · [[Reactive State Model#Workshop Variable|Workshop Variable]]

*clone: simplify · kind: concept · layer: app · source: App-Building reconstruction §4*
#clone/simplify #kind/concept #layer/app

## Action Form

> A UI form auto-generated from an Action Type — the app layer's writeback surface.

Parameters bind from app state (local Workshop defaults override global); [[Actions#Submission Criteria|Submission Criteria]] surface inline as issues; submit is enabled only when all parameters validate, then data refreshes. 'Writeback and the UI for it are not defined separately.'

**Invariants:** [[Governed Writeback]]

**Related:** [[Actions#Action Type|Action Type]] · [[Actions#Submission Criteria|Submission Criteria]] · [[Reactive State Model#Workshop Variable|Workshop Variable]] · [[Operational Application]] · [[Actions#Edits-Only-via-Actions|Edits-Only-via-Actions]]

**For our clone:** Keep — generating the form from the action definition is a key define-once win.

*clone: keep · kind: mechanism · layer: app · source: App-Building reconstruction §5*
#clone/keep #kind/mechanism #layer/app

## Auto-Refresh

> Module-level live data updates: watches registered object sets and refreshes when they change anywhere in Foundry.

Reflects other users' actions, upstream edits, and streaming sources without user interaction — the app-layer realization of [[Read-Your-Writes]]. Limited to [[Object Storage#Object Storage V2 (OSv2)|OSv2]]-backed object types.

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[Read-Your-Writes]] · [[Object Storage#Object Storage V2 (OSv2)|Object Storage V2 (OSv2)]] · [[Widgets, Binding & Writeback#Object Set Binding|Object Set Binding]]

*clone: simplify · kind: mechanism · layer: app · source: App-Building reconstruction §5*
#clone/simplify #kind/mechanism #layer/app

## AIP Agent Widget

> A Workshop widget embedding an AIP agent/chatbot — the AIP↔app seam.

Maps the agent's 'application variables' to Workshop variables (read/write); its tools include AIP Logic and [[Functions#Functions on Objects (FOO)|Functions on Objects (FOO)]]. How AI reaches the user surface; see [[Integration & Automation#AIP Tool Exposure|AIP Tool Exposure]] and the [[AIP Layer]].

**Invariants:** [[Semantic Model Over Data]] · [[Governed Writeback]]

**Related:** [[AIP Layer]] · [[Integration & Automation#AIP Tool Exposure|AIP Tool Exposure]] · [[Widgets, Binding & Writeback#Widget|Widget]] · [[Functions#Functions on Objects (FOO)|Functions on Objects (FOO)]]

**For our clone:** Defer — the AI surface is post-MVP.

*clone: defer · kind: mechanism · layer: app · source: App-Building reconstruction §3*
#clone/defer #kind/mechanism #layer/app
