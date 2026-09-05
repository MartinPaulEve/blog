"""Apply labelled reference sets to post front matter.

Reads manifest.json (extract_manifest.py), url_status.json (check_urls.py)
and labels.json (the agent-produced {post: [{url, comment}]} map), validates
every entry — the URL must appear in the post's manifest and must have
resolved as alive — and appends a `references:` block of bare URL entries
with identifying comments to each post's front matter. Only front matter is
ever touched; the body is byte-identical. Run from the blog root:

    uv run --with pyyaml _references/apply_references.py --dry-run
    uv run --with pyyaml _references/apply_references.py
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(os.path.dirname(HERE), "_posts")

FRONT_MATTER_RE = re.compile(r"\A---\n(.*?\n)---\n", re.DOTALL)
REFERENCES_RE = re.compile(r"^references:", re.MULTILINE)


def is_alive(status):
    """Whether an HTTP status counts as 'still resolves'.

    Access-restricted responses (401/403/405/429) resolve: the resource
    exists but refuses bots. Only hard misses (404/410), server errors,
    and connection failures (status None) count as dead.
    """
    if status is None:
        return False
    if status in (401, 403, 405, 429):
        return True
    return 200 <= status < 400


def format_reference_line(url, comment=None):
    """One `- url # comment` YAML list line (comment whitespace-collapsed)."""
    line = f"- {url}"
    if comment:
        collapsed = re.sub(r"\s+", " ", str(comment)).strip()
        if collapsed:
            line += f" # {collapsed}"
    return line


def insert_references_block(text, entries):
    """Append a references: block to the front matter; body untouched.

    entries is a list of {"url", "comment"} mappings. Raises ValueError if
    the post has no front matter or already carries a references: key.
    Returns text unchanged when entries is empty.
    """
    m = FRONT_MATTER_RE.match(text)
    if not m:
        raise ValueError("no front matter found")
    if REFERENCES_RE.search(m.group(1)):
        raise ValueError("already has a references: block")
    if not entries:
        return text
    block = "references:\n" + "".join(
        format_reference_line(entry["url"], entry.get("comment")) + "\n"
        for entry in entries
    )
    return text[: m.end(1)] + block + text[m.end(1):]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=os.path.join(HERE, "manifest.json"))
    parser.add_argument("--status", default=os.path.join(HERE, "url_status.json"))
    parser.add_argument("--labels", default=os.path.join(HERE, "labels.json"))
    parser.add_argument("--posts-dir", default=POSTS_DIR)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    import yaml

    with open(args.manifest, encoding="utf-8") as f:
        manifest = json.load(f)
    with open(args.status, encoding="utf-8") as f:
        status = json.load(f)
    with open(args.labels, encoding="utf-8") as f:
        labels = json.load(f)

    changed = skipped = dead = rejected = 0
    for fname, entries in sorted(labels.items()):
        allowed = {item["url"] for item in manifest.get(fname, [])}
        valid = []
        for entry in entries:
            url = entry.get("url", "")
            if url not in allowed:
                print(f"REJECTED {fname}: {url} not in manifest", file=sys.stderr)
                rejected += 1
                continue
            verdict = status.get(url, {})
            if not is_alive(verdict.get("status")):
                dead += 1
                continue
            valid.append(entry)
        if not valid:
            skipped += 1
            continue

        path = os.path.join(args.posts_dir, fname)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        try:
            new = insert_references_block(text, valid)
        except ValueError as exc:
            print(f"FAILED {fname}: {exc}", file=sys.stderr)
            continue
        yaml.safe_load(FRONT_MATTER_RE.match(new).group(1))  # must stay valid
        changed += 1
        if args.dry_run:
            print(f"would update {fname} (+{len(valid)} references)")
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)

    label = "would update" if args.dry_run else "updated"
    print(
        f"{label}: {changed}; no live links: {skipped}; "
        f"dead links dropped: {dead}; rejected: {rejected}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
