"""Apply reviewed category assignments to post front matter.

Rewrites ONLY the `categories:` block of each post named in mapping.yml,
using targeted text manipulation (never YAML re-serialization, which would
mangle comments, smart quotes, and unquoted timestamps elsewhere in the
front matter). Run from the blog root:

    uv run --with pyyaml _categorization/apply_categories.py --validate
    uv run --with pyyaml _categorization/apply_categories.py --dry-run
    uv run --with pyyaml _categorization/apply_categories.py
    uv run --with pyyaml _categorization/apply_categories.py --check
"""

import argparse
import difflib
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

FRONT_MATTER_RE = re.compile(r"\A---\n(.*?\n)---\n", re.DOTALL)
# The key line (block list, inline [] or scalar) plus any column-0 "- " items.
# The item pattern requires a leading dash, so a following key such as
# `comments: []` can never be swallowed.
CATEGORIES_RE = re.compile(r"^categories:[^\n]*\n(?:[ \t]*-[ \t][^\n]*\n)*", re.MULTILINE)


def _front_matter(text):
    if "\r" in text:
        raise ValueError("CRLF/CR line endings; refusing to edit")
    m = FRONT_MATTER_RE.match(text)
    if not m:
        raise ValueError("no front matter found")
    return m


def replace_categories_block(text, categories):
    """Return post file text with its front-matter categories replaced.

    Inserts the block at the end of the front matter (a top-level boundary,
    so it can never land inside a nested map) when no categories key exists.
    """
    m = _front_matter(text)
    fm = m.group(1)
    block = "categories:\n" + "".join(f"- {c}\n" for c in categories)
    if CATEGORIES_RE.search(fm):
        new_fm = CATEGORIES_RE.sub(lambda _: block, fm, count=1)
    else:
        new_fm = fm + block
    return text[: m.start(1)] + new_fm + text[m.end(1):]


def strip_categories_block(text):
    """Return the text with any front-matter categories block removed."""
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return text
    new_fm = CATEGORIES_RE.sub("", m.group(1), count=1)
    return text[: m.start(1)] + new_fm + text[m.end(1):]


def validate_mapping(records, taxonomy, post_filenames):
    """Return a list of human-readable validation errors (empty when valid)."""
    errors = []
    canonical = set(taxonomy)
    seen = set()
    for r in records:
        f = r.get("file", "<missing file key>")
        if f in seen:
            errors.append(f"{f}: appears more than once in the mapping")
        seen.add(f)
        new = r.get("new") or []
        if not 1 <= len(new) <= 3:
            errors.append(f"{f}: has {len(new)} categories (must be 1-3)")
        if len(set(new)) != len(new):
            errors.append(f"{f}: repeats a category")
        for c in new:
            if c not in canonical:
                errors.append(f"{f}: unknown category '{c}'")
    posts = set(post_filenames)
    for f in sorted(seen - posts):
        errors.append(f"{f}: mapping entry has no matching post file")
    for f in sorted(posts - seen):
        errors.append(f"{f}: post file missing from the mapping")
    return errors


def apply_mapping(records, posts_dir, dry_run=False):
    """Apply assignments to files. Returns the list of changed filenames.

    Self-check invariant: refuses (raises) if a rewrite would alter any byte
    outside the categories block. Idempotent: unchanged files are not written.
    """
    changed = []
    for r in records:
        path = os.path.join(posts_dir, r["file"])
        with open(path, encoding="utf-8", newline="") as fh:
            old = fh.read()
        new = replace_categories_block(old, r["new"])
        if new == old:
            continue
        if strip_categories_block(new) != strip_categories_block(old):
            raise RuntimeError(
                f"{r['file']}: rewrite would alter bytes outside the "
                "categories block; refusing to write")
        changed.append(r["file"])
        if not dry_run:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(new)
    return changed


def load_taxonomy(path):
    import yaml
    with open(path, encoding="utf-8") as fh:
        return [c["name"] for c in yaml.safe_load(fh)["categories"]]


def load_records(path):
    import yaml
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)["posts"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mapping", default=os.path.join(HERE, "mapping.yml"))
    ap.add_argument("--taxonomy", default=os.path.join(HERE, "taxonomy.yml"))
    ap.add_argument("--posts", default="_posts")
    ap.add_argument("--only", help="apply to a single post file")
    ap.add_argument("--dry-run", action="store_true",
                    help="print diffs; write nothing")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any file would change (idempotency check)")
    ap.add_argument("--validate", action="store_true",
                    help="validate the mapping and exit")
    args = ap.parse_args(argv)

    records = load_records(args.mapping)
    taxonomy = load_taxonomy(args.taxonomy)
    post_files = sorted(os.path.basename(p)
                        for p in glob.glob(os.path.join(args.posts, "*.md")))
    errors = validate_mapping(records, taxonomy, post_files)
    if errors:
        for e in errors:
            print(f"INVALID: {e}", file=sys.stderr)
        return 1
    if args.validate:
        print(f"mapping valid: {len(records)} posts, {len(taxonomy)} categories")
        return 0

    if args.only:
        records = [r for r in records if r["file"] == args.only]
        if not records:
            print(f"{args.only} not found in mapping", file=sys.stderr)
            return 1

    if args.dry_run:
        would = apply_mapping(records, args.posts, dry_run=True)
        for f in would:
            path = os.path.join(args.posts, f)
            with open(path, encoding="utf-8", newline="") as fh:
                old = fh.read()
            rec = next(r for r in records if r["file"] == f)
            new = replace_categories_block(old, rec["new"])
            sys.stdout.writelines(difflib.unified_diff(
                old.splitlines(keepends=True), new.splitlines(keepends=True),
                fromfile=f"a/{f}", tofile=f"b/{f}"))
        print(f"\ndry run: {len(would)} of {len(records)} files would change")
        return 0

    if args.check:
        would = apply_mapping(records, args.posts, dry_run=True)
        if would:
            print(f"check failed: {len(would)} files would change", file=sys.stderr)
            return 1
        print("check passed: no files would change")
        return 0

    changed = apply_mapping(records, args.posts)
    print(f"applied: {len(changed)} of {len(records)} files changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
