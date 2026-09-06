"""Stamp last_modified_at into post front matter.

Sets `last_modified_at: YYYY-MM-DD` on each given post, taking the date
from the post's last git commit unless --date overrides it. The key sits
directly under the date: line so temporal metadata stays grouped, and
restamping is idempotent. The layout shows the value as an "Updated"
line (HTML and PDF), jekyll-feed and the signposting metadata pick it up
as dateModified, and kcworks-update uses it to decide which repository
deposits are stale. Run from the blog root:

    uv run _references/stamp_last_modified.py _posts/....md [--date YYYY-MM-DD]
    git show --name-only --format= <commit> -- _posts | \
        xargs uv run _references/stamp_last_modified.py
"""

import argparse
import re
import subprocess
import sys

FRONT_MATTER_RE = re.compile(r"\A---\n(.*?\n)---\n", re.DOTALL)
LAST_MODIFIED_RE = re.compile(r"^last_modified_at:[^\n]*\n", re.MULTILINE)
DATE_LINE_RE = re.compile(r"^date:[^\n]*\n", re.MULTILINE)


def stamp_last_modified(text, date_str):
    """Post text with last_modified_at set to date_str; body untouched."""
    m = FRONT_MATTER_RE.match(text)
    if not m:
        raise ValueError("no front matter found")
    fm = m.group(1)
    fm = LAST_MODIFIED_RE.sub("", fm)
    line = f"last_modified_at: {date_str}\n"
    date_line = DATE_LINE_RE.search(fm)
    at = date_line.end() if date_line else len(fm)
    fm = fm[:at] + line + fm[at:]
    return text[: m.start(1)] + fm + text[m.end(1):]


def git_date(path):
    out = subprocess.check_output(
        ["git", "log", "-1", "--format=%as", "--", path], text=True
    ).strip()
    return out or None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("posts", nargs="+")
    parser.add_argument("--date", default=None, help="override YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    changed = failed = 0
    for path in args.posts:
        date_str = args.date or git_date(path)
        if not date_str:
            print(f"FAILED {path}: no git date", file=sys.stderr)
            failed += 1
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        try:
            new = stamp_last_modified(text, date_str)
        except ValueError as exc:
            print(f"FAILED {path}: {exc}", file=sys.stderr)
            failed += 1
            continue
        if new == text:
            continue
        changed += 1
        if args.dry_run:
            print(f"would stamp {path}: {date_str}")
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)

    label = "would stamp" if args.dry_run else "stamped"
    print(f"{label}: {changed}; failed: {failed}; total: {len(args.posts)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
