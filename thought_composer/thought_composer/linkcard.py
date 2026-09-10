"""Fetching Open Graph metadata for Bluesky link-preview cards.

Mastodon builds its own preview server-side; Bluesky shows a card only
when the post embeds one, so the composer scrapes the first link's OG
tags (falling back to <title>) and downloads a thumbnail when one is
offered and small enough to upload.
"""

from html.parser import HTMLParser

import requests

THUMB_MAX_BYTES = 950_000
TIMEOUT = 10
USER_AGENT = "eve.gd thought-composer (+https://eve.gd)"


class _OpenGraphParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.og = {}
        self.title_text = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "meta":
            prop = attributes.get("property", "")
            content = attributes.get("content")
            if prop.startswith("og:") and content:
                self.og.setdefault(prop[3:], content)
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title_text += data


def parse_open_graph(html: str) -> dict:
    """og:title/og:description/og:image (title falling back to <title>)."""
    parser = _OpenGraphParser()
    parser.feed(html)
    return {
        "title": parser.og.get("title") or (parser.title_text.strip() or None),
        "description": parser.og.get("description"),
        "image": parser.og.get("image"),
    }


def fetch_card(url: str, get=None) -> dict | None:
    """A Bluesky external-embed card for a URL, or None when unusable.

    Returns ``{"uri", "title", "description", "thumb_data",
    "thumb_mime"}`` (thumb keys absent when there is no usable image).
    Failures never raise — a thought must still post when a link's site
    is down.
    """
    get = get or requests.get
    try:
        page = get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        if page.status_code != 200:
            return None
        graph = parse_open_graph(page.text)
        if not graph.get("title"):
            return None
        card = {
            "uri": url,
            "title": graph["title"],
            "description": graph.get("description") or "",
        }
        if graph.get("image"):
            thumb = get(
                graph["image"],
                headers={"User-Agent": USER_AGENT},
                timeout=TIMEOUT,
            )
            if (
                thumb.status_code == 200
                and thumb.content
                and len(thumb.content) <= THUMB_MAX_BYTES
            ):
                card["thumb_data"] = thumb.content
                card["thumb_mime"] = thumb.headers.get(
                    "Content-Type", "image/jpeg"
                ).split(";")[0]
        return card
    except Exception:  # noqa: BLE001 — a dead link site must not block posting
        return None
