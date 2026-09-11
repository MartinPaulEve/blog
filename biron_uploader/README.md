# biron-uploader

Deposits eve.gd blog posts to BIROn (Birkbeck Institutional Research
Online, an EPrints 3.3 repository) over SWORD 1.3 with the built PDF
edition and the markdown source attached, mirroring the metadata of the
blog posts already in the repository.

BIROn authenticates everything through Microsoft SSO (Shibboleth), its
machine-facing Basic-auth fallback validates nothing, and the EPrints
session cookie is session-only (never in the browser's on-disk store).
So the tool drives its own login: `./biron.sh login` opens a dedicated
Chromium profile for the Microsoft sign-in and stores the harvested
cookie in `.biron_cookie` (gitignored). After that first interactive
run, the Microsoft session persisted in the profile usually completes
the redirect loop unattended — probe/deposit/backfill verify the
cookie before use and silently re-harvest it headlessly when stale
(`./biron.sh login --headless` does the same by hand). Set
`BIRON_COOKIE=auto` in `.env` so the evedeploy deposit step knows it
is configured; a literal `BIRON_COOKIE=secure_eprints_session…=value`
remains a manual override, and `BIRON_USERNAME`/`BIRON_PASSWORD` Basic
auth is still supported should the systems team ever enable it.

Commands (all via `./biron.sh` from the blog root):

- `biron-probe` — verify credentials and list the deposit collections.
- `biron-upload [--dry-run] _posts/YYYY-MM-DD-slug.md` — deposit one post.
- `biron-backfill [--dry-run]` — deposit every post that lacks a
  `biron:` front-matter key, is not pending in `_biron/deposited.yml`,
  and is not listed in `_biron/skip.yml`.

Deposits land in the repository's review workflow, not the live
archive; the `biron:` key is stamped later by the `_biron` fetch sweep
once the record is public. The `_biron/deposited.yml` ledger stops a
post being redeposited while it waits for review.
