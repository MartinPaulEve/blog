"""Command-line entry points for short thoughts.

    thought                       # open the composer, post, quick-deploy
    thought --image shot.png      # with an attachment (repeatable)
    thought --text "..."          # skip the TUI
    thought --dry-run --text "…"  # show how it would thread, touch nothing
    thought --no-post --no-deploy # keep it local
    thought-probe                 # check both services' credentials

Credentials come from BLUESKY_APP_PASSWORD and MASTODON_ACCESS_TOKEN
(the .env file via thought.sh); BLUESKY_IDENTIFIER and
MASTODON_BASE_URL override the account defaults.
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from . import bluesky as bluesky_module
from . import mastodon as mastodon_module
from .linkcard import fetch_card
from .store import add_thought, load_image_file, save_image, set_syndication
from .text import find_links, split_thread, status_line


def _bluesky_client():
    password = os.environ.get("BLUESKY_APP_PASSWORD")
    if not password:
        return None
    return bluesky_module.BlueskyClient(
        os.environ.get("BLUESKY_IDENTIFIER", "eve.gd"),
        password,
        base_url=os.environ.get("BLUESKY_BASE_URL", bluesky_module.BASE_URL),
    )


def _mastodon_client():
    token = os.environ.get("MASTODON_ACCESS_TOKEN")
    if not token:
        return None
    return mastodon_module.MastodonClient(
        os.environ.get("MASTODON_BASE_URL", mastodon_module.BASE_URL),
        token,
    )


def store_thought(root: Path, text: str, images: list[dict]) -> dict:
    """Persist the thought and its images; return the stored entry.

    Images are written (and constrained) first so the entry can carry
    their final paths; each image dict gains the final ``data``/``mime``
    that syndication must upload.
    """
    now = datetime.now().astimezone()
    thought_id = now.strftime("%Y%m%d%H%M%S")
    stored_images = []
    for seq, image in enumerate(images, 1):
        entry, final_data, final_mime = save_image(
            root,
            image["data"],
            image["mime"],
            thought_id,
            seq,
            alt=image.get("alt", ""),
        )
        image["data"], image["mime"] = final_data, final_mime
        stored_images.append(entry)
    return add_thought(root, text, images=stored_images, now=now)


def syndicate(
    root: Path,
    entry: dict,
    segments: list[str],
    images: list[dict],
    echo=print,
) -> dict:
    """Post the thread to Bluesky and Mastodon; record the URLs.

    Each service is tried independently — one failing must not stop the
    other, or the blog publish. Returns {"bluesky": url, "mastodon":
    url} with None for any service that failed or lacks credentials.
    """
    card = None
    links = find_links(" ".join(segments))
    if links and not images:
        card = fetch_card(links[0]["url"])

    result = {"bluesky": None, "mastodon": None}

    client = _bluesky_client()
    if client is None:
        echo("Bluesky: no BLUESKY_APP_PASSWORD set; skipped.")
    else:
        try:
            urls = client.post_thread(
                segments, images=images or None, card=card
            )
            result["bluesky"] = urls[0]
            echo(f"Bluesky: {urls[0]}")
        except Exception as exc:  # noqa: BLE001 — one service down must not stop the rest
            echo(f"WARNING: Bluesky post failed: {exc}")

    client = _mastodon_client()
    if client is None:
        echo("Mastodon: no MASTODON_ACCESS_TOKEN set; skipped.")
    else:
        try:
            media_ids = [
                client.upload_media(
                    image["data"], image["mime"], alt=image.get("alt", "")
                )
                for image in images[:4]
            ]
            urls = client.post_thread(segments, media_ids=media_ids or None)
            result["mastodon"] = urls[0]
            echo(f"Mastodon: {urls[0]}")
        except Exception as exc:  # noqa: BLE001 — one service down must not stop the rest
            echo(f"WARNING: Mastodon post failed: {exc}")

    if result["bluesky"] or result["mastodon"]:
        set_syndication(
            root,
            entry["id"],
            bluesky=result["bluesky"],
            mastodon=result["mastodon"],
        )
    return result


def _parser():
    parser = argparse.ArgumentParser(description="Post a short thought")
    parser.add_argument("--text", help="the thought (skips the composer)")
    parser.add_argument(
        "--image",
        action="append",
        type=Path,
        default=[],
        help="attach an image file (repeatable, up to 4)",
    )
    parser.add_argument(
        "--alt",
        action="append",
        default=[],
        help="alt text for the matching --image (repeatable)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-post", action="store_true")
    parser.add_argument("--no-deploy", action="store_true")
    parser.add_argument("--root", type=Path, default=Path("."))
    return parser


def main(argv=None):
    args = _parser().parse_args(argv)

    images = []
    for index, path in enumerate(args.image[:4]):
        data, mime = load_image_file(path)
        alt = args.alt[index] if index < len(args.alt) else ""
        images.append({"data": data, "mime": mime, "alt": alt})

    if args.text is not None:
        text = args.text
    else:
        from . import tui

        text = tui.compose(images)
        if text is None or not text.strip():
            print("Cancelled; nothing posted.")
            return 1
        tui.ask_alt_text(images)

    segments = split_thread(text)
    if not segments:
        print("Empty thought; nothing to do.")
        return 1

    if args.dry_run:
        print(status_line(text, images=len(images)))
        for number, segment in enumerate(segments, 1):
            print(f"--- post {number} ---")
            print(segment)
        return 0

    entry = store_thought(args.root, text, images)
    print(f"Stored thought {entry['id']} ({len(segments)} post(s)).")

    if not args.no_post:
        syndicate(args.root, entry, segments, images)

    if not args.no_deploy:
        deploy = subprocess.run(
            [
                "uv", "run", "--env-file", ".env",
                "--project", "evedeploy", "evedeploy", "--quick",
            ],
            cwd=args.root,
            check=False,
        )
        if deploy.returncode != 0:
            print(
                "WARNING: quick deploy failed; run ./deploy.sh --quick "
                "to publish the page.",
                file=sys.stderr,
            )
            return 1
    return 0


def probe_main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check Bluesky and Mastodon credentials"
    )
    parser.parse_args(argv)
    failed = False

    client = _bluesky_client()
    if client is None:
        print("Bluesky: BLUESKY_APP_PASSWORD not set (see .env)")
        failed = True
    else:
        try:
            did = client.login()
            print(f"Bluesky: authenticated as {client.identifier} ({did})")
        except Exception as exc:  # noqa: BLE001 — probe reports, never crashes
            print(f"Bluesky: FAILED — {exc}")
            failed = True

    client = _mastodon_client()
    if client is None:
        print("Mastodon: MASTODON_ACCESS_TOKEN not set (see .env)")
        failed = True
    else:
        try:
            acct = client.verify()
            print(f"Mastodon: authenticated as @{acct} on {client.base_url}")
        except Exception as exc:  # noqa: BLE001 — probe reports, never crashes
            print(f"Mastodon: FAILED — {exc}")
            failed = True
    return 1 if failed else 0
