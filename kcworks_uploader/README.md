# kcworks-uploader

Uploads a post from the eve.gd Jekyll blog to [KC Works](https://works.hcommons.org/)
as a **draft** record, attaching the post's markdown source and its built PDF
edition, with full bibliographic metadata (CC BY 4.0, ORCID, KC username,
both institutional affiliations, canonical URL, tags, and the post's DOI as an
externally-managed identifier).

## Usage

From the blog root, via the driver script:

```sh
./kcworks.sh dry-run _posts/YYYY-MM-DD-slug.md    # record JSON, no network
./kcworks.sh deposit _posts/YYYY-MM-DD-slug.md    # create a draft (default)
./kcworks.sh deposit --live _posts/YYYY-MM-DD-slug.md   # publish immediately
./kcworks.sh publish <uploads-url-or-record-id>   # publish a reviewed draft
./kcworks.sh backfill                             # deposit every pending post
```

Once a deposit is published, record it in the post's front matter so the
blog and repository records stay linked:

```yaml
kcworks: https://works.hcommons.org/records/<id>
```

The signposting plugin emits this as `archivedAt` in the post's
metadata.json (the KC Works record already points back through its
canonical-URL identifier).

## Backfilling the whole blog

`./kcworks.sh backfill` works through every post that has no `kcworks:`
front-matter record yet, publishing each one live (markdown + PDF, into
the configured collection) and stamping the new record URL straight back
into the post's front matter. Because the stamp is what marks a post as
deposited, the run is resumable: interrupt it or hit failures, and
re-running picks up exactly where it left off, retrying only what is
missing.

```sh
./kcworks.sh backfill --dry-run     # list what would be deposited
./kcworks.sh backfill --limit 5     # a cautious first batch
./kcworks.sh backfill               # the lot (~10s per post)
```

Every outcome is appended as a JSON line to `kcworks-backfill.log` in
the blog root (`--log PATH` to move it), so a long run can be audited
afterwards — failures carry the full error:

```sh
grep '"failed"' kcworks-backfill.log
```

Options: `--delay SECONDS` spaces out deposits (default 10, which keeps
well under the API rate limits — the client also honours `Retry-After`
and backs off automatically on 429/5xx responses); `--limit N` caps the
run; `--posts-dir`, `--collection`/`--no-collection`, `--no-doi`,
`--base-url` and `--token` behave as for the other commands. The exit
code is non-zero when anything failed; a run interrupted with Ctrl-C
exits 130 and leaves the log and stamps intact.

## The blog collection

`kcworks_collection` in the blog's `_config.yml` names the KC Works
collection every published deposit is included in (at publish time, both
for `deposit --live` and `publish`; drafts join on publishing). Override
with `--collection SLUG` or skip with `--no-collection`. One-time setup
and maintenance:

```sh
# Create the collection (slug from _config.yml)
./kcworks.sh collection create --title "eve.gd: Martin Paul Eve's blog posts"

# Include every post with a kcworks: front-matter deposit
./kcworks.sh collection backfill

# Set the collection icon (the stylised portrait lives in images/)
./kcworks.sh collection logo images/kcworks-collection-icon.png
```

The token comes from `.env` in the blog root (`KCWORKS_API_TOKEN=...`), which the
driver script and the `--env-file` examples load automatically. Backfill is idempotent: records already
in the collection report `already`.

Or from this directory:

```sh
# Preview the record JSON without touching the network
uv run kcworks-upload ../_posts/2026-08-28-some-post.md --dry-run

# Create the draft (review it in the browser before publishing)
uv run --env-file ../.env kcworks-upload ../_posts/2026-08-28-some-post.md

# Or skip the draft stage and publish immediately
uv run --env-file ../.env kcworks-upload ../_posts/2026-08-28-some-post.md --live

# Publish a previously created draft (takes the uploads URL or a bare id)
uv run --env-file ../.env kcworks-publish https://works.hcommons.org/uploads/<id>
```

The upload tool prints the draft's edit URL
(https://works.hcommons.org/uploads/&lt;id&gt;) so the record can be checked and
published by hand — either in the browser or with `kcworks-publish`.

Options for `kcworks-upload`:

- `--dry-run` — print the record JSON and the files that would be attached.
- `--live` — publish immediately instead of leaving a draft for review
  (draft is the default).
- `--no-doi` — omit the post's front-matter DOI from the record's `pids`
  (use this if KC Works rejects the DOI as belonging to its own prefix).
- `--pdf PATH` — attach a specific PDF instead of the cached build
  (`.pdf_cache/<slug>.pdf`, falling back to `_site/PDF/<slug>.pdf`).
- `--base-url URL` — a different KC Works instance (default
  `https://works.hcommons.org/api`).
- `--token TOKEN` — API token (defaults to `$KCWORKS_API_TOKEN`).

## Tests

```sh
uv run pytest
```
