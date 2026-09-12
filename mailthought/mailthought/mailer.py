"""Outbound mail: dry-run reports, receipts and failure notices.

All replies go through Mailgun's Messages API, only ever to the
already-validated sender, threaded onto the original mail with
In-Reply-To. The builders return (subject, body) pairs so their words
are testable without any HTTP.
"""

import requests

SITE_BASE = "https://eve.gd"

POST_INSTRUCTIONS = (
    "To publish exactly this, reply to this email with POST (in capitals)\n"
    "as the very first line of your message. To discard it, do nothing —\n"
    "drafts expire after 30 days."
)


def send_email(
    config,
    to: str,
    subject: str,
    body: str,
    in_reply_to: str | None = None,
    post=requests.post,
) -> bool:
    """Send a reply via Mailgun; True on acceptance.

    Never raises — a failed receipt must not fail the publish that
    preceded it.
    """
    data = {
        "from": config.mail_from,
        "to": to,
        "subject": subject,
        "text": body,
    }
    if in_reply_to:
        data["h:In-Reply-To"] = in_reply_to
    url = f"{config.mailgun_api_base}/v3/{config.mailgun_domain}/messages"
    try:
        response = post(url, auth=("api", config.mailgun_api_key), data=data,
                        timeout=30)
    except Exception:  # noqa: BLE001 — a receipt must never break the pipeline
        return False
    return 200 <= getattr(response, "status_code", 0) < 300


def dry_run_report(draft_id: str, result, image_count: int) -> tuple:
    """(subject, body) for a dry-run report.

    The subject carries the draft id ("Thought draft [mt-…]: N post(s),
    M image(s)"); the body says how the thought threads, how many
    images ride on the first post, previews every post, and explains
    the reply-with-POST step.
    """
    count = len(result.posts)
    subject = (
        f"Thought draft [mt-{draft_id}]: {count} post(s), "
        f"{image_count} image(s)"
    )
    lines = ["Here is what this thought would do.", ""]
    if count > 1:
        lines.append(f"It will be split into {count} posts (a thread).")
    else:
        lines.append("It will go out as a single post.")
    if image_count:
        lines.append(
            f"{image_count} image(s) attached — they ride on the first post."
        )
    else:
        lines.append("No images attached.")
    if result.status:
        lines.append(f"Character count: {result.status}")
    lines.append("")
    lines.append("Preview:")
    for number, segment in enumerate(result.posts, 1):
        lines.append(f"--- post {number} of {count} ---")
        lines.append(segment)
    lines.append("")
    lines.append(POST_INSTRUCTIONS)
    return subject, "\n".join(lines)


def receipt(result) -> tuple:
    """(subject, body) for a published thought: where it now lives."""
    subject = f"Thought published: {result.thought_id}"
    lines = [
        f"Your thought is live ({result.posts} post(s)).",
        "",
        f"Blog: {SITE_BASE}/thoughts/#t{result.thought_id}",
        f"Bluesky: {result.bluesky or 'not posted'}",
        f"Mastodon: {result.mastodon or 'not posted'}",
    ]
    if result.warnings:
        lines.append("")
        lines.append("Notes:")
        lines.extend(result.warnings)
    return subject, "\n".join(lines)


def failure_notice(reason: str) -> tuple:
    """(subject, body) when a job failed outright."""
    body = (
        "The thought was not published. The pipeline said:\n\n"
        f"{reason}\n\n"
        "Nothing was stored; sending the email again will retry from "
        "scratch."
    )
    return "Thought failed to publish", body


def bad_reply_notice(draft_id: str) -> tuple:
    """(subject, body) when a draft reply's first line was not POST."""
    body = (
        f"Your reply about draft [mt-{draft_id}] was not published.\n\n"
        "To publish the draft, reply with POST (in capitals) as the very\n"
        "first line of the email. Anything else is ignored so a stray\n"
        "reply can never publish by accident."
    )
    return f"Draft [mt-{draft_id}] not published", body


def missing_draft_notice(draft_id: str) -> tuple:
    """(subject, body) when a POST reply names an unknown/expired draft."""
    body = (
        f"No draft with id {draft_id} exists — it may have expired (drafts\n"
        "are kept for 30 days) or already been published.\n\n"
        "Send the thought again (with --dry run in the subject for a new\n"
        "preview) if you still want it posted."
    )
    return f"Draft [mt-{draft_id}] not found", body
