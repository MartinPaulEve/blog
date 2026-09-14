# thought-composer

The eve.gd "short thought" tool: an interactive terminal composer with a
live Bluesky character count (300 graphemes), link facets and preview
cards, image attachments (pasted from the clipboard or given as files),
and cross-posting to Bluesky (@eve.gd) and Mastodon (@mpe@hcommons.social)
— threading automatically when a thought runs over a limit, without
ever altering the words. Each service threads against its own limit:
Bluesky at 300 graphemes, Mastodon at its instance's character limit
(hcommons.social allows 1,000, URLs counting as 23; override with
`MASTODON_CHARACTER_LIMIT` in `.env`) — so a thought that threads on
Bluesky often posts to Mastodon whole.

The thought itself is stored untouched in `_data/thoughts.yml`, which
feeds /thoughts/, the post sidebar widget, and the homepage block. After
posting, the tool runs the quick deploy (`evedeploy --quick`: jekyll
build + rsync only — no Sequoia, no git, no deposits).

Run via `./thought.sh` from the blog root:

- `./thought.sh` — open the composer (Enter posts, Alt+Enter newline,
  Ctrl+P pastes an image from the clipboard, Ctrl+C cancels).
- `./thought.sh --image shot.png` — attach an image file (repeatable).
- `./thought.sh --text "..."` — skip the TUI.
- `./thought.sh --dry-run --text "..."` — show how it would thread.
- `./thought.sh --no-post` / `--no-deploy` — keep it local.
- `./thought.sh probe` — check both services' credentials.

Credentials in `.env`: `BLUESKY_APP_PASSWORD` (app password for eve.gd,
from bsky.app Settings → App Passwords) and `MASTODON_ACCESS_TOKEN`
(hcommons.social Preferences → Development → New application, scopes
`write:statuses write:media read:accounts`). `BLUESKY_IDENTIFIER` and
`MASTODON_BASE_URL` override the defaults.
