#!/usr/bin/env python3
"""check_vault.py — deterministic structural gate for the Foundry Obsidian vault.

Parses every note once and reports structural defects with `note:line`, a proposed
fix, and an `auto-fixable?` flag. Designed to be re-run after every change to the
vault or to its generators (build_vault.py / consolidate.py / vault_tools.py).

What makes this correct for THIS vault (and what a naive checker gets wrong):
  - ALIAS-AWARE: a bare [[Action Parameter]] resolves to Actions.md because that doc
    declares "Action Parameter" in its `aliases:`. Ignoring aliases cries wolf.
  - BLOCK-LIST-AWARE: aliases here are multi-line YAML block lists, not inline [a, b].
  - ANCHOR-AWARE: [[Doc#Section]] is only valid if Doc resolves AND has that heading;
    [[Doc#^id]] only if the block id exists.
  - CASE-INSENSITIVE name/alias resolution (Obsidian behaviour).

Checks (each finding carries severity P0..P3):
  broken-link, broken-embed, broken-anchor, name/alias collision, orphan,
  unreachable, frontmatter (parse / duplicate-key / missing-required / empty),
  carrier-B footer conformance, missing/orphan attachment, tag drift, detritus,
  stub/empty note, TODO/FIXME/XXX placeholders.

Usage:
  python3 check_vault.py                 # audit the default vault, markdown report
  python3 check_vault.py /path/to/Vault  # audit a specific vault
  python3 check_vault.py --json          # machine-readable findings
  python3 check_vault.py --quiet         # summary + nonzero exit only

Exit code = number of P0+P1 findings (0 == gate passes).
"""
import os, re, sys, json, argparse
from collections import defaultdict, Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Harvest/_audit/check_vault.py -> repo root is two levels up; vault is repoRoot/Vault.
DEFAULT_VAULT = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "Vault"))

# Intentional, by-design exceptions — do not flag these.
WHITELIST_NO_FM = {"Welcome"}        # the entry note is deliberately frontmatter-less
ROOT_NOTE = "Welcome"                # reachability BFS root
STUB_WORDS = 25                      # body word count below which a note is a "stub"
# Controlled vocabularies from Taxonomy (Legend) / Vault Metadata Standard.
LAYER_VOCAB = {"data", "semantic", "kinetic", "dynamic", "app", "aip",
               "security", "platform", "crosscutting"}
KIND_VOCAB = {"concept", "mechanism", "service", "type", "pattern", "property", "reference"}
CLONE_VOCAB = {"core", "keep", "simplify", "defer", "drop"}
PLACEHOLDER_RE = re.compile(r"\b(TODO|FIXME|XXX|TBD|WIP)\b")
WIKILINK_RE = re.compile(r"(!?)\[\[([^\]]+)\]\]")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
BLOCKID_RE = re.compile(r"(?:^|\s)\^([A-Za-z0-9][\w-]*)\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")

SEV_ORDER = ["P0", "P1", "P2", "P3"]


# --------------------------------------------------------------------------- #
# Frontmatter (dependency-free; needs duplicate-key detection PyYAML hides).
# --------------------------------------------------------------------------- #
def split_frontmatter(text):
    """Return (fm_text, body_text, body_start_line). fm_text is None if absent."""
    if not text.startswith("---\n") and text != "---":
        return None, text, 1
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return None, text, 1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fm = "\n".join(lines[1:i])
            body = "\n".join(lines[i + 1:])
            return fm, body, i + 2  # 1-based line where body starts
    return None, text, 1  # unterminated frontmatter -> treat as no FM (flagged below)


