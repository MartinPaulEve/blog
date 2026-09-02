#!/usr/bin/env python3
"""Send outbound webmentions for published posts, exactly once per revision.

Run from the blog root after the built _site is live (stdlib only):

    uv run _webmentions/send_webmentions.py [--baseline|--dry-run]

Walks the built _site's post pages, pulls every external link out of each
post body, discovers each target's webmention endpoint and POSTs
source+target to it. _webmentions/sent.json records what was sent against a
hash of the post body, so a deploy never re-sends anything: a post only
notifies its targets again when its content actually changes (updates), and
targets dropped from an updated post get a final notification so the far end
can delete the stale mention (per the Webmention spec).

--baseline records the current state of every post as already-sent without
any network traffic: run once at adoption so years of archives don't blast
mentions at the whole web.
"""

from __future__ import annotations

import argparse
import hashlib
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
    """The inner HTML of the post-body div, or None when absent."""
    match = BODY_START.search(html)
    if not match:
        return None
    depth = 1
    for tag in DIV_TAG.finditer(html, match.end()):
        if tag.group().startswith("</"):
            depth -= 1
            if depth == 0:
                return html[match.end():tag.start()]
        else:
            depth += 1
    return None


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
    except (OSError, ValueError):
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

    for action in actions:
        source_url = SITE_URL + action["source"]
        record = recorded.setdefault(action["source"], {"sent": {}})
        endpoint = discover(action["target"])

        if action["reason"] == "removed":
            # Best-effort deletion notice; the target leaves the ledger
            # either way, or it would linger forever.
            if endpoint:
                status = post(endpoint, {"source": source_url,
                                         "target": action["target"]})
                echo(f"webmention removal notice {action['target']}: {status}")
            record["sent"].pop(action["target"], None)
            continue

        if endpoint is None:
            record["sent"][action["target"]] = {"at": now, "endpoint": None}
            continue

        status = post(endpoint, {"source": source_url,
                                 "target": action["target"]})
        if 200 <= status < 300:
            record["sent"][action["target"]] = {
                "at": now, "endpoint": endpoint, "status": status}
            echo(f"webmention sent ({action['reason']}) "
                 f"{action['target']} -> {endpoint}: {status}")
        else:
            echo(f"webmention FAILED {action['target']} -> {endpoint}: "
                 f"{status} (will retry next deploy)")
    return state


def run(root, mode="send", fetch=http_fetch, post=http_post, echo=print):
    """Collect, plan and execute; returns a process exit code."""
    root = pathlib.Path(root)
    site_dir = root / "_site"
    if not site_dir.is_dir():
        echo("send_webmentions: no _site build found; run jekyll build first")
        return 1

    posts = collect_posts(site_dir)
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
        for action in actions:
            echo(f"would send ({action['reason']}): "
                 f"{SITE_URL}{action['source']} -> {action['target']}")
        echo(f"send_webmentions: {len(actions)} pending")
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
    args = parser.parse_args(argv)
    mode = "baseline" if args.baseline else "dry-run" if args.dry_run else "send"
    root = pathlib.Path(__file__).resolve().parent.parent
    return run(root, mode=mode)


if __name__ == "__main__":
    sys.exit(main())
