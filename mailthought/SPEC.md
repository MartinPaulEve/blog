# Spec: mailthought — email-to-thought gateway

## Objective

A Docker Compose app (deployed on Coolify) that turns email into published
short thoughts. Martin emails a dedicated address; the gateway validates the
sender, extracts the thought (text, links, images), and runs the existing
thought pipeline: store in `_data/thoughts.yml`, cross-post to Bluesky and
Mastodon (threading when long), push the change back to GitHub, and
build+rsync the site — exactly what `./thought.sh` does locally, minus the
TUI, plus git.

User stories:

- Send a plain email → the thought is live on eve.gd, Bluesky and Mastodon
  within minutes; a receipt email links to all three.
- Send with subject `--dry run` → nothing is published; a report email
  describes what would happen (thread split, image count, per-post preview)
  under a subject carrying a draft identifier.
- Reply to that report with `POST` as the first body line → the saved draft
  is published as-is.
- Anyone else emailing the address is silently dropped (no backscatter).

## Tech Stack

- Python ≥3.12, uv project (matches thought_composer/evedeploy conventions).
- Flask + gunicorn for the webhook receiver (small, easily unit-tested).
- Mailgun for inbound (Routes → forward to webhook) and outbound (Messages
  API). Chosen because its inbound parse ships `stripped-text` /
  `stripped-signature` (solves "ignore email signatures" natively), signed
  webhooks (HMAC), and SPF/DKIM verdicts on received mail.
- Existing in-repo tooling, reused rather than reimplemented:
  - `thought_composer` — storage, thread splitting, image constraints,
    Bluesky/Mastodon posting (invoked as `uv run --project thought_composer
    thought …` inside the runtime clone, same as thought.sh).
  - `evedeploy --quick` — jekyll build + rsync (invoked by the thought CLI).
- Docker: Debian-based image with ruby + jekyll 4.4.1 + jekyll-feed +
  liquid 4.0.4, chromium (+fonts) for the OG-image build pass, git, rsync,
  openssh-client, uv, exiftool.

## Architecture

```
Mailgun route  ──POST──▶  /inbound (Flask, gunicorn)
                            │  verify webhook HMAC signature
                            │  verify sender ∈ ALLOWED_SENDERS
                            │  verify SPF/DKIM verdicts (anti-spoof)
                            │  dedupe on Message-Id
                            │  classify: THOUGHT | DRY RUN | POST reply
                            │  persist job to /data/inbox → 200
                            ▼
                     worker thread (serialised)
                            │
        ┌───────────────────┼──────────────────────┐
        ▼                   ▼                      ▼
    DRY RUN             THOUGHT               POST reply
  thought --dry-run   git pull --rebase     load /data/drafts/<id>
  save draft to       thought --text …      → same as THOUGHT
  /data/drafts        --image … (stores,
  email report        syndicates, builds,
  [draft-id] back     rsyncs)
                      git commit+push
                      email receipt back
```

State lives on a persistent volume `/data`: the blog clone (`/data/blog`,
cloned on first boot, pulled per job — keeps the gitignored `.og_cache` /
`.pdf_cache` warm across emails), drafts, inbox jobs, processed-message
ledger, uv cache.

## Commands

- Test: `cd mailthought && uv run pytest`
- Lint: `cd mailthought && uvx ruff check .`
- Run locally: `cd mailthought && uv run gunicorn -b 127.0.0.1:8080 'mailthought.app:create_app()'`
- Container build: `docker compose -f mailthought/docker-compose.yml build`

## Project Structure

