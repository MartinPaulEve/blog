"""Counting, link detection and thread splitting for short thoughts.

Bluesky's limit is 300 grapheme clusters per post; Mastodon's is per
instance (hcommons.social allows 1,000 characters, overridable via
MASTODON_CHARACTER_LIMIT) with every URL counted as 23. Each service
gets its own thread split against its own limit — a thought that
threads on Bluesky may fit Mastodon in one post. The words themselves
are never altered: segments are cut only at existing whitespace
(boundary whitespace is consumed by the cut), or mid-token as a last
resort when a single token exceeds the limit outright.
"""

import os

import regex

BLUESKY_LIMIT = 300
MASTODON_LIMIT = int(os.environ.get("MASTODON_CHARACTER_LIMIT", "1000"))
MASTODON_URL_LENGTH = 23

URL_RE = regex.compile(r"https?://\S+")
GRAPHEME_RE = regex.compile(r"\X")
TRAILING_PUNCTUATION = ".,;:!?…'\"”’"


def grapheme_length(text: str) -> int:
    """The Bluesky length of text: extended grapheme clusters."""
    return len(GRAPHEME_RE.findall(text))


def mastodon_length(text: str) -> int:
    """The Mastodon length of text: characters, URLs counting as 23."""
    length = len(text)
    for link in find_links(text):
        length -= len(link["url"]) - MASTODON_URL_LENGTH
    return length


def _trim_url(url: str) -> str:
    while url:
        if url[-1] in TRAILING_PUNCTUATION or url[-1] == ")" and url.count("(") < url.count(")"):
            url = url[:-1]
        else:
            break
    return url


def find_links(text: str) -> list[dict]:
    """The http(s) URLs in text with their UTF-8 byte ranges.

    Returns ``[{"url", "byte_start", "byte_end"}]`` in order. Trailing
    punctuation (and an unbalanced closing parenthesis) is not part of
    the URL.
    """
    links = []
    for match in URL_RE.finditer(text):
        url = _trim_url(match.group(0))
        if len(url) <= len("https://"):
            continue
        byte_start = len(text[: match.start()].encode("utf-8"))
        links.append(
            {
                "url": url,
                "byte_start": byte_start,
                "byte_end": byte_start + len(url.encode("utf-8")),
            }
        )
    return links


def _bluesky_fits(segment: str) -> bool:
    return grapheme_length(segment) <= BLUESKY_LIMIT


def _mastodon_fits(segment: str) -> bool:
    return mastodon_length(segment) <= MASTODON_LIMIT


def _best_break(text: str, fits) -> tuple[int, int] | None:
    """The (start, end) of the whitespace run to cut at, or None.

    Only runs whose preceding text fits the service's limit qualify;
    among those, the last paragraph break wins, then the last line
    break, then the last sentence end, then the last plain space.
    """
    fitting = [
        (m.start(), m.end(), m.group(0))
        for m in regex.finditer(r"\s+", text)
        if m.start() > 0 and fits(text[: m.start()])
    ]
    if not fitting:
        return None
    for qualifies in (
        lambda s, e, ws: ws.count("\n") >= 2,
        lambda s, e, ws: "\n" in ws,
        lambda s, e, ws: text[s - 1] in ".!?…",
    ):
        matches = [(s, e) for s, e, ws in fitting if qualifies(s, e, ws)]
        if matches:
            return matches[-1]
    start, end, _ = fitting[-1]
    return (start, end)


def _split(text: str, fits, hard_take: int) -> list[str]:
    remaining = text.strip()
    if not remaining:
        return []
    segments = []
    while remaining:
        if fits(remaining):
            segments.append(remaining)
            break
        cut = _best_break(remaining, fits)
        if cut is None:
            clusters = GRAPHEME_RE.findall(remaining)
            take = hard_take
            while take > 1 and not fits("".join(clusters[:take])):
                take -= 1
            segments.append("".join(clusters[:take]))
            remaining = "".join(clusters[take:])
        else:
            start, end = cut
            segments.append(remaining[:start])
            remaining = remaining[end:]
    return segments


def split_thread(text: str) -> list[str]:
    """Break text into thread segments within Bluesky's limit.

    A fitting text comes back as a single segment, byte-identical.
    Longer text is cut at whitespace — preferring a paragraph break,
    then a line break, then a sentence end, then any space — with the
    whitespace at each cut consumed. Nothing is added: no counters, no
    ellipses.
    """
    return _split(text, _bluesky_fits, BLUESKY_LIMIT)


def split_thread_mastodon(text: str) -> list[str]:
    """Break text into thread segments within Mastodon's limit alone.

    Same cutting rules as :func:`split_thread`, but against the
    instance's (higher) character limit — so a thought that threads on
    Bluesky often posts to Mastodon whole.
    """
    return _split(text, _mastodon_fits, MASTODON_LIMIT)


def status_line(text: str, images: int = 0) -> str:
    """The composer's live status: count, limit, and how it will post."""
    count = grapheme_length(text)
    bluesky_posts = len(split_thread(text))
    mastodon_posts = len(split_thread_mastodon(text))
    if bluesky_posts <= 1 and mastodon_posts <= 1:
        posting = "1 post"
    else:
        posting = (
            f"will thread as {bluesky_posts} post"
            + ("s" if bluesky_posts != 1 else "")
            + f" on Bluesky · {mastodon_posts} post"
            + ("s" if mastodon_posts != 1 else "")
            + " on Mastodon"
        )
    line = f"{count}/{BLUESKY_LIMIT} · {posting}"
    if images:
        line += f" · {images} image" + ("s" if images != 1 else "")
    return line
