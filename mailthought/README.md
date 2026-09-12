# mailthought

Email-to-thought gateway: send an email, publish a short thought. The
gateway receives mail through a Mailgun inbound route, checks that it
really came from you, and then runs the exact pipeline `./thought.sh`
runs locally — the thought is stored untouched in `_data/thoughts.yml`,
cross-posted to Bluesky and Mastodon (threading when long, images on
the first post), committed and pushed back to GitHub, and shipped with
the quick deploy (jekyll build + rsync).

## How you use it

- **Publish**: email the thought address. The body is the thought
  (the subject is discarded — thoughts have no titles). Attach images
  (up to 4) or write HTML with links; signatures and quoted text are
  stripped. You get a receipt email with the blog, Bluesky and
  Mastodon URLs.
- **Preview**: put `--dry run` in the subject. Nothing publishes; you
  get a report — how many posts the thread splits into, how many
  images ride on the first post, and a preview of every post — under a
  subject like `Thought draft [mt-1a2b3c4d]: 3 post(s), 1 image(s)`.
- **Confirm**: reply to that report with `POST` (capitals) as the
  first line. The stored draft publishes exactly as previewed. Any
  other reply gets instructions back and publishes nothing. Drafts
  expire after 30 days.

## Security model

A mail publishes only if all of these hold:

1. the webhook POST carries a valid Mailgun HMAC signature (fresh
   timestamp, replay-guarded token);
2. the From address is in `ALLOWED_SENDERS`;
3. Mailgun's SPF **and** DKIM verdicts on the message are both Pass
   (`REQUIRE_AUTH=false` disables this, e.g. while testing);
4. the Message-Id has not been processed before.

Anything else is answered 406 (Mailgun stops retrying) and never gets
a reply email, so the address cannot be used for backscatter.

## Mailgun setup

1. Create a Mailgun account and add a **receiving domain**, e.g.
   `mg.eve.gd` (EU region works too — set `MAILGUN_API_BASE` to
   `https://api.eu.mailgun.net`).
2. DNS for that subdomain (Mailgun shows the exact records):
   - MX → `mxa.mailgun.org` and `mxb.mailgun.org` (receiving);
   - TXT SPF + the DKIM record (sending — the receipts/reports);
   - do **not** put these on eve.gd itself, only on the subdomain.
3. Receiving → Create Route:
   - expression: `match_recipient("thought@mg.eve.gd")`
   - action: `forward("https://<your-coolify-domain>/inbound")` and
     `stop()`
4. Collect the two secrets: the sending **API key** (Settings → API
   Security) and the **HTTP webhook signing key** (Sending →
   Webhooks). They are different keys; the gateway needs both.

## Access keys

- **GitHub push** — `ssh-keygen -t ed25519 -f mailthought_git -N ""`,
  add the public half as a repository **deploy key with write
  access**; the private half becomes `GIT_SSH_KEY`.
- **rsync deploy** — a key whose public half is in
  `~/.ssh/authorized_keys` for the rsync user on the web server; the
  private half becomes `RSYNC_SSH_KEY` (leave unset to reuse
  `GIT_SSH_KEY`). Set `RSYNC_HOST` to the server's real hostname — the
  entrypoint maps evedeploy's hardcoded `reclaim` SSH alias onto it.
  Optionally pin the server with `KNOWN_HOSTS` (`ssh-keyscan <host>`);
  without it the first connection is trusted and then pinned.
- **Bluesky / Mastodon** — the same credentials `.env` uses locally:
  `BLUESKY_APP_PASSWORD` (bsky.app → Settings → App Passwords) and
  `MASTODON_ACCESS_TOKEN` (hcommons.social → Development, scopes
  `write:statuses write:media read:accounts`). Leave one unset and the
  CLI simply skips that service.

## Coolify setup

1. New resource → **Docker Compose**, pointing at this repository,
   **base directory `/mailthought`**.
2. Attach a domain with HTTPS to port 8080 — Mailgun must be able to
   reach `https://…/inbound`.
3. Set the environment variables in the Coolify UI (see
   `docker-compose.yml` for the full annotated contract; the required
   ones are `ALLOWED_SENDERS`, `MAILGUN_API_KEY`,
   `MAILGUN_SIGNING_KEY`, `MAILGUN_DOMAIN`, `MAIL_FROM`,
   `GIT_SSH_KEY`, `RSYNC_HOST`, plus the social tokens). Multiline SSH
   keys paste fine into Coolify's env editor.
4. Deploy. First boot clones the blog onto the `mailthought-data`
   volume and the first email triggers a cold jekyll build (the OG
   card cache warms up once; expect the first publish to be slow).
   Everything after that is incremental — the clone, its build caches
   and the uv environments all live on the volume.

`GET /healthz` is the health endpoint (wired into the compose
healthcheck).

## Behaviour notes

- Thread splitting, grapheme counting, link facets/cards and image
  constraints are thought_composer's — the gateway shells out to
  `uv run --project thought_composer thought …` in the clone, so the
  email path can never drift from the local path.
- Images are stored under `assets/thoughts/` and embedded on the
  **first post** of the thread on both services; an attachment's
  filename (minus extension) becomes its alt text.
- Body text is never rewritten: CRLF normalisation, outer trim,
  signature removal and RFC 3676 flowed unwrapping only. Plain text is
  preferred (Mailgun's `stripped-text`); HTML-only mail is converted
  with link URLs kept inline.
- Each publish is `git pull --rebase` → thought CLI → `git commit`
  (`chore(thoughts): add <id> via mail gateway`) → `git push`, so your
  local checkout picks thoughts up with a plain pull. A rejected push
  is rebased and retried once.
- `JEKYLL_SKIP_PDFS=1` in the container: the PDF pass is skipped (the
  rsync never deletes, so the PDFs your machine deployed stay live);
  thoughts pages opt out of PDFs anyway.
- Partial failures behave like the CLI: one social service being down
  doesn't stop the blog publish — the receipt email says exactly what
  happened, including any deploy or push warning.
- Jobs are persisted to the volume before Mailgun gets its 200 and are
  processed strictly one at a time, so restarts lose nothing and
  builds never interleave.

## Development

```
cd mailthought
uv run pytest        # full suite (all side effects mocked)
uvx ruff check .
docker compose build # or: docker build -t mailthought .
```