def parse_frontmatter(fm_text):
    """Minimal YAML for this vault's controlled frontmatter.
    Returns (data, ordered_keys, duplicate_keys, errors)."""
    data, order, dups, errors = {}, [], [], []
    if fm_text is None:
        return data, order, dups, errors
    cur_key = None
    for raw in fm_text.split("\n"):
        if not raw.strip():
            continue
        if re.match(r"^[ \t]*-\s+", raw):  # block-list item
            if cur_key is None:
                errors.append(f"list item with no key: {raw.strip()!r}")
                continue
            item = re.sub(r'^[ \t]*-\s+', '', raw).strip().strip('"').strip("'")
            data.setdefault(cur_key, [])
            if not isinstance(data[cur_key], list):
                data[cur_key] = []
            data[cur_key].append(item)
            continue
        m = re.match(r"^([A-Za-z0-9_\-]+):\s*(.*)$", raw)
        if not m:
            errors.append(f"unparsable line: {raw.strip()!r}")
            continue
        key, val = m.group(1), m.group(2).strip()
        if key in data:
            dups.append(key)
        order.append(key)
        cur_key = key
        if val == "" or val == "[]":
            data[key] = [] if val == "[]" else None
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            data[key] = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()] if inner else []
        else:
            data[key] = val.strip().strip('"').strip("'")
    return data, order, dups, errors


# --------------------------------------------------------------------------- #
# Note model
# --------------------------------------------------------------------------- #
class Note:
    def __init__(self, path, vault):
        self.path = path
        self.rel = os.path.relpath(path, vault)
        self.folder = os.path.dirname(self.rel)
        self.name = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding="utf-8") as f:
            self.text = f.read()
        self.fm_text, self.body, self.body_line = split_frontmatter(self.text)
        self.fm, self.fm_order, self.fm_dups, self.fm_errors = parse_frontmatter(self.fm_text)
        self.aliases = self._aliases()
        self.headings = self._headings()      # set of lowercased heading texts
        self.h2_lines = self._h2_lines()      # [(line, text)] for ## sections
        self.blockids = self._blockids()      # set of block ids
        self.links = self._links()            # [(is_embed, target, anchor, line, raw)]
        self.tags = self._tags()              # list of tag strings (fm + inline)
        self.words = len(re.findall(r"\w+", self.body))

    def _aliases(self):
        a = self.fm.get("aliases")
        if a is None:
            return []
        return [a] if isinstance(a, str) else list(a)

    def _headings(self):
        hs = set()
        for ln in self.text.split("\n"):
            m = HEADING_RE.match(ln)
            if m:
                hs.add(m.group(2).strip().lower())
        return hs

    def _h2_lines(self):
        out = []
        for i, ln in enumerate(self.text.split("\n"), 1):
            m = HEADING_RE.match(ln)
            if m and len(m.group(1)) == 2:
                out.append((i, m.group(2).strip()))
        return out

    def _blockids(self):
        ids = set()
        for ln in self.text.split("\n"):
            m = BLOCKID_RE.search(ln)
            if m:
                ids.add(m.group(1).lower())
        return ids

    def _links(self):
        out, in_fence = [], False
        for i, ln in enumerate(self.text.split("\n"), 1):
            if FENCE_RE.match(ln):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for m in WIKILINK_RE.finditer(ln):
                is_embed = m.group(1) == "!"
                inner = m.group(2)
                target_part = inner.split("|", 1)[0].strip()
                note_part, anchor = (target_part.split("#", 1) + [None])[:2] \
                    if "#" in target_part else (target_part, None)
                out.append((is_embed, note_part.strip(), (anchor.strip() if anchor else None), i, m.group(0)))
        return out

    def _tags(self):
        tags = []
        ft = self.fm.get("tags")
        if isinstance(ft, list):
            tags += ft
        elif isinstance(ft, str):
            tags.append(ft)
        # inline tags, but not '#' inside wikilinks/code
        in_fence = False
        for ln in self.text.split("\n"):
            if FENCE_RE.match(ln):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            stripped = WIKILINK_RE.sub("", ln)
            for m in re.finditer(r"(?:^|\s)#([A-Za-z][\w/\-]*)", stripped):
                tags.append(m.group(1))
        return tags


