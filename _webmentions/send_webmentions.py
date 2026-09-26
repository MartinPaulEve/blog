#!/usr/bin/env python3
"""Send outbound webmentions for published posts, exactly once per revision.

Run from the blog root after the built _site is live (stdlib only):

    uv run _webmentions/send_webmentions.py [--baseline|--dry-run]

Walks the built _site's post pages, pulls every external link out of each
post body, discovers each target's webmention endpoint and POSTs
source+target to it. Short thoughts (the per-month /thoughts/<YYYY-MM>/
pages) are sources too: each h-entry article is one source, addressed as
the month page plus its #t<id> fragment, so receivers can find the exact
entry; --only-thoughts restricts a pass to them (the quick deploy after a
thought uses this so it never rescans the post archive). _webmentions/sent.json records what was sent against a
hash of the post body, so a deploy never re-sends anything: a post only
notifies its targets again when its content actually changes (updates), and
targets dropped from an updated post get a final notification so the far end
can delete the stale mention (per the Webmention spec).

--baseline records the current state of every post as already-sent without
any network traffic: run once at adoption so years of archives don't blast
mentions at the whole web. Thoughts need no baseline: ids before
THOUGHTS_SINCE (the adoption date) are never collected at all, which also
keeps 27k imported entries out of the ledger.
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import pathlib
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser

SITE_URL = "https://eve.gd"
SKIP_HOSTS = {"eve.gd", "www.eve.gd", "doi.org", "dx.doi.org", "localhost",
              "127.0.0.1"}
STATE_FILE = "_webmentions/sent.json"
TIMEOUT = 15
MAX_FETCH_BYTES = 500_000

BODY_START = re.compile(r'<div class="post-body[^"]*">')
DIV_TAG = re.compile(r"<div\b[^>]*>|</div>")
# The post sidebar directly follows the post body in the layout; it carries
# chrome (share-intent buttons, the Last.fm widget) that must never count as
# content, so it doubles as a hard end-of-content boundary.
SIDEBAR_MARKER = '<aside class="post-sidebar"'

# Thoughts are compact local timestamps (YYYYMMDDHHMMSS) and a month page
# is /thoughts/<YYYY-MM>/, so the id alone locates its entry. The layout
# renders each entry as an article with the text in an e-content <p>; the
# footer's syndication links (Bluesky/Mastodon) are chrome, never targets.
THOUGHTS_DIR = "thoughts"
THOUGHT_ARTICLE = re.compile(
    r'<article class="thought-entry h-entry" id="t(\d{14})">')
THOUGHT_TEXT = re.compile(
    r'<p class="thought-text e-content">(.*?)</p>', re.DOTALL)


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


def http_fetch(url):
    """GET a URL following redirects; returns (status, headers, body, final_url)."""
    request = urllib.request.Request(
        url, headers={"User-Agent": "eve.gd-webmention-sender/1.0"})
    with urllib.request.urlopen(request, timeout=TIMEOUT,
                                context=_ssl_context()) as response:
        body = response.read(MAX_FETCH_BYTES).decode("utf-8", "replace")
        return response.status, dict(response.headers), body, response.geturl()


def http_post(url, data):
    """POST form data; returns the response status code."""
    request = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(data).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded",
                 "User-Agent": "eve.gd-webmention-sender/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT,
                                    context=_ssl_context()) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code


def extract_post_body(html):
    """The inner HTML of the post-body div, or None when absent.

    Capped at the post sidebar: an unclosed <div> in a hand-written post
    (there are two decades of them) offsets the depth scan so it overruns
    the real post-body close and swallows the sidebar, whose share buttons
    and Last.fm widget would then be collected as outbound targets. The
    sidebar is a firm content boundary, so trim there regardless of how the
    div scan lands.
    """
    match = BODY_START.search(html)
    if not match:
        return None
    body = None
    depth = 1
    for tag in DIV_TAG.finditer(html, match.end()):
        if tag.group().startswith("</"):
            depth -= 1
            if depth == 0:
                body = html[match.end():tag.start()]
                break
        else:
            depth += 1
    if body is None:  # never balanced: fall back to the rest of the page
        body = html[match.end():]
    cut = body.find(SIDEBAR_MARKER)
    return body[:cut] if cut != -1 else body


class _LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        href = dict(attrs).get("href") or ""
        if href.startswith(("http://", "https://")) and href not in self.links:
            self.links.append(href)


def body_links(body_html):
    """All absolute http(s) hrefs inside a post body, in document order."""
    collector = _LinkCollector()
    collector.feed(body_html)
    return collector.links


def eligible(url):
    """True for external targets worth mentioning (skips self, DOIs...)."""
    host = urllib.parse.urlsplit(url).hostname or ""
    return bool(url.startswith(("http://", "https://")) and host
                and host not in SKIP_HOSTS)


def content_hash(body_html):
    """Stable hash of a post body used to detect published revisions."""
    return hashlib.sha256(body_html.encode("utf-8")).hexdigest()


def endpoint_from_link_header(value, base):
    """Webmention endpoint from an HTTP Link header value, or None."""
    for part in (value or "").split(","):
        segments = part.split(";")
        target = segments[0].strip()
        if not (target.startswith("<") and target.endswith(">")):
            continue
        for param in segments[1:]:
            name, _, val = param.partition("=")
            if name.strip().lower() != "rel":
                continue
            if "webmention" in val.strip().strip('"').lower().split():
                return urllib.parse.urljoin(base, target[1:-1])
    return None


class _EndpointFinder(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href = None

    def handle_starttag(self, tag, attrs):
        if self.href is not None or tag not in ("link", "a"):
            return
        attrs = dict(attrs)
        rels = (attrs.get("rel") or "").lower().split()
        if "webmention" in rels and attrs.get("href") is not None:
            self.href = attrs["href"]


def endpoint_from_html(html, base):
    """First <link>/<a> rel=webmention href in the document, or None."""
    finder = _EndpointFinder()
    finder.feed(html)
    if finder.href is None:
        return None
    return urllib.parse.urljoin(base, finder.href)


def discover_endpoint(target, fetch=http_fetch):
    """Resolve a target's webmention endpoint (header first, then HTML)."""
    try:
        status, headers, body, final_url = fetch(target)
    except (OSError, ValueError, http.client.HTTPException):
        # http.client.HTTPException covers InvalidURL (raised for a target
        # whose path carries a literal space or other control character,
        # e.g. an un-encoded PDF link) — it subclasses neither OSError nor
        # ValueError, so without it one malformed link aborts the whole
        # send pass before any state is written.
        return None
    if status >= 400:
        return None
    lowered = {k.lower(): v for k, v in (headers or {}).items()}
    endpoint = endpoint_from_link_header(lowered.get("link", ""), final_url)
    if endpoint:
        return endpoint
    return endpoint_from_html(body or "", final_url)


