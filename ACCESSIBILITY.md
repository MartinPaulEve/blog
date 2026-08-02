# Accessibility follow-up list (human actions required)

This file is for you to read and act on; it is excluded from the Jekyll build
(`exclude:` in `_config.yml`) and should not be committed. Everything that
could be fixed in the site's structure, CSS, templates, and post corpus has
been fixed directly. What remains below needs either your judgement, external
tools, or changes to the external generators.

## 1. PDFs

### The CV — already tagged, but verify quality

Good news: both copies of the CV (`/c-v/Eve-CV.pdf` and `/about/Eve-CV.pdf`)
are **already tagged** PDFs (`pdfinfo` reports `Tagged: yes`). The CaSSius-CV
pipeline prints via headless Chrome (Skia), which derives PDF structure tags
from the source HTML. You therefore do not need to change the generator's
output format — but tag *quality* follows the HTML's semantics, so in the
CaSSius-CV templates it is worth checking that:

- headings are real `<h1>`–`<h4>` elements, not styled `<div>`s;
- lists are real `<ul>`/`<li>`;
- the document language is set (`<html lang="en">`);
- any images carry alt text;
- the visual ALL-CAPS section headings ("ACADEMIC TEACHING" etc.) are produced
  with `text-transform: uppercase` rather than typed in capitals — screen
  readers can spell out literal capitals letter-by-letter. (The same fragments
  are copied into `_includes/` at deploy time, so this fixes the web CV too.)

