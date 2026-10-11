# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""Mirror the built blog posts to smol.pub as text-only gemtext.

Run from the blog root after a `jekyll build` (see README.md for the spec):

    uv run --env-file .env _smolpub/sync_smolpub.py --dry-run    # convert only
    uv run --env-file .env _smolpub/sync_smolpub.py --only SLUG   # one post
    uv run --env-file .env _smolpub/sync_smolpub.py               # new + changed
    uv run --env-file .env _smolpub/sync_smolpub.py --force       # everything

Each post's built page under _site (the post-body div, so every era of
markup, Liquid tag and footnote has already been rendered by Jekyll) is
converted to gemtext, written to _smolpub/out/<slug>.gmi, and POSTed to
smol.pub through the same form endpoints its smolpub.sh uses. The token is
SMOL_PUB_KEY (environment or .env). _data/smolpub.yml records the content
hash of everything pushed, so only new or changed posts are sent, and the
post layout reads the same file to decide whether to show the gem.eve.gd
links.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import ssl
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import date, datetime
from html.parser import HTMLParser

SITE_URL = "https://eve.gd"
API_HOST = "https://smol.pub"
SAVE_URL = f"{API_HOST}/posts/save"
UPDATE_URL = f"{API_HOST}/posts/{{slug}}/update"
TIMEOUT = 30
DEFAULT_SITE = "_site"
DEFAULT_OUT = "_smolpub/out"
DEFAULT_LEDGER = "_data/smolpub.yml"

BODY_START = re.compile(r'<div class="post-body[^"]*">')
TITLE_RE = re.compile(r'<h1 class="post-title[^"]*">(.*?)</h1>', re.DOTALL)
PUBLISHED_RE = re.compile(r'<time[^>]*itemprop="datePublished[^"]*"[^>]*datetime="([^"]+)"')
MODIFIED_RE = re.compile(r'<time[^>]*itemprop="dateModified"[^>]*datetime="([^"]+)"')
DIV_TAG = re.compile(r"<div\b[^>]*>|</div>")


class SmolPubError(RuntimeError):
    """A post could not be published."""


# --- token ---------------------------------------------------------------------


