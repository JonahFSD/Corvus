---
name: note-consolidator
description: >-
  Consolidate a folder of many small atomic Markdown notes into a few larger documents
  grouped by subdomain — losslessly. Preserves every definition, paragraph, metadata field,
  and [[wikilink]] (former note titles become aliases so inbound links keep resolving) and
  rebuilds the hub/index. Use whenever the user wants to merge, condense, consolidate, combine,
  or group many small notes or Markdown files into fewer larger ones; reduce note sprawl in an
  Obsidian/Zettelkasten/Foundry-style vault; turn atomic notes into documentation; or says
  things like "condense this folder", "merge these notes", "fewer bigger files", or "group these
  by topic" — even if they don't name the method.
---

# Note Consolidator

Turn a folder of many tiny atomic notes into a handful of larger, readable subdomain
documents **without losing anything** — not a sentence of prose, not a metadata field,
and not a single working link.

## Why "lossless" is the whole game

In a linked vault the value isn't only the text — it's the graph. Other notes point at these
concepts with `[[wikilinks]]`, and a query layer (Dataview) may read their frontmatter. So
"condensing" must keep three things intact:

1. **Content** — every definition, paragraph, and decision note survives verbatim.
2. **Metadata** — per-note fields (type, status, source, invariants…) survive, surfaced inline
   since one merged document can't carry twenty frontmatter blocks.
3. **Links** — every `[[Old Note Title]]` must still resolve. The trick: add each former title
   to the new document's `aliases:`. The vault then resolves the old link to the new doc with
   zero edits anywhere else.

If you can't promise those three, you're reshuffling, not consolidating.

## Procedure

### 1. Snapshot and survey
Commit the vault first (git) so the change is reversible. Read every note in the target folder.
Count inbound `[[links]]` from *other* folders — high inbound counts are exactly why you must
preserve resolution via aliases. Check whether a Dataview view reads these notes' frontmatter
(if so, see Gotchas).

### 2. Group by subdomain — and confirm with the user
Cluster the notes into a few coherent subdomains (the natural "nouns"/themes of the folder).
Propose the grouping and let the user adjust borderline members before you touch anything.
Grouping is a judgment call they own.

### 3. Assemble one document per subdomain
Use `scripts/consolidate.py`. Each former note becomes a `## <Title>` section containing, in
order: its `>` definition, its prose, any bold-label carry-through lines (`**Related:**`,
`**For our clone:**`, …) kept verbatim, and a compact italic meta line built from chosen
frontmatter fields. The document's frontmatter lists every member title (and any short aliases
the notes had) under `aliases:`.

**Never rewrite the prose.** Consolidation *moves* text; it does not edit it.

### 4. Verify coverage, then delete the originals
The script checks that every member's definition, prose, and carry-through lines appear in its
new doc, and that no alias collides. Only after that passes, delete the originals (`--delete`).
If deletion is blocked ("Operation not permitted"), request file-delete permission rather than
leaving duplicates behind.

### 5. Rebuild the hub / index
Update the folder's map-of-content note to list the new documents, using `[[Doc#Section]]` links
that jump straight to each concept so nothing becomes harder to find.

### 6. Final link audit
Across the whole vault, confirm every former title resolves (as a file or an alias) and that any
inbound `[[Title#heading]]` link still finds its heading. Report the before/after file and line
counts so the user can see the real reduction (count files, not just lines — line counts flatter
the result because most removed lines are short metadata).

## The script

`scripts/consolidate.py` does the assembly, aliasing, coverage verification, and optional
deletion. It is **dry-run by default** — writes nothing until `--apply`, and won't delete until
coverage passes.

```bash
# 1) write a grouping config (see assets/example-groups.json)
cat > groups.json <<'JSON'
{
  "Objects":    {"intro": "The object model …", "members": ["Object Type", "Object", "Primary Key"]},
  "Properties": {"intro": "Typed attributes …",  "members": ["Property", "Value Type", "Derived Property"]}
}
JSON

# 2) dry run — see what it would build, nothing written
python scripts/consolidate.py --folder "Vault/04 Ontology - Semantic" --config groups.json

# 3) apply: write docs + verify coverage
python scripts/consolidate.py --folder "Vault/04 Ontology - Semantic" --config groups.json --apply

# 4) apply and remove originals once coverage passes
python scripts/consolidate.py --folder "Vault/04 Ontology - Semantic" --config groups.json --apply --delete
```

`--meta-fields clone,kind,invariants,source` (default) selects which frontmatter fields are
surfaced in each section's meta line. The body parser treats the leading `>` block as the
definition, text up to the first `**Label:**` line as prose, and every `**Label:**` line as a
verbatim carry-through.

## Gotchas

- **Dataview that queries per-note frontmatter** (a table of "every note where status = active")
  will no longer enumerate concepts that became sections — they aren't separate pages anymore.
  The data is preserved inline; tell the user and offer to convert that view or move fields to
  inline-field syntax.
- **Aliases land a link at the document top**, not the exact section. Fine for reading. If a few
  heavily-linked concepts need section precision, optionally rewrite those specific inbound links
  to `[[Doc#Section]]`.
- **Don't merge across a meaningful boundary** (different layers/top-level folders) unless asked
  — consolidate *within* a subdomain.

## Example

**Input:** 26 atomic notes in `04 Ontology - Semantic/` (Object, Object Type, Property, Link
Type, …), each ~25 lines, heavily cross-linked.
**Output:** 5 subdomain docs (`Objects`, `Properties`, `Links`, `Ontology & Metadata`,
`Object Storage`) + the hub. 26 → 7 files. Every former title aliased onto its doc; all ~200
inbound links still resolve; every definition and decision note preserved verbatim.
