"""Turning a parsed Mailgun POST into a thought.

The subject only ever carries control information (--dry run, the
draft id in a reply); the body is the thought and is never altered
beyond line-ending normalisation, an outer trim, signature removal and
RFC 3676 unwrapping when the sender's client declares format=flowed —
the repo ethos is that thought text goes out exactly as written.
"""

import json
import os
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import ClassVar

# What an inbound mail asks for.
KIND_PUBLISH = "publish"
KIND_DRY_RUN = "dry_run"
KIND_POST_DRAFT = "post_draft"
KIND_BAD_REPLY = "bad_reply"

# The draft identifier planted in (and parsed back out of) subjects.
DRAFT_ID_RE = re.compile(r"\[mt-([0-9a-f]{8})\]")
DRY_RUN_RE = re.compile(r"--dry[-\s]run\b", re.IGNORECASE)

# A signature delimiter line ("-- " per RFC 3676, though many clients
# drop the trailing space) or a mobile client's stock signoff.
SIGNATURE_LINE_RE = re.compile(
    r"^(?:-- ?|Sent from my .+|Get Outlook for .+|Sent via .+)$"
)

# Image types thought_composer's store accepts (see store.MIME_EXTENSIONS).
IMAGE_MIMES = frozenset(
    {"image/jpeg", "image/png", "image/gif", "image/webp"}
)
MAX_IMAGES = 4  # the Bluesky embed limit, as the CLI enforces


@dataclass(frozen=True)
class Action:
    kind: str
    draft_id: str | None = None


def find_draft_id(subject: str) -> str | None:
    """The 8-hex draft id from a subject, or None."""
    match = DRAFT_ID_RE.search(subject or "")
    return match.group(1) if match else None


def wants_dry_run(subject: str) -> bool:
    """True when the subject asks for a dry run (--dry run / --dry-run)."""
    return bool(DRY_RUN_RE.search(subject or ""))


def first_line_is_post(body: str) -> bool:
    """True when the first non-blank line is exactly POST (in capitals)."""
    for line in (body or "").splitlines():
        if line.strip():
            return line.strip() == "POST"
    return False


def classify(subject: str, body: str) -> Action:
    """Decide what an inbound mail asks for.

    A draft id in the subject wins over everything: a reply quotes the
    report's subject, so the id — not any literal --dry run also quoted
    there — is authoritative. With an id present, a POST first line
    publishes the draft and anything else is a bad reply (answered with
    instructions rather than accidentally published as a new thought).
    """
    draft_id = find_draft_id(subject)
    if draft_id:
        if first_line_is_post(body):
            return Action(KIND_POST_DRAFT, draft_id)
        return Action(KIND_BAD_REPLY, draft_id)
    if wants_dry_run(subject):
        return Action(KIND_DRY_RUN)
    return Action(KIND_PUBLISH)


def select_body(form) -> str:
    """The thought text from a parsed Mailgun POST (a form mapping).

    Preference order: stripped-text (Mailgun already removed quotes and
    the signature block) → stripped-html/body-html rendered to text
    with link URLs preserved → body-plain with our own signature
    stripping. Whatever the source, the result is CRLF-normalised,
    flowed-unwrapped when declared, and outer-trimmed.
    """
    stripped = (form.get("stripped-text") or "").replace("\r\n", "\n")
    if stripped.strip():
        return stripped.strip()

    html = form.get("stripped-html") or form.get("body-html") or ""
    if html.strip():
        return strip_signature(html_to_text(html)).strip()

    plain = (form.get("body-plain") or "").replace("\r\n", "\n")
    if not plain.strip():
        return ""
    plain = unwrap_flowed(plain, _content_type(form.get("message-headers")))
    return strip_signature(plain).strip()


