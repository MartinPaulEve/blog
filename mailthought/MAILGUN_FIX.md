# The Mailgun image-email fix

What was wrong, how it was diagnosed, and what changed, for the
email-to-thought gateway (mail to the thought@ address → blog thought
+ Bluesky/Mastodon). Text-only email always worked; any email with an
image attached always failed.

## The failure chain

1. **Mailgun only stamps SPF/DKIM verdicts on mail its spam scan
   processes, and the scan skips "large" messages.** In practice the
   threshold is tiny: a ~167 KB email with one photo was already
   skipped. So every email with an attachment arrives at the webhook
   with *no* verdict headers at all.
2. The gateway's security model requires passing verdicts, so for
   verdict-less mail it must verify DKIM itself against the raw
   message. Originally it tried to fetch that raw copy back from
   Mailgun's storage API (Events API lookup by Message-Id, then the
   event's storage URL).
3. **That fetch can never work on this account.** First suspect was a
   missing `store()` route action (a forward-only route keeps no copy,
   so storage URLs answer 404). But even with `store()` on the route,
   manual retrieval answered **HTTP 405 — "Message retrieval disabled
   for domain"**: the Mailgun plan has no message retention, so the
   storage API is simply walled off. The worker polled for 5 minutes,
   every fetch failed, and the thought was dropped with a failure
   notice. That was the actual problem.

## The fix

Stop depending on Mailgun storing anything. A Mailgun route can carry
a second `forward()` action, and **a forward URL ending in `mime`
makes Mailgun POST the full raw MIME of the message** (as a
`body-mime` field) instead of the parsed form. So:

- The gateway grew a second endpoint, **`POST /inbound/mime`**. It
  verifies the same Mailgun webhook signature, replay guard and
  sender allowlist as `/inbound`, then stashes the raw message on
  disk, keyed by a hash of its Message-Id (TTL-pruned, size-capped,
  first-write-wins).
- The background worker now verifies DKIM against that **local
  stash** (polling ~2 minutes for the copy to arrive) instead of
  Mailgun's storage API, which survives only as a one-shot fallback
  for deployments whose plan does have retention.
- After DKIM passes, the worker also **binds the queued content to
  the verified message** — sender, Message-Id, Subject, image bytes
  and text must all be present in the raw copy — so a forged
  delivery reusing a genuine Message-Id cannot ride on its
  verification. (Full threat-model notes are in SPEC.md.)
- Diagnostics: failed storage fetches now log the event types and a
  copy-pasteable curl command, and the failure-notice email names the
  real remedy (the missing `/inbound/mime` forward) instead of a
  vague "could not be retrieved".

## What the operator must configure

1. **Redeploy the gateway** so `/inbound/mime` exists.
2. In Mailgun (Receiving → Routes) set the route's actions to:
   - `forward("https://<gateway-domain>/inbound")`
   - `forward("https://<gateway-domain>/inbound/mime")`
   - `stop()`

   `store()` is no longer needed and can be removed.

A successful image email then logs, in order: the parsed POST
deferring verification, `raw MIME for '<…>' stashed`, `deferred DKIM
verification passed`, and the publish.

## Also in this round (unrelated to Mailgun)

Trailing `alt:` / `alt2:` / … directives at the end of an email set
the attached images' alt text; matching is case-insensitive
(`Alt:`, `ALT2:` work) and the directive lines are stripped from the
published thought.
