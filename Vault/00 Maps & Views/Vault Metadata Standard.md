---
tags:
  - hub
  - meta
  - standard
updated: 2026-06-14
---

# Vault Metadata Standard

> The one canonical way every concept carries queryable metadata. Resolves the dual-schema drift: typed properties on single-disposition notes, a standardized footer **plus Obsidian-indexed inline tags** on every concept inside a multi-concept document. Enforced by `vault_tools.py`. See [[Taxonomy (Legend)]] for the value vocabulary and [[Build View — What We're Cloning]] / [[Build Matrix (Layer × Disposition)]] for the generated query views.

## The problem this fixes

Obsidian properties — and **Bases** — are **per-file**: one note is one row. After consolidation, the unit of meaning became **per-section** (five-to-eight concepts in one document). A page-level property can't describe eight concepts with different dispositions, so per-concept metadata had drifted into prose footers that nothing could query. This standard makes every concept queryable again **with no plugin**, by pairing a human-readable footer with real inline tags that Obsidian's core tag pane, search, and graph all index.

## Two carriers, one rule

**Single-disposition notes** — folders `02 Foundations`, `03 Data Foundation`, the 8 layer hubs, and any one-concept file. Metadata lives in **YAML frontmatter**, mirrored as tags so it is queryable at the file level:

```yaml
---
aliases: [ "Magritte", "Connector" ]
tags: [ layer/data, kind/service, clone/simplify ]
layer: data
kind: service
clone: simplify
invariants: [ "[[Versioned Data Foundation]]", "[[Security Travels With Data]]" ]
source: "Data reconstruction §2–2.5"
updated: 2026-06-13
---
```

**Multi-concept documents** — folders `04`–`10`, where the [[Build View — What We're Cloning|Build View]] links to `#section` anchors. Frontmatter carries only `aliases` + `updated` (plus optional doc-level `layer/kind/clone` for the document as a whole). Each concept `## Section` ends with a **two-line footer**: an italic record line, then an inline-tag line.

```markdown
## Action Type

> A governed, transactional definition of a set of edits to objects/links, plus side effects.

…body…

**Invariants:** [[Governed Writeback]]
**Related:** [[Action Parameter]] · [[Submission Criteria]]
**For our clone:** Keep (the heart). See [[Design Decisions|D10]].

*clone: keep · kind: concept · layer: kinetic · invariants: [[Governed Writeback]] · source: Kinetic reconstruction §2*
#clone/keep #kind/concept #layer/kinetic
```

The **rule for which carrier**: if the Build View references the doc by `#section` (multiple concepts, mixed dispositions) → section footer. If it links the whole document (one disposition) → frontmatter. That boundary is not arbitrary — it is exactly where the disposition stops being uniform across the file.

## Canonical footer format

```
*clone: <disp> · kind: <kind> · layer: <layer> · invariants: [[A]] [· [[B]] …] · source: <text>*
#clone/<disp> #kind/<kind> #layer/<layer>
```

Field order is fixed: **clone · kind · layer · invariants · source**. `invariants` is omitted only when the concept embodies none. The tag line is always `#clone/… #kind/… #layer/…`. Value vocabularies (`layer`, `kind`, `clone`, the five `invariants`) are defined in [[Taxonomy (Legend)]].

## How to query — no plugin needed

- **Tag pane / search / graph:** `tag:#clone/keep`, `tag:#layer/semantic`, `tag:#kind/service`. This now resolves across **both** carriers — frontmatter tags on single-disposition notes and inline tags on every section — so a single `#clone/keep` surfaces the whole build set.
- **Generated views:** [[Build View — What We're Cloning]] (every concept by disposition) and [[Build Matrix (Layer × Disposition)]] (the cross-tab). These are emitted from the canonical concept data, so they never drift.
- **Bases / Dataview (optional):** work file-by-file for single-disposition notes. They cannot treat a `##` section as a row, so for the multi-concept docs use the inline tags or the generated views — that is the deliberate trade behind this standard.

## Tooling & pipeline

`vault_tools.py` (repo root) enforces the standard and refreshes the views. Both subcommands are **dry-run by default**; pass `--apply` to write. Commit the vault (git) before applying.

```bash
python3 vault_tools.py normalize        # preview footer + tag changes in 04–10
python3 vault_tools.py normalize --apply
python3 vault_tools.py views --apply     # regenerate the Build Matrix
```

`normalize` is **idempotent** — it strips any prior tag lines and re-emits, so it is safe to re-run after any edit. It is the final pass of the full rebuild pipeline:

```
build_vault.py  →  note-consolidator (consolidate.py)  →  vault_tools.py normalize --apply  →  vault_tools.py views --apply
```

Because `normalize` runs last and is idempotent, the standard self-heals after a regeneration or a hand-edit without touching the generator or the consolidator.

---

[[Foundry — Home (MOC)|← Home]] · [[Taxonomy (Legend)]] · [[Build View — What We're Cloning]] · [[Build Matrix (Layer × Disposition)]]
