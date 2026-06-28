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
  attr_reader :url, :data, :content
  def initialize(url:, data:, content: nil); @url = url; @data = data; @content = content; end
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
    @config = { "url" => "https://eve.gd", "title" => "Martin Paul Eve", "owner" => { "job" => "Test Job Title" } }
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

  def test_in_scope_page_is_processed
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

  def png_bytes(w, h)
    "\x89PNG\r\n\x1a\n".b + [13].pack("N") + "IHDR".b + [w].pack("N") + [h].pack("N") + ("\x00" * 5).b
  end

  def test_wide_banner_feature_falls_back_to_full_width
    FileUtils.mkdir_p(File.join(@source, "images"))
    File.binwrite(File.join(@source, "images", "banner.png"), png_bytes(1902, 353))
    p = post(data: { "layout" => "post", "title" => "Banner", "excerpt" => "x",
                     "image" => { "feature" => "banner.png" } })
    run_generator(posts: [p])
    html = File.read(File.join(@source, ".og_cache", "2026-06-23-harvestable.png"))
    assert_includes html, "og-full"
    refute_includes html, "data:image/png;base64,"
  end

  def test_og_card_image_override_is_used_and_bypasses_banner_check
    FileUtils.mkdir_p(File.join(@source, "images"))
    # a wide banner that would normally be dropped, but an explicit override wins
    File.binwrite(File.join(@source, "images", "wide.png"), png_bytes(1902, 353))
    p = post(data: { "layout" => "post", "title" => "Override", "excerpt" => "x",
                     "og_card_image" => "wide.png" })
    run_generator(posts: [p])
    html = File.read(File.join(@source, ".og_cache", "2026-06-23-harvestable.png"))
    assert_includes html, "data:image/png;base64,"
    assert_includes html, 'class="right"'
  end

  def test_home_snippet_uses_owner_job
    home = FakeDoc.new(url: "/", data: { "layout" => "home", "title" => "Home" })
    run_generator(pages: [home])
    html = File.read(File.join(@source, ".og_cache", "index.png"))
    assert_includes html, "Test Job Title"
  end

  def test_portrait_card_image_uses_taller_frame
    FileUtils.mkdir_p(File.join(@source, "images"))
    File.binwrite(File.join(@source, "images", "cover.png"), png_bytes(640, 1024))
    p = post(data: { "layout" => "post", "title" => "Cover", "excerpt" => "x",
                     "og_card_image" => "cover.png" })
    run_generator(posts: [p])
    html = File.read(File.join(@source, ".og_cache", "2026-06-23-harvestable.png"))
    assert_includes html, "height:534px"
  end

  def test_page_snippet_falls_back_to_content
    page = FakeDoc.new(url: "/about/", data: { "layout" => "page", "title" => "About" },
                       content: "<p>Bio body text.</p>")
    run_generator(pages: [page])
    html = File.read(File.join(@source, ".og_cache", "about.png"))
    assert_includes html, "Bio body text."
  end
end
