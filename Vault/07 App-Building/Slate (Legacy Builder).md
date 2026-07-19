---
tags:
  - layer/app
aliases:
  - Slate
  - Slate Node Graph
  - Handlebars (Slate)
updated: 2026-06-13
---

# Slate (Legacy Builder)

> The legacy power-user builder for pixel-level custom or public unauthenticated apps: a lazy node graph of widgets, variables, queries, and functions, wired by Handlebars templating — preserved for context, superseded by Workshop.

## Slate

> The legacy power-user builder (HTML/JS/CSS) for pixel-level custom or public unauthenticated apps.

A [[Slate (Legacy Builder)#Slate Node Graph|graph of nodes]] referenced via [[Slate (Legacy Builder)#Handlebars (Slate)|Handlebars]]; higher customization at higher maintenance. Recommended only when Workshop can't express the design; legacy data paths are deprecated.

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[Slate (Legacy Builder)#Slate Node Graph|Slate Node Graph]] · [[Slate (Legacy Builder)#Handlebars (Slate)|Handlebars (Slate)]] · [[Workshop, Modules & Views#Workshop|Workshop]]

**For our clone:** Skip — Workshop's model is the one to emulate.

*clone: drop · kind: service · layer: app · source: App-Building reconstruction §6*
#clone/drop #kind/service #layer/app

## Slate Node Graph

> Slate's model: widgets, variables, queries, and functions are nodes whose JSON outputs reference each other.

Explicitly lazy — a node re-evaluates only when an upstream reference changes value. The same reactive idea as Workshop's [[Reactive State Model#Reactivity Model|Reactivity Model]], but hand-managed.

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[Slate (Legacy Builder)#Slate|Slate]] · [[Slate (Legacy Builder)#Handlebars (Slate)|Handlebars (Slate)]] · [[Reactive State Model#Reactivity Model|Reactivity Model]]

*clone: simplify · kind: mechanism · layer: app · source: App-Building reconstruction §6*
#clone/simplify #kind/mechanism #layer/app

## Handlebars (Slate)

> Slate's `{{ }}` templating syntax that both reads node outputs and declares dependencies.

References to widgets/variables/environment define the dependency edges of the [[Slate (Legacy Builder)#Slate Node Graph|Slate Node Graph]]. The wiring mechanism of a Slate app.

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[Slate (Legacy Builder)#Slate|Slate]] · [[Slate (Legacy Builder)#Slate Node Graph|Slate Node Graph]]

*clone: simplify · kind: mechanism · layer: app · source: App-Building reconstruction §6*
#clone/simplify #kind/mechanism #layer/app
