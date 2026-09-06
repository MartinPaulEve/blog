"""Strip affiliate and tracking clutter from reference URLs.

Rewrites the URLs inside posts' references: front matter (bare lines and
structured url: values alike): Amazon links collapse to a canonical
/dp/ASIN form with no affiliate query, amzn.to short links resolve to
their target first (via url_status.json's recorded final_url), and
utm_* tracking parameters are dropped everywhere. Post bodies are never
touched. Run from the blog root:

    uv run _references/clean_reference_urls.py --dry-run
    uv run _references/clean_reference_urls.py
"""

import argparse
import json
import os
import re
import sys
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

HERE = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(os.path.dirname(HERE), "_posts")

FRONT_MATTER_RE = re.compile(r"\A---\n(.*?\n)---\n", re.DOTALL)
REFERENCES_BLOCK_RE = re.compile(
    r"^references:[ \t]*\n((?:(?:- |  ).*\n?)*)", re.MULTILINE
)
ASIN_RE = re.compile(r"/(?:dp|gp/product|gp/aw/d)/([A-Z0-9]{10})")


def clean_reference_url(url, resolved=None):
    """A cleaned form of url, or url unchanged when nothing applies.

    amzn.to links are replaced with their resolved target (when known)
    before cleaning; Amazon product links become
    https://<host>/dp/<ASIN>; utm_* query parameters are stripped from
    every URL (preserving other parameters).
    """
    working = url
    parts = urlsplit(working)
    if parts.netloc.lower() in ("amzn.to", "www.amzn.to"):
        if not resolved:
            return url
        working = resolved
        parts = urlsplit(working)

    if "amazon." in parts.netloc.lower():
        m = ASIN_RE.search(parts.path)
        asin = m.group(1) if m else dict(parse_qsl(parts.query)).get(
            "creativeASIN", ""
        )
        if re.fullmatch(r"[A-Z0-9]{10}", asin or ""):
            return f"{parts.scheme}://{parts.netloc}/dp/{asin}"

    pairs = parse_qsl(parts.query, keep_blank_values=True)
    kept = [(k, v) for k, v in pairs if not k.lower().startswith("utm_")]
    if len(kept) != len(pairs):
        working = urlunsplit(
            (parts.scheme, parts.netloc, parts.path, urlencode(kept), parts.fragment)
        )
    return working


def rewrite_reference_urls(text, mapping):
    """Post text with reference URLs swapped per mapping, labels intact.

    Only the references: block of the front matter changes: bare lines
    keep their `# label` comments, structured entries keep every other
    field. Returns text unchanged when no mapped URL appears.
    """
    if not mapping:
        return text
    fm = FRONT_MATTER_RE.match(text)
    if not fm:
        return text
    block = REFERENCES_BLOCK_RE.search(fm.group(1))
    if not block:
        return text

    old_block = block.group(1)
    new_block = old_block
    for old, new in sorted(mapping.items(), key=lambda kv: -len(kv[0])):
        new_block = new_block.replace(old, new)
    if new_block == old_block:
        return text

    fm_text = fm.group(1)
    new_fm = fm_text[: block.start(1)] + new_block + fm_text[block.end(1):]
    return text[: fm.start(1)] + new_fm + text[fm.end(1):]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--posts-dir", default=POSTS_DIR)
    parser.add_argument("--status", default=os.path.join(HERE, "url_status.json"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    resolved = {}
    if os.path.exists(args.status):
        with open(args.status, encoding="utf-8") as f:
            resolved = {
                url: verdict.get("final_url")
                for url, verdict in json.load(f).items()
            }

    changed = replaced = 0
    for name in sorted(os.listdir(args.posts_dir)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(args.posts_dir, name)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        fm = FRONT_MATTER_RE.match(text)
        if not fm:
            continue
        block = REFERENCES_BLOCK_RE.search(fm.group(1))
        if not block:
            continue
        urls = re.findall(r"https?://\S+", block.group(1))
        mapping = {}
        for url in urls:
            cleaned = clean_reference_url(url, resolved.get(url))
            if cleaned != url:
                mapping[url] = cleaned
        if not mapping:
            continue
        new = rewrite_reference_urls(text, mapping)
        if new == text:
            continue
        changed += 1
        replaced += len(mapping)
        if args.dry_run:
            for old, cleaned in mapping.items():
                print(f"{name}: {old}\n  -> {cleaned}")
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)

    label = "would clean" if args.dry_run else "cleaned"
    print(f"{label}: {replaced} urls in {changed} posts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