def load_token(root, env=None):
    """SMOL_PUB_KEY from the environment, else the root .env file, else None."""
    env = os.environ if env is None else env
    token = (env.get("SMOL_PUB_KEY") or "").strip()
    if token:
        return token
    env_file = pathlib.Path(root) / ".env"
    if env_file.is_file():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("SMOL_PUB_KEY="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                return value or None
    return None


# --- built site --------------------------------------------------------------------


def extract_post_body(page_html):
    """The inner HTML of the post-body div (nested divs balanced)."""
    start = BODY_START.search(page_html)
    if not start:
        raise ValueError("no post-body div in page")
    depth = 1
    pos = start.end()
    for tag in DIV_TAG.finditer(page_html, pos):
        depth += -1 if tag.group().startswith("</") else 1
        if depth == 0:
            return page_html[pos:tag.start()]
    return page_html[pos:]


def source_slugs(posts_dir):
    """The URL slugs of the Markdown posts in ``posts_dir`` (None if absent)."""
    posts = pathlib.Path(posts_dir)
    if not posts.is_dir():
        return None
    return {re.sub(r"^\d{4}-\d{2}-\d{2}-", "", p.stem) for p in posts.glob("*.md")}


def collect_posts(site_dir, posts_dir=None):
    """Every built post page: url_slug, title, url, dates and body HTML.

    Post pages live at _site/YYYY/MM/DD/<slug>/ beside the metadata.json the
    build writes for them (@type BlogPosting); anything else under a dated
    path is ignored, as is a stale page whose source post no longer exists
    (``posts_dir`` defaults to the _posts beside the site).
    """
    site = pathlib.Path(site_dir)
    if not site.is_dir():
        raise FileNotFoundError(f"{site} is not a built site; run jekyll build")
    sources = source_slugs(posts_dir if posts_dir is not None else site.parent / "_posts")
    posts = []
    for page in sorted(site.glob("[0-9]*/[0-9]*/[0-9]*/*/index.html")):
        if sources is not None and page.parent.name not in sources:
            continue
        html = page.read_text()
        try:
            body = extract_post_body(html)
        except ValueError:
            continue
        meta = page_metadata(page.with_name("metadata.json"), html)
        if meta is None:
            continue
        posts.append({
            "url_slug": page.parent.name,
            "title": meta.get("title") or page.parent.name,
            "url": meta.get("url") or f"{SITE_URL}/{page.parent.relative_to(site)}/",
            "date_published": meta.get("date_published"),
            "date_modified": meta.get("date_modified"),
            "body_html": body,
        })
    return posts


def page_metadata(meta_file, html):
    """Title, URL and dates from the page's metadata.json, falling back to
    the page's own markup (the sidecar is missing for a few non-ASCII
    paths). None when the page is not a post at all."""
    if meta_file.is_file():
        try:
            meta = json.loads(meta_file.read_text())
        except ValueError:
            meta = {}
        if meta.get("@type") == "BlogPosting":
            return {
                "title": meta.get("name") or meta.get("headline"),
                "url": meta.get("url"),
                "date_published": meta.get("datePublished"),
                "date_modified": meta.get("dateModified"),
            }
    title = TITLE_RE.search(html)
    if not title:
        return None
    published = PUBLISHED_RE.search(html)
    modified = MODIFIED_RE.search(html)
    return {
        "title": _collapse(html_text(title.group(1))),
        "url": None,
        "date_published": published.group(1)[:10] if published else None,
        "date_modified": modified.group(1)[:10] if modified else None,
    }


def html_text(fragment):
    """Plain text of an HTML fragment (tags stripped, entities decoded)."""
    return parse_html(fragment).text()


# --- HTML -> gemtext -----------------------------------------------------------------

VOID = {"br", "hr", "img", "input", "meta", "link", "source", "wbr", "area",
        "base", "col", "embed", "param", "track"}
DROP = {"script", "style", "noscript", "template", "svg", "math", "canvas",
        "button", "input", "select", "textarea", "head", "title", "meta",
        "link", "option"}
HEADINGS = {"h1": "## ", "h2": "## ", "h3": "### ", "h4": "### ",
            "h5": "### ", "h6": "### "}
LISTS = {"ul", "ol", "dl"}
CONTAINERS = {"p", "div", "section", "article", "main", "aside", "header",
              "footer", "nav", "figure", "figcaption", "details", "summary",
              "form", "fieldset", "legend", "address", "center", "body",
              "html", "dd", "dt", "li", "td", "th", "tr", "thead", "tbody",
              "tfoot", "caption", "colgroup"}
EMBEDS = {"iframe", "embed", "object", "video", "audio"}
BLOCKS = (set(HEADINGS) | LISTS | CONTAINERS | EMBEDS
          | {"blockquote", "pre", "table", "hr"})


class Node:
    __slots__ = ("tag", "attrs", "children")

    def __init__(self, tag, attrs=None):
        self.tag = tag
        self.attrs = attrs or {}
        self.children = []

    def classes(self):
        return (self.attrs.get("class") or "").split()

    def find(self, tag):
        for child in self.children:
            if isinstance(child, Node):
                if child.tag == tag:
                    yield child
                yield from child.find(tag)

    def text(self):
        """Raw concatenated text of all descendants (no normalisation)."""
        parts = []
        for child in self.children:
            if isinstance(child, str):
                parts.append(child)
            elif child.tag == "br":
                parts.append("\n")
            elif child.tag not in DROP:
                parts.append(child.text())
        return "".join(parts)


class TreeBuilder(HTMLParser):
    """A forgiving tag soup -> Node tree builder."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("root")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        if tag == "p" and self.stack[-1].tag == "p":
            self.stack.pop()  # an unclosed paragraph
        if tag == "li" and self.stack[-1].tag == "li":
            self.stack.pop()  # an unclosed list item
        node = Node(tag, {k: (v if v is not None else "") for k, v in attrs})
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.stack.pop()

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def parse_html(html):
    builder = TreeBuilder()
    builder.feed(html)
    builder.close()
    return builder.root


class Links:
    """Link lines gathered while rendering a scope, deduplicated by URL."""

    def __init__(self):
        self.items = []
        self.seen = set()

    def add(self, url, text=""):
        if not url or url in self.seen:
            return
        self.seen.add(url)
        self.items.append((url, text))

    def lines(self):
        return [f"=> {url} {text}".rstrip() if text and text != url
                else f"=> {url}" for url, text in self.items]


class DroppedLinks(Links):
    def add(self, url, text=""):
        return


def _collapse(text):
    return re.sub(r"\s+", " ", text).strip()


def iri_to_uri(url):
    """Percent-encode the non-ASCII characters of a URL (gemtext link lines
    carry URIs, and the blog's own URLs include accented slugs)."""
    return urllib.parse.quote(url, safe=":/?#[]@!$&'()*+,;=%")


# A text line that happens to start like a heading, link, list item or
# preformat toggle would be read as one; a leading space keeps it text.
_MARKUP_START = re.compile(r"^(#|=>|\* |```)")


def _escape_text_line(line):
    return " " + line if _MARKUP_START.match(line) else line


class Inline:
    """Accumulates inline text (split on <br>) and its links for one run."""

    def __init__(self, renderer, links, prefix=""):
        self.renderer = renderer
        self.links = links
        self.prefix = prefix
        self.lines = [[]]

    def text(self, data):
        self.lines[-1].append(data)

    def newline(self):
        self.lines.append([])

    def empty(self):
        return not any(_collapse("".join(line)) for line in self.lines)

    def flush(self):
        out = []
        for parts in self.lines:
            line = _collapse("".join(parts))
            if line:
                out.append(self.prefix + _escape_text_line(line))
        self.lines = [[]]
        return out


class Renderer:
    def __init__(self, base_url):
        self.base = base_url.rstrip("/") + "/"
        self.blocks = []
        self.quote = ""

    # -- helpers ------------------------------------------------------------

    def emit(self, lines):
        lines = [line for line in lines if line is not None]
        if lines:
            self.blocks.append(lines)

    def absolute(self, href):
        href = (href or "").strip()
        if not href or href.startswith("#") or href.lower().startswith("javascript:"):
            return None
        return iri_to_uri(urllib.parse.urljoin(self.base, href))

    @staticmethod
    def skip(node):
        return node.tag in DROP or "hidden" in node.attrs

    @staticmethod
    def is_footnote_ref(node):
        if node.tag != "sup":
            return False
        anchors = [c for c in node.children if isinstance(c, Node) and c.tag == "a"]
        return any((a.attrs.get("href") or "").startswith("#fn")
                   or "footnote" in a.classes()
                   or a.attrs.get("role") == "doc-noteref" for a in anchors)

    @staticmethod
    def is_backlink(node):
        return node.tag == "a" and (
            "reversefootnote" in node.classes()
            or node.attrs.get("role") == "doc-backlink"
            or (node.attrs.get("href") or "").startswith("#fnref"))

    # -- inline ---------------------------------------------------------------

    def inline(self, node, buf):
        """Pour an inline node's content into ``buf``."""
        for child in node.children:
            self.inline_node(child, buf)

    def inline_node(self, child, buf):
        """Pour one inline node (or text) into ``buf``."""
        if isinstance(child, str):
            buf.text(child)
        elif self.skip(child):
            return
        elif child.tag == "br":
            buf.newline()
        elif child.tag == "img":
            url = self.absolute(child.attrs.get("src"))
            alt = _collapse(child.attrs.get("alt") or "")
            buf.links.add(url, f"Image: {alt}" if alt else "Image")
        elif child.tag == "a":
            if self.is_backlink(child):
                return
            probe = Inline(self, DroppedLinks())
            self.inline(child, probe)
            text = " ".join(probe.flush())
            self.inline(child, buf)
            url = self.absolute(child.attrs.get("href"))
            if url:
                buf.links.add(url, text)
        elif self.is_footnote_ref(child):
            probe = Inline(self, DroppedLinks())
            self.inline(child, probe)
            buf.text(f"[{' '.join(probe.flush())}]")
        elif child.tag in BLOCKS:
            # Block markup inside an inline run (legacy <p><blockquote>):
            # finish the run, render the block, start a fresh run.
            self.emit(buf.flush())
            self.block(child, buf.links)
        else:
            self.inline(child, buf)

    def inline_text(self, node, links, stop=()):
        """One line of text for a node, treating nested blocks as spaces.

        Nested nodes whose tag is in ``stop`` are skipped (the caller renders
        them separately) and returned.
        """
        deferred = []
        buf = Inline(self, links)

        def walk(n):
            for child in n.children:
                if isinstance(child, str):
                    buf.text(child)
                elif self.skip(child):
                    continue
                elif child.tag in stop:
                    deferred.append(child)
                elif child.tag == "br":
                    buf.text(" ")
                elif child.tag == "img":
                    url = self.absolute(child.attrs.get("src"))
                    alt = _collapse(child.attrs.get("alt") or "")
                    buf.links.add(url, f"Image: {alt}" if alt else "Image")
                elif child.tag == "a":
                    if self.is_backlink(child):
                        continue
                    probe = Inline(self, DroppedLinks())
                    self.inline(child, probe)
                    buf.text(" ".join(probe.flush()))
                    url = self.absolute(child.attrs.get("href"))
                    if url:
                        buf.links.add(url, " ".join(probe.flush()) or
                                      _collapse(child.text()))
                elif self.is_footnote_ref(child):
                    buf.text(f"[{_collapse(child.text())}]")
                elif child.tag == "pre":
                    buf.text(" " + child.text() + " ")
                else:
                    if child.tag in BLOCKS:
                        buf.text(" ")
                    walk(child)
                    if child.tag in BLOCKS:
                        buf.text(" ")

        walk(node)
        return " ".join(buf.flush()), deferred

    # -- blocks --------------------------------------------------------------------

    def container(self, node, links=None):
        """Render a container: inline runs become text blocks, each with its
        own links unless an enclosing scope (list, quote, table) owns them."""
        own = links is None
        buf = Inline(self, links or Links(), prefix=self.quote)
        for child in node.children:
            if isinstance(child, str):
                buf.text(child)
            elif self.skip(child):
                continue
            elif child.tag == "br":
                buf.newline()
            elif child.tag in BLOCKS:
                self.emit(buf.flush() + (buf.links.lines() if own else []))
                if own:
                    buf = Inline(self, Links(), prefix=self.quote)
                self.block(child, links)
            else:
                self.inline_node(child, buf)
        self.emit(buf.flush() + (buf.links.lines() if own else []))

    def block(self, node, links=None):
        tag = node.tag
        if self.skip(node):
            return
        if tag in HEADINGS:
            text, _ = self.inline_text(node, DroppedLinks())
            if text:
                self.emit([HEADINGS[tag] + text])
        elif tag == "hr":
            return
        elif tag == "pre":
            self.preformatted(node)
        elif tag in LISTS:
            self.list(node, links)
        elif tag == "blockquote":
            self.blockquote(node, links)
        elif tag == "table":
            self.table(node, links)
        elif tag in EMBEDS:
            url = self.absolute(node.attrs.get("src") or node.attrs.get("data"))
            if url:
                scope = links or Links()
                scope.add(url, "Embedded content")
                if links is None:
                    self.emit(scope.lines())
        elif tag == "div" and "footnotes" in node.classes():
            self.footnotes(node)
        elif tag == "img":
            scope = links or Links()
            url = self.absolute(node.attrs.get("src"))
            alt = _collapse(node.attrs.get("alt") or "")
            scope.add(url, f"Image: {alt}" if alt else "Image")
            if links is None:
                self.emit(scope.lines())
        else:
            self.container(node, links)

    def preformatted(self, node):
        text = node.text().replace("\r\n", "\n")
        if text.endswith("\n"):
            text = text[:-1]
        if not text.strip():
            return
        lines = [(" " + line) if line.startswith("```") else line
                 for line in text.split("\n")]
        self.emit(["```", *lines, "```"])

    def list(self, node, links=None):
        scope = links or Links()
        self.list_items(node, scope, [])
        if links is None and scope.items:
            self.blocks[-1].extend(scope.lines()) if self.blocks else self.emit(scope.lines())

    def list_items(self, node, scope, out):
        own = not out
        counter = 0
        for child in node.children:
            if isinstance(child, str) or self.skip(child):
                continue
            if child.tag in ("li", "dt", "dd"):
                counter += 1
                text, nested = self.inline_text(child, scope, stop=LISTS)
                if text:
                    marker = f"{counter}. " if node.tag == "ol" else "* "
                    out.append(self.quote + marker + text)
                for sub in nested:
                    self.list_items(sub, scope, out)
            elif child.tag in LISTS:
                self.list_items(child, scope, out)
            else:
                text, nested = self.inline_text(child, scope, stop=LISTS)
                if text:
                    out.append(self.quote + "* " + text)
                for sub in nested:
                    self.list_items(sub, scope, out)
        if own:
            self.emit(out)

    def blockquote(self, node, links=None):
        scope = links or Links()
        saved = self.quote
        self.quote = saved + "> "
        start = len(self.blocks)
        self.container(node, scope)
        self.quote = saved
        if links is None and scope.items:
            if len(self.blocks) > start:
                self.blocks[-1].extend(scope.lines())
            else:
                self.emit(scope.lines())

    def table(self, node, links=None):
        scope = links or Links()
        rows = []
        for row in node.find("tr"):
            cells = []
            for cell in row.children:
                if isinstance(cell, Node) and cell.tag in ("td", "th") and not self.skip(cell):
                    text, _ = self.inline_text(cell, scope)
                    cells.append(text)
            line = " | ".join(cells).strip(" |")
            if line:
                rows.append(self.quote + line)
        if links is None:
            rows.extend(scope.lines())
        self.emit(rows)

    def footnotes(self, node):
        notes = []
        counter = 0
        for item in node.find("li"):
            counter += 1
            match = re.search(r"fn:?(\w+)", item.attrs.get("id") or "")
            label = match.group(1) if match else str(counter)
            scope = Links()
            text, _ = self.inline_text(item, scope)
            if text:
                notes.append(f"[{label}] {text}")
                notes.extend(scope.lines())
        if notes:
            self.emit(["## Notes"])
            self.emit(notes)

    # -- entry --------------------------------------------------------------------

    def render(self, root):
        self.container(root)
        return "\n\n".join("\n".join(block) for block in self.blocks)


def html_to_gemtext(html, base_url=SITE_URL):
    """Convert a fragment of post HTML to gemtext (see README for the mapping)."""
    return Renderer(base_url).render(parse_html(html))


# --- documents ---------------------------------------------------------------------


def _long_date(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value)[:19])
    except ValueError:
        return str(value)
    return f"{parsed.day} {parsed:%B %Y}"


def render_document(meta, body):
    """The full gemtext document: title heading, provenance, body."""
    published = _long_date(meta.get("date_published"))
    modified = _long_date(meta.get("date_modified"))
    provenance = "Originally published on eve.gd"
    if published:
        provenance += f" on {published}"
    if modified and modified != published:
        provenance += f", last updated {modified}"
    provenance += "."
    lines = [
        f"# {_collapse(meta['title'])}",
        "",
        provenance,
        f"=> {iri_to_uri(meta['url'])} Read this post on the web (with images, PDF and citation details)",
        "",
        body.strip(),
        "",
    ]
    return "\n".join(lines)


def split_document(document):
    """(title, content) as smol.pub wants them: the content starts after the
    blank line that follows the title heading."""
    lines = document.split("\n")
    title = lines[0][2:].strip() if lines and lines[0].startswith("# ") else ""
    content = "\n".join(lines[2:]) if len(lines) > 2 else ""
    return title, content.strip("\n") + "\n"


def smol_slug(url_slug):
    """The flat smol.pub slug for a URL slug: ASCII, lower case, hyphens."""
    ascii_text = unicodedata.normalize("NFKD", url_slug).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")


def content_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# --- planning and publishing --------------------------------------------------------


def plan_sync(documents, ledger, force=False, only=None):
    """The documents to push: new or changed ones, or everything with
    ``force``, or just those named in ``only`` (URL or smol.pub slug)."""
    if only:
        wanted = set(only)
        return [d for d in documents
                if d["url_slug"] in wanted or d["slug"] in wanted]
    picked = []
    for doc in documents:
        entry = ledger.get(doc["url_slug"])
        if force or not entry or entry.get("hash") != content_hash(doc["content"]):
            picked.append(doc)
    return picked


def encode_multipart(fields):
    """(content_type, body) for a multipart/form-data POST of text fields."""
    boundary = uuid.uuid4().hex
    body = bytearray()
    for name, value in fields.items():
        body += f"--{boundary}\r\n".encode()
        body += f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        body += str(value).encode("utf-8") + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    return f"multipart/form-data; boundary={boundary}", bytes(body)


_SSL_CONTEXT = None


def _ssl_context():
    """Default TLS context, falling back to the system CA bundle: the
    uv-managed Python on NixOS ships with an empty default cert store."""
    global _SSL_CONTEXT
    if _SSL_CONTEXT is None:
        _SSL_CONTEXT = ssl.create_default_context()
        if not _SSL_CONTEXT.get_ca_certs():
            for bundle in ("/etc/ssl/certs/ca-certificates.crt",
                           "/etc/ssl/certs/ca-bundle.crt"):
                if pathlib.Path(bundle).is_file():
                    _SSL_CONTEXT.load_verify_locations(bundle)
                    break
    return _SSL_CONTEXT


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def post_form(url, fields, token):
    """POST the fields as smol.pub's CLI does; returns the HTTP status."""
    content_type, body = encode_multipart(fields)
    request = urllib.request.Request(url, data=body, method="POST", headers={
        "Content-Type": content_type,
        "Cookie": f"smolpub={token}",
        "User-Agent": "eve.gd smol.pub mirror (+https://eve.gd)",
    })
    opener = urllib.request.build_opener(
        _NoRedirect, urllib.request.HTTPSHandler(context=_ssl_context()))
    try:
        with opener.open(request, timeout=TIMEOUT) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except (urllib.error.URLError, OSError) as exc:
        raise SmolPubError(f"{url}: {exc}") from exc


def publish(slug, title, content, token, http=post_form, known=False):
    """Create or update one post; returns "created" or "updated".

    /posts/save answers 302 when it creates the post and something else when
    the slug already exists, in which case /posts/<slug>/update replaces it
    (``known`` goes straight there).
    """
    fields = {"title": title, "slug": slug, "content": content}
    if not known:
        status = http(SAVE_URL, fields, token)
        if status == 302:
            return "created"
    status = http(UPDATE_URL.format(slug=slug), fields, token)
    if 200 <= status < 400:
        return "updated"
    raise SmolPubError(f"smol.pub refused {slug!r} (HTTP {status})")


def update_ledger(ledger, url_slug, slug, digest, today):
    out = dict(ledger)
    out[url_slug] = {"slug": slug, "hash": digest, "synced": str(today)}
    return out


def _load_ledger(path):
    import yaml
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text()) or {}
    return {str(k): v for k, v in data.items()}


