# evedeploy

The eve.gd deployment pipeline as a proper Python app — everything
`deploy.sh` does, with a click CLI and the block-pixel wordmark banner.

Pipeline order (faithful to the shell script): preflight checks (sequoia on
PATH, node ≥ 19 if present) → resize oversized cover images → sequoia
dry-run preview → interactive confirmation gate → sequoia publish →
refresh the CV from `../eprintsToCV/output` → `jekyll build` → git commit
and push → rsync `_site/` to the server.

## Running it: the container

`./deploy.sh` runs the pipeline inside a container image so a fresh clone
deploys from any machine. The host needs only Docker (or Podman), python3,
and an SSH agent holding the deploy and commit-signing keys; everything the
pipeline shells out to — Jekyll 4.4.1 with the site's gem set, headless
Chromium for the PDF editions and OG cards, exiftool, ImageMagick, uv,
Node + sequoia-cli, rsync, git — is in the image
(`evedeploy/container/Dockerfile`).

The first run builds the image (a few minutes); it is rebuilt automatically
whenever the Dockerfile, the entrypoint, `Gemfile` or `Gemfile.lock`
change (the tag is a digest of those files). What the container sees:

- the repository, read-write, at its host path — `.env`, `.pdf_cache`,
  `.og_cache`, `.jekyll-cache` and `_site` are the host's own files, so
  cached PDFs and OG cards carry over and builds stay fast;
- every entry of `~/.ssh` and the git config, read-only, at their host
  paths — mounted from their resolved locations, since home-manager keeps
  them as symlinks into `/nix/store` — so `Host` aliases, `IdentityFile`
  lines and your git identity keep working;
- `~/.config/sequoia` (the ATProto credentials sequoia stores), read-write
  so refreshed tokens persist;
- one SSH agent socket: `$EVEDEPLOY_SSH_AGENT` if set; otherwise, inside
  an SSH session (where nobody can approve a desktop agent's prompt), the
  agent forwarded from your own machine (`$SSH_AUTH_SOCK`); otherwise
  `~/.bitwarden-ssh-agent.sock`, then `~/.1password/agent.sock`, then
  `$SSH_AUTH_SOCK`. It is mounted at its own path, becomes the
  container's `SSH_AUTH_SOCK`, and is also mounted at the desktop agents'
  paths, so `IdentityAgent` lines in `~/.ssh/config` that point at
  1Password or Bitwarden reach the chosen agent instead. Commit signing
  is redirected to plain `ssh-keygen`, which signs with the key that
  agent offers (the host's signing wrapper is host-specific);
- `/etc/hosts`, read-only, so the rsync target alias resolves;
- `../eprintsToCV/output`, read-only, when that sibling checkout exists;
- a named volume (`evedeploy-uv-cache`) for uv's download cache.

It runs on the host network with a TTY, so the banner, the step log, the
ATProto confirmation gate, Ctrl+C and the `--build-only` preview server
on 127.0.0.1:8000 all behave as before.

Launcher-only switches (consumed by `deploy.sh`, never forwarded):

- `--native` — the old behaviour: run with the host's toolchain.
- `--shell` — a bash prompt inside the container, for poking around.
- `--rebuild-image` — force a fresh image build before running.
- `EVEDEPLOY_RUNTIME=podman` picks the runtime (default: docker, then
  podman); `EVEDEPLOY_SSH_AGENT=/path/agent.sock` names the agent.

What stays on the host: `./biron.sh login` (an interactive browser
sign-in; the cookie it stores in the repo is what the container uses)
and `sequoia auth` (its OAuth flow opens a browser; the credentials it
writes to `~/.config/sequoia` are what the container reads).

Two things the image does to match the Nix-built site byte for byte:
`Gemfile` includes `liquid-c`, because Jekyll loads it whenever it is
installed and its whitespace handling differs from pure Liquid's (which
would shift every PDF cache key), and `_config.yml` pins
`timezone: Europe/London`, because Jekyll otherwise stamps posts in the
system zone and a UTC container shifts dates and can move a midnight post
to a different day's URL.

## Building on a remote host

Set `REMOTE_BUILD_HOST=<ssh host>` in `.env` (and, optionally,
`REMOTE_BUILD_DIR`, default `~/build/martineve/blog`) and `./deploy.sh`
splits the run in two, for connections too thin to rsync the site:

1. **Here:** cover resize, CV refresh (the `../eprintsToCV` sibling is
   local), commit and push. `.env` and the BIROn cookie are copied to the
   host; sequoia's credential store is seeded only if the host has none.
2. **On the host:** clone on first use, reset the checkout to the pushed
   branch, then `./deploy.sh --remote-phase …` (local run, no resize or
   CV step, a REMOTE BUILD SERVER wordmark so the two halves of the
   output tell apart) — the same container image, built there on first
   use — for everything else:
   Sequoia (its confirmation gate reaches your terminal through `ssh -t`),
   feed fetches, build, KC Works, commit and push, rsync, webmentions, the
   Rogue Scholar wait, BIROn.
3. **Here again:** `git pull --ff-only` collects whatever the host
   committed (deposit stamps, the webmention ledger).

Your SSH agent is forwarded (`ssh -A`), so the host signs commits and
reaches the deploy server with this machine's keys; the host needs the
deploy server's and GitHub's host keys in its `known_hosts`. Inside the
host's container the forwarded agent is mounted at the desktop agents'
paths as well, so an `IdentityAgent` line in the host's own
`~/.ssh/config` (waldorf steers sessions without a TTY to a 1Password
socket) still reaches it. `./deploy.sh --remote-check` tries every hop
and reports, pinning the forwarded agent for the same reason. `--local`
runs everything here regardless; `--build-only` always stays local.
`./thought.sh` goes through the same hand-off (`--quick`), committing
the thought first.

### The build cache across machines

The deploy server is the canonical PDF/OG cache: the PDFs it serves are
byte-for-byte the `.pdf_cache` renders, the OG cards likewise, and the
PDF content hashes are mirrored to `~/blog/.pdf_cache/` there after
every ship. Each build pulls all three into `.pdf_cache`/`.og_cache`
first (incremental, never deleting, never overwriting a newer local
file), so a cache hit means "the live PDF already matches this page"
whichever machine last built. `--no-cache-sync` skips both the pull and
the hash push (say, to avoid a large pull right after a print-CSS change
re-rendered every PDF elsewhere).

## Usage

From the blog root (or anywhere inside it):

```sh
uv run --project evedeploy evedeploy ["commit message"]
uv run --project evedeploy evedeploy --no-resize ["commit message"]
```

Or, inside the container, via `./deploy.sh ["commit message"]`.

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
