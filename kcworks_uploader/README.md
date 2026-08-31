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
```

Once a deposit is published, record it in the post's front matter so the
blog and repository records stay linked:

```yaml
kcworks: https://works.hcommons.org/records/<id>
```

The signposting plugin emits this as `archivedAt` in the post's
metadata.json (the KC Works record already points back through its
canonical-URL identifier).

Or from this directory:

```sh
# Preview the record JSON without touching the network
uv run kcworks-upload ../_posts/2026-08-28-some-post.md --dry-run

# Create the draft (review it in the browser before publishing)
KCWORKS_API_TOKEN=... uv run kcworks-upload ../_posts/2026-08-28-some-post.md

# Or skip the draft stage and publish immediately
KCWORKS_API_TOKEN=... uv run kcworks-upload ../_posts/2026-08-28-some-post.md --live

# Publish a previously created draft (takes the uploads URL or a bare id)
KCWORKS_API_TOKEN=... uv run kcworks-publish https://works.hcommons.org/uploads/<id>
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