```
mailthought/
  SPEC.md            → this document
  README.md          → Coolify + Mailgun setup runbook (DNS, route, keys)
  pyproject.toml     → uv project (flask, gunicorn, requests, dev: pytest)
  Dockerfile         → jekyll + chromium + uv + git/rsync/ssh runtime
  docker-compose.yml → Coolify service: port, volume, env contract
  entrypoint.sh      → SSH/git/.env materialisation, first-boot clone, gunicorn
  mailthought/
    config.py        → env parsing/validation (fail fast on missing vars)
    security.py      → Mailgun HMAC verify, timestamp/replay guard,
                       sender allowlist, SPF/DKIM verdict checks
    extract.py       → subject classification (--dry run / draft-id / POST),
                       body selection (stripped-text → html → plain +
                       own signature stripper fallback), HTML→text with
                       links preserved, image attachment collection
    drafts.py        → draft persistence (/data/drafts/<id>/…), id scheme
    publisher.py     → worker: git pull/commit/push, thought CLI invocation,
                       CLI output parsing (id, post count, service URLs)
    mailer.py        → outbound Mailgun (dry-run report, receipts, failures)
    app.py           → Flask app factory: POST /inbound, GET /healthz
  tests/             → pytest unit tests, one file per module, all
                       network/subprocess/filesystem side effects mocked
```

## Behavioural contract

Classification (in order):

1. Subject contains a draft identifier `[mt-<8 hex>]` AND first non-blank
   body line is exactly `POST` (uppercase, ignoring surrounding whitespace)
   → publish that draft. Unknown/expired id → error email.
2. Subject equals/contains `--dry run` (also accept `--dry-run`,
   case-insensitive) → dry run. Report email subject:
   `Thought draft [mt-<id>]: <N> post(s), <M> image(s)`; body states the
   thread split, image count, and a per-post preview (the CLI's
   `--- post N ---` blocks); ends with reply-with-POST instructions.
3. Otherwise → publish immediately. The subject is discarded (thoughts have
   no titles); only the body is the thought.

Body extraction:

- Prefer Mailgun `stripped-text` (quotes and signatures already removed).
  Empty → `stripped-html`/`body-html` converted to text with `<a href>`
  URLs preserved inline (dedup when the anchor text is the URL). Last
  resort: `body-plain` minus everything after a `^-- $` line or a known
  mobile signoff ("Sent from my iPhone" etc.).
- Text is otherwise never altered (repo ethos): CRLF→LF and outer trim
  only. RFC 3676 format=flowed unwrapping only when the message declares it.
- For a POST reply, the body (beyond the POST line) is ignored — the draft
  text is what gets published.

Images:

- Attachments with an image MIME type in thought_composer's supported set
  (jpeg/png/gif/webp), plus inline `cid:` images referenced from the HTML,
  in received order, capped at 4 (the Bluesky limit, as the CLI does).
  Filename becomes default alt text (extension stripped).
- Placement follows the existing pipeline: stored under `assets/thoughts/`,
  embedded on the **first post** of the thread on both services.

Publishing (worker, one job at a time):

