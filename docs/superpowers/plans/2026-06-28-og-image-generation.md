# Generated OG/Twitter Card Images — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate a designed 1200×630 social-preview image per post and per main content page, in the site's red/black brand language, cached outside `_site`, driving `og:image` and a 1200×628 `twitter:image`.

**Architecture:** A new Ruby Jekyll plugin `_plugins/og_image.rb` mirrors `_plugins/signposting.rb`: a pure `OgImage` module (slug/excerpt/data-URI/HTML-template helpers, unit-tested without Jekyll) plus a `Jekyll::OgImageGenerator` that renders each card once via headless Chrome (injected, like the signposting DOI fetcher), crops the Twitter variant with ImageMagick, caches to `.og_cache/`, copies the served copies into `_site/images/og/`, and sets `og_image`/`og_image_twitter` on each document for the head include.

**Tech Stack:** Ruby (Jekyll generator, no gems beyond stdlib `base64`/`json`/`fileutils`/`open3`), headless `google-chrome`, ImageMagick `convert`, committed Fraunces + IBM Plex Mono TTFs, minitest.

## Global Constraints

- OG image size: **1200×630**. Twitter image size: **1200×628** (1.91:1).
- Brand colours (verbatim): background `#0b0b0b`; red `#b3122a`; red-dark `#8c0d20`; hairline `#e63946`; title `#ffffff`; snippet muted `#b3ada3`.
- Fonts: title **Fraunces** (~600 weight); pill/snippet/button **IBM Plex Mono**.
- Pill text (verbatim): `eve.gd: Martin Paul Eve`. Button: `Read post` for posts, `Read more` for pages.
- Scope: `site.posts.docs` + `site.pages` whose `layout` ∈ {`home`,`page`,`post-index`,`category`}. HTML output only.
- Cache dir `.og_cache/` is **gitignored**, outside `_site`; cache key is the document slug only; delete a cache file to regenerate.
- Plugin style: pure module guarded by `if defined?(Jekyll::Generator)` for the generator half, so the module unit-tests in plain Ruby (follow `_plugins/signposting.rb`).
- Stub-first TDD: new methods first raise `NotImplementedError`; write a behaviour test that fails for the right reason, then implement.
- Commits: conventional, no issue number available, no co-author/attribution. Source only — never stage `_site/` or `.og_cache/`.

---

### Task 1: Fonts + gitignore (setup)

**Files:**
- Create: `_og/fonts/Fraunces.ttf`, `_og/fonts/IBMPlexMono-Regular.ttf`, `_og/fonts/IBMPlexMono-SemiBold.ttf`, `_og/fonts/LICENSING.md`
- Modify: `.gitignore`

- [ ] **Step 1: Download the OFL fonts**

```bash
cd /home/martin/Documents/Programming/blog
mkdir -p _og/fonts
curl -sL -o _og/fonts/Fraunces.ttf "https://github.com/google/fonts/raw/main/ofl/fraunces/Fraunces%5BSOFT%2CWONK%2Copsz%2Cwght%5D.ttf"
curl -sL -o _og/fonts/IBMPlexMono-Regular.ttf "https://github.com/google/fonts/raw/main/ofl/ibmplexmono/IBMPlexMono-Regular.ttf"
curl -sL -o _og/fonts/IBMPlexMono-SemiBold.ttf "https://github.com/google/fonts/raw/main/ofl/ibmplexmono/IBMPlexMono-SemiBold.ttf"
```

- [ ] **Step 2: Verify the files are real TrueType fonts**

Run: `file _og/fonts/*.ttf`
Expected: each line reports `TrueType Font data` (or `OpenType`), sizes ~360KB / ~135KB / ~140KB.

- [ ] **Step 3: Add a licence note**

Create `_og/fonts/LICENSING.md`:

```markdown
# Fonts

Bundled for build-time Open Graph image rendering only.

- **Fraunces** — SIL Open Font License 1.1 — https://github.com/undercasetype/Fraunces
- **IBM Plex Mono** — SIL Open Font License 1.1 — https://github.com/IBM/plex

Both fonts are redistributable under the OFL; these copies are taken from the
Google Fonts repository (https://github.com/google/fonts).
```

- [ ] **Step 4: Ignore the cache directory**

Append to `.gitignore`:

```
# Generated Open Graph image cache (regenerated locally; served copies live in _site)
.og_cache/
```

- [ ] **Step 5: Commit**

```bash
git add _og/fonts/Fraunces.ttf _og/fonts/IBMPlexMono-Regular.ttf _og/fonts/IBMPlexMono-SemiBold.ttf _og/fonts/LICENSING.md .gitignore
git commit -m "chore(og-image): bundle OFL fonts and ignore the og cache dir"
```

---

### Task 2: `OgImage` string helpers (slug, scope, label, title, asset URL)

**Files:**
- Create: `_plugins/og_image.rb`
- Test: `test/test_og_image.rb`