def collect_posts(site_dir):
    """Built post pages as [{"path": url_path, "hash": ..., "targets": [...]}].

    Posts are the pretty-URL pages under _site's year directories; the path
    is percent-encoded the way Jekyll writes doc.url.
    """
    site_dir = pathlib.Path(site_dir)
    posts = []
    for index in sorted(site_dir.glob("[0-9][0-9][0-9][0-9]/*/*/*/index.html")):
        body = extract_post_body(index.read_text(encoding="utf-8",
                                                 errors="replace"))
        if body is None:
            continue
        relative = index.parent.relative_to(site_dir).as_posix()
        posts.append({
            "path": "/" + urllib.parse.quote(relative, safe="/") + "/",
            "hash": content_hash(body),
            "targets": [url for url in body_links(body) if eligible(url)],
        })
    return posts


# Thoughts posted from this local timestamp on send webmentions; earlier
# ones (two decades of imports) are never even collected. Set at adoption
# on 2026-09-26 to the start of that week.
THOUGHTS_SINCE = "20260921000000"


def extract_thoughts(html):
    """[(id, text_html)] for every thought entry on a month page.

    The text is the escaped, linkified inner HTML of the e-content
    paragraph (what a receiver will see), which doubles as the entry's
    revision content for the ledger hash.
    """
    entries = []
    starts = list(THOUGHT_ARTICLE.finditer(html))
    for index, start in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(html)
        text = THOUGHT_TEXT.search(html, start.end(), end)
        if text is None:
            continue
        entries.append((start.group(1), text.group(1)))
    return entries


