# Zotero metadata for blog posts

How the `<head>` (and `<html>`) tags on each post (`_layouts/post.html`) make
Zotero's built-in **Embedded Metadata** translator import the page as a
**Blog Post** — no custom translator, nothing for readers to install.

## The key: force the item type with `zotero:itemType`

Genre/OpenGraph hints alone are unreliable — `prism.genre=blogentry` is *supposed*
to map to Blog Post, but in practice Zotero kept importing posts as **Web Page**
(the OpenGraph default won). The dependable fix is Zotero's own RDFa override,
`zotero:itemType`, which is read **first** in the translator's type precedence
(`t.zotero || t.bib || t.prism || … || t.og || …` in `RDF.js`) and beats
everything else.

Two parts are required, because `zotero` is **not** a built-in prefix in the
translator (only the short `z` is), so it must be declared:

1. Declare the prefix on the `<html>` element (the translator's `getPrefixes`
   reads the `prefix` attribute of `<html>` and `<head>`):

   ```html
   <html lang="en" prefix="og: http://ogp.me/ns# article: http://ogp.me/ns/article# zotero: http://www.zotero.org/namespaces/export#">
   ```

2. Emit the override (note `property=`, not `name=`):

   ```html
   <meta property="zotero:itemType" content="blogPost">
   ```

The `prefix` value is RDFa syntax: `prefix: uri` pairs separated by spaces (a
space **after** each colon is required by the parser's `(\w+):\s+(\S+)` regex).

## Required tags

| Tag | Value | Effect |
|---|---|---|
| `<html prefix="…zotero: http://www.zotero.org/namespaces/export#">` | (declaration) | Registers the `zotero` prefix so the next tag is understood. |
| `zotero:itemType` *(property)* | `blogPost` | **Forces item type → Blog Post.** Highest-priority signal. |
| `prism.publicationName` | `<span class="nocase">eve.gd</span>: Martin Paul Eve` | **Blog Title.** Read before `og:site_name`. The `<span class="nocase">` is CSL markup so styles don't title-case `eve.gd` into `Eve.Gd`. |
| `og:title` | post title | **Title.** Use OpenGraph/`dc.title`, **not** `citation_title` (see below). |
| `citation_author` | `Eve, Martin Paul` | **Author** (`Last, First`; repeat for multiple). |
| `citation_publication_date` | `2022/07/26` | **Date** (`YYYY/MM/DD`). |
| `citation_doi` | `10.59348/kv1zh-wn208` | **DOI** (bare, not a URL). |
| `citation_public_url` | `https://eve.gd/2022/07/26/.../` | **URL** (absolute). |
| `citation_language` | `en` | **Language.** |

## Secondary / belt-and-braces

| Tag | Purpose |
|---|---|
| `prism.genre` = `blogentry` | Secondary type hint (kept in case `zotero:itemType` is ever ignored). |
| `dc.title` / `dc.creator` / `dc.date` / `dc.language` | Dublin Core fallbacks for other reference tools. |

## Tags to AVOID for a blog post

| Tag | Problem |
|---|---|
| `citation_journal_title` | **Forces** the `journalArticle` type. |
| `citation_title` | Makes the translator **guess** `journalArticle`. Supply the title via `og:title` / `dc.title` instead. |

## Notes

- All of these are emitted on **blog posts only** (`_layouts/post.html`) — not on
  the About page, the post index, or the homepage.
- `og:site_name` stays clean (`eve.gd: Martin Paul Eve`, no markup) because it
  also drives social-card previews; the case-protected title rides in
  `prism.publicationName`, which Zotero reads first.
- `<span class="nocase">…</span>` is one of Zotero's allowed rich-text tags, so it
  survives import; Zotero's item pane may show the raw markup in the field even
  though citations render correctly.
- After changing these tags, **Reset Translators** in Zotero (Preferences →
  Advanced) and test on the deployed page, since the connector caches translators.