**Interfaces:**
- Produces:
  - `OgImage::SCOPE_LAYOUTS` → `%w[home page post-index category]`
  - `OgImage::SITE_AUTHOR` → `"eve.gd: Martin Paul Eve"`
  - `OgImage::CARD_W=1200 CARD_H=630 TW_W=1200 TW_H=628`
  - `OgImage.slug(url) -> String`
  - `OgImage.scope_layout?(layout) -> Boolean`
  - `OgImage.button_label(is_post) -> String`
  - `OgImage.title_for(doc_title, site_title) -> String`
  - `OgImage.asset_url(base_url, slug, twitter: false) -> String`

- [ ] **Step 1: Write the failing tests**

Create `test/test_og_image.rb`:

```ruby
# Unit tests for the pure OgImage builders. Run: ruby test/test_og_image.rb
require "minitest/autorun"
require_relative "../_plugins/og_image"

class TestOgImage < Minitest::Test
  def test_slug_from_post_url
    assert_equal "2026-06-23-harvestable", OgImage.slug("/2026/06/23/harvestable/")
  end

  def test_slug_from_page_url
    assert_equal "about", OgImage.slug("/about/")
  end

  def test_slug_for_apex_is_index
    assert_equal "index", OgImage.slug("/")
  end

  def test_slug_strips_host_and_index_and_html
    assert_equal "books", OgImage.slug("https://eve.gd/books/index.html")
    assert_equal "404", OgImage.slug("/404.html")
  end

  def test_scope_layout
    assert OgImage.scope_layout?("page")
    assert OgImage.scope_layout?("home")
    refute OgImage.scope_layout?("redirect")
    refute OgImage.scope_layout?(nil)
  end

  def test_button_label
    assert_equal "Read post", OgImage.button_label(true)
    assert_equal "Read more", OgImage.button_label(false)
  end

  def test_title_for_falls_back_to_site_title
    assert_equal "About", OgImage.title_for("About", "Martin Paul Eve")
    assert_equal "Martin Paul Eve", OgImage.title_for("", "Martin Paul Eve")
    assert_equal "Martin Paul Eve", OgImage.title_for(nil, "Martin Paul Eve")
  end

  def test_asset_url
    assert_equal "https://eve.gd/images/og/about.png",
                 OgImage.asset_url("https://eve.gd", "about")
    assert_equal "https://eve.gd/images/og/about.twitter.png",
                 OgImage.asset_url("https://eve.gd", "about", twitter: true)
  end
end
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `ruby test/test_og_image.rb`
Expected: FAIL — `uninitialized constant OgImage` (file does not exist yet).

- [ ] **Step 3: Create the module with these helpers**

Create `_plugins/og_image.rb`:

```ruby
# Build-time Open Graph / Twitter card images (1200x630 / 1200x628) for posts
# and main content pages. The pure builders below carry no Jekyll dependency so
# they can be unit-tested in plain Ruby; Jekyll::OgImageGenerator (defined only
# inside Jekyll) wires them into the build.
module OgImage
  CARD_W = 1200
  CARD_H = 630
  TW_W   = 1200
  TW_H   = 628

  SITE_AUTHOR   = "eve.gd: Martin Paul Eve".freeze
  SCOPE_LAYOUTS = %w[home page post-index category].freeze

  # Filesystem-safe cache slug from a document's output URL.
  def self.slug(url)
    s = url.to_s
           .sub(%r{\Ahttps?://[^/]+}, "")
           .sub(%r{index\.html\z}, "")
           .sub(%r{\.html\z}, "")
           .gsub(%r{\A/|/\z}, "")
    s = "index" if s.empty?
    s.gsub(%r{[^a-zA-Z0-9._-]+}, "-")
  end

  def self.scope_layout?(layout)
    SCOPE_LAYOUTS.include?(layout.to_s)
  end

  def self.button_label(is_post)
    is_post ? "Read post" : "Read more"
  end

  def self.title_for(doc_title, site_title)
    t = doc_title.to_s.strip
    t.empty? ? site_title.to_s : t
  end

  def self.asset_url(base_url, slug, twitter: false)
    name = twitter ? "#{slug}.twitter.png" : "#{slug}.png"
    File.join(base_url.to_s, "images", "og", name)
  end
end

require "json"
require "base64"
require "fileutils"
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `ruby test/test_og_image.rb`
Expected: PASS (all assertions).

- [ ] **Step 5: Commit**

```bash
git add _plugins/og_image.rb test/test_og_image.rb
git commit -m "feat(og-image): add slug, scope, label and asset-url helpers"
```

---

### Task 3: `OgImage` content helpers (`excerpt_text`, `data_uri`)

**Files:**
- Modify: `_plugins/og_image.rb`
- Test: `test/test_og_image.rb`

**Interfaces:**
- Produces:
  - `OgImage.excerpt_text(raw, limit = 160) -> String`
  - `OgImage.data_uri(path, mime = nil) -> String|nil`
  - `OgImage.html_escape(text) -> String`

- [ ] **Step 1: Write the failing tests** (append to `test/test_og_image.rb`, before the final `end`)

```ruby
  def test_excerpt_strips_html_and_collapses_whitespace
    raw = "<p>Hello   <strong>there</strong>\n\nworld</p>"
    assert_equal "Hello there world", OgImage.excerpt_text(raw)
  end

  def test_excerpt_truncates_on_word_boundary_with_ellipsis
    raw = "one two three four five six seven eight nine ten eleven twelve"
    out = OgImage.excerpt_text(raw, 20)
    assert out.length <= 21, "truncated to ~limit plus ellipsis"
    assert out.end_with?("…")
    refute_includes out, "  "
  end

  def test_excerpt_blank
    assert_equal "", OgImage.excerpt_text(nil)
    assert_equal "", OgImage.excerpt_text("   ")
  end

  def test_data_uri_from_png_fixture
    require "tmpdir"
    Dir.mktmpdir do |d|
      path = File.join(d, "x.png")
      File.binwrite(path, "\x89PNG\r\n\x1a\nDATA")
      uri = OgImage.data_uri(path)
      assert uri.start_with?("data:image/png;base64,")
      assert_equal "\x89PNG\r\n\x1a\nDATA".b,
                   Base64.decode64(uri.sub("data:image/png;base64,", "")).b
    end
  end

  def test_data_uri_missing_file_is_nil
    assert_nil OgImage.data_uri("/no/such/file.png")
    assert_nil OgImage.data_uri(nil)
  end

  def test_html_escape
    assert_equal "a &amp; b &lt;c&gt; &quot;d&quot;", OgImage.html_escape('a & b <c> "d"')
  end
```

- [ ] **Step 2: Run to verify failure**

Run: `ruby test/test_og_image.rb`
Expected: FAIL — `NoMethodError: undefined method 'excerpt_text'`.

- [ ] **Step 3: Implement** (insert these methods into `module OgImage`, after `asset_url`)

```ruby
  IMAGE_MIME = {
    ".png" => "image/png", ".jpg" => "image/jpeg", ".jpeg" => "image/jpeg",
    ".gif" => "image/gif", ".webp" => "image/webp", ".svg" => "image/svg+xml"
  }.freeze

  # Plain-text snippet: strip tags/entities, collapse whitespace, truncate on a
  # word boundary with an ellipsis.
  def self.excerpt_text(raw, limit = 160)
    text = raw.to_s.gsub(/<[^>]+>/, " ").gsub(/&[#a-zA-Z0-9]+;/, " ").gsub(/\s+/, " ").strip
    return "" if text.empty?
    return text if text.length <= limit

    text[0, limit].sub(/\s+\S*\z/, "").rstrip + "…"
  end

  # base64 data URI for a local file, or nil when absent.
  def self.data_uri(path, mime = nil)
    return nil unless path && File.exist?(path)

    mime ||= IMAGE_MIME[File.extname(path).downcase] || "application/octet-stream"
    "data:#{mime};base64,#{Base64.strict_encode64(File.binread(path))}"
  end

  def self.html_escape(text)
    text.to_s.gsub("&", "&amp;").gsub("<", "&lt;").gsub(">", "&gt;").gsub('"', "&quot;")
  end
```

- [ ] **Step 4: Run to verify pass**

Run: `ruby test/test_og_image.rb`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add _plugins/og_image.rb test/test_og_image.rb
git commit -m "feat(og-image): add excerpt, data-uri and escape helpers"
```

---

### Task 4: `OgImage.render_html` template

**Files:**
- Modify: `_plugins/og_image.rb`
- Test: `test/test_og_image.rb`

**Interfaces:**
- Produces: `OgImage.render_html(pill:, title:, snippet:, button:, image_uri:, fonts:) -> String`
  - `fonts` is a hash with symbol keys `:fraunces`, `:mono_regular`, `:mono_semibold`, each a data URI string or nil.

- [ ] **Step 1: Write the failing tests** (append before the final `end`)

```ruby
  def render(image_uri: "data:image/png;base64,AAA", fonts: {})
    OgImage.render_html(pill: OgImage::SITE_AUTHOR, title: "My <Post>",
                        snippet: "A snippet & more", button: "Read post",
                        image_uri: image_uri, fonts: fonts)
  end

  def test_render_html_contains_core_content_escaped
    html = render
    assert_includes html, "eve.gd: Martin Paul Eve"
    assert_includes html, "My &lt;Post&gt;"          # title escaped
    assert_includes html, "A snippet &amp; more"      # snippet escaped
    assert_includes html, "Read post"
    assert_includes html, "1200px"
    assert_includes html, "#b3122a"
  end

  def test_render_html_includes_image_card_when_image_present
    html = render(image_uri: "data:image/png;base64,ZZZ")
    assert_includes html, "data:image/png;base64,ZZZ"
    assert_includes html, 'class="right"'
  end

  def test_render_html_omits_image_card_when_absent
    html = render(image_uri: nil)
    refute_includes html, 'class="right"'
    assert_includes html, "og-full"                   # full-width modifier
  end

  def test_render_html_embeds_fonts_when_provided
    html = render(fonts: { fraunces: "data:font/ttf;base64,FFF",
                           mono_regular: "data:font/ttf;base64,MMM",
                           mono_semibold: "data:font/ttf;base64,SSS" })
    assert_includes html, "@font-face"
    assert_includes html, "data:font/ttf;base64,FFF"
    assert_includes html, "Fraunces"
  end
```

- [ ] **Step 2: Run to verify failure**

Run: `ruby test/test_og_image.rb`
Expected: FAIL — `NoMethodError: undefined method 'render_html'`.

- [ ] **Step 3: Implement** (insert into `module OgImage`, after `html_escape`)

```ruby
  # Assemble the 1200x630 card HTML. image_uri nil => full-width text layout.
  def self.render_html(pill:, title:, snippet:, button:, image_uri:, fonts:)
    faces = +""
    if fonts[:fraunces]
      faces << "@font-face{font-family:'Fraunces';font-weight:100 900;" \
               "src:url(#{fonts[:fraunces]}) format('truetype')}"
    end
    if fonts[:mono_regular]
      faces << "@font-face{font-family:'IBM Plex Mono';font-weight:400;" \
               "src:url(#{fonts[:mono_regular]}) format('truetype')}"
    end
    if fonts[:mono_semibold]
      faces << "@font-face{font-family:'IBM Plex Mono';font-weight:600;" \
               "src:url(#{fonts[:mono_semibold]}) format('truetype')}"
    end

    has_image = !image_uri.nil? && !image_uri.empty?
    full = has_image ? "" : " og-full"
    snippet_html = snippet.to_s.empty? ? "" :
      %(<p class="snippet">#{html_escape(snippet)}</p>)
    right_html = has_image ?
      %(<div class="right"><div class="imgcard"><img src="#{image_uri}" alt=""></div></div>) : ""

    <<~HTML
      <!doctype html><html><head><meta charset="utf-8"><style>
      #{faces}
      *{margin:0;padding:0;box-sizing:border-box}
      html,body{width:1200px;height:630px}
      .card{position:relative;width:1200px;height:630px;background:#0b0b0b;
        overflow:hidden;font-family:'IBM Plex Mono',ui-monospace,monospace}
      .bg{position:absolute;inset:0;overflow:hidden}
      .wedge{position:absolute;top:-12%;right:-6%;width:54%;height:124%;
        background:linear-gradient(160deg,#b3122a,#8c0d20);
        transform:skewX(-4deg);transform-origin:top right}
      .line{position:absolute;left:-30%;width:160%;height:3px;background:#e63946;
        opacity:.55;transform:rotate(-4deg)}
      .line1{top:16%}.line2{top:84%}
      .content{position:relative;display:flex;width:1200px;height:630px}
      .left{width:62%;padding:72px 64px;display:flex;flex-direction:column;
        justify-content:center}
      .og-full .left{width:100%}
      .pill{align-self:flex-start;background:#b3122a;color:#fff;font-weight:600;
        font-size:22px;padding:11px 24px;border-radius:999px;letter-spacing:.01em}
      .title{font-family:'Fraunces',Georgia,serif;font-weight:600;color:#fff;
        font-size:60px;line-height:1.07;margin:30px 0 20px;
        display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
      .snippet{color:#b3ada3;font-size:24px;line-height:1.45;max-width:94%;
        display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
      .btn{align-self:flex-start;margin-top:36px;background:#b3122a;color:#fff;
        font-weight:600;font-size:22px;padding:16px 32px;border-radius:10px}
      .right{width:38%;position:relative;display:flex;align-items:center;
        justify-content:center;padding:48px 56px 48px 0}
      .imgcard{width:100%;height:454px;border-radius:24px;overflow:hidden;
        box-shadow:0 28px 60px rgba(0,0,0,.55);background:#1a1a1a}
      .imgcard img{width:100%;height:100%;object-fit:cover;display:block}
      </style></head>
      <body><div class="card#{full}">
      <div class="bg"><div class="wedge"></div>
        <div class="line line1"></div><div class="line line2"></div></div>
      <div class="content">
        <div class="left">
          <span class="pill">#{html_escape(pill)}</span>
          <h1 class="title">#{html_escape(title)}</h1>
          #{snippet_html}
          <span class="btn">#{html_escape(button)}</span>
        </div>
        #{right_html}
      </div>
      </div></body></html>
    HTML
  end
```

- [ ] **Step 4: Run to verify pass**

Run: `ruby test/test_og_image.rb`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add _plugins/og_image.rb test/test_og_image.rb
git commit -m "feat(og-image): add the card HTML template builder"
```

---

### Task 5: `Jekyll::OgImageGenerator` (cache, copy, meta) with injected renderer/cropper

**Files:**
- Modify: `_plugins/og_image.rb`
- Test: `test/test_og_image_generator.rb`

**Interfaces:**
- Consumes: all `OgImage.*` helpers from Tasks 2–4.
- Produces (generator):
  - `attr_writer :renderer` — callable `(html, width, height, out_path)`
  - `attr_writer :cropper` — callable `(src_path, out_path, width, height)`
  - `generate(site)` sets `doc.data["og_image"]` and `doc.data["og_image_twitter"]`, writes `.og_cache/<slug>.png` + `.twitter.png`, copies both to `<dest>/images/og/`.

- [ ] **Step 1: Write the failing tests**

Create `test/test_og_image_generator.rb`:

```ruby
# Integration tests for OgImageGenerator with stubbed Jekyll + injected
# renderer/cropper so no browser or ImageMagick runs. Run:
#   ruby test/test_og_image_generator.rb
require "minitest/autorun"
require "tmpdir"
require "fileutils"

module Jekyll
  class Generator
    def self.safe(*); end
    def self.priority(*); end
  end
  class StaticFile
    attr_reader :dir, :name
    def initialize(_site, _base, dir, name); @dir = dir; @name = name; end
  end
end

require_relative "../_plugins/og_image"

class FakeDoc
  attr_reader :url, :data
  def initialize(url:, data:); @url = url; @data = data; end
  def output_ext; @url.end_with?("/") ? ".html" : File.extname(@url); end
end

class FakePosts
  attr_reader :docs
  def initialize(docs); @docs = docs; end
end

class FakeSite
  attr_reader :dest, :source, :config, :static_files, :pages
  def initialize(dest:, source:, posts: [], pages: [])
    @dest = dest; @source = source
    @config = { "url" => "https://eve.gd", "title" => "Martin Paul Eve" }
    @static_files = []; @posts = FakePosts.new(posts); @pages = pages
  end
  def posts; @posts; end
end

class TestOgImageGenerator < Minitest::Test
  def setup
    @dest = Dir.mktmpdir
    @source = Dir.mktmpdir
    @rendered = []
    @cropped = []
    @renderer = lambda do |html, w, h, out|
      @rendered << [w, h, out]
      File.write(out, html) # stub: store the HTML so tests can inspect it
    end
    @cropper = lambda do |src, out, w, h|
      @cropped << [src, out, w, h]
      FileUtils.cp(src, out)
    end
  end

  def teardown
    FileUtils.remove_entry(@dest)
    FileUtils.remove_entry(@source)
  end

  def run_generator(posts: [], pages: [])
    site = FakeSite.new(dest: @dest, source: @source, posts: posts, pages: pages)
    gen = Jekyll::OgImageGenerator.new
    gen.renderer = @renderer
    gen.cropper = @cropper
    gen.generate(site)
    site
  end

  def post(url: "/2026/06/23/harvestable/", data: nil)
    FakeDoc.new(url: url,
                data: data || { "layout" => "post", "title" => "Harvestable",
                                "excerpt" => "<p>An excerpt.</p>" })
  end

  def test_renders_and_caches_og_and_twitter
    run_generator(posts: [post])
    assert File.exist?(File.join(@source, ".og_cache", "2026-06-23-harvestable.png"))
    assert File.exist?(File.join(@source, ".og_cache", "2026-06-23-harvestable.twitter.png"))
    assert_equal [[1200, 630, File.join(@source, ".og_cache", "2026-06-23-harvestable.png")]],
                 @rendered
    assert_equal 1, @cropped.length
    assert_equal [1200, 628], @cropped.first.last(2)
  end

  def test_copies_into_dest_and_sets_meta
    site = run_generator(posts: [post])
    assert File.exist?(File.join(@dest, "images", "og", "2026-06-23-harvestable.png"))
    assert File.exist?(File.join(@dest, "images", "og", "2026-06-23-harvestable.twitter.png"))
    d = site.posts.docs.first.data
    assert_equal "https://eve.gd/images/og/2026-06-23-harvestable.png", d["og_image"]
    assert_equal "https://eve.gd/images/og/2026-06-23-harvestable.twitter.png", d["og_image_twitter"]
    names = site.static_files.map(&:name)
    assert_includes names, "2026-06-23-harvestable.png"
    assert_includes names, "2026-06-23-harvestable.twitter.png"
  end

  def test_cache_hit_does_not_rerender
    FileUtils.mkdir_p(File.join(@source, ".og_cache"))
    File.binwrite(File.join(@source, ".og_cache", "2026-06-23-harvestable.png"), "CACHED")
    File.binwrite(File.join(@source, ".og_cache", "2026-06-23-harvestable.twitter.png"), "CACHED")
    run_generator(posts: [post])
    assert_empty @rendered, "must not re-render a cached card"
    assert_empty @cropped
  end

  def test_in_scope_page_is_processed_post_index_is_not_excluded
    page = FakeDoc.new(url: "/about/",
                       data: { "layout" => "page", "title" => "About", "excerpt" => "Bio." })
    site = run_generator(pages: [page])
    assert_equal "https://eve.gd/images/og/about.png", site.pages.first.data["og_image"]
  end

  def test_out_of_scope_page_is_skipped
    page = FakeDoc.new(url: "/r/", data: { "layout" => "redirect" })
    site = run_generator(pages: [page])
    assert_nil site.pages.first.data["og_image"]
    assert_empty @rendered
  end

  def test_no_feature_image_still_renders_full_width
    p = post(data: { "layout" => "post", "title" => "No image", "excerpt" => "x" })
    run_generator(posts: [p])
    html = File.read(File.join(@source, ".og_cache", "2026-06-23-harvestable.png"))
    assert_includes html, "og-full"
    refute_includes html, 'class="right"'
  end

  def test_feature_image_is_embedded_when_present
    FileUtils.mkdir_p(File.join(@source, "images"))
    File.binwrite(File.join(@source, "images", "gavel.jpg"), "JPGDATA")
    p = post(data: { "layout" => "post", "title" => "Has image", "excerpt" => "x",
                     "image" => { "feature" => "gavel.jpg" } })
    run_generator(posts: [p])
    html = File.read(File.join(@source, ".og_cache", "2026-06-23-harvestable.png"))
    assert_includes html, "data:image/jpeg;base64,"
    assert_includes html, 'class="right"'
  end
end
```

- [ ] **Step 2: Run to verify failure**

Run: `ruby test/test_og_image_generator.rb`
Expected: FAIL — `NameError: uninitialized constant Jekyll::OgImageGenerator`.

- [ ] **Step 3: Implement the generator** (append to `_plugins/og_image.rb`, after the `require` lines)

```ruby
if defined?(Jekyll::Generator)
module Jekyll
  # Renders one social card per in-scope document, caches it outside _site, and
  # serves a copy from <dest>/images/og/. The renderer (headless Chrome) and
  # cropper (ImageMagick) are injectable so the wiring tests run without them.
  class OgImageGenerator < Generator
    safe false
    priority :low

    OG_DEST_DIR = "images/og".freeze
    CACHE_DIR   = ".og_cache".freeze

    attr_writer :renderer, :cropper

    def renderer
      @renderer ||= method(:chrome_render)
    end

    def cropper
      @cropper ||= method(:imagemagick_crop)
    end

    def generate(site)
      @site = site
      @fonts = load_fonts
      base_url = site.config["url"].to_s

      documents(site).each do |doc, is_post|
        next unless html_output?(doc)

        slug = OgImage.slug(doc.url)
        og_cache = cache_path("#{slug}.png")
        tw_cache = cache_path("#{slug}.twitter.png")
        next unless og_cache && tw_cache

        ensure_cached(doc, is_post, og_cache, tw_cache)
        next unless File.exist?(og_cache)

        copy_to_dest(og_cache, "#{slug}.png")
        copy_to_dest(tw_cache, "#{slug}.twitter.png") if File.exist?(tw_cache)

        doc.data["og_image"] = OgImage.asset_url(base_url, slug)
        doc.data["og_image_twitter"] = OgImage.asset_url(base_url, slug, twitter: true)
      end
    end

    private

    # [doc, is_post] for every post and in-scope page.
    def documents(site)
      pairs = site.posts.docs.map { |d| [d, true] }
      site.pages.each do |p|
        pairs << [p, false] if OgImage.scope_layout?(p.data["layout"])
      end
      pairs
    end

    def html_output?(doc)
      ext = doc.respond_to?(:output_ext) ? doc.output_ext : File.extname(doc.url)
      ext == ".html" || ext == ".htm"
    end

    def cache_path(name)
      return nil unless @site.respond_to?(:source) && @site.source

      File.join(@site.source, CACHE_DIR, name)
    end

    def ensure_cached(doc, is_post, og_cache, tw_cache)
      unless File.exist?(og_cache)
        html = build_html(doc, is_post)
        FileUtils.mkdir_p(File.dirname(og_cache))
        renderer.call(html, OgImage::CARD_W, OgImage::CARD_H, og_cache)
      end
      return unless File.exist?(og_cache) && !File.exist?(tw_cache)

      cropper.call(og_cache, tw_cache, OgImage::TW_W, OgImage::TW_H)
    end

    def build_html(doc, is_post)
      OgImage.render_html(
        pill: OgImage::SITE_AUTHOR,
        title: OgImage.title_for(doc.data["title"], @site.config["title"]),
        snippet: OgImage.excerpt_text(doc.data["excerpt"].to_s),
        button: OgImage.button_label(is_post),
        image_uri: feature_uri(doc),
        fonts: @fonts,
      )
    end

    def feature_uri(doc)
      feature = doc.data["image"] && doc.data["image"]["feature"]
      return nil unless feature.is_a?(String) && !feature.empty?
      return nil if feature.include?("http") # only embed local files

      OgImage.data_uri(File.join(@site.source, "images", feature))
    end

    def load_fonts
      return {} unless @site.respond_to?(:source) && @site.source

      dir = File.join(@site.source, "_og", "fonts")
      {
        fraunces: OgImage.data_uri(File.join(dir, "Fraunces.ttf"), "font/ttf"),
        mono_regular: OgImage.data_uri(File.join(dir, "IBMPlexMono-Regular.ttf"), "font/ttf"),
        mono_semibold: OgImage.data_uri(File.join(dir, "IBMPlexMono-SemiBold.ttf"), "font/ttf"),
      }
    end

    def copy_to_dest(src, name)
      dest_dir = File.join(@site.dest, OG_DEST_DIR)
      FileUtils.mkdir_p(dest_dir)
      FileUtils.cp(src, File.join(dest_dir, name))
      @site.static_files << OgImageFile.new(@site, @site.dest, OG_DEST_DIR, name)
    end
  end

  class OgImageFile < StaticFile
    def modified?; false; end
    def write(_dest); true; end
  end
end
end
```

- [ ] **Step 4: Run to verify pass**

Run: `ruby test/test_og_image_generator.rb`
Expected: PASS (all tests).

- [ ] **Step 5: Commit**

```bash
git add _plugins/og_image.rb test/test_og_image_generator.rb
git commit -m "feat(og-image): generate, cache, serve and wire card images"
```

---

### Task 6: Default Chrome renderer + ImageMagick cropper

**Files:**
- Modify: `_plugins/og_image.rb`

**Interfaces:**
- Produces (private generator methods): `chrome_render(html, width, height, out_path)`, `imagemagick_crop(src_path, out_path, width, height)`.

These shell out to real binaries and are verified in Task 8 (real build), not unit-tested.

- [ ] **Step 1: Add the stdlib requires**

At the end of `_plugins/og_image.rb`'s top require block (next to `require "json"` / `require "base64"` / `require "fileutils"`), add:

```ruby
require "open3"
require "tmpdir"
```

- [ ] **Step 2: Implement the two shell-outs** (insert into `class OgImageGenerator`, in the `private` section, after `copy_to_dest`)

```ruby
    CHROME_BINS = %w[google-chrome google-chrome-stable chromium chromium-browser].freeze

    def chrome_render(html, width, height, out_path)
      bin = CHROME_BINS.find { |b| system("command -v #{b} >/dev/null 2>&1") }
      raise "no Chrome binary found (tried: #{CHROME_BINS.join(', ')})" unless bin

      Dir.mktmpdir("og") do |tmp|
        html_path = File.join(tmp, "card.html")
        File.write(html_path, html)
        cmd = [bin, "--headless=new", "--disable-gpu", "--no-sandbox",
               "--hide-scrollbars", "--force-device-scale-factor=1",
               "--default-background-color=00000000",
               "--window-size=#{width},#{height}",
               "--screenshot=#{out_path}", "file://#{html_path}"]
        _out, err, status = Open3.capture3(*cmd)
        unless status.success? && File.exist?(out_path)
          Jekyll.logger.warn "OgImage:", "render failed for #{out_path}: #{err.lines.last}"
        end
      end
    end

    def imagemagick_crop(src_path, out_path, width, height)
      cmd = ["convert", src_path, "-gravity", "center",
             "-crop", "#{width}x#{height}+0+0", "+repage", out_path]
      _out, err, status = Open3.capture3(*cmd)
      unless status.success? && File.exist?(out_path)
        Jekyll.logger.warn "OgImage:", "crop failed for #{out_path}: #{err.lines.last}"
        FileUtils.cp(src_path, out_path) # fall back to the uncropped image
      end
    end
```

- [ ] **Step 3: Confirm the module still loads and unit tests pass**

Run: `ruby test/test_og_image.rb && ruby test/test_og_image_generator.rb`
Expected: PASS (the injected renderer/cropper still override these in tests).

- [ ] **Step 4: Smoke-test a single real render**

```bash
ruby -e '
require "./_plugins/og_image"
fonts = {
  fraunces: OgImage.data_uri("_og/fonts/Fraunces.ttf","font/ttf"),
  mono_regular: OgImage.data_uri("_og/fonts/IBMPlexMono-Regular.ttf","font/ttf"),
  mono_semibold: OgImage.data_uri("_og/fonts/IBMPlexMono-SemiBold.ttf","font/ttf")
}
html = OgImage.render_html(pill: OgImage::SITE_AUTHOR, title: "FAIR and Square: making a static site support FAIR signposting",
  snippet: "After my previous post about Zotero ingest, I wondered what else I might do to make this scholarly blog more accessible.",
  button: "Read post", image_uri: OgImage.data_uri("images/gavel.jpg"), fonts: fonts)
File.write("/tmp/og_card.html", html)
'
google-chrome --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
  --force-device-scale-factor=1 --window-size=1200,630 \
  --screenshot=/tmp/og_card.png "file:///tmp/og_card.html"
identify /tmp/og_card.png
```
Expected: `identify` reports `/tmp/og_card.png PNG 1200x630`.

- [ ] **Step 5: Visually review and tune**

Open `/tmp/og_card.png` (Read tool / image viewer). Compare against the brief: red pill top-left with "eve.gd: Martin Paul Eve", Fraunces title, snippet, red "Read post" button, gavel image in a rounded card on the right, red/black diagonal background. Adjust the CSS constants in `render_html` (sizes, wedge angle, padding) until it reads well, re-running Steps 4–5. **Delete `/tmp/og_card.png` between runs.**

- [ ] **Step 6: Commit**

```bash
git add _plugins/og_image.rb
git commit -m "feat(og-image): add headless-Chrome renderer and ImageMagick crop"
```

---

### Task 7: Wire `og:image` / `twitter:image` in `_head.html`

**Files:**
- Modify: `_includes/_head.html` (the `og:image` block ~lines 94–98 and the `twitter:image` block ~lines 109–113)

**Interfaces:**
- Consumes: `page.og_image`, `page.og_image_twitter` set by the generator.

- [ ] **Step 1: Replace the `og:image` block**

Find:

```liquid
{% if page.image.feature %}
<meta property="og:image" content="https://eve.gd/images/{{ page.image.feature }}">
{% else %}
<meta property="og:image" content="https://eve.gd/images/og.png">
{% endif %}
```

Replace with:

```liquid
{% if page.og_image %}
<meta property="og:image" content="{{ page.og_image }}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
{% elsif page.image.feature %}
<meta property="og:image" content="https://eve.gd/images/{{ page.image.feature }}">
{% else %}
<meta property="og:image" content="https://eve.gd/images/og.png">
{% endif %}
```

- [ ] **Step 2: Replace the `twitter:image` block**

Find:

```liquid
{% if page.image.feature %}
<meta name="twitter:image" content="https://eve.gd/images/{{ page.image.feature }}">
{% else %}
<meta name="twitter:image" content="https://eve.gd/images/og.png">
{% endif %}
```

Replace with:

```liquid
{% if page.og_image_twitter %}
<meta name="twitter:image" content="{{ page.og_image_twitter }}">
{% elsif page.image.feature %}
<meta name="twitter:image" content="https://eve.gd/images/{{ page.image.feature }}">
{% else %}
<meta name="twitter:image" content="https://eve.gd/images/og.png">
{% endif %}
```

- [ ] **Step 3: Commit**

```bash
git add _includes/_head.html
git commit -m "feat(og-image): prefer generated cards for og:image and twitter:image"
```

---

### Task 8: Real-build verification (one post + one page)

**Files:** none (verification only).

- [ ] **Step 1: Fast verification build (a few posts + all pages)**

`--limit_posts` keeps this quick by rendering only a handful of post cards while
still building every page (so `/about/` etc. get cards):

```bash
cd /home/martin/Documents/Programming/blog
bundle exec jekyll build --limit_posts 5 2>&1 | grep -iE "ogimage|error" | tail -20
```
Expected: no errors; `.og_cache/` now holds a few `*.png` + `*.twitter.png` pairs.

- [ ] **Step 2: Confirm generated files and sizes**

```bash
ls -la .og_cache/ | head
identify _site/images/og/about.png _site/images/og/about.twitter.png 2>/dev/null
```
Expected: `about.png` is `1200x630`, `about.twitter.png` is `1200x628`.

- [ ] **Step 3: Confirm the meta tags point at the generated images**

```bash
grep -E 'og:image|twitter:image' _site/about/index.html
```
Expected: `og:image` → `https://eve.gd/images/og/about.png`; `twitter:image` → `.../about.twitter.png`; plus `og:image:width/height` 1200/630.

- [ ] **Step 4: Visually review a generated card**

Read `_site/images/og/about.png` and confirm it matches the brief (pill, Fraunces title, snippet, button, image card, red/black diagonal). If tuning is needed, adjust `render_html`, delete the affected files from `.og_cache/`, and rebuild.

- [ ] **Step 5: Full cache warm (one-time, optional now)**

```bash
time bundle exec jekyll build   # generates all remaining cards; subsequent builds are fast
```
Note: this can take 15–30 minutes the first time. Do not commit `.og_cache/` (gitignored); the served copies live in `_site/images/og/` and deploy as usual.

- [ ] **Step 6: Final full-suite check**

Run: `ruby test/test_og_image.rb && ruby test/test_og_image_generator.rb && ruby test/test_signposting.rb && ruby test/test_signposting_generator.rb`
Expected: all PASS.

---

## Notes for the implementer

- Follow the existing `_plugins/signposting.rb` conventions exactly (module + `if defined?(Jekyll::Generator)` guard, `StaticFile` no-op subclass for generated files, `:low` priority).
- Never stage `_site/` or `.og_cache/` in feature commits — source only.
- The `excerpt` for posts is Jekyll's auto-excerpt object; `.to_s` yields its HTML, which `OgImage.excerpt_text` strips. Pages use the front-matter `excerpt` string directly.
- If a card looks wrong, the fix is almost always a CSS constant in `render_html`; delete the stale files in `.og_cache/` to force a re-render.
</content>
