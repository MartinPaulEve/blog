"""Apply Rogue Scholar and atProto identifiers to post front matter.

Adds a `roguescholar:` (Rogue Scholar record URL) and an `atproto:`
(at:// URI of the site.standard.document record) key to each post named
in mapping.yml, using targeted text manipulation (never YAML
re-serialization, which would mangle comments, smart quotes, and
unquoted timestamps elsewhere in the front matter). Run from the blog
root:

    uv run --with pyyaml _identifiers/apply_identifiers.py --dry-run
    uv run --with pyyaml _identifiers/apply_identifiers.py
    uv run --with pyyaml _identifiers/apply_identifiers.py --check
"""

import argparse
import os
import re
import sys
from urllib.parse import unquote

HERE = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(os.path.dirname(HERE), "_posts")

FRONT_MATTER_RE = re.compile(r"\A---\n(.*?\n)---\n", re.DOTALL)
KCWORKS_RE = re.compile(r"^kcworks:[^\n]*\n", re.MULTILINE)
DOI_RE = re.compile(r"^doi:[^\n]*\n", re.MULTILINE)
ROGUESCHOLAR_RE = re.compile(r"^roguescholar:[^\n]*\n", re.MULTILINE)
ATPROTO_RE = re.compile(r"^atproto:[^\n]*\n", re.MULTILINE)


def _front_matter(text):
    if "\r" in text:
        raise ValueError("CRLF/CR line endings; refusing to edit")
    m = FRONT_MATTER_RE.match(text)
    if not m:
        raise ValueError("no front matter found")
    return m


def insert_identifiers(text, roguescholar=None, atproto=None):
    """Return post file text with roguescholar/atproto front-matter keys set.

    The keys are placed directly after `kcworks:` (or `doi:` when there is
    no kcworks line, or at the end of the front matter when neither
    exists), so the identifier lines stay grouped. Existing values are
    replaced, making the operation idempotent.
    """
    m = _front_matter(text)
    fm = m.group(1)
    fm = ROGUESCHOLAR_RE.sub("", fm)
    fm = ATPROTO_RE.sub("", fm)

    block = ""
    if roguescholar:
        block += f"roguescholar: {roguescholar}\n"
    if atproto:
        block += f"atproto: {atproto}\n"
    if block:
        anchor = KCWORKS_RE.search(fm) or DOI_RE.search(fm)
        at = anchor.end() if anchor else len(fm)
        fm = fm[:at] + block + fm[at:]

    return text[: m.start(1)] + fm + text[m.end(1) :]


def _normalize_doi(doi):
    if not doi:
        return None
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", doi.strip()).lower()


def _normalize_path(path_or_url):
    if not path_or_url:
        return None
    path = re.sub(r"^https?://[^/]+", "", path_or_url.strip())
    return unquote(path).rstrip("/").lower()


def _slug(path):
    return path.rsplit("/", 1)[-1] if path else None


def build_mapping(posts, records, atdocs):
    """Match posts to Rogue Scholar records and atProto documents.

    Each post is `{"file", "doi", "path"}`; each record is
    `{"id", "doi", "url", "created"}`; each atdoc is `{"uri", "path"}`.
    Matching is by DOI first, falling back to the post's URL path. A DOI
    match is trusted only when the record's URL slug agrees with the
    post's (dates sometimes drift between the blog and the archive, so
    only the slug is compared); this catches front-matter DOIs that were
    copy-pasted from another post. Where several records share one URL
    (re-harvest duplicates), the oldest — whose DOI has been in
    circulation longest — wins. Returns (mapping, anomalies) where
    mapping is `{file: {"roguescholar": url|None, "atproto": uri|None}}`.
    """
    by_doi = {}
    by_path = {}
    for r in records:
        ndoi = _normalize_doi(r.get("doi"))
        if ndoi:
            by_doi[ndoi] = r
        npath = _normalize_path(r.get("url"))
        if npath:
            existing = by_path.get(npath)
            if existing is None or (r.get("created") or "") < (existing.get("created") or ""):
                by_path[npath] = r

    at_by_path = {_normalize_path(d["path"]): d for d in atdocs}

    mapping = {}
    anomalies = []
    claims = {}  # record id -> [post file, ...]
    for p in posts:
        fname = p["file"]
        ndoi = _normalize_doi(p.get("doi"))
        npath = _normalize_path(p.get("path"))

        record = by_doi.get(ndoi) if ndoi else None
        if record is not None:
            rpath = _normalize_path(record.get("url"))
            if rpath and _slug(rpath) != _slug(npath):
                anomalies.append(
                    f"{fname}: DOI {ndoi} belongs to a record for {record.get('url')} "
                    f"(slug mismatch); DOI match rejected"
                )
                record = None
        if record is None:
            record = by_path.get(npath)

        atdoc = at_by_path.get(npath)
        if atdoc is None:
            anomalies.append(f"{fname}: no atProto document found for path {p.get('path')}")

        if record is None:
            anomalies.append(f"{fname}: no Rogue Scholar record found")
            mapping[fname] = {"roguescholar": None, "atproto": atdoc["uri"] if atdoc else None}
            continue

        claims.setdefault(record["id"], []).append(fname)
        mapping[fname] = {
            "roguescholar": f"https://rogue-scholar.org/records/{record['id']}",
            "atproto": atdoc["uri"] if atdoc else None,
        }

    for rec_id, files in claims.items():
        if len(files) > 1:
            for fname in files:
                anomalies.append(f"{fname}: record {rec_id} claimed by multiple posts: {files}")
            record = next(r for r in records if r["id"] == rec_id)
            rpath = _normalize_path(record.get("url"))
            for fname in files:
                post = next(p for p in posts if p["file"] == fname)
                if _normalize_path(post.get("path")) != rpath:
                    mapping[fname]["roguescholar"] = None

    return mapping, anomalies


def main(argv=None):
    import yaml

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mapping", default=os.path.join(HERE, "mapping.yml"))
    parser.add_argument("--posts-dir", default=POSTS_DIR)
    parser.add_argument("--dry-run", action="store_true", help="report without writing")
    parser.add_argument("--check", action="store_true", help="verify mapping is applied")
    args = parser.parse_args(argv)

    with open(args.mapping, encoding="utf-8") as f:
        mapping = yaml.safe_load(f)

    changed = missing = failed = 0
    for fname, ids in sorted(mapping.items()):
        path = os.path.join(args.posts_dir, fname)
        if not os.path.exists(path):
            print(f"MISSING {fname}", file=sys.stderr)
            missing += 1
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        try:
            new = insert_identifiers(
                text,
                roguescholar=ids.get("roguescholar"),
                atproto=ids.get("atproto"),
            )
        except ValueError as e:
            print(f"FAILED {fname}: {e}", file=sys.stderr)
            failed += 1
            continue
        if new == text:
            continue
        changed += 1
        if args.check:
            print(f"UNAPPLIED {fname}", file=sys.stderr)
        elif args.dry_run:
            print(f"would update {fname}")
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)

    label = "unapplied" if args.check else ("would update" if args.dry_run else "updated")
    print(f"{label}: {changed}; missing: {missing}; failed: {failed}; total: {len(mapping)}")
    return 1 if (missing or failed or (args.check and changed)) else 0


if __name__ == "__main__":
    sys.exit(main())