def thought_path(thought_id):
    """Source path for a thought id: its month page plus fragment."""
    return f"/{THOUGHTS_DIR}/{thought_id[:4]}-{thought_id[4:6]}/#t{thought_id}"


def collect_thoughts(site_dir, since=THOUGHTS_SINCE):
    """Built thought entries as [{"path", "hash", "targets"}], like posts.

    Only entries with an id at or after ``since`` and at least one
    eligible target are returned: link-free thoughts have nothing to
    mention and would only pad the ledger.
    """
    site_dir = pathlib.Path(site_dir)
    since = str(since).ljust(14, "0")
    thoughts = []
    for index in sorted(site_dir.glob(
            f"{THOUGHTS_DIR}/[0-9][0-9][0-9][0-9]-[0-9][0-9]/index.html")):
        month = index.parent.name.replace("-", "")
        if month < since[:6]:
            continue
        html = index.read_text(encoding="utf-8", errors="replace")
        for thought_id, text in extract_thoughts(html):
            if thought_id < since:
                continue
            targets = [url for url in body_links(text) if eligible(url)]
            if not targets:
                continue
            thoughts.append({"path": thought_path(thought_id),
                             "hash": content_hash(text),
                             "targets": targets})
    return thoughts


def plan(state, posts):
    """Actions to take as [{"source": path, "target": url, "reason": ...}].

    reason: "new" (post never seen), "update" (content hash changed),
    "removed" (target dropped by an update), "retry" (recorded revision
    never successfully reached this target).
    """
    actions = []
    recorded = state.get("posts") or {}
    for post_info in posts:
        record = recorded.get(post_info["path"])
        if record is None:
            reasons = {target: "new" for target in post_info["targets"]}
        elif record.get("content_hash") != post_info["hash"]:
            reasons = {target: "update" for target in post_info["targets"]}
            for gone in record.get("sent") or {}:
                if gone not in reasons:
                    reasons[gone] = "removed"
        else:
            sent = record.get("sent") or {}
            reasons = {target: "retry" for target in post_info["targets"]
                       if target not in sent}
        actions.extend({"source": post_info["path"], "target": target,
                        "reason": reason} for target, reason in reasons.items())
    return actions


def baseline(state, posts, now=None):
    """State with every current post/target recorded as sent, no network."""
    now = now or datetime.now(timezone.utc).isoformat(timespec="seconds")
    state = json.loads(json.dumps(state))
    recorded = state.setdefault("posts", {})
    for post_info in posts:
        recorded[post_info["path"]] = {
            "content_hash": post_info["hash"],
            "sent": {target: {"at": now, "endpoint": None, "baseline": True}
                     for target in post_info["targets"]},
        }
    return state