1. `git -C /data/blog pull --rebase` (fresh thoughts.yml; rebase because
   Martin's machine also pushes).
2. `uv run --env-file .env --project thought_composer thought --text …
   [--image …]` — stores, syndicates, quick-deploys (jekyll build with
   `JEKYLL_SKIP_PDFS=1` in-container; rsync ships only changes and never
   deletes, so server-side PDFs are untouched).
3. `git add _data/thoughts.yml assets/thoughts && git commit -m
   "chore(thoughts): add <id> via mail gateway" && git push`; on rejection,
   one `pull --rebase` retry.
4. Receipt email: blog/Bluesky/Mastodon URLs, or the failure verbatim.
   Partial failure (e.g. one service down) is reported as such — the
   thought still publishes to the blog, matching CLI behaviour.

## Security model

- Webhook: reject unless Mailgun HMAC-SHA256(timestamp+token) matches
  `MAILGUN_SIGNING_KEY`, timestamp within ±5 min, token not seen before
  (persisted replay cache).
- Sender: the RFC 5322 From address must be in `ALLOWED_SENDERS`
  (comma-separated env var, case-insensitive).
- Anti-spoof: Mailgun's SPF and DKIM verdicts on the inbound message must
  both be Pass (header names confirmed against current Mailgun docs at
  implementation time). `REQUIRE_AUTH=false` escape hatch, default true.
- Rejected mail → HTTP 406 (Mailgun: permanent, no retry), no reply email
  ever (no backscatter). Transient faults → 5xx so Mailgun retries.
- Outbound replies go only to the validated sender, threaded via
  In-Reply-To.
- Secrets only via environment (Coolify-managed); nothing secret on disk
  except the SSH material the entrypoint writes to `~/.ssh` (0600) and the
  clone's `.env` (both on the private volume/container).
- Email content is data, never shell: subprocess invocations use argument
  vectors, no shell interpolation.

## Environment contract (docker-compose)

Required: `ALLOWED_SENDERS`, `MAILGUN_API_KEY`, `MAILGUN_SIGNING_KEY`,
`MAILGUN_DOMAIN`, `MAIL_FROM`, `GIT_SSH_KEY`, `RSYNC_HOST`.
Optional (defaults): `MAILGUN_API_BASE` (https://api.mailgun.net),
`REQUIRE_AUTH` (true), `GIT_REPO_URL` (git@github.com:MartinPaulEve/blog.git),
`GIT_USER_NAME`/`GIT_USER_EMAIL`, `RSYNC_SSH_KEY` (falls back to
`GIT_SSH_KEY`), `RSYNC_USER` (evegd), `RSYNC_PORT` (22), `KNOWN_HOSTS`
(else ssh-keyscan on first boot; GitHub's published keys baked in),
`JEKYLL_SKIP_PDFS` (1), `TZ` (Europe/London), `DATA_DIR` (/data),
plus the pass-through social credentials `BLUESKY_APP_PASSWORD`,
`MASTODON_ACCESS_TOKEN` (and their base-url/identifier overrides).

The entrypoint materialises: `~/.ssh/id_gateway*` + `~/.ssh/config`
(mapping evedeploy's hardcoded `reclaim` alias to `RSYNC_HOST`), git
identity, the clone (first boot), and the clone's `.env` (social tokens)
— then execs gunicorn.

## Code Style

Match thought_composer: module docstrings explaining the *why*, small pure
functions taking injectable side-effect callables, stdlib+requests bias,
double quotes, ruff-clean. Example:

```python
def classify(subject: str, body: str) -> Action:
    """Decide what an inbound mail asks for.

    POST replies win over --dry run: a reply to a draft report quotes the
    old subject, so the draft id, not the literal flag, is authoritative.
    """
```

## Testing Strategy

pytest, `mailthought/tests/`, red/green: every public function stubbed
with `NotImplementedError` first, tests written and failing, then
implemented. Behavioural tests only — mock Mailgun HTTP, subprocess, clock
and filesystem boundaries; assert on return values and produced artefacts
(job files, email payloads, git command vectors), never on call counts or
logging. The Flask test client exercises /inbound end-to-end with forged
multipart payloads (valid/invalid signatures, disallowed senders, replays,
attachments).

## Boundaries

- Always: run `uv run pytest` + `uvx ruff check` before every commit;
  reuse thought_composer/evedeploy rather than duplicating pipeline logic;
  return 200 to Mailgun only after the job is durably on disk.
- Ask first: changing anything outside `mailthought/` other than the
  planned one-line `_config.yml` exclude entry; adding new runtime
  dependencies beyond flask/gunicorn/requests; changing thought_composer.
- Never: commit secrets or real tokens (tests use fakes); reply to
  unvalidated senders; alter thought text beyond the documented
  normalisation; push to any branch but main.

## Success Criteria

- `uv run pytest` green in `mailthought/`; `uvx ruff check` clean.
- Forged-signature, disallowed-sender, SPF/DKIM-fail and replayed webhook
  POSTs are all rejected with 406 and produce no job, no email.
- A valid THOUGHT mail produces (mocked) `git pull` → `thought --text …`
  → `git commit/push` in order, and a receipt email with the parsed URLs.
- A `--dry run` mail publishes nothing, persists a draft, and the report
  email contains the post count, image count, per-post previews and a
  `[mt-…]` subject id.
- A POST reply to that id publishes the draft verbatim (including images).
- `docker compose build` succeeds; `jekyll build` works inside the image
  against a fresh clone with `JEKYLL_SKIP_PDFS=1`.
- The image and compose file carry no secrets; all configuration flows
  through the documented env contract.

## Open Questions

- Exact Mailgun header names for inbound SPF/DKIM verdicts — confirm
  against current Mailgun docs during implementation of security.py.
- Mailgun region (US vs EU API base) and the receiving domain/address —
  deployment-time choices for the README runbook, not code changes.