A quick manual check: open the CV in a screen reader (or Acrobat's "Read Out
Loud" / accessibility checker) and confirm reading order and heading nesting.

### Untagged PDFs served by the site

These report `Tagged: no`. Most are historical documents; re-exporting from
source (LibreOffice/Word "tagged PDF" export) or running them through a
tagging tool would be needed for full AAA parity. Suggested priority order:

**Higher priority (linked from live posts/pages, your own authored content):**
- `book_proposals/Proposal for Oxford University Press for The Digital Humanities and Literary Studies.pdf`
- `book_proposals/Proposal for punctum books for Warez 2018.pdf`
- `book_proposals/Proposal for Stanford University Press for Theses on the Metaphors of Digital-Textual History.pdf`
- `images/Eve - Plan S Response.pdf`
- `images/Eve-Redaction.pdf`, `images/Eve-LIT-Egan.pdf`, `images/Resignation.pdf`
- `images/s1-olh-82_eve.pdf`, `images/s2-olh-82_eve.pdf`
- `derrida/*.pdf` (five scanned/typeset Derrida readings — if these are scans
  they would also need OCR before tagging)
- `images/uploads/**` — c. 20 authored papers, reviews, syllabi and posters
  from 2010–2014 (full list via
  `find . -name '*.pdf' -exec sh -c 'pdfinfo "$1" | grep -q "Tagged:.*no" && echo "$1"' _ {} \;`)

**Consider removing instead of fixing:**
- `output.pdf` in the repository root looks like a stray build artefact and is
  published at `/output.pdf`; if it is not deliberate, delete or exclude it.
- `cassius/sample.pdf` is a demo artefact of the (archived) CaSSius project.
- Third-party documents you merely mirror (e.g.
  `images/uploads/2013/11/Monographs-ERG01Min-Notes-of-meeting-4-November-20131.pdf`,
  `images/CMA-RELX.pdf`, `images/HEFCEREF.pdf`, `images/allingtonetal.pdf`,
  `images/Freer.pdf`) — you are not the author; an accessibility statement
  can scope these as third-party/archival content.
- Everything under `19/websites/` is the preserved *19* journal archive
  (mixed tagged/untagged) — reasonably scoped as an unmodified historical
  archive in the accessibility statement (now done).

## 2. Embedded media — captions and transcripts

Structural fixes — descriptive `title` attributes on all 21 iframes across 12
posts — have been applied in the posts themselves. What remains is the
captions/transcript work below. Every embed was checked against the provider
(oEmbed), so dead embeds are marked as such — those need removal or an
archive link, not captions.

### Live videos that need captions + transcript

- `_posts/2011-05-06-on-pynchon-and-privacy.md` — YouTube `9k_TNk2mtTA`,
  1997 CNN report on Thomas Pynchon (spoken news segment).
- `_posts/2011-11-05-brian-lobel-ball-and-other-funny-stories-about-cancer.md`
  — YouTube `2aia9H6867Q`, opening of Brian Lobel's performance *BALL*.
- `_posts/2012-04-09-the-future-of-academic-publishing-qa.md` — YouTube
  `J5NCGvGgVrM`, UKSG 2012 plenary Q&A (you are a speaker — you may have
  notes to seed a transcript).
- `_posts/2012-04-11-video-of-my-uksglive-presentation-on-the-future-of-academic-publishing.md`
  — YouTube `aQxNN3Ujjn4`, your UKSG 2012 presentation. The same post links a
  direct download `href="/Files/0101-Martin-Paul-Eve-mp4"` — the href looks
  malformed (`-mp4` rather than `.mp4`); one transcript covers both.
- `_posts/2021-03-27-how-to-fix-a-broken-crumar-bit99-synthesizer.md` —
  YouTube `_ymxa2kSqbs`, your restored Bit99 demo; if it is synth audio only,
  a one-line descriptive transcript ("the repaired synthesizer playing…")
  suffices.

### Live music embeds (AAA: lyric transcript, or an "instrumental" note)

- `_posts/2014-11-23-current-working-music.md` — live: Hardway Bros *Sleaze*
  (instrumental), Fanfara Tirana & Transglobal Underground *Mehndi*, Paloma
  Faith *Stone Cold Sober* (has lyrics → lyric transcript), SoundCloud
  tracks *Return of the Oscillator* and *Trust Me (Gemini Brothers Remix)*
  (instrumental/electronic).
- `_posts/2019-03-29-on-music-tici-taci-and-a-new-release.md` — five live
  YouTube embeds; four instrumental electronic (note as instrumental), plus
  Pete Seeger *Little Boxes* (has lyrics → lyric transcript).
- `_posts/2019-07-12-ratholin.md` — two SoundCloud clips; the post body
  already prints the full lyrics, so a one-line note tying the lyrics to the
  players completes AAA.
- `_posts/2019-04-26-the-learning-experience-out-today-...md` — SoundCloud
  playlist *The Learning Experience EP*: lyric transcript for the Ratholin'
  vocal track, instrumental note for the rest.

### Audio-only recording that needs a transcript

- `_posts/2011-03-09-richard-stallman-at-the-university-of-sussex.md` —
  direct `.ogg` link to your recording of Stallman's 2011 Sussex lecture,
  hosted at old `martineve.com` (check for link rot too). Audio-only →
  transcript required for AAA.

### Dead embeds — remove or replace with archive links (nothing to caption)

- YouTube removed: `MWQKmjMRyI8` (Inherent Vice fan adaptation,
  `_posts/2012-01-09-...`); `Rt20nXN5U_U` and `UenjwNLC6IU` (two tracks in
  `_posts/2014-11-23-current-working-music.md`).
- Storify (service dead since 2018):
  `_posts/2014-04-19-openness-for-society-or-for-profit.md` (iframe; the
  post's `archive:` front-matter link may already capture it) and
  `_posts/2012-09-16-weird-council-...-storify.md` (script embed; tweet text
  is fortunately reproduced in the post HTML).
- Flash Prezi players (Flash EOL 2020) in five posts, each already followed
  by a plain prezi.com link: `2010-10-24-notes-and-presentation-from-my-open-access-talk.md`,
  `2011-05-23-using-twitter-for-research.md`,
  `2011-10-25-open-access-week-at-the-university-of-sussex.md` (also has
  visibly broken fallback-link markup around line 36),
  `2012-02-09-wordpress-for-academics.md`,
  `2012-07-19-thomas-pynchon-david-foster-wallace-...md`. Delete the
  `<object>` blocks, keep the links; the Prezis are silent slides, and where
  the paper text is in the post that is already the AAA text alternative.
- Prezi iframe in `_posts/2013-07-05-digital-literatures-digital-democracies-digital-threats.md`
  is a classic-Prezi `http:` embed (mixed content on an https site — likely
  blocked/broken). The full paper text is in the post, which is the AAA text
  alternative; swap the iframe for a plain prezi.com link.
- Scribd Flash viewer in `_posts/2010-03-17-david-foster-wallace-archive-material.md`
  (plain scribd.com link precedes it — delete the Flash block).
- VideoPress Flash player in `_posts/2011-02-14-the-analytic-of-patriotism-...md`
  (retired endpoint; remove, or relocate the clip).
- Mendeley Android screencasts in three posts use YouTube's dead `/v/` Flash
  endpoint, but the videos themselves are still live: `KJshIJOdf5Y`
  (`2010-12-20-...`), `15DzM6USj74` (`2011-01-04-...`), `czEPziT13io`
  (`2011-01-05-...`). Replace the Flash objects with modern titled iframes;
  they appear to be silent emulator demos — if so, a short descriptive
  transcript suffices.
- The `<object>/<embed>` strings in
  `_posts/2007-11-09-xss-for-the-common-good-greasemousey.md` are inside a
  JavaScript code listing, not real embeds — no action.

## 3. Changes needed in the external generators

### eprintsToCV (`_includes/publications.html`)

- **307 "Download" links use colour alone** (green = green OA, goldenrod =
  gold OA) to convey the OA route. Site CSS now retunes both colours to AAA
  contrast in both themes, but colour-only meaning still fails WCAG 1.4.1
  (level A) and identical "Download" texts fail 2.4.9 Link Purpose (AAA).
  In the generator: emit e.g. `Download (gold OA)` / `Download (green OA)` as
  the link text, or add an `aria-label` such as
  `Download 'Title' (green open access)` — ideally both.
- **Non-English titles lack `lang` attributes** (Chinese, Korean, Spanish
  titles in the books list) — WCAG 3.1.2 wants
  `<i lang="zh">数字人文与文学研究</i>`-style markup. This needs to come from the
  generator since the file is regenerated at deploy.
- Publications section headings are `<h3 class="sectionheader">` directly
  under the page `<h1>`; emitting `<h2>` would give a correct outline.

### CaSSius-CV fragments (`_includes/Teaching`, `PeerReview`, …)

- Literal ALL-CAPS heading text (see CV note above).
- Fragments start at `<h2>`, which is correct under the page `<h1>` — keep.

### bookPull / musicBrainzPull

- Already emit good alt text on every cover image — no change needed.

## 4. Content-level AAA criteria that remain editorial

These cannot be closed by markup alone; they are judgement calls per post:

- **1.2.6 Sign language for pre-recorded audio**: not provided; the
  accessibility statement now says so honestly. Providing BSL interpretation
  for old talk videos is realistically out of reach for a personal site.
- **3.1.3 Unusual words / 3.1.4 Abbreviations / 3.1.5 Reading level**:
  scholarly posts use specialist vocabulary. Where a post is aimed at a
  general audience, a short plain-language summary at the top satisfies
  3.1.5. Expanding abbreviations on first use (e.g. "open access (OA)") is
  already your general habit — keep doing it.
- **3.1.2 Language of parts** in old posts: quotations in French/German/etc.
  inside historical posts would ideally get `lang` attributes if you ever
  edit those posts anyway.

## 5. Incidental issues found during the audit

- **Wrong cover image**: in
  `_posts/2025-12-16-my-2025-end-of-year-reading-and-writing-roundup.md`, the
  image used for *The Poisonwood Bible* (`cover_08.jpg`) is actually the
  Faber cover of *The Lacuna* (the same file is correctly reused for *The
  Lacuna* later in the post). The alt text now honestly describes what the
  image shows; substitute a real Poisonwood Bible cover when convenient.
- **Dead hotlinked images** (alt text added from context, but the images
  themselves almost certainly no longer load — consider re-hosting from the
  Wayback Machine or removing the tags):
  - `_posts/2010-11-09-demo-2010.md` — `we_will_march_black.png` (old
    martineve.com WordPress path, file not in repo)
  - `_posts/2010-11-19-rockaby-text-annotation-software-gpl-alpha-announcement.md`
    — `gplv3-127x51.png` (same)
  - `_posts/2010-05-10-new-david-foster-wallace-book-fall-2010.md` —
    `posterous.com/images/filetypes/pdf.png` (Posterous shut down in 2013)
- **Ten images in the March–September 2010 posts are missing entirely** — not
  just from the repo but from the live site and from web archives (Wayback has
  no snapshots of the old martineve.com URLs, and the Archive-It capture of
  eve.gd did not include them). Alt text has been written from post context so
  screen-reader users lose nothing further, but the images themselves are
  broken for everyone. Affected posts: international-pynchon-week-2010-abstracts,
  implementing-coins, upcoming-performance-lucy-and-martha,
  upcoming-journal-publishing-workshop, thomas-pynchon-critical-bibliography-zotero-group,
  using-tech-to-help-with-structure, can-we-avoid-the-s-word, dark-cloud-looming,
  british-library-usage-made-clear, humanities-map. Options: delete the `<img>`
  tags, or replace from personal backups if any survive.
  - One alt is a **guess needing your check**:
    `_posts/2010-03-13-thomas-pynchon-critical-bibliography-zotero-group.md`
    (`34-1-200x300.jpg`, described as "Cover of a Thomas Pynchon novel" purely
    from context).
- Five 2010 images that DO exist locally under `/images/uploads/2010/...` are
  still hotlinked via absolute `www.martineve.com/wp-content/...` URLs
  (sshsplit ×2, navy-days ×2, htc-wildfire ×1) — repoint the `src`s at the
  local copies.
- More broadly, many old posts' image `src` attributes still point at
  `martineve.com/wp-content/...` or `eve.gd/wp-content/...`; the `.htaccess`
  rewrites cover these, but a one-off `src` migration to `/images/uploads/...`
  would remove the dependency on redirects.
- `_config.yml` contains **two `exclude:` keys**; YAML keeps only the second.
  Consider merging them (ACCESSIBILITY.md was added to the effective, second
  list).

## 6. What "AAA" means once this list is done

With the structural work now in place (contrast, focus, targets, motion,
headings, alt text, iframe titles, link purpose), the site's own HTML/CSS
meets WCAG 2.2 AAA. The genuine residue is: untagged historical PDFs,
captions/transcripts (and, strictly, sign language) for old embedded media,
and the editorial criteria in §4. The accessibility statement
(`/accessibility/`) has been updated to state the AAA aim and to scope the
archival sub-sites and third-party players honestly — which is exactly what a
conformance claim requires when perfection isn't attainable.
