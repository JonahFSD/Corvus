---
tags:
  - hub
  - meta
updated: 2026-06-13
---

# Taxonomy (Legend)

> How this vault is categorized and queried. Every concept note carries typed **properties** (for Obsidian **Bases** / Dataview) and mirrored **tags** (for the tag pane and graph). The vault is deliberately **flat** — navigation is by MOC, organization is by property/tag.

## Properties on every concept

| Property | Meaning | Values |
|---|---|---|
| `layer` | Which Foundry layer it belongs to | data · semantic · kinetic · dynamic · app · aip · security · platform · crosscutting |
| `kind` | What kind of idea it is | concept · mechanism · service · type · pattern · property · reference |
| `clone` | Disposition for *our* build | core · keep · simplify · defer · drop |
| `invariants` | The promise(s) it embodies (links) | one or more of the 5 invariants |
| `source` | Which reconstruction it came from | text |
| `aliases` | Acronyms (OSv2, FOO, CBAC, …) | list |

## Clone dispositions

- **core** — the irreducible essence; principles we embody.
- **keep** — replicate faithfully (the build list).
- **simplify** — keep the idea, shrink the implementation.
- **defer** — add later without rework.
- **drop** — Palantir-scale machinery we don't need.

Sorted index: [[Build View — What We're Cloning]].

## Layers (MOCs)

- [[Data Integration & Pipeline Layer]]
- [[Ontology — Semantic Layer]]
- [[Ontology — Kinetic Layer]]
- [[Ontology — Dynamic Layer]]
- [[Security & Governance Layer]]
- [[App-Building Layer]]
- [[AIP Layer]]
- [[Platform & Ecosystem Layer]]

## The five invariants (MOCs)

- [[Semantic Model Over Data]]
- [[Versioned Data Foundation]]
- [[Governed Writeback]]
- [[Security Travels With Data]]
- [[End-to-End Lineage]]

## How to query — no plugin needed

**Obsidian Bases (core):** new Base → add filters like `clone is keep` or `layer is semantic` → group by `layer`. Renders as a live table/cards.

**Property search:** in Search, type `["clone":"keep"]` or `["layer":"kinetic"]`.

**Tag pane / graph:** filter by `#clone/keep`, `#layer/semantic`, `#kind/service`.

**Dataview (optional plugin):**

```dataview
TABLE layer, clone, source
WHERE kind != null AND clone = "keep"
SORT layer ASC
```

## Why flat + MOCs + properties (not folders)

Best practice for a large reference vault: folders force a single home per note. This vault instead stays **flat** and uses **MOCs** (the [[Foundry — Home (MOC)|Home]], the 5 invariant hubs, the 8 layer hubs) for navigation, with **properties/tags** for cross-cutting filtering — so any note can appear in many views at once.

---

[[Foundry — Home (MOC)|← Home]]