def apply(state, posts, actions, discover=discover_endpoint, post=http_post,
          echo=print, now=None):
    """Execute a plan; returns the new state.

    A target with no discoverable endpoint is recorded (endpoint None) so it
    is not probed again until the post changes; a failed POST is left
    unrecorded so the next deploy retries it.
    """
    now = now or datetime.now(timezone.utc).isoformat(timespec="seconds")
    state = json.loads(json.dumps(state))
    recorded = state.setdefault("posts", {})
    for post_info in posts:
        record = recorded.setdefault(post_info["path"], {"sent": {}})
        record["content_hash"] = post_info["hash"]

    total = len(actions)
    if total:
        echo(f"send_webmentions: processing {total} target(s)")
    tally = {"sent": 0, "no endpoint": 0, "failed": 0, "removed": 0}

    for index, action in enumerate(actions, 1):
        target = action["target"]
        source_url = SITE_URL + action["source"]
        record = recorded.setdefault(action["source"], {"sent": {}})
        # One line per target BEFORE the network work, so a slow discovery or
        # POST shows what is in flight rather than a silent pause.
        echo(f"  [{index}/{total}] {action['reason']}: {target}")
        endpoint = discover(target)

        if action["reason"] == "removed":
            # Best-effort deletion notice; the target leaves the ledger
            # either way, or it would linger forever.
            if endpoint:
                status = post(endpoint, {"source": source_url,
                                         "target": target})
                echo(f"      removal notice -> {endpoint}: {status}")
            record["sent"].pop(target, None)
            tally["removed"] += 1
            continue

        if endpoint is None:
            record["sent"][target] = {"at": now, "endpoint": None}
            echo("      no webmention endpoint; recorded so it is not reprobed")
            tally["no endpoint"] += 1
            continue

        status = post(endpoint, {"source": source_url, "target": target})
        if 200 <= status < 300:
            record["sent"][target] = {
                "at": now, "endpoint": endpoint, "status": status}
            echo(f"      sent -> {endpoint}: {status}")
            tally["sent"] += 1
        else:
            echo(f"      FAILED -> {endpoint}: {status} (will retry next deploy)")
            tally["failed"] += 1

    if total:
        summary = (f"send_webmentions: done — {tally['sent']} sent, "
                   f"{tally['no endpoint']} without an endpoint, "
                   f"{tally['failed']} failed")
        if tally["removed"]:
            summary += f", {tally['removed']} removal notice(s)"
        echo(summary)
    return state


def run(root, mode="send", fetch=http_fetch, post=http_post, echo=print,
        only_thoughts=False):
    """Collect, plan and execute; returns a process exit code."""
    root = pathlib.Path(root)
    site_dir = root / "_site"
    if not site_dir.is_dir():
        echo("send_webmentions: no _site build found; run jekyll build first")
        return 1

    posts = [] if only_thoughts else collect_posts(site_dir)
    posts += collect_thoughts(site_dir)
    state_path = root / STATE_FILE
    state = {"posts": {}}
    if state_path.is_file():
        state = json.loads(state_path.read_text())

    def write_state(new_state):
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(
            json.dumps(new_state, indent=1, sort_keys=True) + "\n")

    if mode == "baseline":
        write_state(baseline(state, posts))
        echo(f"send_webmentions: baselined {len(posts)} post(s) "
             "without sending anything")
        return 0

    actions = plan(state, posts)
    if mode == "dry-run":
        by_reason = {}
        for action in actions:
            by_reason[action["reason"]] = by_reason.get(action["reason"], 0) + 1
            echo(f"would send ({action['reason']}): "
                 f"{SITE_URL}{action['source']} -> {action['target']}")
        breakdown = ", ".join(f"{count} {reason}"
                              for reason, count in sorted(by_reason.items()))
        summary = f"send_webmentions: {len(actions)} pending"
        if breakdown:
            summary += f" ({breakdown})"
        echo(summary)
        return 0

    if not actions:
        echo("send_webmentions: nothing to send")
        return 0

    state = apply(state, posts, actions,
                  discover=lambda target: discover_endpoint(target, fetch),
                  post=post, echo=echo)
    write_state(state)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--baseline", action="store_true",
                       help="record current posts as sent without sending")
    group.add_argument("--dry-run", action="store_true",
                       help="print the send plan without sending")
    parser.add_argument("--only-thoughts", action="store_true",
                        help="consider short thoughts only, not posts "
                             "(the quick deploy's post-thought pass)")
    args = parser.parse_args(argv)
    mode = "baseline" if args.baseline else "dry-run" if args.dry_run else "send"
    root = pathlib.Path(__file__).resolve().parent.parent
    # Flush each line so progress streams live under the deploy pipeline
    # (stdout is block-buffered when piped, not line-buffered as at a TTY).
    return run(root, mode=mode, echo=lambda *a: print(*a, flush=True),
               only_thoughts=args.only_thoughts)


if __name__ == "__main__":
    sys.exit(main())
