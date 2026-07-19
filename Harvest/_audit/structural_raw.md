# Structural audit — check_vault.py

- vault: `/Users/jonahelliott/ARCHIPELIGO/Foundry/Vault`
- notes parsed: **71**  ·  junk files: 2  ·  non-md files: 1
- wikilinks/embeds scanned: **1937**  ·  declared aliases: **193**  ·  distinct resolvable names: 264
- findings: **24**  (P0 0, P1 0, P2 8, P3 16)

| Category | Count |
|---|--:|
| vocabulary | 15 |
| disposition | 4 |
| detritus | 3 |
| footer | 2 |

## P2 (8)

| location | category | finding | proposed fix | auto-fix? |
|---|---|---|---|:--:|
| `.DS_Store` | detritus | committed OS cruft (.DS_Store) | git rm --cached and add to .gitignore (already ignored at Vault/.DS_Store) | ✅ |
| `.junk/captest_1781388682/dirB/f.md` | detritus | scratch/capability-test file under .junk/ (gitignored but present on disk) | delete from working tree (rm -rf Vault/.junk) | ✅ |
| `.junk/t.md` | detritus | scratch/capability-test file under .junk/ (gitignored but present on disk) | delete from working tree (rm -rf Vault/.junk) | ✅ |
| `Data Connection (Magritte):1` | disposition | file-level clone: simplify but sub-concepts are also ['drop'] — per-concept disposition is not tag-queryable | split doc or add per-section #clone tags (vault_tools normalize covers 04–10 only) | — |
| `Data Health & Lineage:1` | disposition | file-level clone: keep but sub-concepts are also ['simplify'] — per-concept disposition is not tag-queryable | split doc or add per-section #clone tags (vault_tools normalize covers 04–10 only) | — |
| `Dataset & Transactions:1` | disposition | file-level clone: keep but sub-concepts are also ['drop', 'simplify'] — per-concept disposition is not tag-queryable | split doc or add per-section #clone tags (vault_tools normalize covers 04–10 only) | — |
| `Transforms & Build:1` | disposition | file-level clone: simplify but sub-concepts are also ['keep'] — per-concept disposition is not tag-queryable | split doc or add per-section #clone tags (vault_tools normalize covers 04–10 only) | — |
| `Object Storage:1` | footer | 5 ## sections but 0 footer lines (*clone: …*) — 5 unstandardized | run `python3 vault_tools.py normalize --apply` | ✅ |

## P3 (16)

| location | category | finding | proposed fix | auto-fix? |
|---|---|---|---|:--:|
| `Object Storage:1` | footer | 5 ## sections but 0 inline #clone tag lines | run `python3 vault_tools.py normalize --apply` | ✅ |
| `Apollo & the Delivery Engine:1` | vocabulary | frontmatter kind: 'doc' is outside the documented kind vocabulary | use one of ['concept', 'mechanism', 'pattern', 'property', 'reference', 'service', 'type'] or document 'doc' in Taxonomy (Legend) | — |
| `Audit & Lineage:1` | vocabulary | frontmatter kind: 'doc' is outside the documented kind vocabulary | use one of ['concept', 'mechanism', 'pattern', 'property', 'reference', 'service', 'type'] or document 'doc' in Taxonomy (Legend) | — |
| `Data-Level Security Policies:1` | vocabulary | frontmatter kind: 'doc' is outside the documented kind vocabulary | use one of ['concept', 'mechanism', 'pattern', 'property', 'reference', 'service', 'type'] or document 'doc' in Taxonomy (Legend) | — |
| `Ecosystem & Lineage:1` | vocabulary | frontmatter kind: 'doc' is outside the documented kind vocabulary | use one of ['concept', 'mechanism', 'pattern', 'property', 'reference', 'service', 'type'] or document 'doc' in Taxonomy (Legend) | — |
| `Encryption, Network & Compliance:1` | vocabulary | frontmatter kind: 'doc' is outside the documented kind vocabulary | use one of ['concept', 'mechanism', 'pattern', 'property', 'reference', 'service', 'type'] or document 'doc' in Taxonomy (Legend) | — |
| `Identity & Authentication:1` | vocabulary | frontmatter kind: 'doc' is outside the documented kind vocabulary | use one of ['concept', 'mechanism', 'pattern', 'property', 'reference', 'service', 'type'] or document 'doc' in Taxonomy (Legend) | — |
| `Infrastructure Substrate:1` | vocabulary | frontmatter kind: 'doc' is outside the documented kind vocabulary | use one of ['concept', 'mechanism', 'pattern', 'property', 'reference', 'service', 'type'] or document 'doc' in Taxonomy (Legend) | — |
| `Links:1` | vocabulary | frontmatter kind: 'domain' is outside the documented kind vocabulary | use one of ['concept', 'mechanism', 'pattern', 'property', 'reference', 'service', 'type'] or document 'domain' in Taxonomy (Legend) | — |
| `Mandatory Controls & Classification:1` | vocabulary | frontmatter kind: 'doc' is outside the documented kind vocabulary | use one of ['concept', 'mechanism', 'pattern', 'property', 'reference', 'service', 'type'] or document 'doc' in Taxonomy (Legend) | — |
| `Marketplace & Packaging:1` | vocabulary | frontmatter kind: 'doc' is outside the documented kind vocabulary | use one of ['concept', 'mechanism', 'pattern', 'property', 'reference', 'service', 'type'] or document 'doc' in Taxonomy (Legend) | — |
| `Objects:1` | vocabulary | frontmatter kind: 'domain' is outside the documented kind vocabulary | use one of ['concept', 'mechanism', 'pattern', 'property', 'reference', 'service', 'type'] or document 'domain' in Taxonomy (Legend) | — |
| `Ontology & Metadata:1` | vocabulary | frontmatter kind: 'domain' is outside the documented kind vocabulary | use one of ['concept', 'mechanism', 'pattern', 'property', 'reference', 'service', 'type'] or document 'domain' in Taxonomy (Legend) | — |
| `Properties:1` | vocabulary | frontmatter kind: 'domain' is outside the documented kind vocabulary | use one of ['concept', 'mechanism', 'pattern', 'property', 'reference', 'service', 'type'] or document 'domain' in Taxonomy (Legend) | — |
| `Releases, Channels & Promotion:1` | vocabulary | frontmatter kind: 'doc' is outside the documented kind vocabulary | use one of ['concept', 'mechanism', 'pattern', 'property', 'reference', 'service', 'type'] or document 'doc' in Taxonomy (Legend) | — |
| `Roles & Authorization:1` | vocabulary | frontmatter kind: 'doc' is outside the documented kind vocabulary | use one of ['concept', 'mechanism', 'pattern', 'property', 'reference', 'service', 'type'] or document 'doc' in Taxonomy (Legend) | — |

