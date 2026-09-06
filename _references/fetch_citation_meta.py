"""Fetch raw citation metadata for the applied non-DOI reference URLs.

For every live, non-DOI URL used in a post's references: block, GET the
page and harvest whatever citation evidence it exposes — <title>,
OpenGraph, Highwire citation_* tags, Dublin Core, JSON-LD — into
citation_meta.json for downstream normalisation. DOI references are
skipped: the signposting plugin already models those from their
registration metadata at build time. Run from the blog root:

    uv run --with requests --with beautifulsoup4 _references/fetch_citation_meta.py
"""

import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

HERE = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(os.path.dirname(HERE), "_posts")
META_FILE = os.path.join(HERE, "citation_meta.json")

FRONT_MATTER_RE = re.compile(r"\A---\n(.*?\n)---\n", re.DOTALL)
BARE_REF_RE = re.compile(r"^- (https?://\S+)(?: # .*)?$", re.MULTILINE)
DOI_URL_RE = re.compile(r"\Ahttps?://(dx\.)?doi\.org/", re.IGNORECASE)

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0"
)
TIMEOUT = 20
WORKERS = 24
MAX_BYTES = 600_000


REFERENCES_BLOCK_RE = re.compile(
    r"^references:[ \t]*\n((?:(?:- |  ).*\n?)*)", re.MULTILINE
)
BARE_LINE_RE = re.compile(r"\A- (https?://\S+)(?: # .*)?\Z")


def bare_reference_urls(post_text):
    """The bare `- <url>` reference URLs in a post's front matter, DOI-free."""
    m = FRONT_MATTER_RE.match(post_text)
    if not m:
        return []
    block = REFERENCES_BLOCK_RE.search(m.group(1))
    if not block:
        return []
    urls = []
    for line in block.group(1).splitlines():
        bare = BARE_LINE_RE.match(line)
        if bare and not DOI_URL_RE.match(bare.group(1)):
            urls.append(bare.group(1))
    return urls


def _json_ld_node(soup):
    """The most citation-like JSON-LD node on the page, or {}."""
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except (ValueError, TypeError):
            continue
        nodes = data if isinstance(data, list) else [data]
        expanded = []
        for node in nodes:
            if isinstance(node, dict) and isinstance(node.get("@graph"), list):
                expanded.extend(x for x in node["@graph"] if isinstance(x, dict))
            elif isinstance(node, dict):
                expanded.append(node)
        for node in expanded:
            if "headline" in node or "datePublished" in node or "author" in node:
                return node
    return {}


def _ld_names(value):
    """Every name string in a JSON-LD person/organisation value."""
    if isinstance(value, list):
        return [name for item in value for name in _ld_names(item)]
    if isinstance(value, dict):
        name = value.get("name")
        return [name.strip()] if isinstance(name, str) and name.strip() else []
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _trim(value, limit=300):
    return re.sub(r"\s+", " ", value).strip()[:limit]


def extract_page_meta(html_text):
    """Raw citation evidence from a page: title, authors, date, site, type.

    Collects, in rough order of trustworthiness: Highwire citation_* tags,
    JSON-LD (headline/name, author names, datePublished, publisher,
    isPartOf), OpenGraph (og:title, og:site_name, og:type,
    article:published_time, article:author), Dublin Core, plain meta
    author/date, and the <title> element. Only evidence present in the
    page appears in the result; every value is a trimmed string (authors:
    list of strings).
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_text, "html.parser")
    by_name = {}
    by_prop = {}
    for tag in soup.find_all("meta"):
        content = (tag.get("content") or "").strip()
        if not content:
            continue
        name = (tag.get("name") or "").lower()
        prop = (tag.get("property") or "").lower()
        if name:
            by_name.setdefault(name, []).append(content)
        if prop:
            by_prop.setdefault(prop, []).append(content)

    def first(table, *keys):
        for key in keys:
            if key in table:
                return table[key][0]
        return None

    ld = _json_ld_node(soup)
    ld_str = lambda key: ld.get(key) if isinstance(ld.get(key), str) else None

    title = (
        first(by_name, "citation_title", "dc.title")
        or ld_str("headline")
        or ld_str("name")
        or first(by_prop, "og:title")
        or (soup.title.get_text() if soup.title else None)
    )
    authors = (
        by_name.get("citation_author")
        or _ld_names(ld.get("author"))
        or by_name.get("dc.creator")
        or by_name.get("author")
        or by_prop.get("article:author")
    )
    date = (
        first(by_name, "citation_publication_date", "citation_date")
        or ld_str("datePublished")
        or first(by_prop, "article:published_time")
        or first(by_name, "dc.date", "date")
    )
    site = (
        first(by_name, "citation_journal_title")
        or first(by_prop, "og:site_name")
        or next(iter(_ld_names(ld.get("publisher"))), None)
        or next(iter(_ld_names(ld.get("isPartOf"))), None)
    )
    ld_type = ld.get("@type")
    if isinstance(ld_type, list):
        ld_type = ld_type[0] if ld_type else None
    page_type = ld_type or first(by_prop, "og:type")

    meta = {}
    if title:
        meta["title"] = _trim(title)
    if authors:
        meta["authors"] = [_trim(a) for a in authors if a.strip()][:8]
    if date:
        meta["date"] = _trim(date, 40)
    if site:
        meta["site"] = _trim(site, 120)
    if page_type:
        meta["type"] = _trim(str(page_type), 40)
    return meta


def _fetch(url):
    import requests

    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,*/*"}
    response = requests.get(
        url, headers=headers, timeout=TIMEOUT, allow_redirects=True, stream=True
    )
    content = response.raw.read(MAX_BYTES, decode_content=True)
    response.close()
    ctype = response.headers.get("Content-Type", "")
    return response.status_code, ctype, content


def check(url):
    import requests

    try:
        status, ctype, content = _fetch(url)
    except requests.RequestException as exc:
        return {"fetched": False, "error": type(exc).__name__}
    if status >= 400:
        return {"fetched": False, "status": status}
    if "html" not in ctype and b"<html" not in content[:2000].lower():
        return {"fetched": True, "status": status, "content_type": ctype.split(";")[0]}
    try:
        html_text = content.decode("utf-8", errors="replace")
    except Exception:
        return {"fetched": True, "status": status}
    meta = extract_page_meta(html_text)
    meta.update({"fetched": True, "status": status})
    return meta


def main():
    urls = []
    seen = set()
    for name in sorted(os.listdir(POSTS_DIR)):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(POSTS_DIR, name), encoding="utf-8") as f:
            text = f.read()
        for url in bare_reference_urls(text):
            if url not in seen:
                seen.add(url)
                urls.append(url)

    results = {}
    if os.path.exists(META_FILE):
        with open(META_FILE, encoding="utf-8") as f:
            results = json.load(f)
    todo = [u for u in urls if u not in results]
    print(f"{len(urls)} unique non-DOI reference URLs; {len(todo)} to fetch", flush=True)

    lock = Lock()
    done = 0

    def flush():
        with open(META_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=0, ensure_ascii=False)

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(check, url): url for url in todo}
        for future in as_completed(futures):
            with lock:
                results[futures[future]] = future.result()
                done += 1
                if done % 200 == 0:
                    flush()
                    print(f"fetched {done}/{len(todo)}", flush=True)
    flush()
    titled = sum(1 for v in results.values() if v.get("title"))
    print(f"done: {len(results)} fetched, {titled} with a title")
    return 0


if __name__ == "__main__":
    sys.exit(main())
