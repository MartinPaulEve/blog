# Editorial Red — site redesign + light/dark theming

Date: 2026-06-22

## Goal

Replace the current "Soft Minimalism" teal/green design with a cohesive deep-red
editorial identity, preserve the clean readable-text focus of the reading pages,
keep the About page's publications layout untouched, and add a light/dark theme
toggle defaulting to light (dark mode = striking black + red).

## Architecture context

Jekyll site. Styling lives in two files, both consuming CSS custom properties:

- `assets/css/styles.css` — loaded on every page via `_includes/_head.html`;
  contains the `:root` palette + homepage/global styles.
- `assets/css/blog-post.css` — additionally loaded on post/page/index reading
  pages; consumes the same variables but also has some hardcoded colours.

Shared includes: `_head.html`, `_navigation.html`, `_footer.html`.
Layouts: `home.html`, `post.html`, `page.html`, `post-index.html`, `category.html`.
The About page uses `layout: page` and includes the large `publications.html`.

## Colour system

Defined once in `styles.css` `:root` (light) with a `[data-theme="dark"]`
override. All hardcoded teal/green values in both CSS files are routed through
these variables.

Light (default):
- `--bg-primary #faf8f5`, `--bg-white #ffffff`
- `--text-primary #1a1a1a`, `--text-secondary #5c5853`, `--text-muted #8a857d`
- `--accent-primary #b3122a`, `--accent-secondary #8c0d20`
- `--border-color #e7e1d7`

Dark:
- `--bg-primary #0d0d0d`, `--bg-white #161616`
- `--text-primary #f2efe9`, `--text-secondary #b3ada3`, `--text-muted #7d7870`
- `--accent-primary #e63946`, `--accent-secondary #ff5a5a`
- `--border-color #282828`

## Typography

- Headings: **Fraunces** (display serif). Body: **Newsreader** (reading serif).
- Update the Google Fonts link in `_head.html` and the `--font-serif` /
  `--font-sans` variables. Literary-journal serif-on-serif feel.

## Theme toggle

- Sun/moon button added to `_navigation.html` (visible desktop + mobile).
- State persisted in `localStorage` under `theme`; **defaults to light**.
- Inline no-flash script in `_head.html` sets `data-theme` on `<html>` before
  paint.
- Toggle logic + highlight.js theme swap (atom-one-light ⇄ atom-one-dark) in
  `/assets/js/script.js`.

## Per-page changes

- Homepage: keep all sections; re-skin; drop the teal "profile glow".
- Reading pages: re-skin only; red blockquote rule; dark-aware code blocks.
- About page: structurally untouched — publications `.bibitem`/`.prefix` layout
  unchanged, inherits new colours only.

## Verification

Build the site and screenshot homepage, a post, and About in both light and dark
modes; confirm no residual teal and the publications layout is intact.
