"""Fetch the Rogue Scholar record for freshly deployed posts.

Rogue Scholar harvests the blog's feed on a pull cycle, so a new post's
record only appears some minutes after deploy. This tool looks the given
post(s) up in the Rogue Scholar "eve" community (DOI first, URL path as a
fallback — the same matching as fetch_mapping.py) and stamps the record
URL into the post's front matter as `roguescholar:`. An existing
`atproto:` line is preserved; when the post has an `atUri:` line (written
at ATProto publish time) but no `atproto:`, the value is mirrored across
so the page's AT Protocol link renders. Run from the blog root:

    ./roguescholar.sh _posts/YYYY-MM-DD-slug.md
    ./roguescholar.sh --attempts 10 --interval 120 _posts/YYYY-MM-DD-slug.md

or directly:

    uv run --with pyyaml --with certifi _identifiers/fetch_roguescholar.py <post>
"""

import argparse
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from apply_identifiers import (
    FRONT_MATTER_RE,
    build_mapping,
    insert_identifiers,
)


ATPROTO_VALUE_RE = re.compile(r"^atproto:\s*(\S+)\s*$", re.MULTILINE)
ATURI_VALUE_RE = re.compile(r'^atUri:\s*"?([^"\s]+)"?\s*$', re.MULTILINE)


def load_post(path):
    """Read one _posts file into the {"file", "doi", "path"} mapping shape."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = FRONT_MATTER_RE.match(text)
    if not m:
        raise ValueError("no front matter found")
    dm = re.search(r"^doi:\s*(\S+)\s*$", m.group(1), re.MULTILINE)
    fname = os.path.basename(path)
    stem = fname[:-3] if fname.endswith(".md") else fname
    year, month, day, slug = stem.split("-", 3)
    return {
        "file": fname,
        "doi": dm.group(1) if dm else None,
        "path": f"/{year}/{month}/{day}/{slug}",
    }


def find_record_url(post, records):
    """Match one post against Rogue Scholar records.

    Returns (record_url_or_None, anomalies) using the same DOI-first,
    URL-path-fallback rules as the full mapping build. Anomalies about
    atProto documents and simple not-yet-harvested misses are dropped:
    the former are out of scope here, the latter are the normal state
    while Rogue Scholar's pull cycle catches up.
    """
    mapping, anomalies = build_mapping([post], records, [])
    url = mapping[post["file"]]["roguescholar"]
    relevant = [
        a
        for a in anomalies
        if "atProto" not in a and "no Rogue Scholar record" not in a
    ]
    return url, relevant


def stamp_roguescholar(text, url):
    """Return post text with `roguescholar:` set to url.

    Preserves an existing `atproto:` line; backfills `atproto:` from an
    `atUri:` line when the post has one but no `atproto:` yet.
    """
    m = FRONT_MATTER_RE.match(text)
    if not m:
        raise ValueError("no front matter found")
    fm = m.group(1)
    existing = ATPROTO_VALUE_RE.search(fm)
    aturi = ATURI_VALUE_RE.search(fm)
    atproto = existing.group(1) if existing else (
        aturi.group(1) if aturi else None
    )
    return insert_identifiers(text, roguescholar=url, atproto=atproto)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("posts", nargs="+", help="_posts/*.md file(s)")
    parser.add_argument(
        "--attempts",
        type=int,
        default=1,
        help="how many times to poll before giving up (default: 1)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=120.0,
        help="seconds between polls (default: 120)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="report without writing"
    )
    args = parser.parse_args(argv)

    from fetch_mapping import fetch_rogue_scholar_records

    pending = {}
    for path in args.posts:
        try:
            pending[path] = load_post(path)
        except (OSError, ValueError) as exc:
            print(f"FAILED {path}: {exc}", file=sys.stderr)
            return 1

    stamped = 0
    for attempt in range(1, args.attempts + 1):
        records = fetch_rogue_scholar_records()
        for path, post in sorted(pending.items()):
            url, anomalies = find_record_url(post, records)
            for anomaly in anomalies:
                print(f"NOTE {anomaly}", file=sys.stderr)
            if not url:
                continue
            with open(path, encoding="utf-8") as f:
                text = f.read()
            new = stamp_roguescholar(text, url)
            if args.dry_run:
                print(f"would stamp {post['file']}: {url}")
            elif new != text:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new)
                print(f"stamped {post['file']}: {url}")
            else:
                print(f"already stamped {post['file']}: {url}")
            del pending[path]
            stamped += 1
        if not pending:
            break
        if attempt < args.attempts:
            print(
                f"not yet harvested ({len(pending)} post(s)); "
                f"retrying in {args.interval:.0f}s "
                f"[attempt {attempt}/{args.attempts}]"
            )
            time.sleep(args.interval)

    for path in sorted(pending):
        print(f"no Rogue Scholar record yet: {path}", file=sys.stderr)
    return 0 if not pending else 1


if __name__ == "__main__":
    sys.exit(main())
