# Unit + wiring tests for the PDF page generator. Run: ruby test/test_pdf_pages.rb
require "minitest/autorun"
require "tmpdir"
require "fileutils"

# Minimal Jekyll stubs so _plugins/pdf_pages.rb loads in isolation (the hook
# registration is guarded on Jekyll::Hooks, which these stubs omit).
module Jekyll
  class Generator
    def self.safe(*); end
    def self.priority(*); end
  end

  class StaticFile
    attr_reader :dir, :name
    def initialize(_site, _base, dir, name)
      @dir = dir
      @name = name
    end
  end
end

require_relative "../_plugins/pdf_pages"

class TestPdfPages < Minitest::Test
  # --- scope ---------------------------------------------------------------

  def test_posts_and_pages_are_in_scope
    assert PdfPages.scope_layout?("post")
    assert PdfPages.scope_layout?("page")
    refute PdfPages.scope_layout?("home")
    refute PdfPages.scope_layout?("redirect")
    refute PdfPages.scope_layout?(nil)
  end

  # --- naming --------------------------------------------------------------

  def test_pdf_url_uses_slug_under_PDF_dir
    assert_equal "https://eve.gd/PDF/2026-08-02-voyager.pdf",
                 PdfPages.pdf_url("https://eve.gd", "2026-08-02-voyager")
  end

  def test_slug_matches_og_slug_convention
    assert_equal "2026-06-23-harvestable", PdfPages.slug("/2026/06/23/harvestable/")
    assert_equal "about", PdfPages.slug("/about/")
  end

  # --- hash normalisation --------------------------------------------------
  # The cache key must be stable across build-time noise: the ?v= cache-buster
  # changes every build, and the related-posts sidebar changes whenever any new
  # post is published; neither affects the printed page (print CSS hides the
  # sidebar entirely).

  def page_html(v: "111", sidebar: "old")
    <<~HTML
      <html><head>
      <link rel="stylesheet" href="/assets/css/styles.css?v=#{v}">
      </head><body>
      <div class="post-body">The content.</div>
      <aside class="post-sidebar">related: #{sidebar}</aside>
      <footer>foot</footer>
      </body></html>
    HTML
  end

  def test_hash_stable_across_cache_buster_and_sidebar_changes
    a = PdfPages.content_hash(page_html(v: "111", sidebar: "old"))
    b = PdfPages.content_hash(page_html(v: "222", sidebar: "new"))
    assert_equal a, b
  end

  def test_hash_changes_when_content_changes
    a = PdfPages.content_hash(page_html)
    b = PdfPages.content_hash(page_html.sub("The content.", "Different content."))
    refute_equal a, b
  end

  # --- webmention markup insensitivity ------------------------------------
  # The webmention layer adds endpoint/rel=me links in the head, mf2 classes
  # on the article/title/body, its own stylesheet and a data-driven mentions
  # section. None of it affects the printed page (webmentions.css hides the
  # section in print; class tokens carry no print styling), so the cache key
  # must not see any of it — otherwise adding the feature (or merely
  # receiving a mention) would re-render every PDF on the site.

  def page_html_plain(v: "111", sidebar: "old")
    <<~HTML
      <html><head>
      <link rel="stylesheet" href="/assets/css/styles.css?v=#{v}">
          <link rel="stylesheet" href="/assets/css/blog-post.css?v=#{v}">
      <link href="https://eve.gd/feed/feed.atom" type="application/atom+xml" rel="alternate" title="Feed">
      </head><body>
      <article class="blog-post">
      <h1 class="post-title">Title</h1>
      <div class="post-content">
      <div class="post-body">The content.</div>
      <aside class="post-sidebar">related: #{sidebar}</aside>
      </div>
          </article>
      </body></html>
    HTML
  end

  def page_html_webmentions(v: "222", sidebar: "new", mentions: "3 likes")
    <<~HTML
      <html><head>
      <link rel="stylesheet" href="/assets/css/styles.css?v=#{v}">
          <link rel="stylesheet" href="/assets/css/blog-post.css?v=#{v}">
          <link rel="stylesheet" href="/assets/css/webmentions.css?v=#{v}">
      <link href="https://eve.gd/feed/feed.atom" type="application/atom+xml" rel="alternate" title="Feed">
      <link rel="webmention" href="https://webmention.io/eve.gd/webmention" />
      <link rel="pingback" href="https://webmention.io/eve.gd/xmlrpc" />
      <link rel="me" href="https://github.com/MartinPaulEve" />
      <link rel="me" href="mailto:martin@eve.gd" />
      </head><body>
      <article class="blog-post h-entry">
      <h1 class="post-title p-name">Title</h1>
      <div class="post-content">
      <div class="post-body e-content">The content.</div>
      <aside class="post-sidebar">related: #{sidebar}</aside>
      </div>
          <section class="post-webmentions">
      <div class="webmention-meta"><a class="u-url" href="/x/">x</a></div>
      <h2>Webmentions</h2><p>#{mentions}</p>
      </section>

          </article>
      </body></html>
    HTML
  end

  def test_hash_unchanged_by_adding_the_webmention_layer
    assert_equal PdfPages.content_hash(page_html_plain),
                 PdfPages.content_hash(page_html_webmentions)
  end

  def test_hash_unchanged_when_a_blank_line_precedes_the_mentions_section
    # The real layout renders "</div>\n\n        <section ...": the blank
    # line before the include must vanish with the section, or every post
    # gains one extra newline over its pre-webmentions self and every PDF
    # re-renders (this happened; hence the regression test).
    spaced = page_html_webmentions.sub(
      "</div>\n    <section class=\"post-webmentions\">",
      "</div>\n\n        <section class=\"post-webmentions\">"
    )
    assert_equal PdfPages.content_hash(page_html_plain),
                 PdfPages.content_hash(spaced)
  end

  def test_hash_unchanged_when_mention_data_changes
    a = PdfPages.content_hash(page_html_webmentions(mentions: "3 likes"))
    b = PdfPages.content_hash(page_html_webmentions(mentions: "99 likes, 12 replies"))
    assert_equal a, b
  end

  def test_hash_still_changes_when_content_changes_under_webmentions
    a = PdfPages.content_hash(page_html_webmentions)
    b = PdfPages.content_hash(
      page_html_webmentions.sub("The content.", "Different content.")
    )
    refute_equal a, b
  end

  # --- batch renderer with cache -------------------------------------------

  def with_dirs
    Dir.mktmpdir do |cache|
      Dir.mktmpdir do |dest|
        yield cache, dest
      end
    end
  end

  def pages(html = "<div class=\"post-body\">x</div>")
    [{ slug: "p1", url: "/p1/", html: html }]
  end

  def fake_renderer(log)
    lambda do |page, out_path|
      log << page[:slug]
      File.binwrite(out_path, "%PDF-fake #{page[:slug]}")
      true
    end
  end

  def test_first_run_renders_and_copies_to_dest
    with_dirs do |cache, dest|
      log = []
      stats = PdfPages::Batch.new(cache_dir: cache, dest_dir: dest,
                                  renderer: fake_renderer(log)).process(pages)
      assert_equal ["p1"], log
      assert_equal 1, stats[:rendered]
      assert File.exist?(File.join(dest, "p1.pdf")), "pdf copied into dest"
      assert File.exist?(File.join(cache, "p1.pdf")), "pdf kept in cache"
    end
  end

  def test_unchanged_page_is_served_from_cache_without_rendering
    with_dirs do |cache, dest|
      PdfPages::Batch.new(cache_dir: cache, dest_dir: dest,
                          renderer: fake_renderer([])).process(pages)
      log = []
      stats = PdfPages::Batch.new(cache_dir: cache, dest_dir: dest,
                                  renderer: fake_renderer(log)).process(pages)
      assert_empty log, "no re-render for unchanged content"
      assert_equal 1, stats[:cached]
      assert File.exist?(File.join(dest, "p1.pdf")), "cached pdf still copied to dest"
    end
  end

  def test_changed_content_is_rerendered
    with_dirs do |cache, dest|
      PdfPages::Batch.new(cache_dir: cache, dest_dir: dest,
                          renderer: fake_renderer([])).process(pages("<p>one</p>"))
      log = []
      PdfPages::Batch.new(cache_dir: cache, dest_dir: dest,
                          renderer: fake_renderer(log)).process(pages("<p>two</p>"))
      assert_equal ["p1"], log
    end
  end

  def test_failed_render_is_not_cached_and_not_copied
    with_dirs do |cache, dest|
      failing = ->(_page, _out) { false }
      stats = PdfPages::Batch.new(cache_dir: cache, dest_dir: dest,
                                  renderer: failing).process(pages)
      assert_equal 1, stats[:failed]
      refute File.exist?(File.join(dest, "p1.pdf"))
      # next run must try again
      log = []
      PdfPages::Batch.new(cache_dir: cache, dest_dir: dest,
                          renderer: fake_renderer(log)).process(pages)
      assert_equal ["p1"], log
    end
  end

  # --- generator wiring (pdf_url + signposting item data) -------------------

  class FakeDoc
    attr_reader :url, :data
    def initialize(url:, data:)
      @url = url
      @data = data
    end

    def output_ext
      @url.end_with?("/") ? ".html" : File.extname(@url)
    end
  end

  class FakePosts
    attr_reader :docs
    def initialize(docs); @docs = docs; end
  end

  class FakeSite
    attr_reader :config, :pages
    def initialize(posts: [], pages: [])
      @config = { "url" => "https://eve.gd" }
      @posts = FakePosts.new(posts)
      @pages = pages
    end

    def posts; @posts; end
  end

  def run_generator(posts: [], pages: [])
    site = FakeSite.new(posts: posts, pages: pages)
    Jekyll::PdfPagesGenerator.new.generate(site)
    site
  end

  def test_generator_sets_pdf_url_and_signposting_item_on_posts
    doc = FakeDoc.new(url: "/2026/08/02/voyager/", data: { "layout" => "post" })
    run_generator(posts: [doc])
    assert_equal "https://eve.gd/PDF/2026-08-02-voyager.pdf", doc.data["pdf_url"]
    assert_includes Array(doc.data["pdf"]), "https://eve.gd/PDF/2026-08-02-voyager.pdf"
  end

  def test_generator_preserves_existing_pdf_front_matter
    doc = FakeDoc.new(url: "/2026/08/02/voyager/",
                      data: { "layout" => "post", "pdf" => ["/files/handout.pdf"] })
    run_generator(posts: [doc])
    assert_includes Array(doc.data["pdf"]), "/files/handout.pdf"
    assert_includes Array(doc.data["pdf"]), "https://eve.gd/PDF/2026-08-02-voyager.pdf"
  end

  def test_generator_skips_out_of_scope_layouts_and_non_pretty_urls
    home = FakeDoc.new(url: "/", data: { "layout" => "home" })
    notfound = FakeDoc.new(url: "/404.html", data: { "layout" => "page" })
    run_generator(pages: [home, notfound])
    assert_nil home.data["pdf_url"]
    assert_nil notfound.data["pdf_url"]
  end
end
