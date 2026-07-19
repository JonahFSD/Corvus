# VAULT_AUDIT — Foundry/Vault

*Audit date: 2026-06-14 · Auditor: Claude (Opus 4.8) · Scope: `Foundry/Vault/` and the tools that generate it.*

Companion deliverables in this folder: `structural.md` (deterministic findings), `claims.md` (semantic ledger), `fixes.md` (action plan), `check_vault.py` (re-runnable gate), plus raw `structural_raw.md` / `structural_findings.json`.

---

## Verdict (the punchline)

**This is a high-quality vault.** Its prose verifies against Palantir's primary documentation with unusual fidelity — of ~23 load-bearing claims I spot-checked against `docs.palantir.com`, all but two VERIFIED with exact quotes, and every sampled note faithfully represents its cited research source. Structurally it is clean: **0 broken links, 0 broken anchors, 0 collisions, 0 orphans** across 1,937 wikilinks. The probe's two "candidate broken links" (`[[Action Parameter]]`, `[[Submission Criteria]]`) are **false positives** — they resolve through block-list aliases on `Actions.md`.

The things that actually undermine trust are not in the notes' content — they are in **provenance and freshness**:

1. **P0 (latent data-loss).** The vault has silently **forked from its generator.** `build_vault.py` emits 194 *atomic* notes; the live vault is 71 *consolidated* docs with no committed tool to reproduce them. Re-running `build_vault.py` — which the README's "Regenerating the vault" section and *this audit's own prompt* invite — would **corrupt** the vault: resurrect ~194 atomic stubs, revert the `[[Doc#Section]]` link rewrites, and drop hand-added hub links. The premise "edits to `.md` are ephemeral, fix the generator" is **false for this vault** and acting on it is destructive.
2. **P1 (stale headline numbers).** The **Build View** ("the actionable spec view / the build list") and the **README** report a build set of **58** (keep 51 / simplify 35 / drop 34). The generator and the regenerated **Build Matrix** say **60** (keep 53 / simplify 49 / drop 39). The actionable view is wrong.
3. **P1 (stale decision register).** The **Design Decisions** note frames D1–D15 as "open forks." `Spec/SPEC_Foundry-Clone_Build-Blueprint.md` (same day) **resolves and commits all 15.**

Everything else is conformance drift (P2) and nits (P3). Full ranking below.

---

## VAULT PROFILE

