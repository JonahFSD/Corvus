#!/usr/bin/env python3
"""vault_tools.py — enforce the Vault Metadata Standard and emit generated views.

Three subcommands:

  normalize   Standardize the per-section metadata footer in the multi-concept
              ("H2 section") docs (folders 04-10) to ONE canonical form, and append an
              Obsidian-indexed inline-tag line so every concept is queryable by
              `#clone/..`, `#kind/..`, `#layer/..` with no plugin. Idempotent.

  views       (Re)generate the "Build Matrix (Layer x Disposition)" note from the
              canonical concept data in build_vault.py.

  check       Gate (read-only): run the structural checker, then assert the Build
              View's headline counts still match the canonical concept dispositions.
              Exits non-zero on drift. Wire into pre-commit / CI.

normalize and views are DRY-RUN by default (pass --apply to write); check is read-only.

Pipeline:  python3 build_vault.py            # emit atomic graph (now tag-aware)
           python3 Skills/note-consolidator/scripts/consolidate.py ...   # consolidate
           python3 vault_tools.py normalize --apply                      # standardize
           python3 vault_tools.py views --apply                          # refresh views

See `Vault/00 Maps & Views/Vault Metadata Standard`.
"""
import os, re, sys, glob
from collections import Counter, defaultdict

HERE  = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.join(HERE, "Vault")

# Folders whose docs use H2 sections with per-section footers
# (these are exactly the docs the Build View links to via #section anchors).
FOLDER_LAYER = {
    "04 Ontology - Semantic":  "semantic",
    "05 Ontology - Kinetic":   "kinetic",
    "06 Ontology - Dynamic":   "dynamic",
    "07 App-Building":         "app",
    "08 AIP":                  "aip",
    "09 Security & Governance":"security",
    "10 Platform & Ecosystem": "platform",
}

FOOTER_RE  = re.compile(r'^\*clone:.*\*[ \t]*$', re.M)   # a per-section meta footer line
PRIOR_TAGS = re.compile(r'\n[ \t]*#clone/\S+[^\n]*(?=\n|$)')  # tag lines we added before
KEY_RE     = re.compile(r'^(clone|kind|layer|invariants|source):\s*(.*)$')


def parse_footer(line):
    """Split '*clone: keep · kind: x · invariants: [[A]] · [[B]] · source: ...*' into a dict,
    re-merging ' · ' separators that belong inside the invariants list."""
    inner = line.strip().strip('*').strip()
    seg, cur = {}, None
    for part in inner.split(' · '):
        m = KEY_RE.match(part)
        if m:
            cur = m.group(1)
            seg[cur] = m.group(2).strip()
        elif cur:                       # continuation of a multi-value field (invariants)
            seg[cur] += ' · ' + part.strip()
    return seg


def canonical(seg, layer):
    """Return (footer_line, tag_line) in canonical order: clone · kind · layer · invariants · source."""
    clone = seg.get('clone', '').strip()
    kind  = seg.get('kind', '').strip()
    fields = [f"clone: {clone}", f"kind: {kind}", f"layer: {layer}"]
    if seg.get('invariants'):
        fields.append(f"invariants: {seg['invariants'].strip()}")
    fields.append(f"source: {seg.get('source', '').strip()}")
    footer  = "*" + " · ".join(fields) + "*"
    tagline = f"#clone/{clone} #kind/{kind} #layer/{layer}"
    return footer, tagline


def normalize_text(text, layer):
    text = PRIOR_TAGS.sub('', text)             # drop previously-added tag lines (idempotent)
    n = [0]
    def repl(m):
        n[0] += 1
        footer, tag = canonical(parse_footer(m.group(0)), layer)
        return footer + "\n" + tag
    text = FOOTER_RE.sub(repl, text)
    return text, n[0]


def cmd_normalize(apply):
    total_files = total_secs = 0
    for folder, layer in FOLDER_LAYER.items():
        for path in sorted(glob.glob(os.path.join(VAULT, folder, "*.md"))):
            old = open(path, encoding="utf-8").read()
            new, n = normalize_text(old, layer)
            if n and new != old:
                total_files += 1; total_secs += n
                rel = os.path.relpath(path, VAULT)
                print(f"  {'WROTE' if apply else 'would update'}: {rel}  ({n} sections)")
                if apply:
                    open(path, "w", encoding="utf-8").write(new)
    print(f"\n{'Applied' if apply else 'DRY-RUN'} — {total_secs} sections across {total_files} files."
          + ("" if apply else "  Re-run with --apply to write."))


