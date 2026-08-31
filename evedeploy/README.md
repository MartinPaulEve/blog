# evedeploy

The eve.gd deployment pipeline as a proper Python app — everything
`newdeploy.sh` did, with a click CLI and the block-pixel wordmark banner.

Pipeline order (faithful to the shell script): preflight checks (sequoia on
PATH, node ≥ 19 if present) → resize oversized cover images → sequoia
dry-run preview → interactive confirmation gate → sequoia publish →
refresh the CV from `../eprintsToCV/output` → `jekyll build` → git commit
and push → rsync `_site/` to the server.

## Usage

From the blog root (or anywhere inside it):

```sh
uv run --project evedeploy evedeploy ["commit message"]
uv run --project evedeploy evedeploy --no-resize ["commit message"]
```

Or via the compatibility shim: `./newdeploy.sh ["commit message"]`.

To build the site locally to `_site` and preview it — PDF editions
included, nothing published, committed or deployed:

```sh
uv run --project evedeploy evedeploy --build-only
```

This serves the preview at http://127.0.0.1:8000/ (falling over to the
next free port when 8000 is taken) until Ctrl+C. Pass `--no-server` to
just build without serving.

Options:

- `MESSAGE` — the git commit message (default: `Publish YYYY-MM-DD HH:MM`).
- `--build-only` — just resize covers and `jekyll build` to `_site`, then
  serve the local preview (the pdf_pages plugin renders the PDF editions
  during the build); skips sequoia, the CV refresh, git and rsync entirely.
- `--no-server` — with `--build-only`: skip the preview server.
- `--no-resize` — skip the cover-image resize step.
- `--yes` — skip the interactive "Publish these to ATProto for real?" gate.
- `--root PATH` — the blog root (default: found by walking up from the
  working directory to the nearest `_config.yml`).

## Tests

```sh
uv run pytest
```