| Property | Value (verified) |
|---|---|
| **Generated or authored?** | **Generated, then forked.** `build_vault.py` (1,459 lines; concept data inlined as `CONCEPTS`) emits 194 atomic notes → `Skills/note-consolidator/scripts/consolidate.py` merges them into ~50 multi-concept docs and deletes the atomics → `vault_tools.py normalize` adds footers/inline tags → `vault_tools.py views` regenerates the Build Matrix. **The consolidation group-configs for folders 03,05–10 and the link-rewriting step are NOT in the repo, so the live vault is not reproducible from committed sources.** See "Where fixes go" below. |
| **Generator path** | `Foundry/build_vault.py` (concept registry + atomic emitter, `build()` unsafe to re-run wholesale) · `Foundry/vault_tools.py` (`normalize`, `views` — safe, idempotent) · `Foundry/Skills/note-consolidator/scripts/consolidate.py` (one-shot, needs uncommitted configs) |
| **Note count** | **73** `.md` total = **71 real notes** + 2 under `.junk/`. (README's "68 documents" is stale.) |
| **Attachments** | **None.** No images/PDFs/embeds. Non-`.md` files: `.obsidian/` config (5 json) + tracked `.DS_Store` files (cruft). |
| **Folder structure** | 12 numbered domain folders: `00 Maps & Views`, `01 Invariants`, `02 Foundations`, `03 Data Foundation` … `10 Platform & Ecosystem`. Foldered by domain, flat by link. |
| **Frontmatter schema (the contract)** | Defined by `00 Maps & Views/Vault Metadata Standard.md` — **two carriers**: **(A)** single-disposition notes (02, 03, atomic) carry full typed frontmatter (`tags, layer, kind, clone, invariants?, source, updated, aliases?`); **(B)** multi-concept docs (04–10) carry minimal frontmatter (`aliases, updated`, + *optional* doc-level `layer/kind/clone`) and put per-concept metadata in a two-line `## section` footer (`*clone: … *` + `#clone/… #kind/… #layer/…`). Welcome has no frontmatter, by design. |
| **Frontmatter keys in use** | `tags` 57 · `updated` 55 · `aliases` 51 · `layer` 32 · `kind` 32 · `clone` 28 · `source` 28 · `invariants` 17 (across 70 notes). |
| **Link conventions** | `[[wikilink]]` (alias-resolved), `[[Doc#Section\|alias]]` (the dominant post-consolidation form), `[[link\|alias]]`. **Aliases are multi-line YAML block lists** — 193 declared across the corpus; resolution MUST be alias- and block-list-aware (a naive checker reports false broken links). No embeds, no block refs in active use. |
| **Reachability / hubs** | `Welcome` → `Foundry — Home (MOC)` → 5 invariant hubs + 8 layer hubs + working views (Build View, Build Matrix, Taxonomy, Design Decisions, Vault Metadata Standard). Layer hubs list atomic concept titles that resolve via alias to the consolidated docs. **All 71 notes reachable; 0 orphans.** Highest inbound: the 5 invariants (Security Travels With Data 107, Semantic Model Over Data 83) then Actions 73 / Objects 59 / Functions 53. |
| **Canonical concept data** | 194 concepts in `build_vault.py`; dispositions via `disposition()`: **core 7 · keep 53 · simplify 49 · defer 46 · drop 39** (build set = core+keep = **60**). The Build Matrix matches this; the Build View and README do not. |

---

## How this audit was verified (so it isn't "just another opinion")

- **Structural facts** are output of `check_vault.py`, which I wrote, ran, and *debugged against reality* (my first run produced 13 false positives from a wrong carrier-classification rule; I corrected the classifier — discriminate by `## section` body shape, not by the presence of a `layer:` scalar, which the Standard explicitly allows on carrier-B docs — and re-ran). Command: `python3 Harvest/_audit/check_vault.py`. Result embedded in `structural.md`.
- **Generated-vs-forked** confirmed by: `grep -c 'dict(t=' build_vault.py` → 194 atomic vs 71 consolidated note files; `git show a508725` ("Fold … delete root stubs"); reading `consolidate.py` (line 99 adds former titles to `aliases:`; `--delete` removes originals); README line 184 ("a raw regeneration reverts to the atomic layout").
- **Content claims** double-verified: **external** web checks vs `docs.palantir.com` (≈23 claims) and **internal** source-grounding vs `ResearchResults/` (12 claim/source pairs). Tables in `claims.md`. I mark VERIFIED only where a primary source supports the *specific* assertion; otherwise REPORTED.
- **Cross-layer/Spec drift** confirmed by reading `Spec/SPEC_Foundry-Clone_Build-Blueprint.md` (resolves D1–D15) and `Spec/SPEC_Foundry-Clone_Spec-Audit.md`.
- **Self-correction:** I withdrew an in-progress finding ("only the Semantic reconstruction is evidence-tagged") after a loose re-grep showed it was an artifact of exact-match `\[Documented\]` missing the real `[Documented, High]` format. The reconstructions are, in fact, densely graded.

---

## Findings, ranked

> Severity: **P0** broken/contradicted/data-loss · **P1** undermines trust in the spec · **P2** conformance/consistency · **P3** nit. Every fix is routed to the correct pipeline stage in `fixes.md`.

### P0 — latent data-loss

**P0-1 · The vault has forked from its generator; re-running `build_vault.py` corrupts it.**
- Evidence: `build_vault.py:1292-1293` writes one note per concept for all 194 `CONCEPTS`; live vault has 71 consolidated docs (`Objects.md`, `Properties.md`, `Actions.md`…) whose names are not in `CONCEPTS`. The 194 atomic titles (`Object Type`, `Action Parameter`, …) exist as **no file** — they are `aliases:`/`## sections` inside the consolidated docs. `git show a508725` deleted the atomic stubs and rewrote links. `The Closed Loop.md:21,25` shows links hand-rewritten to `[[Actions#Action Type|…]]` / `[[Audit & Writeback#Writeback Path|…]]` — forms `build_vault.py` does not emit.
- Impact: running `python3 build_vault.py` (per README "Regenerating the vault", and per *this audit prompt's* stated premise) would (a) create ~194 atomic `.md` files, (b) collide aliases (Obsidian would prefer a new `Action Parameter.md` over the `Actions` alias, silently redirecting links), (c) revert the `#section` rewrites in 02/03 to bare links that no longer resolve. Net: structural corruption.
- Also: the consolidation is **not reproducible** — only a 3-doc `Skills/note-consolidator/assets/example-groups.json` is committed; the group-configs that produced `Actions.md`, the 03 docs, and folders 05–10 are absent, as is the link-rewriter.
- Fix: see `fixes.md` §P0 — adopt the corrected fix-routing model; add a guard/README banner; commit the consolidation configs so the pipeline is reproducible. **Do not "fix the generator and re-run" for content.**

### P1 — undermines trust in the spec

**P1-1 · The Build View and README report a stale build set (58) vs the true 60.**
- Evidence: `disposition()` over `CONCEPTS` → core 7/keep 53/simplify 49/defer 46/drop 39 (sum 194; build set 60). `Build Matrix (Layer × Disposition).md:24-26` agrees (60). But `Build View — What We're Cloning.md:16,30,56` headers say keep **(51)** / simplify **(35)** / drop **(34)**, and `README.md:102-110,223` says keep 51/simplify 35/drop 34, "core+keep (58)". The Build View is titled "the actionable spec view … the build list."
- Root cause: the Build View is emitted by `build_vault.py build()` (unsafe to re-run, so never refreshed) and then hand-edited; the Build Matrix is emitted by `vault_tools.py views` (safe, re-run, correct). The two generated views disagree.

**P1-2 · The Design Decisions register is stale: D1–D15 shown "open," but the Spec resolved all 15.**
- Evidence: `Design Decisions.md` (from `build_vault.py:1327`) says "Open forks to resolve … (Phase 3)"; `Minimum Viable Foundry` calls them open. `Spec/SPEC_Foundry-Clone_Build-Blueprint.md` (2026-06-14) §3: "This blueprint commits them. Each is an engine choice" — e.g. D1=PostgreSQL single instance, D2=append-only `edit_event` log ("not literal SNAPSHOT/APPEND/UPDATE/DELETE"), D5=hybrid `objects`+JSONB+typed views, D6=unified `links` table, D11=TypeScript/Node, D15=RBAC+row policies.
- Impact: a reader using the vault as "the living spec" (README) sees unresolved decisions the project has actually closed.

### P2 — conformance / consistency

**P2-1 · `Object Storage.md` is invisible to tag/graph queries.** Has neither a frontmatter `tags:` block nor inline `#clone/#kind/#layer` section tags (5 `##` sections, 0 footers — `Object Storage:1`). `vault_tools.py normalize` only transforms *existing* footer lines (`FOOTER_RE`), so it silently skips this doc forever. A `#clone/drop` or `#layer/semantic` filter misses all 5 of its concepts.

**P2-2 · Four folder-03 docs flatten mixed dispositions to one file-level `clone`, contradicting the Standard's own carrier rule.** `Dataset & Transactions` (`clone: keep`, contains `drop`+`simplify` sub-concepts), `Data Connection (Magritte)` (simplify + drop), `Data Health & Lineage` (keep + simplify), `Transforms & Build` (simplify + keep). The Standard says single-disposition frontmatter applies only "where the disposition stops being uniform" — these aren't uniform, so `#clone/keep` wrongly surfaces docs containing dropped concepts. (The canonical per-concept dispositions in `build_vault.py`/Build Matrix remain correct; only the note-level tags mislead.)

**P2-3 · Phase numbering is inconsistent across three places.** README "Phase 2 (in progress) — domain adaptation"; vault Design Decisions "Phase 3"; `Build-Blueprint.md:5` "Phase 2 … comes after [the engine spec]." No single source of truth for project phase.

**P2-4 · Committed/working-tree detritus.** Tracked `.DS_Store` at repo root, `DeepResearch/`, and `Vault/.DS_Store` (the last is in `.gitignore` but was committed before ignore). `Vault/.junk/t.md` and `Vault/.junk/captest_1781388682/dirB/f.md` present on disk (gitignored, so *not* committed — the probe's "committed detritus" was wrong here).

### P3 — nits

- **P3-1 · `kind:` vocabulary drift.** 15 docs carry a doc-level `kind:` outside the Taxonomy vocabulary: `doc` (11, folders 05/09/10) and `domain` (4, folder 04) — and the two are used inconsistently for the same idea. Either add `doc`/`domain` to `Taxonomy (Legend)` as legitimate doc-level kinds, or normalize to one.
- **P3-2 · "Model Gateway" is an invented proper noun.** The governed multi-LLM layer is real and VERIFIED (proxy endpoints, ZDR, GPT/Claude/Gemini/Grok/Llama), but Palantir names it "LLM-provider compatible APIs"/"Model Catalog," never "Model Gateway." Stated as fact in `Model Gateway & Governance.md`. Mark as reconstruction label.
- **P3-3 · "Slate (Legacy Builder)" — contested characterization.** Current `docs.palantir.com/.../app-building/overview` lists Workshop **and** Slate as co-equal "primary application building tools" and never calls Slate legacy. The "legacy/power-user" framing is the vault's editorial judgment, baked into the note title; defensible but not documented. (See `claims.md`.)
- **P3-4 · Staleness landmine.** `Phonograph (OSv1)` note: "end-of-life after June 30, 2026" — VERIFIED accurate today, but the phrasing will read wrong in 17 days; convert to a dated, after-the-fact-safe statement.
- **P3-5 · Home MOC diverged from generator.** `Foundry — Home (MOC).md:43,46` lists `Build Matrix` and `Vault Metadata Standard`, but `build_vault.py:1342` does not emit them (hand-added in `af350cc`). A symptom of P0-1; harmless until a regen drops them.
- **P3-6 · README counts stale.** "68 documents" (now 71), "~195 atomic concepts" (194).

---

## What's good (trust calibration)

- **Link integrity is excellent.** 1,937 links / 193 block-list aliases / 264 resolvable names → 0 broken, 0 dangling anchors, 0 collisions. The consolidation + link-rewrite was executed carefully and losslessly.
- **Graph is healthy.** 0 orphans, every note reachable from `Welcome`; invariants correctly central.
- **Content is well-sourced.** Every sampled note matches its cited reconstruction, and the reconstructions match Palantir's live docs (exact quotes in `claims.md`). The vault's own confidence-grading (`[Documented, High]`, etc.) is applied across all eight layers.
- **The metadata Standard is coherent and largely honored** — the two-carrier model is real and mostly conformant; the drift items above are the exceptions, not the rule.
- **The deterministic gate now exists** (`check_vault.py`) and passes; wire it into the build pipeline so this stays true.

---

## Out of scope (noted, not audited here)

- `Spec/SPEC_Foundry-Clone_Spec-Audit.md` already enumerates 8 reproduced SQL bugs + 6 design gaps in the **Build-Blueprint** (the clone's Postgres schema). Those are defects in the *implementation spec*, not the vault, and are already tracked there — not duplicated in this audit.
- External link-rot scanning (network) was not run.