def _save_ledger(path, ledger):
    import yaml
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(ledger, sort_keys=True, allow_unicode=True,
                                   default_flow_style=False))


# --- CLI ----------------------------------------------------------------------------


def build_documents(posts):
    documents = []
    for post in posts:
        body = html_to_gemtext(post["body_html"])
        document = render_document(post, body)
        title, content = split_document(document)
        documents.append({
            "url_slug": post["url_slug"],
            "slug": smol_slug(post["url_slug"]),
            "title": title,
            "content": content,
            "document": document,
        })
    return documents


def main(argv=None, http=post_form, env=None, today=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="convert and report; no network, no ledger")
    parser.add_argument("--force", action="store_true",
                        help="push every post, changed or not")
    parser.add_argument("--only", nargs="+", metavar="SLUG",
                        help="push just these posts (URL or smol.pub slug)")
    parser.add_argument("--limit", type=int, default=0,
                        help="push at most this many posts this run")
    parser.add_argument("--sleep", type=float, default=0.5,
                        help="seconds between requests")
    parser.add_argument("--site", default=DEFAULT_SITE)
    parser.add_argument("--posts", default="_posts",
                        help="source posts; built pages without one are skipped")
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--ledger", default=DEFAULT_LEDGER)
    args = parser.parse_args(argv)

    root = pathlib.Path.cwd()
    try:
        posts = collect_posts(root / args.site, posts_dir=root / args.posts)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    documents = build_documents(posts)

    out_dir = root / args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    for doc in documents:
        (out_dir / f"{doc['slug']}.gmi").write_text(doc["document"])
    print(f"converted {len(documents)} post(s) to {out_dir}")

    ledger_path = root / args.ledger
    ledger = _load_ledger(ledger_path)
    planned = plan_sync(documents, ledger, force=args.force, only=args.only)
    if args.limit:
        planned = planned[:args.limit]
    new = sum(1 for d in planned if d["url_slug"] not in ledger)
    print(f"{len(planned)} to push ({new} new, {len(planned) - new} changed); "
          f"{len(documents) - len(planned)} up to date")
    if args.dry_run:
        for doc in planned:
            print(f"  would push {doc['slug']}")
        return 0
    if not planned:
        return 0

    token = load_token(root, env)
    if not token:
        print("ERROR: SMOL_PUB_KEY not set (environment or .env)", file=sys.stderr)
        return 2

    failures = 0
    stamp = today or date.today().isoformat()
    for index, doc in enumerate(planned):
        known = doc["url_slug"] in ledger
        try:
            outcome = publish(doc["slug"], doc["title"], doc["content"], token,
                              http=http, known=known)
        except SmolPubError as exc:
            failures += 1
            print(f"  FAILED {doc['slug']}: {exc}", file=sys.stderr)
            continue
        ledger = update_ledger(ledger, doc["url_slug"], doc["slug"],
                               content_hash(doc["content"]), stamp)
        _save_ledger(ledger_path, ledger)
        print(f"  {outcome} {doc['slug']}")
        if args.sleep and index + 1 < len(planned):
            time.sleep(args.sleep)

    if failures:
        print(f"{failures} post(s) failed; the next run retries them",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