# --------------------------------------------------------------------------- #
# Audit
# --------------------------------------------------------------------------- #
class Finding:
    def __init__(self, sev, cat, note, line, msg, fix, auto):
        self.sev, self.cat, self.note, self.line = sev, cat, note, line
        self.msg, self.fix, self.auto = msg, fix, auto

    def loc(self):
        return f"{self.note}:{self.line}" if self.line else self.note

    def as_dict(self):
        return dict(severity=self.sev, category=self.cat, location=self.loc(),
                    message=self.msg, fix=self.fix, auto_fixable=self.auto)


def collect_md(vault):
    notes, junk = [], []
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d != ".obsidian"]
        for fn in files:
            if not fn.endswith(".md"):
                continue
            p = os.path.join(root, fn)
            if os.sep + ".junk" + os.sep in p or "/.junk/" in p.replace(os.sep, "/"):
                junk.append(p)
            else:
                notes.append(p)
    return sorted(notes), sorted(junk)


def list_nonmd(vault):
    out = []
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d != ".obsidian"]
        for fn in files:
            if fn.endswith(".md"):
                continue
            out.append(os.path.relpath(os.path.join(root, fn), vault))
    return sorted(out)


def build_index(notes):
    """name(lower) -> set(note.name). Includes basenames and aliases."""
    idx = defaultdict(set)
    by_name = {}
    for n in notes:
        by_name[n.name] = n
        idx[n.name.lower()].add(n.name)
        for a in n.aliases:
            idx[a.lower()].add(n.name)
    return idx, by_name


def resolve(note_part, anchor, idx, by_name, notes_by_relkey):
    """Return (resolved_note_name_or_None, reason)."""
    key = note_part.strip()
    if key == "":
        return ("__SELF__", None)  # same-file anchor
    # path-style target (with / or trailing .md)
    cand = key
    if cand.lower().endswith(".md"):
        cand = cand[:-3]
    lk = cand.lower()
    if lk in idx:
        targets = idx[lk]
        if len(targets) == 1:
            return (next(iter(targets)), None)
        return (None, f"ambiguous (resolves to {sorted(targets)})")
    # try final path component
    if "/" in cand:
        tail = cand.split("/")[-1].lower()
        if tail in idx and len(idx[tail]) == 1:
            return (next(iter(idx[tail])), None)
        # try full relpath match
        if lk in notes_by_relkey:
            return (notes_by_relkey[lk], None)
    return (None, "unresolved")


