"""Build mapping.yml linking posts to BIROn (Birkbeck repository) eprints.

Fetches the JSON export of every BIROn item by Martin Paul Eve (a single
request, so the repository is not hammered), keeps the ones whose
official_url lives on eve.gd or that carry a DOI, matches them to
_posts files (URL path first, DOI and slug as fallbacks — see
apply_biron.build_mapping), applies overrides.yml for hand-curated
cases, and writes mapping.yml plus an anomalies.md audit trail. Run
from the blog root:

    uv run --with pyyaml --with certifi _biron/fetch_mapping.py
    uv run --with pyyaml --with certifi _biron/fetch_mapping.py --feed biron.json
"""

import argparse
import glob
import json
import os
import re
import ssl
import sys
import urllib.request
from urllib.parse import quote_plus

import yaml

# uv-managed Pythons don't always see the system CA bundle, so prefer
# certifi's when it is available.
try:
    import certifi

    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from apply_biron import (
    FRONT_MATTER_RE,
    POSTS_DIR,
    apply_overrides,
    build_mapping,
    unclaimed_blog_eprints,
)

EXPORT_URL = (
    "https://eprints.bbk.ac.uk/cgi/exportview?format=JSON&_action_export_redir=Export"
    "&view=people&values=Eve%3D3AMartin_Paul%3D3A%3D3A"
)
BLOG_URL_RE = re.compile(r"^https?://(www\.)?eve\.gd/", re.IGNORECASE)
DOI_URL_RE = re.compile(r"^https?://(dx\.)?doi\.org/", re.IGNORECASE)


def fetch_feed(feed_path=None):
    if feed_path:
        with open(feed_path, encoding="utf-8") as f:
            return json.load(f)
    req = urllib.request.Request(EXPORT_URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, context=SSL_CONTEXT) as r:
        return json.load(r)


def extract_eprints(feed):
    """Reduce the raw export to matchable records.

    An item's DOI can hide in id_number or rioxx2_version_of_record, and
    some deposits put the DOI URL in official_url itself — those are
    treated as DOIs, not URLs, so slug checking is not misled. Items
    with neither an eve.gd official_url nor a DOI cannot be matched
    automatically and are dropped (books, articles, talks, and the
    overrides.yml cases).
    """
    eprints = []
    for d in feed:
        url = (d.get("official_url") or "").strip() or None
        doi = d.get("id_number") or d.get("rioxx2_version_of_record")
        if url and DOI_URL_RE.match(url):
            doi = doi or url
            url = None
        if url and not BLOG_URL_RE.match(url):
            url = None
        if not url and not doi and d.get("publication") != "eve.gd":
            continue
        eprints.append(
            {
                "eprintid": d["eprintid"],
                "uri": d["uri"],
                "url": url,
                "doi": doi,
                "title": d.get("title"),
                "publication": d.get("publication"),
                "official_url": (d.get("official_url") or "").strip() or None,
            }
        )
    return eprints


def load_posts():
    posts = []
    for path in sorted(glob.glob(os.path.join(POSTS_DIR, "*.md"))):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        m = FRONT_MATTER_RE.match(text)
        doi = title = None
        if m:
            dm = re.search(r"^doi:\s*(\S+)\s*$", m.group(1), re.MULTILINE)
            doi = dm.group(1) if dm else None
            tm = re.search(r"^title:\s*(.+?)\s*$", m.group(1), re.MULTILINE)
            title = tm.group(1).strip("'\"") if tm else None
        fname = os.path.basename(path)
        year, month, day, slug = fname[:-3].split("-", 3)
        posts.append(
            {
                "file": fname,
                "doi": doi,
                "path": f"/{year}/{month}/{day}/{slug}",
                "title": title,
            }
        )
    return posts


SEARCH_URL = "https://eprints.bbk.ac.uk/cgi/search?q="


def render_anomalies(anomalies, mapping, titles, unclaimed):
    """Render anomalies.md: matching notes, unmatched posts (with titles
    and a BIROn search link), and unclaimed blog-side eprints — so missed
    matches can be reviewed by eye across the last two sections."""
    notes = [a for a in anomalies if not a.endswith("no BIROn eprint found")]
    unmatched = sorted(f for f, v in mapping.items() if not v)

    lines = ["# BIROn matching anomalies", ""]

    lines += [f"## Matching notes ({len(notes)})", ""]
    lines += [f"- {n}" for n in notes] or ["None."]
    lines.append("")

    lines += [f"## Posts with no BIROn eprint ({len(unmatched)})", ""]
    for fname in unmatched:
        title = titles.get(fname) or "(no title)"
        search = SEARCH_URL + quote_plus(title)
        lines.append(f"- `{fname}` — {title} — [search BIROn]({search})")
    if not unmatched:
        lines.append("None.")
    lines.append("")

    lines += [f"## Blog-side eprints claimed by no post ({len(unclaimed)})", ""]
    for e in unclaimed:
        url = e.get("official_url") or "(no official_url)"
        title = e.get("title") or "(no title)"
        lines.append(f"- [{e['eprintid']}]({e['uri'].rstrip('/')}/) — {title} — {url}")
    if not unclaimed:
        lines.append("None.")
    lines.append("")

    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--feed", help="read the JSON export from a file instead of BIROn")
    args = parser.parse_args(argv)

    posts = load_posts()
    print(f"posts: {len(posts)}")
    feed = fetch_feed(args.feed)
    print(f"BIROn items: {len(feed)}")
    eprints = extract_eprints(feed)
    print(f"matchable eprints: {len(eprints)}")

    mapping, anomalies = build_mapping(posts, eprints)

    overrides_path = os.path.join(HERE, "overrides.yml")
    if os.path.exists(overrides_path):
        with open(overrides_path, encoding="utf-8") as f:
            overrides = yaml.safe_load(f) or {}
        mapping = apply_overrides(mapping, overrides, eprints)

    with open(os.path.join(HERE, "mapping.yml"), "w", encoding="utf-8") as f:
        yaml.safe_dump(mapping, f, allow_unicode=True, sort_keys=True, width=1000)

    titles = {p["file"]: p["title"] for p in posts}
    unclaimed = unclaimed_blog_eprints(mapping, eprints)
    with open(os.path.join(HERE, "anomalies.md"), "w", encoding="utf-8") as f:
        f.write(render_anomalies(anomalies, mapping, titles, unclaimed))

    matched = sum(1 for v in mapping.values() if v)
    print(f"matched: {matched}/{len(posts)}")
    print(f"anomalies: {len(anomalies)}; unclaimed eprints: {len(unclaimed)} (see _biron/anomalies.md)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
