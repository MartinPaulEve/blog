# smol.pub mirror (gem.eve.gd)

Spec and operating notes for the small-web edition of the blog. Tracked in
GitHub issue #4.

## Objective

Every published post is mirrored, as a text-only gemtext document, to the
smol.pub journal attached to `gem.eve.gd`, so the archive is readable at
`https://gem.eve.gd/<slug>` and `gemini://gem.eve.gd/<slug>`. Each post page
on eve.gd links to both. Images and files are never uploaded (the journal has
100 MB of storage); pictures become link lines pointing at the eve.gd copy.

Success looks like:

- `uv run --env-file .env _smolpub/sync_smolpub.py --dry-run` converts all
  1,007 posts to gemtext under `_smolpub/out/` without touching the network.
- A real run pushes only posts that are new or whose text changed since the
  last run, and records what it pushed in `_smolpub/synced.yml`.
- `./deploy.sh` runs the sync after the Jekyll build, rebuilds when a post was
  pushed for the first time (so its links render), and never fails a deploy
  because smol.pub is down.
- A post page shows "View this item on https://gem.eve.gd" and "View this
  item on gemini://gem.eve.gd" once the post is on smol.pub (its front
  matter carries `smolpub: <slug>`), and nothing before, with no PDF
  re-renders (the links live in the paragraph the PDF cache key ignores).

## Design

The source of each document is the **built** page in `_site`, not the
Markdown. Jekyll has already resolved Liquid tags, the `{% highlight %}`
blocks, kramdown footnotes, the content-warning disclosures and the
generated reference list, and the oldest 500-odd posts are raw WordPress HTML
anyway. One HTML-to-gemtext converter therefore covers every era. The post's
title, date and canonical URL come from the `metadata.json` Jekyll writes
beside each page.

Gemtext mapping (the format has text, `=>` links, `#`/`##`/`###` headings,
`*` list items, `>` quotes and ``` preformatted toggles, nothing else):

| HTML                         | gemtext                                            |
| ---------------------------- | -------------------------------------------------- |
| `<p>`                        | one text line; its links follow as `=>` lines      |
| `<h1>`/`<h2>`                | `##` (the post title is the document's `#`)        |
| `<h3>` and deeper            | `###`                                              |
| `<ul><li>`                   | `* item` (nesting flattened)                       |
| `<ol><li>`                   | `1. item` text lines                               |
| `<blockquote>`               | `> ` per paragraph                                 |
| `<pre>`                      | ``` block, entities decoded, highlighting dropped  |
| `<table>`                    | one text line per row, cells joined with ` \| `    |
| `<img>`                      | `=> https://eve.gd/... Image: alt text`            |
| `<iframe>`                   | `=> src Embedded content`                          |
| footnote reference           | `[n]` inline; the notes list becomes `[n] text`    |
| `<details>`/`<summary>`      | transparent (heading + "Content warning: …" line)  |
| `hidden`, `<script>`, styles | dropped (the APA/Chicago reference variants etc.)  |
| `<em>`, `<strong>`, `<code>` | plain text                                         |

Relative links are made absolute against `https://eve.gd`; same-page
fragment links are dropped. The document opens with the title, a provenance
line giving the original publication date (smol.pub lists posts by the date
they were created there, so the backfill would otherwise look like one
day's work) and a link back to the web edition.

Slugs are flat: the last segment of the eve.gd URL, lower-cased with anything
outside `a-z0-9-` turned into `-`. Slugs are unique across the archive.

## Sync protocol

smol.pub's API is the one its `smolpub.sh` uses: a multipart form POST of
`title`, `slug` and `content` with the token as a `smolpub` cookie.
`POST /posts/save` answers 302 on creation; anything else means the slug
exists, and `POST /posts/<slug>/update` replaces it. The token is
`SMOL_PUB_KEY` in the environment or `.env`.

`_smolpub/synced.yml` is the ledger: URL slug → `{slug, hash, synced}`. The
hash is of the gemtext content, so an unchanged post is never re-sent and an
edit is. A published post also gets `smolpub: <slug>` stamped into its front
matter, beside the other identifier keys, and that key is what the post
layout consults to show the two links. Posts in the ledger that lack the key
are re-stamped on any run, with no network access needed.

## Commands

```
uv run --with pyyaml --with pytest -m pytest _tests/test_smolpub_sync.py
uv run --env-file .env _smolpub/sync_smolpub.py --dry-run     # convert only
uv run --env-file .env _smolpub/sync_smolpub.py --only SLUG    # one post
uv run --env-file .env _smolpub/sync_smolpub.py                # new + changed
uv run --env-file .env _smolpub/sync_smolpub.py --force        # everything
cd evedeploy && uv run pytest                                  # pipeline
```

## Structure

```
_smolpub/sync_smolpub.py   converter + API client + CLI (stdlib + pyyaml)
_smolpub/out/<slug>.gmi    generated documents (gitignored)
_smolpub/synced.yml          ledger, committed by the deploy
_tests/test_smolpub_sync.py
evedeploy/evedeploy/pipeline.py  sync_smolpub() step
_layouts/post.html         the two links
```

## Boundaries

- Always: run from a fresh `jekyll build`; keep the links inside the
  `post-pdf` paragraph; keep the step tolerant in the deploy.
- Ask first: deleting posts on smol.pub, uploading any file, changing slugs
  once published (they are the public URLs).
- Never: commit the token; print it; store images.

## Assumptions

- smol.pub accepts slugs of up to ~190 characters (the longest here is 188).
- The `update` endpoint accepts the same form fields as `save`.
- Posts are never deleted from the blog; removal from smol.pub is manual.