def audit(vault):
    note_paths, junk_paths = collect_md(vault)
    notes = [Note(p, vault) for p in note_paths]
    idx, by_name = build_index(notes)
    notes_by_relkey = {os.path.splitext(n.rel)[0].lower().replace(os.sep, "/"): n.name for n in notes}
    findings = []
    inbound = Counter()
    graph = defaultdict(set)

    def add(sev, cat, note, line, msg, fix, auto):
        findings.append(Finding(sev, cat, note, line, msg, fix, auto))

    # ---- name / alias collisions -----------------------------------------
    for low, targets in sorted(idx.items()):
        if len(targets) > 1:
            add("P1", "collision", sorted(targets)[0], None,
                f"name/alias '{low}' resolves to {len(targets)} notes: {sorted(targets)}",
                "make the alias unique to one note (edit the consolidated doc's aliases:)", False)

    # ---- per-note checks --------------------------------------------------
    nonmd = set(list_nonmd(vault))
    referenced_nonmd = set()
    for n in notes:
        # frontmatter
        if n.fm_text is None and n.name not in WHITELIST_NO_FM:
            add("P1", "frontmatter", n.name, 1,
                "no YAML frontmatter", "add frontmatter per Vault Metadata Standard", False)
        for d in sorted(set(n.fm_dups)):
            add("P1", "frontmatter", n.name, 1, f"duplicate frontmatter key '{d}'",
                "remove the duplicate key", True)
        for e in n.fm_errors:
            add("P1", "frontmatter", n.name, 1, f"frontmatter parse error: {e}",
                "fix the YAML", False)

        # Carrier classification (per Vault Metadata Standard). The discriminator is the
        # BODY shape, not the presence of a layer: scalar — carrier-B docs are explicitly
        # allowed an optional doc-level layer/kind/clone in addition to aliases+updated.
        #   carrier B = multi-concept doc in 04–10 with ## concept sections (+ *clone:* footers)
        #   carrier A = single-disposition note (02, 03, atomic) with full typed frontmatter
        is_hub = "hub" in (n.tags or [])
        in_0410 = re.match(r"^(0[4-9]|10) ", n.folder) is not None
        is_carrier_b = (not is_hub) and in_0410 and len(n.h2_lines) >= 1
        is_carrier_a = (not is_hub) and (not is_carrier_b) \
            and n.name not in WHITELIST_NO_FM and n.fm_text is not None

        if is_carrier_a:
            for k in ("tags", "layer", "kind", "clone", "source", "updated"):
                if k not in n.fm or n.fm.get(k) in (None, ""):
                    add("P2", "frontmatter", n.name, 1,
                        f"carrier-A note missing/empty required key '{k}'",
                        f"add '{k}:' per the Standard", False)
        elif is_carrier_b:
            for k in ("aliases", "updated"):
                if k not in n.fm:
                    add("P2", "frontmatter", n.name, 1,
                        f"carrier-B doc missing required key '{k}'",
                        f"add '{k}:' per the Standard", False)

        # Vocabulary conformance for typed scalars (Taxonomy / Standard).
        for key, vocab in (("layer", LAYER_VOCAB), ("kind", KIND_VOCAB), ("clone", CLONE_VOCAB)):
            v = n.fm.get(key)
            if isinstance(v, str) and v and v not in vocab:
                add("P3", "vocabulary", n.name, 1,
                    f"frontmatter {key}: '{v}' is outside the documented {key} vocabulary",
                    f"use one of {sorted(vocab)} or document '{v}' in Taxonomy (Legend)", False)

        # Mixed-disposition flattening: a carrier-A consolidated doc whose inline *Clone: X*
        # sub-notes disagree with the single file-level clone (per-concept queryability lost).
        if is_carrier_a and isinstance(n.fm.get("clone"), str):
            inline = set(m.lower() for m in re.findall(r"\*[Cc]lone:\s*([A-Za-z]+)", n.body))
            extra = inline - {n.fm["clone"].lower()}
            if extra:
                add("P2", "disposition", n.name, 1,
                    f"file-level clone: {n.fm['clone']} but sub-concepts are also "
                    f"{sorted(extra)} — per-concept disposition is not tag-queryable",
                    "split doc or add per-section #clone tags (vault_tools normalize covers 04–10 only)", False)

        # carrier-B footer conformance: count ## sections vs footer / tag lines
        if is_carrier_b:
            n_sections = len(n.h2_lines)
            n_footers = len(re.findall(r"^\*clone:.*\*\s*$", n.body, re.M))
            n_taglines = len(re.findall(r"^#clone/\S+\s+#kind/\S+\s+#layer/\S+", n.body, re.M))
            if n_sections and n_footers < n_sections:
                add("P2", "footer", n.name, 1,
                    f"{n_sections} ## sections but {n_footers} footer lines "
                    f"(*clone: …*) — {n_sections - n_footers} unstandardized",
                    "run `python3 vault_tools.py normalize --apply`", True)
            if n_sections and n_taglines < n_sections:
                add("P3", "footer", n.name, 1,
                    f"{n_sections} ## sections but {n_taglines} inline #clone tag lines",
                    "run `python3 vault_tools.py normalize --apply`", True)

        # links / embeds / anchors
        for is_embed, note_part, anchor, line, raw in n.links:
            tgt, reason = resolve(note_part, anchor, idx, by_name, notes_by_relkey)
            # attachment?
            if note_part.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg",
                                           ".pdf", ".webp", ".mp4", ".mov", ".xlsx", ".csv")):
                referenced_nonmd.add(note_part.lstrip("./"))
                if note_part.lstrip("./") not in nonmd:
                    add("P1", "attachment", n.name, line,
                        f"embed/link to missing attachment '{note_part}' ({raw})",
                        "add the file or remove the reference", False)
                continue
            if tgt == "__SELF__":
                target_note = n
            elif tgt is None:
                add("P1", "broken-embed" if is_embed else "broken-link", n.name, line,
                    f"{'embed' if is_embed else 'link'} {raw} -> {reason}",
                    "fix the target name or add an alias on the intended note", False)
                continue
            else:
                graph[n.name].add(tgt)
                if tgt != n.name:
                    inbound[tgt] += 1
                target_note = by_name[tgt]
            # anchor validation
            if anchor:
                if anchor.startswith("^"):
                    if anchor[1:].lower() not in target_note.blockids:
                        add("P2", "broken-anchor", n.name, line,
                            f"block ref {raw} -> ^{anchor[1:]} not found in {target_note.name}",
                            "fix the block id", False)
                else:
                    if anchor.lower() not in target_note.headings:
                        add("P1", "broken-anchor", n.name, line,
                            f"anchor {raw} -> heading '#{anchor}' not in {target_note.name}",
                            "fix the heading text or the link", False)

        # detritus inside a real note
        for i, ln in enumerate(n.body.split("\n"), n.body_line):
            if PLACEHOLDER_RE.search(WIKILINK_RE.sub("", ln)):
                add("P3", "placeholder", n.name, i,
                    f"placeholder marker in prose: {ln.strip()[:70]!r}",
                    "resolve or remove the placeholder", False)

        # stubs / empty
        if n.words == 0 and n.name not in WHITELIST_NO_FM:
            add("P2", "stub", n.name, 1, "empty note (0 words of body)",
                "fold into a consolidated doc or remove", False)
        elif 0 < n.words < STUB_WORDS and n.name not in WHITELIST_NO_FM and not is_hub:
            add("P3", "stub", n.name, 1, f"thin note ({n.words} words < {STUB_WORDS})",
                "expand or consolidate", False)

    # ---- orphans / reachability ------------------------------------------
    # BFS from the root note over resolved links.
    reachable, frontier = set(), [ROOT_NOTE] if ROOT_NOTE in by_name else []
    while frontier:
        cur = frontier.pop()
        if cur in reachable:
            continue
        reachable.add(cur)
        frontier.extend(graph.get(cur, ()))
    for n in notes:
        if n.name == ROOT_NOTE:
            continue
        if inbound[n.name] == 0:
            sev = "P2"
            add(sev, "orphan", n.name, 1,
                "zero inbound links (not linked from any note)",
                "link it from its layer/invariant hub or a sibling", False)
        elif n.name not in reachable:
            add("P2", "unreachable", n.name, 1,
                f"has {inbound[n.name]} inbound link(s) but not reachable from {ROOT_NOTE}",
                "add a path from a hub", False)

    # ---- attachments not referenced --------------------------------------
    for f in sorted(nonmd):
        base = os.path.basename(f)
        if base in ("",) or f in referenced_nonmd or base in referenced_nonmd:
            continue
        if base == ".DS_Store":
            add("P2", "detritus", f, None, "committed OS cruft (.DS_Store)",
                "git rm --cached and add to .gitignore (already ignored at Vault/.DS_Store)", True)
        # .obsidian is skipped by the walker; anything else is an unreferenced asset
        else:
            add("P3", "attachment", f, None, "file in vault referenced by nothing",
                "remove if unused", False)

    # ---- detritus: .junk -------------------------------------------------
    for p in junk_paths:
        add("P2", "detritus", os.path.relpath(p, vault), None,
            "scratch/capability-test file under .junk/ (gitignored but present on disk)",
            "delete from working tree (rm -rf Vault/.junk)", True)

    # ---- tag drift -------------------------------------------------------
    all_tags = Counter()
    for n in notes:
        for t in n.tags:
            all_tags[t] += 1
    lower_groups = defaultdict(set)
    for t in all_tags:
        lower_groups[t.lower()].add(t)
    for low, variants in sorted(lower_groups.items()):
        if len(variants) > 1:
            add("P3", "tag", "(tags)", None,
                f"tag casing drift: {sorted(variants)} differ only by case",
                "pick one casing", True)

    return dict(vault=vault, notes=notes, junk=junk_paths, nonmd=sorted(nonmd),
                findings=findings, idx=idx, inbound=inbound, reachable=reachable,
                all_tags=all_tags)


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
def emit_markdown(res):
    notes = res["notes"]
    F = res["findings"]
    by_sev = Counter(f.sev for f in F)
    by_cat = Counter(f.cat for f in F)
    L = []
    L.append("# Structural audit — check_vault.py")
    L.append("")
    L.append(f"- vault: `{res['vault']}`")
    L.append(f"- notes parsed: **{len(notes)}**  ·  junk files: {len(res['junk'])}  ·  "
             f"non-md files: {len(res['nonmd'])}")
    total_links = sum(len(n.links) for n in notes)
    total_aliases = sum(len(n.aliases) for n in notes)
    L.append(f"- wikilinks/embeds scanned: **{total_links}**  ·  declared aliases: **{total_aliases}**  ·  "
             f"distinct resolvable names: {len(res['idx'])}")
    L.append(f"- findings: **{len(F)}**  (" +
             ", ".join(f"{s} {by_sev.get(s,0)}" for s in SEV_ORDER) + ")")
    L.append("")
    L.append("| Category | Count |")
    L.append("|---|--:|")
    for c, n in by_cat.most_common():
        L.append(f"| {c} | {n} |")
    L.append("")
    for sev in SEV_ORDER:
        items = [f for f in F if f.sev == sev]
        if not items:
            continue
        L.append(f"## {sev} ({len(items)})")
        L.append("")
        L.append("| location | category | finding | proposed fix | auto-fix? |")
        L.append("|---|---|---|---|:--:|")
        for f in sorted(items, key=lambda x: (x.cat, x.note, x.line or 0)):
            msg = f.msg.replace("|", "\\|")
            fix = f.fix.replace("|", "\\|")
            L.append(f"| `{f.loc()}` | {f.cat} | {msg} | {fix} | {'✅' if f.auto else '—'} |")
        L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("vault", nargs="?", default=DEFAULT_VAULT, help="path to the Obsidian vault")
    ap.add_argument("--json", action="store_true", help="emit findings as JSON")
    ap.add_argument("--quiet", action="store_true", help="summary line only")
    a = ap.parse_args()
    vault = os.path.abspath(a.vault)
    if not os.path.isdir(vault):
        print(f"vault not found: {vault}", file=sys.stderr)
        return 2
    res = audit(vault)
    F = res["findings"]
    hard = sum(1 for f in F if f.sev in ("P0", "P1"))
    if a.json:
        print(json.dumps([f.as_dict() for f in F], indent=2))
    elif a.quiet:
        by_sev = Counter(f.sev for f in F)
        print(f"{len(res['notes'])} notes · {len(F)} findings (" +
              ", ".join(f"{s} {by_sev.get(s,0)}" for s in SEV_ORDER) + f") · gate={'PASS' if hard==0 else 'FAIL'}")
    else:
        print(emit_markdown(res))
    return hard


if __name__ == "__main__":
    sys.exit(main())
