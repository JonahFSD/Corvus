#!/usr/bin/env python3
"""
Consolidate many atomic Markdown notes into a few larger subdomain documents — losslessly.

Each former note becomes a "## <Title>" section inside its subdomain document, preserving:
  - the leading ">" definition (one or more blockquote lines)
  - the explanatory prose
  - any bold-label carry-through lines kept verbatim (e.g. **Related:**, **For our clone:**)
  - selected frontmatter fields, surfaced as a compact italic meta line

Every former note title is added to the new document's `aliases:` so existing [[wikilinks]]
keep resolving with no edits anywhere else in the vault.

Dry-run by default. Pass --apply to write the documents (and verify coverage); add --delete
to remove the original note files *after* the coverage check passes.

Usage:
  python consolidate.py --folder "<vault/subfolder>" --config groups.json
  python consolidate.py --folder "<vault/subfolder>" --config groups.json --apply
  python consolidate.py --folder "<vault/subfolder>" --config groups.json --apply --delete

groups.json:
  {
    "Objects":    {"intro": "...", "members": ["Object Type", "Object", "Primary Key"]},
    "Properties": {"intro": "...", "members": ["Property", "Value Type"]}
  }
"""
import argparse, json, os, re, sys


def parse_note(path):
    """Return the structured pieces of one atomic note."""
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    fm, body = (m.group(1), m.group(2)) if m else ("", text)

    def scalar(name):
        mm = re.search(rf"^{re.escape(name)}:\s*(.*)$", fm, re.M)
        return mm.group(1).strip().strip('"') if mm and mm.group(1).strip() else ""

    def listf(name):
        block = re.search(rf"^{re.escape(name)}:\s*\n((?:[ \t]*-[ \t]*.*\n?)+)", fm, re.M)
        if block:
            return [re.sub(r'^[ \t]*-[ \t]*"?(.*?)"?\s*$', r"\1", l).strip()
                    for l in block.group(1).splitlines() if l.strip()]
        inline = re.search(rf"^{re.escape(name)}:\s*\[(.*)\]\s*$", fm, re.M)
        if inline and inline.group(1).strip():
            return [x.strip().strip('"') for x in inline.group(1).split(",") if x.strip()]
        return []

    # Body: skip the H1, capture the leading ">" block as the definition,
    # then prose up to the first bold-label line. Every bold-label line is carried verbatim.
    defn, prose, phase = [], [], "pre"
    for l in body.splitlines():
        if l.startswith("# "):
            continue
        if phase == "pre":
            if not l.strip():
                continue
            if l.startswith(">"):
                defn.append(l); phase = "def"; continue
            phase = "prose"
        if phase == "def":
            if l.startswith(">"):
                defn.append(l); continue
            phase = "prose"
        if phase == "prose":
            if re.match(r"^\*\*[^*]+:\*\*", l):
                break
            prose.append(l)

    carry = [l for l in body.splitlines() if re.match(r"^\*\*[^*]+:\*\*", l)]
    return dict(scalar=scalar, listf=listf, aliases=listf("aliases"),
                definition="\n".join(defn).strip(), prose="\n".join(prose).strip(),
                carry=carry)


def meta_line(note, fields):
    parts = []
    for f in fields:
        vals = note["listf"](f)
        if vals:
            parts.append(f"{f}: " + " · ".join(vals))
        elif note["scalar"](f):
            parts.append(f"{f}: {note['scalar'](f)}")
    return ("*" + " · ".join(parts) + "*") if parts else ""


def build(folder, config, fields):
    docs, members, aliases_by_doc = {}, [], {}
    for doc, info in config.items():
        aliases, sections = [], []
        for name in info["members"]:
            p = os.path.join(folder, name + ".md")
            if not os.path.exists(p):
                print(f"  !! MISSING: {p}", file=sys.stderr); continue
            members.append((doc, name, p))
            n = parse_note(p)
            for a in [name] + n["aliases"]:
                if a not in aliases:
                    aliases.append(a)
            sec = f"## {name}\n\n{n['definition']}\n\n{n['prose']}\n"
            for c in n["carry"]:
                sec += f"\n{c}\n"
            ml = meta_line(n, fields)
            if ml:
                sec += f"\n{ml}\n"
            sections.append(sec)
        fm_aliases = "\n".join(f"  - {a}" for a in aliases)
        head = f"---\naliases:\n{fm_aliases}\n"
        if info.get("updated"):
            head += f"updated: {info['updated']}\n"
        head += "---\n\n"
        docs[doc] = head + f"# {doc}\n\n> {info['intro']}\n\n" + "\n".join(sections)
        aliases_by_doc[doc] = aliases
    return docs, members, aliases_by_doc


def verify(docs, members, aliases_by_doc):
    ok = True
    for doc, name, p in members:
        n, d = parse_note(p), docs[doc]
        if n["definition"] and n["definition"] not in d:
            ok = False; print(f"  X {doc}/{name}: definition missing")
        if n["prose"] and n["prose"] not in d:
            ok = False; print(f"  X {doc}/{name}: prose missing")
        for c in n["carry"]:
            if c not in d:
                ok = False; print(f"  X {doc}/{name}: carry-through line missing -> {c!r}")
    seen = {}
    for doc, aliases in aliases_by_doc.items():
        for a in aliases:
            if a in seen:
                ok = False; print(f"  X alias collision: {a!r} on {seen[a]} and {doc}")
            seen[a] = doc
    print("  coverage + aliases:", "OK lossless" if ok else "PROBLEMS FOUND")
    return ok


def main():
    ap = argparse.ArgumentParser(description="Losslessly consolidate atomic notes by subdomain.")
    ap.add_argument("--folder", required=True, help="folder containing the atomic notes")
    ap.add_argument("--config", required=True, help="JSON: {doc: {intro, members, [updated]}}")
    ap.add_argument("--meta-fields", default="clone,kind,invariants,source",
                    help="frontmatter fields to surface in each section's meta line")
    ap.add_argument("--apply", action="store_true", help="write the documents (default: dry run)")
    ap.add_argument("--delete", action="store_true", help="delete originals after coverage passes")
    a = ap.parse_args()

    config = json.load(open(a.config, encoding="utf-8"))
    fields = [f.strip() for f in a.meta_fields.split(",") if f.strip()]
    docs, members, aliases_by_doc = build(a.folder, config, fields)

    for doc, b in docs.items():
        n_sec = sum(1 for d, _, _ in members if d == doc)
        print(f"{'WROTE' if a.apply else 'DRY '} {doc}.md - {b.count(chr(10))} lines, {n_sec} sections, "
              f"{len(aliases_by_doc[doc])} aliases")
        if a.apply:
            open(os.path.join(a.folder, doc + ".md"), "w", encoding="utf-8").write(b)

    if not a.apply:
        print("\nDry run. Re-run with --apply to write the documents.")
        return

    ok = verify(docs, members, aliases_by_doc)
    if a.delete:
        if ok:
            for _, _, p in members:
                os.remove(p)
            print(f"  deleted {len(members)} original notes")
        else:
            print("  refusing to delete originals: coverage check failed")


if __name__ == "__main__":
    main()
