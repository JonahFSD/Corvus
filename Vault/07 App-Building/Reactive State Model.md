---
tags:
  - layer/app
aliases:
  - Workshop Variable
  - Reactivity Model
  - Recompute Behavior
  - Workshop Event
updated: 2026-06-13
---

# Reactive State Model

> How state moves and recomputes inside a Workshop app: typed reactive variables, the lazy demand-driven dependency graph, the per-variable recompute modes, and the fire-immediately / propagate-asynchronously event semantics a faithful clone must replicate.

## Workshop Variable

> A typed reactive value (input or output) that moves data through a module.

Types include object set, object set filter, string, boolean, numeric, date, geo, array, struct, time-series set. Defined statically or from functions, object properties, aggregations, or object-set definitions; consumed by widgets and recomputed per the [[Reactive State Model#Reactivity Model|Reactivity Model]].

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[Reactive State Model#Reactivity Model|Reactivity Model]] · [[Reactive State Model#Recompute Behavior|Recompute Behavior]] · [[Widgets, Binding & Writeback#Object Set Filter|Object Set Filter]] · [[Reactive State Model#Workshop Event|Workshop Event]] · [[Functions#Functions on Objects (FOO)|Functions on Objects (FOO)]]

**For our clone:** Keep — a typed reactive state model is the heart of the app layer.

*clone: keep · kind: concept · layer: app · source: App-Building reconstruction §4*
#clone/keep #kind/concept #layer/app

## Reactivity Model

> A lazy dependency graph: variables compute only when displayed by a visible widget.

In view mode a variable recomputes only when shown (non-visible pages/tabs/overlays are skipped); in edit mode all compute. Function-backed variables cache on input identity. The make-or-break mechanism to replicate faithfully.

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[Reactive State Model#Workshop Variable|Workshop Variable]] · [[Reactive State Model#Recompute Behavior|Recompute Behavior]] · [[Reactive State Model#Workshop Event|Workshop Event]] · [[Slate (Legacy Builder)#Slate Node Graph|Slate Node Graph]]

**For our clone:** Keep the *behavior* (lazy, demand-driven); the engine internals are unpublished (treat as our design).

*clone: keep · kind: mechanism · layer: app · source: App-Building reconstruction §4*
#clone/keep #kind/mechanism #layer/app

## Recompute Behavior

> How a variable refreshes: Automatic (default), Only-on-event, or On-load-plus-event.

Automatic recomputes when any dependency changes (and may recompute when upstream objects reload after an action or [[Widgets, Binding & Writeback#Auto-Refresh|Auto-Refresh]]). Function results are cached; force recompute via an incrementing 'entropy' variable.

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[Reactive State Model#Reactivity Model|Reactivity Model]] · [[Reactive State Model#Workshop Variable|Workshop Variable]] · [[Widgets, Binding & Writeback#Auto-Refresh|Auto-Refresh]]

*clone: simplify · kind: concept · layer: app · source: App-Building reconstruction §4*
#clone/simplify #kind/concept #layer/app

## Workshop Event

> The explicit state-change mechanism — but events fire immediately and do NOT await downstream recomputation.

Events run sequentially in configured order; the source value is copied to the target immediately, but dependents are not up-to-date before the next event runs. **A faithful clone must replicate this fire-immediately, propagate-asynchronously semantics, not a synchronous transactional update.**

**Invariants:** [[Semantic Model Over Data]] · [[Governed Writeback]]

**Related:** [[Reactive State Model#Reactivity Model|Reactivity Model]] · [[Reactive State Model#Workshop Variable|Workshop Variable]] · [[Widgets, Binding & Writeback#Action Form|Action Form]]

**For our clone:** Critical: copy the async-propagation semantics or app logic will subtly differ.

*clone: keep · kind: mechanism · layer: app · source: App-Building reconstruction §4 (verbatim, verified)*
#clone/keep #kind/mechanism #layer/app
