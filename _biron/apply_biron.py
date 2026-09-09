"""Apply BIROn (Birkbeck institutional repository) links to post front matter.

Adds a `biron:` key (the eprint's canonical URL, e.g.
https://eprints.bbk.ac.uk/id/eprint/57592/) to each post named in
mapping.yml, using targeted text manipulation (never YAML
re-serialization, which would mangle comments, smart quotes, and
unquoted timestamps elsewhere in the front matter). Run from the blog
root:

    uv run --with pyyaml _biron/apply_biron.py --dry-run
    uv run --with pyyaml _biron/apply_biron.py
    uv run --with pyyaml _biron/apply_biron.py --check
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
ATPROTO_RE = re.compile(r"^atproto:[^\n]*\n", re.MULTILINE)
ROGUESCHOLAR_RE = re.compile(r"^roguescholar:[^\n]*\n", re.MULTILINE)
DOI_RE = re.compile(r"^doi:[^\n]*\n", re.MULTILINE)
BIRON_RE = re.compile(r"^biron:[^\n]*\n", re.MULTILINE)


def _front_matter(text):
    if "\r" in text:
        raise ValueError("CRLF/CR line endings; refusing to edit")
    m = FRONT_MATTER_RE.match(text)
    if not m:
        raise ValueError("no front matter found")
    return m


def insert_biron(text, biron=None):
    """Return post file text with the biron front-matter key set.

    The key is placed directly after `kcworks:` (or `atproto:`,
    `roguescholar:`, `doi:` in that order when absent, or at the end of
    the front matter as a last resort), so the identifier lines stay
    grouped. An existing value is replaced, making the operation
    idempotent; `biron=None` removes the line.
    """
    m = _front_matter(text)
    fm = m.group(1)
    fm = BIRON_RE.sub("", fm)

    if biron:
        anchor = (
            KCWORKS_RE.search(fm)
            or ATPROTO_RE.search(fm)
            or ROGUESCHOLAR_RE.search(fm)
            or DOI_RE.search(fm)
        )
        at = anchor.end() if anchor else len(fm)
        fm = fm[:at] + f"biron: {biron}\n" + fm[at:]

    return text[: m.start(1)] + fm + text[m.end(1) :]


def _normalize_doi(doi):
    if not doi:
        return None
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", doi.strip()).lower()


def _normalize_path(path_or_url):
    if not path_or_url:
        return None
    path = re.sub(r"^https?://[^/]+", "", path_or_url.strip())
    path = path.split("#", 1)[0].split("?", 1)[0]
    prev = None
    while path != prev:  # BIROn official_urls are sometimes double-encoded
        prev = path
        path = unquote(prev)
    return _dashed_hex(path.rstrip("/").lower())


def _dashed_hex(path):
    """Spell non-ASCII characters as dashed hex UTF-8 bytes (ά → -ce-ac).

    This is the transformation the blog's slugifier applied to Greek
    post titles (percent signs became hyphens, runs of hyphens
    collapsed), so eprint URLs holding literal or percent-encoded Greek
    compare equal to the ASCII-only post filenames.
    """
    if path.isascii():
        return path
    out = []
    for ch in path:
        if ord(ch) < 128:
            out.append(ch)
        else:
            out.append("".join(f"-{b:02x}" for b in ch.encode("utf-8")))
    path = re.sub(r"-{2,}", "-", "".join(out))
    return re.sub(r"(^|/)-+|-+(?=/|$)", r"\1", path)


def _slug(path):
    return path.rsplit("/", 1)[-1] if path else None


def _biron_url(eprint):
    return eprint["uri"].rstrip("/") + "/"


def build_mapping(posts, eprints):
    """Match posts to BIROn eprints.

    Each post is `{"file", "doi", "path"}`; each eprint is
    `{"eprintid", "uri", "url", "doi", "title"}` where `url` is the
    eprint's official_url (the canonical eve.gd address). Matching is by
    URL path first, then DOI (trusted only when the eprint's URL slug
    agrees with the post's — dates sometimes drift between the blog and
    the deposit, so only the slug is compared), then by slug alone when
    that is unambiguous on both sides. Where several eprints share one
    official_url (re-deposit duplicates), the oldest — lowest eprintid —
    wins. Returns (mapping, anomalies) where mapping is
    `{file: biron_url_or_None}`.
    """
    by_path = {}
    by_doi = {}
    by_slug = {}
    for e in eprints:
        npath = _normalize_path(e.get("url"))
        if npath:
            existing = by_path.get(npath)
            if existing is not None:
                by_path[npath] = min(existing, e, key=lambda x: x["eprintid"])
            else:
                by_path[npath] = e
            by_slug.setdefault(_slug(npath), []).append(e)
        ndoi = _normalize_doi(e.get("doi"))
        if ndoi:
            by_doi[ndoi] = e

    anomalies = []
    for npath, e in sorted(by_path.items()):
        ids = sorted(x["eprintid"] for x in eprints if _normalize_path(x.get("url")) == npath)
        if len(ids) > 1:
            anomalies.append(
                f"duplicate official_url {npath} on eprints {ids}; keeping {e['eprintid']}"
            )

    slug_claims = {}
    for p in posts:
        slug_claims.setdefault(_slug(_normalize_path(p.get("path"))), []).append(p["file"])

    mapping = {}
    for p in posts:
        fname = p["file"]
        npath = _normalize_path(p.get("path"))
        ndoi = _normalize_doi(p.get("doi"))

        eprint = by_path.get(npath)

        if eprint is None and ndoi and ndoi in by_doi:
            candidate = by_doi[ndoi]
            cpath = _normalize_path(candidate.get("url"))
            if cpath and _slug(cpath) != _slug(npath):
                anomalies.append(
                    f"{fname}: DOI {ndoi} belongs to eprint {candidate['eprintid']} "
                    f"for {candidate.get('url')} (slug mismatch); DOI match rejected"
                )
            else:
                eprint = candidate

        if eprint is None:
            slug = _slug(npath)
            candidates = by_slug.get(slug, [])
            if len(candidates) == 1 and len(slug_claims.get(slug, [])) == 1:
                eprint = candidates[0]
                anomalies.append(
                    f"{fname}: matched eprint {eprint['eprintid']} by slug only "
                    f"(date drift: post {p.get('path')} vs deposit {eprint.get('url')})"
                )

        if eprint is None:
            anomalies.append(f"{fname}: no BIROn eprint found")
            mapping[fname] = None
        else:
            mapping[fname] = _biron_url(eprint)

    return mapping, anomalies


def unclaimed_blog_eprints(mapping, eprints):
    """Return blog-side eprints that no post claimed, oldest first.

    Blog-side means the deposit carries an eve.gd official_url or names
    eve.gd as its publication; journal articles matched only by DOI are
    not expected to correspond to posts and are excluded. This is the
    review queue for missed matches.
    """
    claimed = {v for v in mapping.values() if v}
    unclaimed = [
        e
        for e in eprints
        if (e.get("url") or e.get("publication") == "eve.gd")
        and _biron_url(e) not in claimed
    ]
    return sorted(unclaimed, key=lambda e: e["eprintid"])


def apply_overrides(mapping, overrides, eprints):
    """Return mapping with hand-curated `{file: eprintid}` overrides applied.

    Overrides exist for deposits whose metadata carries neither a usable
    official_url nor a DOI, so no automatic match is possible.
    """
    by_id = {e["eprintid"]: e for e in eprints}
    out = dict(mapping)
    for fname, eprintid in overrides.items():
        if eprintid not in by_id:
            raise ValueError(f"override for {fname}: eprint {eprintid} not in feed")
        out[fname] = _biron_url(by_id[eprintid])
    return out


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
    for fname, biron in sorted(mapping.items()):
        path = os.path.join(args.posts_dir, fname)
        if not os.path.exists(path):
            print(f"MISSING {fname}", file=sys.stderr)
            missing += 1
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        try:
            new = insert_biron(text, biron=biron)
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