def cmd_views(apply):
    sys.path.insert(0, HERE)
    import build_vault as bv
    DISPS  = ["core", "keep", "simplify", "defer", "drop"]
    LAYERS = ["crosscutting", "data", "semantic", "kinetic", "dynamic",
              "app", "aip", "security", "platform"]
    LABEL  = {"crosscutting":"Cross-cutting","data":"Data Foundation","semantic":"Ontology — Semantic",
              "kinetic":"Ontology — Kinetic","dynamic":"Ontology — Dynamic","app":"App-Building",
              "aip":"AIP","security":"Security & Governance","platform":"Platform & Ecosystem"}
    grid = defaultdict(Counter)
    for c in bv.CONCEPTS:
        grid[c["L"]][bv.disposition(c)] += 1
    col_tot = Counter(); grand = 0
    rows = []
    for L in LAYERS:
        cells = [grid[L].get(d, 0) for d in DISPS]
        tot = sum(cells); grand += tot
        for d, v in zip(DISPS, cells): col_tot[d] += v
        rows.append((LABEL[L], cells, tot))

    out  = "---\ntags:\n  - hub\n  - index\n  - generated\nupdated: 2026-06-14\n---\n\n"
    out += "# Build Matrix (Layer × Disposition)\n\n"
    out += "> Generated by `vault_tools.py views`. Counts are **atomic concepts** (the canonical "
    out += f"{grand} in `build_vault.py`), cross-tabbed by layer and `clone` disposition. "
    out += "The [[Build View — What We're Cloning]] shows the consolidated section view (fewer rows, "
    out += "because consolidation collapses sub-concepts into shared section links). Filter live via "
    out += "`#clone/keep`, `#layer/semantic`, etc. — see [[Vault Metadata Standard]].\n\n"
    out += "| Layer | core | keep | simplify | defer | drop | **Σ** |\n|---|--:|--:|--:|--:|--:|--:|\n"
    for label, cells, tot in rows:
        out += f"| {label} | " + " | ".join(str(x) if x else "·" for x in cells) + f" | **{tot}** |\n"
    out += ("| **Σ** | " + " | ".join(f"**{col_tot[d]}**" for d in DISPS) + f" | **{grand}** |\n\n")
    out += "**Build set = core + keep** ("
    out += f"{col_tot['core'] + col_tot['keep']} concepts). **Deferred** ({col_tot['defer']}) is the "
    out += "post-MVP surface; **drop** (" + str(col_tot['drop']) + ") is Palantir-scale machinery.\n\n"
    out += "---\n\n[[Foundry — Home (MOC)|← Home]] · [[Build View — What We're Cloning]] · [[Taxonomy (Legend)]]\n"

    dest = os.path.join(VAULT, "00 Maps & Views", "Build Matrix (Layer × Disposition).md")
    print("\n" + out)
    if apply:
        open(dest, "w", encoding="utf-8").write(out)
        print(f"WROTE: {os.path.relpath(dest, VAULT)}")
    else:
        print("DRY-RUN — re-run with --apply to write.")


def cmd_check():
    """Gate (read-only): run the structural checker, then assert the Build View's
    headline counts still match the canonical concept dispositions in build_vault.py.
    Exit non-zero on any drift."""
    import subprocess
    sys.path.insert(0, HERE)
    import build_vault as bv
    ok = True
    cv = os.path.join(HERE, "Harvest", "_audit", "check_vault.py")
    if os.path.exists(cv):
        rc = subprocess.call([sys.executable, cv, "--quiet"])
        print(f"structural gate (check_vault.py): {'PASS' if rc == 0 else 'FAIL'}")
        ok = ok and rc == 0
    canon = Counter(bv.disposition(c) for c in bv.CONCEPTS)
    expect = {"Core": canon.get("core", 0), "Keep": canon.get("keep", 0),
              "Simplify": canon.get("simplify", 0), "Defer": canon.get("defer", 0),
              "Drop": canon.get("drop", 0)}
    bvp  = os.path.join(VAULT, "00 Maps & Views", "Build View — What We're Cloning.md")
    text = open(bvp, encoding="utf-8").read()
    for label, exp in expect.items():
        m = re.search(r"^##\s*" + re.escape(label) + r"\b.*\((\d+)\)\s*$", text, re.M)
        got = int(m.group(1)) if m else None
        if got != exp:
            ok = False
        print(f"  Build View '{label}': header={got} canonical={exp} "
              f"[{'ok' if got == exp else 'MISMATCH'}]")
    print(f"  canonical build set (core + keep) = {expect['Core'] + expect['Keep']}")
    print("GATE:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    cmd = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else ""
    if cmd == "normalize":
        cmd_normalize(apply)
    elif cmd == "views":
        cmd_views(apply)
    elif cmd == "check":
        sys.exit(cmd_check())
    else:
        print(__doc__)
        sys.exit(1)
