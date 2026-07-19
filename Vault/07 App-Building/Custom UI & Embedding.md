---
tags:
  - layer/app
aliases:
  - Custom Widget
  - Widget Set
  - OSDK React Hooks
  - Bidirectional Iframe
  - Embedded Foundry Apps
updated: 2026-06-13
---

# Custom UI & Embedding

> The escape hatch for custom interfaces: developer-built React widgets and their deployable widget sets, the typed OSDK React data layer, bidirectional iframes, and embedding other Foundry surfaces inside a module.

## Custom Widget

> Developer-built React frontend code embedded in Workshop, running in a restrictive sandbox.

Packaged as a [[Custom UI & Embedding#Widget Set|Widget Set]]; declares parameters (host→widget) and events (widget→host); uses [[Custom UI & Embedding#OSDK React Hooks|OSDK React Hooks]] under the user's permissions. No web storage, no external requests, non-configurable CSP. The escape hatch for custom UI.

**Invariants:** [[Semantic Model Over Data]] · [[Security Travels With Data]]

**Related:** [[Custom UI & Embedding#Widget Set|Widget Set]] · [[Custom UI & Embedding#OSDK React Hooks|OSDK React Hooks]] · [[Custom UI & Embedding#Bidirectional Iframe|Bidirectional Iframe]] · [[Workshop, Modules & Views#Workshop|Workshop]]

*clone: simplify · kind: mechanism · layer: app · source: App-Building reconstruction §8*
#clone/simplify #kind/mechanism #layer/app

## Widget Set

> A deployable package of one or more custom widgets (OSDK build artifacts).

Built with `@osdk/widget.*` packages; rendered via the `FoundryWidget` root; registered under `ri.widgetregistry..widget-set`. The distribution unit for custom UI.

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[Custom UI & Embedding#Custom Widget|Custom Widget]] · [[Custom UI & Embedding#OSDK React Hooks|OSDK React Hooks]]

*clone: simplify · kind: concept · layer: app · source: App-Building reconstruction §8*
#clone/simplify #kind/concept #layer/app

## OSDK React Hooks

> The typed React data layer (`useObjectSet`, `useOsdkAction`, …) for custom apps and widgets.

Provide automatic caching, loading states, and real-time updates; require an `OsdkProvider2`. Calls run under the user's permissions. The bridge from custom UI to the [[Ontology & Metadata#Ontology|Ontology]].

**Invariants:** [[Semantic Model Over Data]] · [[Security Travels With Data]]

**Related:** [[Custom UI & Embedding#Custom Widget|Custom Widget]] · [[Custom UI & Embedding#Widget Set|Widget Set]] · [[Objects#Object Set|Object Set]]

*clone: simplify · kind: mechanism · layer: app · source: App-Building reconstruction §8 / §10*
#clone/simplify #kind/mechanism #layer/app

## Bidirectional Iframe

> Embedding an external app that reads/writes Workshop state via `useWorkshopContext`.

The `@osdk/workshop-iframe-custom-widget` context exposes Workshop variable read/write and event execution over `postMessage`. Recommended over the plain iframe widget for custom apps (one per instance; ≤1 on-screen recommended).

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[Custom UI & Embedding#Custom Widget|Custom Widget]] · [[Reactive State Model#Workshop Event|Workshop Event]] · [[Slate (Legacy Builder)#Slate|Slate]]

*clone: simplify · kind: mechanism · layer: app · source: App-Building reconstruction §8*
#clone/simplify #kind/mechanism #layer/app

## Embedded Foundry Apps

> Embedding other Foundry surfaces (Slate, Quiver, Notepad, Vertex, Map) inside a Workshop module.

Cross-app state flows via [[Workshop, Modules & Views#Module Interface|Module Interface]] mappings, drag-and-drop drop zones, and app pairing. Lets a module compose analytical and custom surfaces around the operational core.

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[Workshop, Modules & Views#Workshop Module|Workshop Module]] · [[Workshop, Modules & Views#Module Interface|Module Interface]] · [[Slate (Legacy Builder)#Slate|Slate]] · [[Custom UI & Embedding#Bidirectional Iframe|Bidirectional Iframe]]

*clone: simplify · kind: mechanism · layer: app · source: App-Building reconstruction §8*
#clone/simplify #kind/mechanism #layer/app