class _TextExtractor(HTMLParser):
    """HTML → text with anchor hrefs kept and block structure as breaks."""

    PARAGRAPH_TAGS: ClassVar[frozenset] = frozenset(
        {"p", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote"}
    )
    LINE_TAGS: ClassVar[frozenset] = frozenset(
        {"div", "li", "tr", "ul", "ol", "table"}
    )
    SKIP_TAGS: ClassVar[frozenset] = frozenset(
        {"script", "style", "head", "title"}
    )

    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip_depth = 0
        self.href = None
        self.link_text = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
        elif tag == "br":
            self.parts.append("\n")
        elif tag in self.PARAGRAPH_TAGS:
            self.parts.append("\n\n")
        elif tag in self.LINE_TAGS:
            self.parts.append("\n")
        elif tag == "a":
            self.href = dict(attrs).get("href")
            self.link_text = []

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS:
            self.skip_depth = max(0, self.skip_depth - 1)
        elif tag in self.PARAGRAPH_TAGS:
            self.parts.append("\n\n")
        elif tag in self.LINE_TAGS:
            self.parts.append("\n")
        elif tag == "a":
            href = self.href
            text = "".join(self.link_text).strip()
            if href and not href.startswith(("cid:", "mailto:")) and text != href:
                self.parts.append(f" {href}")
            self.href = None
            self.link_text = []

    def handle_data(self, data):
        if self.skip_depth:
            return
        collapsed = re.sub(r"\s+", " ", data)
        self.parts.append(collapsed)
        if self.href is not None:
            self.link_text.append(data)

    def text(self) -> str:
        joined = "".join(self.parts)
        joined = re.sub(r" *\n *", "\n", joined)
        joined = re.sub(r"\n{3,}", "\n\n", joined)
        joined = re.sub(r" {2,}", " ", joined)
        return joined.strip()


def html_to_text(html: str) -> str:
    """Plain text from an HTML body, keeping the links.

    Anchor hrefs survive inline (after the anchor text, unless the text
    already is the URL); block elements become line breaks; script and
    style contents disappear entirely.
    """
    extractor = _TextExtractor()
    extractor.feed(html or "")
    return extractor.text()


def strip_signature(text: str) -> str:
    """Cut a plain-text body at its signature.

    Handles the RFC 3676 "-- " delimiter line and the common mobile
    signoffs ("Sent from my iPhone" and friends).
    """
    lines = (text or "").split("\n")
    for index, line in enumerate(lines):
        if SIGNATURE_LINE_RE.match(line):
            return "\n".join(lines[:index]).rstrip()
    return text


def unwrap_flowed(text: str, content_type: str) -> str:
    """Rejoin soft-wrapped lines when the part declares format=flowed.

    Space-stuffing and delsp=yes are honoured; a "-- " signature
    delimiter line is never joined. Any other content type returns the
    text untouched.
    """
    declared = (content_type or "").lower()
    if "format=flowed" not in declared.replace(" ", ""):
        return text
    delsp = "delsp=yes" in declared.replace(" ", "")

    out = []
    carry = ""
    for line in text.split("\n"):
        if line != "-- " and line.startswith(" "):
            line = line[1:]  # space-stuffed per RFC 3676
        merged = carry + line
        soft = merged.endswith(" ") and merged != "-- " and line != "-- "
        if soft:
            carry = merged[:-1] if delsp else merged
        else:
            out.append(merged)
            carry = ""
    if carry:
        out.append(carry)
    return "\n".join(out)


def collect_images(files, content_id_map: str | None = None) -> list:
    """The image attachments from a Mailgun POST, in attachment order.

    ``files`` maps field names (attachment-1, attachment-2, …) to
    file-like objects with ``filename``, ``mimetype`` and ``read()``.
    Non-image attachments are ignored; at most MAX_IMAGES survive.
    Returns [{"data", "mime", "alt", "filename"}] with the filename
    stem as default alt text.
    """
    def order(name):
        match = re.search(r"(\d+)$", name)
        return (int(match.group(1)) if match else 0, name)

    images = []
    for name in sorted(files, key=order):
        upload = files[name]
        mime = (getattr(upload, "mimetype", "") or "").lower()
        if mime not in IMAGE_MIMES:
            continue
        filename = upload.filename or "attachment"
        images.append(
            {
                "data": upload.read(),
                "mime": mime,
                "alt": os.path.splitext(os.path.basename(filename))[0],
                "filename": filename,
            }
        )
        if len(images) == MAX_IMAGES:
            break
    return images


def _content_type(message_headers: str | None) -> str:
    return header_value(message_headers, "Content-Type")


def header_value(message_headers: str | None, wanted: str) -> str:
    """A single header's value from the message-headers JSON dump."""
    try:
        headers = json.loads(message_headers or "[]")
    except json.JSONDecodeError:
        return ""
    for entry in headers:
        try:
            if str(entry[0]).lower() == wanted.lower():
                return str(entry[1])
        except (TypeError, IndexError, KeyError):
            continue
    return ""
