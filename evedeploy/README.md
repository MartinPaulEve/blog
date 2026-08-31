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

To build the site locally to `_site` for preview — PDF editions included,
nothing published, committed or deployed:

```sh
uv run --project evedeploy evedeploy --build-only
python3 -m http.server -d _site 8000   # then browse http://localhost:8000
```

Options:

- `MESSAGE` — the git commit message (default: `Publish YYYY-MM-DD HH:MM`).
- `--build-only` — just resize covers and `jekyll build` to `_site` for
  local preview (the pdf_pages plugin renders the PDF editions during the
  build); skips sequoia, the CV refresh, git and rsync entirely.
- `--no-resize` — skip the cover-image resize step.
- `--yes` — skip the interactive "Publish these to ATProto for real?" gate.
- `--root PATH` — the blog root (default: found by walking up from the
  working directory to the nearest `_config.yml`).

## Tests

```sh
uv run pytest
```
