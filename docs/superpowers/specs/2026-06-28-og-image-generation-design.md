# Generated Open Graph / Twitter card images — design

**Date:** 2026-06-28
**Status:** Approved (pending spec review)

## Overview

Replace the current behaviour — using a post's raw `image.feature` as its
social-preview image — with a build-time **generated** card per post: a
designed 1200×630 composition in the site's red/black visual language, cached
on disk so it is produced once per post and re-used on every subsequent build.
The same artwork is used for Open Graph and (at the Twitter-specific size) for
the Twitter/X card.

## Goals

- One designed preview image per `layout: post`, matching the site's brand
  (near-black background, brand-red diagonal, Fraunces serif + IBM Plex Mono).
- Generated once and cached **outside `_site`**; deleting a cached file is the
  only action required to force regeneration.
- Drive `og:image` and `twitter:image` from the generated artwork.
- Reproducible, offline-capable builds (no reliance on remote fonts/services at
  render time).

## Non-goals

- Generating cards for pages other than posts (apex, /about/, etc.). Out of
  scope; can be added later.
- Auto-invalidating the cache when a post's title/excerpt/image changes. By
  design the cache key is the slug only; regeneration is manual (delete file).
- Redesigning the on-page post hero or the site CSS.

## Image sizes

- **Open Graph (`og:image`): 1200×630** — the de-facto standard (Facebook,
  LinkedIn, Slack, Discord, etc.).
- **Twitter/X (`twitter:image`, `summary_large_image`): 1200×628** — X's
  current spec is a 1.91:1 ratio; 1200×628 is the recommended size. This is only
  2px shorter than the OG image, so the two are visually near-identical, but a
  dedicated variant is rendered at the exact Twitter size per requirement. (Some
  third-party guides cite 1200×675/16:9; 1.91:1 is X's official card ratio, so
  1200×628 is used. The height is a single constant, trivially changeable.)

