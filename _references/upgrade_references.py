"""Upgrade bare reference entries to structured citations in front matter.

Reads citations.json (the agent-normalised {url: {title, author, date,
type, isPartOf, publisher}} map) and rewrites each post's references:
block, replacing bare `- url # label` lines with structured mappings in
the house key order. DOI entries and URLs without normalised citations
keep their bare form (the signposting plugin enriches DOIs itself).
Only the references block changes; the rest of the file is untouched.
Run from the blog root:

    uv run --with pyyaml _references/upgrade_references.py --dry-run
    uv run --with pyyaml _references/upgrade_references.py
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(os.path.dirname(HERE), "_posts")

FRONT_MATTER_RE = re.compile(r"\A---\n(.*?\n)---\n", re.DOTALL)
REFERENCES_BLOCK_RE = re.compile(
    r"^references:[ \t]*\n((?:(?:- |  ).*\n?)*)", re.MULTILINE
)
BARE_LINE_RE = re.compile(r"\A- (https?://\S+)(?: # (.*))?\Z")
DOI_URL_RE = re.compile(r"\Ahttps?://(dx\.)?doi\.org/", re.IGNORECASE)

# House key order, matching the hand-written structured entries.
KEY_ORDER = ["author", "date", "title", "type", "publisher", "url", "isPartOf"]


def citation_entry_yaml(citation):
    """One structured `- key: value` references entry in house key order.

    citation maps a subset of KEY_ORDER to values (author may be a string
    or list; isPartOf a mapping with name/type/url). Values are emitted
    through YAML so quoting is always safe. The url key is required.
    """
    import yaml

    ordered = {
        key: citation[key] for key in KEY_ORDER if citation.get(key)
    }
    if "url" not in ordered:
        raise ValueError("citation entry needs a url")
    return yaml.safe_dump(
        [ordered],
        allow_unicode=True,
        sort_keys=False,
        width=1000,
        default_flow_style=False,
    )


def upgrade_references_block(text, citations):
    """Rewrite the references block, upgrading bare lines with citations.

    citations maps url -> citation mapping (without "url"; it is added).
    Bare lines whose URL is a DOI or has no citation are kept verbatim,
    as are already-structured entries. Returns the new text, or the
    original when there is nothing to change. Raises ValueError when the
    result's front matter no longer parses as YAML or the number of
    reference entries changes.
    """
    import yaml

    m = FRONT_MATTER_RE.match(text)
    if not m:
        return text
    fm = m.group(1)
    block = REFERENCES_BLOCK_RE.search(fm)
    if not block:
        return text

    old_lines = block.group(1).splitlines()
    entry_count = sum(1 for line in old_lines if line.startswith("- "))
    out_lines = []
    changed = False
    for line in old_lines:
        bare = BARE_LINE_RE.match(line)
        url = bare.group(1) if bare else None
        if url and not DOI_URL_RE.match(url) and citations.get(url):
            entry = dict(citations[url])
            entry["url"] = url
            out_lines.append(citation_entry_yaml(entry).rstrip("\n"))
            changed = True
        else:
            out_lines.append(line)
    if not changed:
        return text

    new_fm = (
        fm[: block.start(1)] + "\n".join(out_lines) + "\n" + fm[block.end(1):]
    )
    new_text = text[: m.start(1)] + new_fm + text[m.end(1):]
    try:
        parsed = yaml.safe_load(FRONT_MATTER_RE.match(new_text).group(1))
    except yaml.YAMLError as exc:
        raise ValueError(f"front matter no longer parses: {exc}")
    if len(parsed.get("references") or []) != entry_count:
        raise ValueError("reference entry count changed")
    return new_text


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--citations", default=os.path.join(HERE, "citations.json"))
    parser.add_argument("--posts-dir", default=POSTS_DIR)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    with open(args.citations, encoding="utf-8") as f:
        citations = json.load(f)

    changed = failed = 0
    for name in sorted(os.listdir(args.posts_dir)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(args.posts_dir, name)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        try:
            new = upgrade_references_block(text, citations)
        except ValueError as exc:
            print(f"FAILED {name}: {exc}", file=sys.stderr)
            failed += 1
            continue
        if new == text:
            continue
        changed += 1
        if args.dry_run:
            print(f"would upgrade {name}")
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)

    label = "would upgrade" if args.dry_run else "upgraded"
    print(f"{label}: {changed}; failed: {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
