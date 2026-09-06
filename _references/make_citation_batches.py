"""Split fetched citation metadata into batches for label agents.

Joins citation_meta.json (raw page evidence) with the manifest's anchor
text/context and the applied labels, one record per unique URL, and
writes citation_batches/cbatch-NN.json for the normalisation agents.
URLs whose fetch produced no usable evidence are skipped — their posts
keep the bare labelled line. Run from the blog root:

    uv run _references/make_citation_batches.py
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BATCH_DIR = os.path.join(HERE, "citation_batches")
OUT_DIR = os.path.join(HERE, "citations")
BATCH_COUNT = 34


def main():
    with open(os.path.join(HERE, "citation_meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    with open(os.path.join(HERE, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    with open(os.path.join(HERE, "labels.json"), encoding="utf-8") as f:
        labels = json.load(f)

    context = {}
    for fname, entries in manifest.items():
        for entry in entries:
            context.setdefault(entry["url"], {
                "text": entry.get("text"),
                "context": entry.get("context"),
            })
    label_for = {}
    for entries in labels.values():
        for entry in entries:
            label_for.setdefault(entry["url"], entry.get("comment"))

    records = {}
    for url, evidence in meta.items():
        if not evidence.get("fetched"):
            continue
        fields = {
            k: evidence[k]
            for k in ("title", "authors", "date", "site", "type")
            if evidence.get(k)
        }
        if not fields:
            continue
        records[url] = {
            "label": label_for.get(url),
            "anchor_text": context.get(url, {}).get("text"),
            "post_context": context.get(url, {}).get("context"),
            "page_meta": fields,
        }

    os.makedirs(BATCH_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    urls = sorted(records)
    per = math.ceil(len(urls) / BATCH_COUNT) or 1
    names = []
    for i in range(0, len(urls), per):
        name = f"cbatch-{i // per:02d}.json"
        with open(os.path.join(BATCH_DIR, name), "w", encoding="utf-8") as f:
            json.dump(
                {u: records[u] for u in urls[i:i + per]},
                f, indent=1, ensure_ascii=False,
            )
        names.append(name)
    print(f"{len(urls)} urls with evidence into {len(names)} batches")
    print(json.dumps(names))
    return 0


if __name__ == "__main__":
    sys.exit(main())
