# Zotero metadata for blog posts

How the `<head>` tags on each post (`_layouts/post.html`) make Zotero's built-in
**Embedded Metadata** translator import the page as a **Blog Post** — no custom
translator required. Behaviour verified against Zotero's `Embedded Metadata.js`
and `RDF.js` translators.

## Required / recommended tags

| Meta tag | Example value | Zotero result | Why |
|---|---|---|---|
| `prism.genre` | `blogentry` | **Item type → Blog Post** | `RDF.js` maps the `blogentry` genre to `blogPost`; this wins over the OpenGraph `webpage` default. |
| `prism.publicationName` | `<span class="nocase">eve.gd</span>: Martin Paul Eve` | **Blog Title** | Read into `publicationTitle` *before* `og:site_name` and is type-neutral. The `<span class="nocase">` is CSL markup that stops styles title-casing `eve.gd` into `Eve.Gd`. |
| `og:title` | `What is 'the scholarly record'?` | **Title** | Use OpenGraph (or `dc.title`) for the title — **not** `citation_title` (see below). |
| `og:site_name` | `eve.gd: Martin Paul Eve` | Blog Title fallback | Only used if `prism.publicationName` is absent. Kept clean (no markup) because it also drives social-card previews. |
| `og:type` | `article` | helps type detection | Presence of OpenGraph tags makes the translator take its RDF path (which defaults unknown types to `webpage`, then `prism.genre` upgrades to `blogPost`). |
| `citation_author` | `Eve, Martin Paul` | **Author** | `Last, First` is parsed unambiguously. Repeat the tag for multiple authors. |
| `citation_publication_date` | `2022/07/26` | **Date** | `YYYY/MM/DD` (or `YYYY-MM-DD`). |
| `citation_doi` | `10.59348/kv1zh-wn208` | **DOI** | Bare DOI, not a URL. Valid field on Blog Post; if a type lacks a DOI field the translator moves it to *Extra* automatically. |
| `citation_public_url` | `https://eve.gd/2022/07/26/.../` | **URL** | Absolute URL. |
| `citation_language` | `en` | **Language** | — |

## Belt-and-braces (Dublin Core, for other tools)

| Meta tag | Maps to |
|---|---|
| `dc.title` | Title |
| `dc.creator` | Author |
| `dc.date` | Date |
| `dc.language` | Language |

## Tags to AVOID for a blog post

| Meta tag | Problem |
|---|---|
| `citation_title` | The translator *guesses* `journalArticle` whenever it is present (`Embedded Metadata.js`). Supply the title via `og:title` / `dc.title` instead. |
| `citation_journal_title` | *Forces* the `journalArticle` type outright. |

## Notes

- At least one OpenGraph or Dublin Core tag must be present so the translator
  runs its RDF path; without it `prism.genre` is not consulted.
- `<span class="nocase">…</span>` is one of Zotero's allowed rich-text tags, so
  it survives import; styles render the protected text verbatim. Zotero's item
  pane may show the raw `<span …>` markup in the field even though citations are
  correct.
- These tags live in `_layouts/post.html` and are emitted on blog posts only —
  not on the About page, the post index, or the homepage.
