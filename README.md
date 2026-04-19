# eve.gd

The source of the personal site of Professor Martin Paul Eve — Professor of Literature, Technology and Publishing at Birkbeck, University of London, and Technical Lead at Knowledge Commons at Michigan State University — a static Jekyll project, accreted over almost twenty years of posts dating from 2007, rendered into compressed HTML, pushed to Amazon S3, and served through CloudFront at [https://eve.gd](https://eve.gd).

## What lives here

Beneath the apparent simplicity of a blog sit the several layers that a long-running personal site tends to grow over time: a Jekyll theme derived from *Minimal Mistakes*, a small but consequential pair of Ruby plugins generating redirects and cross-post links, a corpus of almost a thousand Markdown essays, a set of auxiliary indexes rebuilt at deploy time from external publication and music databases, and a scattering of preserved sub-sites and archival pages that pre-date the current build. The layout that follows takes each stratum in turn.

## Directory layout

### Jekyll internals

Conventional Jekyll directories — each prefixed with an underscore, each consumed by the build but never emitted verbatim — organise the theme machinery:

- **`_posts/`** — the corpus proper: nearly a thousand Markdown files, each one named in Jekyll's canonical `YYYY-MM-DD-slug.markdown` form, each one carrying its own YAML front matter setting title, layout, optional `alias:` entries for legacy URLs, and occasional `image:` directives for the feature header.
- **`_layouts/`** — the HTML shells (`home.html`, `page.html`, `post.html`, `post-index.html`, `category.html`, `redirect.html`) into which Liquid pours rendered content.
- **`_includes/`** — partials sliced fine, holding the navigation, head, footer, author bio, Open Graph metadata, table of contents, browser-upgrade banner, Disqus block, social-share row, and auto-generated `publications.html`, joined by CV fragments (`Teaching`, `PeerReview`, `Postgrads`, `AcademicAppointments`, `DigitalHumanities`, `Funding`, and their kin) copied in from the external `CaSSius-CV` utility at deploy time.
- **`_sass/`** — modular SCSS partials (`variables`, `mixins`, `typography`, `grid`, `page`, `elements`, `forms`, `normalize`, `pygments`, `coderay`, alongside a `vendor` subfolder) compiled into a single compressed stylesheet.
- **`_plugins/`** — two Ruby plugins extending Jekyll at build time: `alias_generator.rb`, which reads `alias:` entries from post front matter and writes static HTML redirect pages so that moved or renamed URLs continue to resolve; and `jekyll-post-link.rb`, which registers a `{% post_link %}` Liquid tag resolving a slug to its canonical link.
- **`_templates/`** — scaffolds (`post`, `page`, `archive`) used when drafting new material.
- **`_data/`** — small YAML data files: `authors.yml` (biographical metadata for contributors) and `navigation.yml` (top menu items).

### Content and archival directories

- **`about/`**, **`c-v/`** — landing pages for the biography and curriculum vitae, each shipping a PDF copy of `Eve-CV.pdf` generated upstream by the `CaSSius-CV` pipeline.
- **`books/`** — an auto-generated index of monographs and edited collections, regenerated at deploy time by the external `bookPull` utility against `eprints.bbk.ac.uk`, accompanied by cover images, placeholder covers, per-record `.data` sidecars, and an `ids.txt` list specifying which records to fetch.
- **`music/`** — an auto-generated listing of musical works, populated at deploy time by the `musicBrainzPull` utility against MusicBrainz, likewise with `ids.txt` and template files.
- **`book_proposals/`** — a historical archive of proposals submitted to academic presses (Bloomsbury, Cambridge, Oxford, Palgrave, punctum, Stanford, Open Book), published deliberately rather than by oversight.
- **`draft/`** — note that Jekyll's convention for *hidden* drafts is the underscore-prefixed `_drafts/`, so anything in this folder will be built and served.
- **`posts/`** — legacy permalink stubs preserved for inbound links.
- **`19/`**, **`2016-OAWeekCity/`**, **`GreenPaper/`**, **`cassius/`**, **`derrida/`**, **`lens-martineve/`**, **`meve/`**, **`OA/`**, **`hcommons-static/`**, **`imagezoom/`** — preserved sub-sites, one-off projects, and conference microsites that pre-date the current Jekyll build and are kept intact for the historical record.
- **`wp-content/`** — a vestigial path retained so that inbound links from the prior WordPress installation can be rewritten by `.htaccess` into the modern `/images/` tree.
- **`feed.xml`**, **`feed_all.xml`**, **`feed/`** — Atom feeds emitted by the `jekyll-feed` plugin at the locations historical subscribers still expect.
- **`404.md`** — the custom 404 page.
- **`assets/`** — CSS, web fonts, and JavaScript bundles supporting the theme.
- **`images/`** — every raster and vector used across the site, from photographs and book covers through diagrams and scholarly figures to favicons and touch icons.

### Root-level configuration and build tooling

- **`_config.yml`** — Jekyll's primary configuration, collecting site metadata, Kramdown options, Sass settings, plugin list, permalink scheme, and the `exclude:` list that keeps shell scripts, Gemfiles, and the README itself out of the published site.
- **`_octopress.yml`** — vestigial Octopress settings consumed by the `_templates/` scaffolds.
- **`Gemfile`** / **`Gemfile.lock`** — the Ruby dependency manifest, pinning Jekyll, Liquid, `jekyll-feed`, and `bigdecimal`.
- **`package.json`** / **`Gruntfile.js`** — a Grunt pipeline, inherited from Minimal Mistakes, minifying the theme's JavaScript and optimising its images.
- **`.htaccess`** — Apache rewrite rules enforcing canonical hosts (`martineve.com` → `eve.gd`), redirecting HTTP to HTTPS, and serving vanity URLs (`/pynchonphil`, `/sacred`, `/oahums`, and others).
- **`.jshintrc`** — JavaScript linting configuration.
- **`deploy.sh`** — the full deployment pipeline: it runs the `musicBrainzPull` and `bookPull` utilities, invokes `SeleniumDeploy` for publication submission, rebuilds the CV from EPrints, copies `CaSSius-CV` fragments into `_includes/`, refreshes the Birkbeck calendar, executes `bundle exec jekyll build`, pushes `_site/` to `s3://eve.gd`, and invalidates CloudFront.
- **`minideploy.sh`** — a lighter-weight variant, skipping the upstream data fetches for small edits.
- **`push.sh`** — only the S3 sync and CloudFront invalidation, for when the site is already built.
- **`invalidate_cache.sh`** — a standalone CloudFront invalidation covering three distributions.
- **`preview.sh`** — activates a Ruby virtualenv on the Reclaim host and builds into `~/public_html/` for live preview.
- **`getcal.sh`** — fetches the Birkbeck academic calendar into `bbk_cal.ics` via the external `BBKCal` utility.
- **`update_no_fetch.sh`** — rebuilds the CV and the Jekyll site without refetching external publication data.
- **`keybase.txt`** — a public Keybase proof binding this domain to the Keybase identity `eve`.
- **`LICENSE`** — the MIT licence covering the underlying *Minimal Mistakes* theme (see below).
- **`.idea/`** — JetBrains IDE configuration.
- **`.gitignore`** — ignores `_site/`, `.sass-cache/`, `node_modules/`, IDE workspace state, and Jekyll's build caches (`.jekyll-metadata`, `.jekyll-cache/`).

## Build process

### Prerequisites

The local build presupposes Ruby (with Bundler) installed. Deployment additionally requires the AWS CLI configured with credentials for the `eve.gd` bucket and the three CloudFront distributions. Several of the auxiliary pipeline scripts depend on Python utilities — `musicBrainzPull`, `bookPull`, `SeleniumDeploy`, `eprintsCV`, `CaSSius-CV`, `BBKCal` — that live in sibling repositories, not here, and whose absence causes only the relevant stage of `deploy.sh` to fail without affecting a plain Jekyll build.

### Local build

Install the Ruby dependencies:

```bash
bundle install
```

Build the site into `_site/`:

```bash
bundle exec jekyll build
```

For faster iteration during writing, enable incremental builds:

```bash
bundle exec jekyll build --incremental
```

To preview with live reload:

```bash
bundle exec jekyll serve
```

### What the build does

At build time Jekyll runs Kramdown over every post, compiles the SCSS in `_sass/` into a single compressed stylesheet, executes the two custom plugins (generating static redirect pages for every `alias:` entry in front matter, and resolving `{% post_link %}` tags to canonical URLs), syndicates recent posts into Atom feeds via `jekyll-feed`, and writes the complete tree into `_site/`.

### Deployment

Deployment runs through `deploy.sh` in four phases: regeneration of upstream data (music listings, book catalogue, publication index, CV sections, calendar); a commit of any pending changes; a fresh `bundle exec jekyll build`; and an `aws s3 sync` of `_site/` to `s3://eve.gd`, followed by a CloudFront invalidation. For small edits the lighter `minideploy.sh` and `push.sh` scripts skip the upstream fetches entirely.

## Licensing

### Prose

Original blog-post text — every essay authored by Martin Paul Eve under `_posts/`, together with the prose of `about/`, `c-v/`, and the various project directories — is released under the Creative Commons Attribution 4.0 International Licence ([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)). You may share and adapt this material for any purpose, including commercially, provided attribution is given to Martin Paul Eve and a link to the original post is preserved.

### Images

Images bundled in `images/` and the other content directories are **not** covered by the CC BY licence. Many are third-party photographs, book covers, diagrams from other authors' work, press materials, or figures reproduced under fair dealing, fair use, or specific permission, and as such are not mine to relicense. If you wish to reuse an image, trace its provenance — usually evident from its filename, its surrounding context, or the post in which it appears — and seek permission from the original rights-holder rather than from me.

### Theme and third-party code

The underlying theme is (or at least was, at one time) *Minimal Mistakes* by Michael Rose, released under the MIT Licence preserved in `LICENSE`. Third-party JavaScript libraries under `assets/js/vendor/`, `cassius/`, `lens-martineve/`, `imagezoom/`, and similar directories carry their own licences declared in the files themselves.

### Book proposals

The PDFs and ZIPs under `book_proposals/` are made publicly available as a matter of scholarly transparency, but, being written for specific publishers and containing third-party editorial correspondence in places, are not released under an open licence and should not be redistributed wholesale without permission.
