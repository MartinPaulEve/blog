"""Extract candidate external reference URLs from every post lacking references.

Builds manifest.json mapping each post file to its external body links, in
order of first appearance, with the link text and a little surrounding
context for downstream labelling. URLs inside code regions (fenced blocks,
<pre>, <code>, inline backticks) and image constructs are not references
and are skipped, as are internal (eve.gd / site-relative) links. Run from
the blog root:

    uv run _references/extract_manifest.py
"""

import glob
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(os.path.dirname(HERE), "_posts")

FRONT_MATTER_RE = re.compile(r"\A---\n(.*?\n)---\n", re.DOTALL)

INTERNAL_HOSTS = {
    "eve.gd",
    "www.eve.gd",
    "localhost",
    "127.0.0.1",
}


CODE_REGION_RES = [
    re.compile(r"```.*?```", re.DOTALL),
    re.compile(r"~~~.*?~~~", re.DOTALL),
    re.compile(r"<pre\b.*?</pre>", re.DOTALL | re.IGNORECASE),
    re.compile(r"<code\b.*?</code>", re.DOTALL | re.IGNORECASE),
    re.compile(r"`[^`\n]+`"),
]
IMG_MD_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
EMBED_TAG_RE = re.compile(
    r"<(?:img|script|iframe|embed|source|video|audio)\b[^>]*>", re.IGNORECASE
)
MD_LINK_RE = re.compile(r"\[([^\]]*)\]\(\s*(https?://[^)\s]+)\s*\)")
HREF_RE = re.compile(r"""href\s*=\s*["'](https?://[^"']+)["']""", re.IGNORECASE)
ANCHOR_RE = re.compile(
    r"""<a\b[^>]*href\s*=\s*["']([^"']+)["'][^>]*>(.*?)</a>""",
    re.IGNORECASE | re.DOTALL,
)
BARE_URL_RE = re.compile(r"""https?://[^\s<>"')\]]+""")

TRAILING_PUNCT = ".,;:!?"


def _strip_non_reference_regions(body):
    text = body
    for pattern in CODE_REGION_RES:
        text = pattern.sub(lambda m: " " * len(m.group(0)), text)
    text = IMG_MD_RE.sub(lambda m: " " * len(m.group(0)), text)
    return EMBED_TAG_RE.sub(lambda m: " " * len(m.group(0)), text)


def _clean_url(url):
    url = html.unescape(url)
    return url.rstrip(TRAILING_PUNCT)


def _is_internal(url):
    host = re.sub(r"\Ahttps?://", "", url).split("/")[0].split(":")[0].lower()
    return host in INTERNAL_HOSTS


def extract_external_urls(body):
    """External reference URLs from a post body, in order, deduplicated.

    Covers HTML href attributes, markdown links, and bare URLs in prose.
    Skips code regions, images (markdown and <img>), and internal links.
    """
    text = _strip_non_reference_regions(body)
    found = []
    spans = []
    for m in MD_LINK_RE.finditer(text):
        found.append((m.start(2), m.group(2)))
        spans.append(m.span())
    for m in HREF_RE.finditer(text):
        found.append((m.start(1), m.group(1)))
        spans.append(m.span())

    blanked = list(text)
    for start, end in spans:
        blanked[start:end] = " " * (end - start)
    for m in BARE_URL_RE.finditer("".join(blanked)):
        found.append((m.start(), m.group(0)))

    urls, seen = [], set()
    for _, raw in sorted(found, key=lambda item: item[0]):
        url = _clean_url(raw)
        if not url or _is_internal(url) or url in seen:
            continue
        seen.add(url)
        urls.append(url)
    return urls


def link_contexts(body, urls):
    """For each url, (link text or None, ~240 chars of surrounding prose)."""
    text = _strip_non_reference_regions(body)
    contexts = []
    for url in urls:
        link_text = None
        position = None
        for m in MD_LINK_RE.finditer(text):
            if _clean_url(m.group(2)) == url:
                link_text = m.group(1).strip() or None
                position = m.start()
                break
        if position is None:
            for m in ANCHOR_RE.finditer(text):
                if _clean_url(m.group(1)) == url:
                    link_text = (
                        re.sub(r"<[^>]+>", "", m.group(2)).strip() or None
                    )
                    position = m.start()
                    break
        if position is None:
            index = text.find(url)
            position = index if index >= 0 else 0
        window = text[max(0, position - 80): position + 160]
        contexts.append((link_text, re.sub(r"\s+", " ", window).strip()))
    return contexts


def main():
    manifest = {}
    for path in sorted(glob.glob(os.path.join(POSTS_DIR, "*.md"))):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        m = FRONT_MATTER_RE.match(text)
        if not m:
            continue
        if re.search(r"^references:", m.group(1), re.MULTILINE):
            continue
        body = text[m.end():]
        urls = extract_external_urls(body)
        if not urls:
            continue
        contexts = link_contexts(body, urls)
        manifest[os.path.basename(path)] = [
            {"url": url, "text": text_, "context": ctx}
            for url, (text_, ctx) in zip(urls, contexts)
        ]

    out = os.path.join(HERE, "manifest.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, ensure_ascii=False)
    total = sum(len(v) for v in manifest.values())
    print(f"{len(manifest)} posts with external links; {total} link instances")
    return 0


if __name__ == "__main__":
    sys.exit(main())
