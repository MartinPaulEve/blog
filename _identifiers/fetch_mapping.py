"""Build mapping.yml linking posts to Rogue Scholar records and atProto documents.

Fetches every record in the Rogue Scholar "eve" community and every
site.standard.document record in the eve.gd atProto repository, matches
them to _posts files (DOI first, URL path as fallback — see
apply_identifiers.build_mapping), and writes mapping.yml plus an
anomalies.md audit trail. Run from the blog root:

    uv run --with pyyaml --with certifi _identifiers/fetch_mapping.py
"""

import glob
import json
import os
import re
import ssl
import sys
import time
import urllib.request

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

from apply_identifiers import FRONT_MATTER_RE, POSTS_DIR, build_mapping

RS_COMMUNITY_API = "https://rogue-scholar.org/api/communities/eve/records"
PDS = "https://porcini.us-east.host.bsky.network"
DID = "did:plc:hnpt7ns2lecdujegbi6qkqqm"


def _get_json(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, context=SSL_CONTEXT) as r:
        return json.load(r)


def fetch_rogue_scholar_records():
    records, page = [], 1
    while True:
        d = _get_json(f"{RS_COMMUNITY_API}?size=100&page={page}&sort=newest")
        hits = d["hits"]["hits"]
        for h in hits:
            m = h.get("metadata", {})
            urls = [i["identifier"] for i in m.get("identifiers", []) if i.get("scheme") == "url"]
            records.append({
                "id": h["id"],
                "doi": h.get("pids", {}).get("doi", {}).get("identifier"),
                "url": urls[0] if urls else None,
                "created": h.get("created"),
                "title": m.get("title"),
            })
        if len(records) >= d["hits"]["total"] or not hits:
            return records
        page += 1
        time.sleep(0.3)


def fetch_atproto_documents():
    docs, cursor = [], None
    while True:
        url = f"{PDS}/xrpc/com.atproto.repo.listRecords?repo={DID}&collection=site.standard.document&limit=100"
        if cursor:
            url += f"&cursor={cursor}"
        d = _get_json(url)
        for r in d["records"]:
            docs.append({"uri": r["uri"], "path": r["value"]["path"]})
        cursor = d.get("cursor")
        if not cursor or not d["records"]:
            return docs


def load_posts():
    posts = []
    for path in sorted(glob.glob(os.path.join(POSTS_DIR, "*.md"))):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        m = FRONT_MATTER_RE.match(text)
        doi = None
        if m:
            dm = re.search(r"^doi:\s*(\S+)\s*$", m.group(1), re.MULTILINE)
            doi = dm.group(1) if dm else None
        fname = os.path.basename(path)
        year, month, day, slug = fname[:-3].split("-", 3)
        posts.append({"file": fname, "doi": doi, "path": f"/{year}/{month}/{day}/{slug}"})
    return posts


def main():
    posts = load_posts()
    print(f"posts: {len(posts)}")
    records = fetch_rogue_scholar_records()
    print(f"Rogue Scholar records: {len(records)}")
    atdocs = fetch_atproto_documents()
    print(f"atProto documents: {len(atdocs)}")

    mapping, anomalies = build_mapping(posts, records, atdocs)

    with open(os.path.join(HERE, "mapping.yml"), "w", encoding="utf-8") as f:
        yaml.safe_dump(mapping, f, allow_unicode=True, sort_keys=True, width=1000)

    with open(os.path.join(HERE, "anomalies.md"), "w", encoding="utf-8") as f:
        f.write("# Identifier matching anomalies\n\n")
        if anomalies:
            f.writelines(f"- {a}\n" for a in anomalies)
        else:
            f.write("None.\n")

    matched_rs = sum(1 for v in mapping.values() if v["roguescholar"])
    matched_at = sum(1 for v in mapping.values() if v["atproto"])
    print(f"matched Rogue Scholar: {matched_rs}/{len(posts)}")
    print(f"matched atProto: {matched_at}/{len(posts)}")
    for a in anomalies:
        print(f"ANOMALY: {a}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