Sources:
[X (Twitter) image sizes 2026](https://influencermarketinghub.com/twitter-image-size/),
[Twitter card image size guide](https://moda.app/resources/sizes/twitter-card),
[Twitter image specs 2026](https://soona.co/image-resizer/twitter-spec-guide).

## Architecture

A new Ruby Jekyll plugin, `_plugins/og_image.rb`, mirroring the structure of
`_plugins/signposting.rb`:

- A pure module (`OgImage`) holding logic with no Jekyll/Chrome dependency, so
  it is unit-testable in plain Ruby: slug → cache path, excerpt extraction and
  truncation, feature-image resolution + data-URI embedding, HTML template
  assembly, and the served-URL/meta builders.
- A `Jekyll::OgImageGenerator < Generator` (priority `:low`, `safe false`) that
  wires the module into the build.

### Per-post flow (generator)

For each `site.posts.docs` document with `layout: post`:

1. Compute `slug` from the post's output path; cache file = `.og_cache/<slug>.png`
   and `.og_cache/<slug>.twitter.png`.
2. On a cache miss:
   a. Assemble an HTML document (template + post data + embedded feature image +
      `@font-face` from local TTFs).
   b. Render the **OG image** (1200×630) via the **injected renderer** (default:
      headless Chrome); write `<slug>.png`.
   c. Derive the **Twitter variant** (1200×628) from that render by trimming 2px
      with ImageMagick (`convert <png> -gravity center -crop 1200x628+0+0 …`);
      write `<slug>.twitter.png`. This avoids a second Chrome invocation. If
      ImageMagick is unavailable, fall back to a second render at 1200×628.
3. Copy each cached PNG into `_site/images/og/<slug>.png` and
   `_site/images/og/<slug>.twitter.png`; register each as a no-op static file so
   it is served and survives `site.cleanup` (same pattern as `SignpostingFile`).
4. Set `doc.data["og_image"]   = "https://eve.gd/images/og/<slug>.png"` and
   `doc.data["og_image_twitter"] = "https://eve.gd/images/og/<slug>.twitter.png"`.

### Renderer (injected, like the DOI fetcher)

The generator exposes a writable `renderer` collaborator — a callable
`->(html, width, height, out_path) { ... }`. The default shells out to:

```
google-chrome --headless --disable-gpu --no-sandbox --hide-scrollbars \
  --force-device-scale-factor=1 --window-size=<W>,<H> \
  --screenshot=<out_path> file://<temp_html>
```

(`--headless=new` if supported.) Tests inject a fake renderer that writes a
placeholder file, so the generator's caching/copy/meta logic is exercised
without spawning a browser or touching the network. The exact Chrome flag set is
an implementation detail, finalised during the build.

## Cache & invalidation

- Cache dir: **`.og_cache/`** at the repo root — a dotfile directory, so Jekyll
  does not copy it into `_site` (same approach as `.doi_cache.json`).
- **Gitignored, not committed.** Each PNG is ~100–300 KB and there are ~2000 of
  them; committing them would bloat the repo, and the *deployed* artwork already
  lives in the tracked `_site/images/og/`. The cache exists only to avoid
  re-rendering on the local build machine (this site builds and deploys from one
  machine via `deploy.sh`), which satisfies "don't regenerate each time". A fresh
  clone would regenerate the cache on first build.
- Cache key: the post **slug** only. Two files per post (`<slug>.png`,
  `<slug>.twitter.png`).
- **Regeneration:** delete the file(s) in `.og_cache/`; the next build rebuilds
  just those.

## Layout (1200×630; Twitter variant identical at 1200×628)

- **Background:** near-black `#0b0b0b` base, with a brand-red `#b3122a` diagonal
  taper using the site's slope (~4°, mirroring `--slope-v`), plus one or two
  thin `#e63946` diagonal "cutting lines".
- **Left column (~62% width, ~64px padding), light-on-dark:**
  - **Kicker pill:** rounded-full, fill `#b3122a`, text white, IBM Plex Mono,
    content **"eve.gd: Martin Paul Eve"**.
  - **Title:** white `#ffffff`, **Fraunces** ~600 weight, ~60px, clamped to 3
    lines with ellipsis.
  - **Snippet:** muted `#b3ada3`, ~24px, post excerpt — HTML-stripped, collapsed
    whitespace, truncated to ~160 chars / 2–3 lines with ellipsis.
  - **Button:** fill `#b3122a`, white IBM Plex Mono text **"Read post"**.
  - The demo's "Your Startup Logo" element is omitted.
- **Right column (~38%):** the post's resolved feature image in a rounded
  (~24px) shadowed card, `object-fit: cover`, layered above the diagonal.
- **No feature image:** the right card is dropped and the left column spans the
  full width.

Feature-image resolution matches the current site: `page.image.feature`, used as
`/images/<feature>` unless it is an absolute URL. The local file is read and
embedded into the template as a base64 data URI for deterministic rendering.

## Fonts

**Fraunces** (serif display) and **IBM Plex Mono** are downloaded once as TTFs
into a committed `_og/fonts/` directory and referenced via `@font-face` with
`file://` URLs in the template, so rendering needs no network and is
reproducible. Both are SIL OFL licensed; redistribution within the repo is
permitted. A short licence/attribution note accompanies the font files.

## Meta-tag wiring

In `_includes/_head.html`, the existing `og:image` and `twitter:image` blocks
are updated to prefer the generated artwork when present:

- `og:image` → `page.og_image` when set, else current `image.feature`/`og.png`
  fallback. Add `og:image:width` `1200` and `og:image:height` `630`.
- `twitter:card` stays `summary_large_image`; `twitter:image` → the
  `page.og_image_twitter` 1200×628 variant when set, else the existing fallback.

No duplicate tags are introduced; the current fallback markup is preserved for
any document without a generated image.

## Edge cases & fallbacks

- **No feature image:** full-width text layout (above).
- **Missing feature file on disk:** treat as no image (full-width text); log a
  build warning naming the post.
- **Renderer failure / Chrome absent:** log a warning, skip setting
  `og_image*` for that post (head falls back to current behaviour); the build
  does not fail.
- **Very long titles:** clamped to 3 lines with ellipsis in CSS.
- **Empty excerpt:** snippet is omitted; title + pill + button still render.

## Testing strategy

Pure `OgImage` helpers (no Chrome, no network), red/green:

- slug/cache-path derivation from a post URL.
- excerpt extraction: HTML strip, whitespace collapse, truncation + ellipsis.
- feature-image resolution (relative vs absolute) and data-URI embedding from a
  temp fixture image.
- template assembly: contains the pill text, title, snippet, "Read post", the
  embedded image when present, and omits the right card when absent.
- served-URL and `og:image`/`twitter:image` value builders.

Generator integration (fake renderer + temp dirs, no browser):

- cache miss → renderer invoked, files written to `.og_cache/`, copied to
  `_site/images/og/`, registered as static files.
- cache hit → renderer **not** invoked (inject a renderer that raises).
- `doc.data["og_image"]`/`["og_image_twitter"]` set to the expected URLs.
- the OG render is requested at 1200×630 and the Twitter file is produced (crop
  step stubbed in tests).
- no-feature post still produces a card (full-width path).

Real-build verification (manual, like the signposting/DOI work): build a couple
of posts, confirm the PNGs exist at the right size and look correct, and confirm
the head tags point at them.

## Performance

First full build renders up to 994 posts via Chrome (one Chrome invocation each;
the Twitter variant is a cheap ImageMagick crop) — a one-time cost of roughly
15–30 minutes — after which everything is cache-fast. Documented and accepted.
(A future optimisation could throttle per build, but is out of scope here.)

## Risks

- **Chrome/runtime variability** in CI/deploy: mitigated by committing the cache
  so deploy builds normally render nothing.
- **Headless flags** differing across Chrome versions: isolated behind the
  injected renderer and finalised during implementation.
- **First-build duration:** documented; can be pre-warmed locally and committed.

## Files

- `_plugins/og_image.rb` (new) — module + generator.
- `_og/fonts/` (new) — committed Fraunces + IBM Plex Mono TTFs + licence note.
- `.og_cache/` (new, **gitignored**) — generated PNG cache, outside `_site`.
- `.gitignore` (edit) — add `.og_cache/`.
- `_includes/_head.html` (edit) — meta wiring.
- `test/test_og_image.rb`, `test/test_og_image_generator.rb` (new) — tests.
</content>
</invoke>
