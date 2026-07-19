# structural.md — deterministic findings

Output of `check_vault.py` (in this folder), the re-runnable structural gate. Every row here is script output, not opinion.

```
$ python3 Harvest/_audit/check_vault.py            # markdown report (raw copy: structural_raw.md)
$ python3 Harvest/_audit/check_vault.py --quiet     # 71 notes · 24 findings (P0 0, P1 0, P2 8, P3 16) · gate=PASS
$ python3 Harvest/_audit/check_vault.py --json       # machine-readable (structural_findings.json)
```

Exit code = count of P0+P1 findings (**0 → gate passes**). The vault has **no broken links, no broken anchors, no collisions, no orphans, no missing attachments.**

## Headline counts

| Metric | Value |
|---|--:|
| Real notes parsed (excl. `.junk/`) | 71 |
| Wikilinks + embeds scanned | 1,937 |
| Declared aliases (block-list aware) | 193 |
| Distinct resolvable names (basenames + aliases) | 264 |
| Broken links / embeds | **0** |
| Broken `#section` / `^block` anchors | **0** |
| Name/alias collisions | **0** |
| Orphans (0 inbound) / unreachable from Welcome | **0 / 0** |
| Findings (all conformance/consistency) | 24 (P2 8, P3 16) |

## The 24 findings

| location | sev | category | finding | fix | auto |
|---|:--:|---|---|---|:--:|
| `.DS_Store` | P2 | detritus | committed OS cruft | `git rm --cached`; already in `.gitignore` | ✅ |
| `.junk/captest_1781388682/dirB/f.md` | P2 | detritus | scratch capability-test file (gitignored, on disk) | `rm -rf Vault/.junk` | ✅ |
| `.junk/t.md` | P2 | detritus | scratch file (gitignored, on disk) | `rm -rf Vault/.junk` | ✅ |
| `Dataset & Transactions:1` | P2 | disposition | file-level `clone: keep` but sub-concepts also `drop`,`simplify` — not tag-queryable | split or per-section tags | — |
| `Data Connection (Magritte):1` | P2 | disposition | `clone: simplify` but also `drop` | split or per-section tags | — |
| `Data Health & Lineage:1` | P2 | disposition | `clone: keep` but also `simplify` | split or per-section tags | — |
| `Transforms & Build:1` | P2 | disposition | `clone: simplify` but also `keep` | split or per-section tags | — |
| `Object Storage:1` | P2 | footer | 5 `##` sections, 0 `*clone:*` footers — unstandardized & untagged | `vault_tools.py normalize` skips it (no existing footer); add tags manually | ✅* |
| `Object Storage:1` | P3 | footer | 5 `##` sections, 0 inline `#clone` tag lines | same as above | ✅* |
| `Objects` `Properties` `Links` `Ontology & Metadata` (×4) | P3 | vocabulary | doc-level `kind: domain` outside Taxonomy vocab | add `domain` to Taxonomy or normalize | — |
| 11 docs in 05/09/10 | P3 | vocabulary | doc-level `kind: doc` outside Taxonomy vocab | add `doc` to Taxonomy or normalize | — |

`*` auto-fixable in principle but **not** by `vault_tools.py normalize` as written — it transforms only pre-existing footer lines, so `Object Storage` needs a manual seed footer or a normalize tweak.

## What the checker proves about the probe's claims

The 5-minute probe in the audit prompt flagged candidates that this alias-/block-list-aware checker **clears as false positives** — exactly the lesson the prompt set up:

| Probe claim | Reality (verified) |
|---|---|
| `[[Action Parameter]]` likely a broken link | **Resolves** → `Actions.md` alias (`Actions.md:4`, multi-line block list). 0 broken. |
| `[[Submission Criteria]]` likely a broken link | **Resolves** → `Actions.md:7` alias. 0 broken. |
| "~42 declared aliases" | **193** — the probe's single-line parser missed multi-line YAML block lists. |
| `Welcome.md` is the sole orphan + frontmatter-less | **Correct, by design** — it is the BFS root and intentionally has no frontmatter; whitelisted. |
| `.junk/*` is "committed detritus" | `.junk/` is **gitignored** → *not committed*. Present in the working tree only. (The real committed cruft is `.DS_Store`.) |

## A note on auditing the auditor

The first run of `check_vault.py` reported **13 frontmatter findings** that were **my tool's false positives**: it classified any note with a `layer:` scalar as "carrier A" and demanded `clone/source/tags`. But the Vault Metadata Standard *explicitly permits* carrier-B multi-concept docs (04–10) an optional doc-level `layer/kind/clone`. The correct discriminator is the **body shape** (does it have `##` concept sections?), not the frontmatter. I fixed the classifier and re-ran; the 13 vanished and the real issues (vocabulary, disposition-flattening, `Object Storage`) surfaced. The structural pass is only as trustworthy as the checker, so the checker was itself verified.

## Re-running as a gate

`check_vault.py` is dependency-free (stdlib only) and locates the vault relative to its own path, so it runs from anywhere. Wire it after every `build_vault.py` / `consolidate.py` / `vault_tools.py` change:

```bash
python3 Harvest/_audit/check_vault.py --quiet && echo "vault gate: PASS"
```
