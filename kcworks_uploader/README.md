# kcworks-uploader

Deposits posts from the eve.gd Jekyll blog in [KC Works](https://works.hcommons.org/)
through its [streamlined import API](https://mesh-research.github.io/knowledge-commons-works/reference/api.html#streamlined-import-api):
one request creates the work, attaches the post's markdown source and
its built PDF edition, publishes it into the blog collection, and makes
the author's KC account its owner. Every record carries the full
bibliographic metadata (CC BY 4.0, ORCID, KC username, both institutional
affiliations, canonical URL, tags, the generative-AI declaration, and the
post's DOI as an externally-managed identifier).

## Usage

From the blog root, via the driver script:

```sh
./kcworks.sh dry-run _posts/YYYY-MM-DD-slug.md    # record JSON, no network
./kcworks.sh deposit _posts/YYYY-MM-DD-slug.md    # import + publish + stamp
./kcworks.sh backfill                             # deposit every pending post
./kcworks.sh update                               # refresh modified posts
./kcworks.sh publish <uploads-url-or-record-id>   # publish a hand-made draft
```

`deposit`, `backfill` and `update` record the published work in the
post's front matter, so the blog and repository records stay linked:

```yaml
kcworks: https://works.hcommons.org/records/<id>
```

The signposting plugin emits this as `archivedAt` in the post's
metadata.json (the KC Works record already points back through its
canonical-URL identifier). `publish` takes a record id rather than a
post, so after it add that line by hand.

## How a deposit works

Each deposit is a single multipart `POST /api/import/<collection>`
carrying the two files and the record JSON. KC Works creates the work,
uploads and commits the files, publishes, and places the work in the
collection without a review request, because the token's user curates
the collection. There is no draft stage: a deposit is live as soon as
the request returns, and the record URL is stamped straight back into
the post.

The record names the post slug as its `import-recid` identifier and the
post's DOI as its pid. KC Works deduplicates on both, so a repeated
import of the same post updates the existing work rather than creating
another; if the server instead answers 409 Conflict with the existing
work's location, that work is recorded as the deposit.

## Backfilling the whole blog

`./kcworks.sh backfill` works through every post that has no `kcworks:`
front-matter record yet, importing each one (markdown + PDF, into the
configured collection) and stamping the new record URL straight back
into the post's front matter. Because the stamp is what marks a post as
deposited, the run is resumable: interrupt it or hit failures, and
re-running picks up exactly where it left off, retrying only what is
missing.

```sh
./kcworks.sh backfill --dry-run     # list what would be deposited
./kcworks.sh backfill --limit 5     # a cautious first batch
./kcworks.sh backfill               # the lot
```

Every outcome is appended as a JSON line to `kcworks-backfill.log` in
the blog root (`--log PATH` to move it), so a long run can be audited
afterwards — failures carry the full error, including any per-field
validation messages the import API returned:

```sh
grep '"failed"' kcworks-backfill.log
```

Options: `--delay SECONDS` spaces out deposits (default 10, which keeps
well under the API rate limits — the client also honours `Retry-After`
and backs off automatically on 429/5xx responses); `--limit N` caps the
run; `--posts-dir`, `--collection`, `--no-doi`, `--base-url` and
`--token` behave as for the other commands. The exit code is non-zero
when anything failed; a run interrupted with Ctrl-C exits 130 and leaves
the log and stamps intact.

## Updating deposits

`./kcworks.sh update` finds every post with both a `kcworks:` record and
a `last_modified_at` date, and for each whose deposit predates that
date re-imports the post. The import API matches the existing work on
its DOI and `import-recid`, applies the changed metadata (including the
`updated` date) and reconciles the files, re-uploading the markdown and
PDF where their size changed. The work KC Works reports back is
re-stamped into the post. `--dry-run` lists the candidates; outcomes go
to `kcworks-update.log`.

## The blog collection

`kcworks_collection` in the blog's `_config.yml` names the KC Works
collection every deposit is imported into (override with
`--collection SLUG`). The import API always targets a collection, so
one must be configured. The user the API token belongs to must be an
owner, manager or curator of the collection. One-time setup and
maintenance:

```sh
# Create the collection (slug from _config.yml)
./kcworks.sh collection create --title "eve.gd: Martin Paul Eve's blog posts"

# Include every post with a kcworks: front-matter deposit (e.g. records
# published by hand through `publish`, which does not import)
./kcworks.sh collection backfill

# Set the collection icon (the stylised portrait lives in images/)
./kcworks.sh collection logo images/kcworks-collection-icon.png
```

The token comes from `.env` in the blog root (`KCWORKS_API_TOKEN=...`),
which the driver script and the `--env-file` examples load
automatically. Collection backfill is idempotent: records already in
the collection report `already`.

Or from this directory:

```sh
# Preview the record JSON without touching the network
uv run kcworks-upload ../_posts/2026-08-28-some-post.md --dry-run

# Deposit (import, publish, stamp)
uv run --env-file ../.env kcworks-upload ../_posts/2026-08-28-some-post.md

# Publish a draft made by hand (takes the uploads URL or a bare id)
uv run --env-file ../.env kcworks-publish https://works.hcommons.org/uploads/<id>
```

Options for `kcworks-upload`:

- `--dry-run` — print the record JSON and the files that would be attached.
- `--collection SLUG` — import into this collection instead of the
  configured one.
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
