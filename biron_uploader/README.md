# biron-uploader

Deposits eve.gd blog posts to BIROn (Birkbeck Institutional Research
Online, an EPrints 3.3 repository) over SWORD 1.3 with the built PDF
edition and the markdown source attached, mirroring the metadata of the
blog posts already in the repository.

BIROn authenticates everything through Microsoft SSO (Shibboleth), and
its machine-facing Basic-auth fallback validates nothing by default.
Until the systems team enables Basic auth for a deposit account
(`BIRON_USERNAME` / `BIRON_PASSWORD`), authenticate with a logged-in
browser session instead: sign in to BIROn, copy the Cookie header from
any request (F12 → Network), and set `BIRON_COOKIE=eprints_session=…`
in the blog's `.env`. The session cookie is accepted on the `/id/`
CRUD endpoint (and possibly `/sword-app/`); `./biron.sh probe` reports
which, and prints the `BIRON_COLLECTION` override to use when only the
CRUD endpoint is open.

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
