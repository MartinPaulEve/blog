"""Merge batch agent outputs into the reviewable mapping and review document.

Reads batches/*.yml, remap.yml and taxonomy.yml; writes mapping.yml (the
source of truth for apply_categories.py) and review.md (per-category
listings, needs_review items, and conflicts). Run from the blog root:

    uv run --with pyyaml _categorization/merge_batches.py
"""

import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def merge_batches(batches):
    """Merge batch dicts into one filename-sorted list of post records.

    Raises ValueError on duplicate filenames across (or within) batches.
    """
    records = []
    seen = set()
    for batch in batches:
        for r in batch.get("posts") or []:
            f = r["file"]
            if f in seen:
                raise ValueError(f"duplicate filename across batches: {f}")
            seen.add(f)
            records.append(r)
    return sorted(records, key=lambda r: r["file"])


def _remapped_old(record, remap):
    mapped = {remap.get(o) for o in record.get("old") or []}
    return mapped - {None, "DROP"}


def render_review(records, taxonomy, remap):
    """Render review.md: per-category listings with counts, needs_review
    items, and conflicts (posts whose new categories share nothing with
    their remapped old ones)."""
    lines = ["# Category assignment review", ""]
    lines.append(f"{len(records)} posts assigned.")

    by_cat = {name: [] for name in taxonomy}
    for r in records:
        for c in r.get("new") or []:
            by_cat.setdefault(c, []).append(r)

    lines.append("\n## Categories")
    for name in sorted(by_cat):
        posts = by_cat[name]
        lines.append(f"\n### {name} ({len(posts)})\n")
        for r in posts:
            lines.append(f"- {r['file']} — {r.get('title', '')}")

    lines.append("\n## Needs review\n")
    flagged = [r for r in records if r.get("needs_review")]
    for r in flagged:
        lines.append(f"- {r['file']} — {r.get('title', '')}: {r.get('note', '')}")
    if not flagged:
        lines.append("(none)")

    lines.append("\n## Conflicts\n")
    lines.append("Posts whose new categories share nothing with their "
                 "remapped legacy ones.\n")
    conflicts = 0
    for r in records:
        old = _remapped_old(r, remap)
        new = set(r.get("new") or [])
        if old and not old & new:
            conflicts += 1
            lines.append(f"- {r['file']} — old {sorted(old)} vs new "
                         f"{r.get('new')} — {r.get('title', '')}")
    if not conflicts:
        lines.append("(none)")

    return "\n".join(lines) + "\n"


def main():
    import yaml

    with open(os.path.join(HERE, "taxonomy.yml"), encoding="utf-8") as fh:
        taxonomy = [c["name"] for c in yaml.safe_load(fh)["categories"]]
    with open(os.path.join(HERE, "remap.yml"), encoding="utf-8") as fh:
        remap = yaml.safe_load(fh)["remap"]

    batches = []
    for path in sorted(glob.glob(os.path.join(HERE, "batches", "*.yml"))):
        with open(path, encoding="utf-8") as fh:
            batches.append(yaml.safe_load(fh))
    if not batches:
        print("no batch files found", file=sys.stderr)
        return 1

    records = merge_batches(batches)

    with open(os.path.join(HERE, "mapping.yml"), "w", encoding="utf-8") as fh:
        yaml.safe_dump({"prompt_version": 1, "posts": records}, fh,
                       allow_unicode=True, sort_keys=False, width=1000)
    with open(os.path.join(HERE, "review.md"), "w", encoding="utf-8") as fh:
        fh.write(render_review(records, taxonomy, remap))

    # Early validation feedback; the apply script re-validates and hard-fails.
    sys.path.insert(0, HERE)
    import apply_categories
    post_files = sorted(os.path.basename(p) for p in glob.glob("_posts/*.md"))
    errors = apply_categories.validate_mapping(records, taxonomy, post_files)
    print(f"merged {len(batches)} batches -> {len(records)} records")
    if errors:
        print(f"{len(errors)} validation problems (fix before applying):")
        for e in errors[:40]:
            print(f"  - {e}")
        if len(errors) > 40:
            print(f"  ... and {len(errors) - 40} more")
    else:
        print("mapping is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
