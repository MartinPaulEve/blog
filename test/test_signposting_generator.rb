# Integration test for SignpostingGenerator, using mocked Jekyll objects so it
# runs without the Jekyll gem (the real build runs server-side on Ruby >= 2.7).
# Run with:  ruby test/test_signposting_generator.rb
require "minitest/autorun"
require "tmpdir"
require "json"

# Minimal Jekyll stubs so _plugins/signposting.rb loads in isolation.
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

require_relative "../_plugins/signposting"

class FakeDoc
  attr_reader :url, :data, :date
  def initialize(url:, data:, date: nil)
    @url = url
    @data = data
    @date = date
  end

  def output_ext
    @url.end_with?("/") ? ".html" : File.extname(@url)
  end
end

class FakePosts
  attr_reader :docs
  def initialize(docs)
    @docs = docs
  end
end

class FakeSite
  attr_reader :dest, :config, :static_files, :pages
  def initialize(dest:, posts: [], pages: [])
    @dest = dest
    @config = { "url" => "https://eve.gd" }
    @static_files = []
    @posts = FakePosts.new(posts)
    @pages = pages
  end

  def posts
    @posts
  end
end

class TestSignpostingGenerator < Minitest::Test
  def setup
    @dir = Dir.mktmpdir
  end

  def teardown
    FileUtils.remove_entry(@dir)
  end

  def run_generator(posts: [], pages: [])
    site = FakeSite.new(dest: @dir, posts: posts, pages: pages)
    Jekyll::SignpostingGenerator.new.generate(site)
    site
  end

  def post_doc
    FakeDoc.new(
      url: "/2026/06/23/making-blog-harvestable/",
      data: { "layout" => "post", "title" => "Making blog harvestable",
              "doi" => "https://doi.org/10.59348/vrt01-f3b49" },
      date: Time.new(2026, 6, 23),
    )
  end

  def test_writes_htaccess_with_link_header_for_post
    run_generator(posts: [post_doc])
    path = File.join(@dir, "2026/06/23/making-blog-harvestable", ".htaccess")
    assert File.exist?(path), "expected .htaccess to be written"
    ht = File.read(path)
    assert_includes ht, '<Files "index.html">'
    assert_includes ht, "Header set Link"
    assert_includes ht, 'rel=\"cite-as\"'
    assert_includes ht, "https://doi.org/10.59348/vrt01-f3b49"
    assert_includes ht, '<Files "metadata.json">'
  end

  def test_writes_valid_jsonld_describedby_target
    run_generator(posts: [post_doc])
    path = File.join(@dir, "2026/06/23/making-blog-harvestable", "metadata.json")
    assert File.exist?(path), "expected metadata.json to be written"
    json = JSON.parse(File.read(path))
    assert_equal "BlogPosting", json["@type"]
    assert_equal "https://doi.org/10.59348/vrt01-f3b49", json["identifier"]
    assert_equal Signposting::AUTHOR_ORCID, json["author"]["identifier"]
    assert_equal "2026-06-23", json["datePublished"]
  end

  def test_sets_level1_links_on_document
    site = run_generator(posts: [post_doc])
    links = site.posts.docs.first.data["signposting_links"]
    assert_includes links, '<link rel="author" href="https://orcid.org/0000-0002-5589-8511">'
    assert_includes links, '<link rel="cite-as" href="https://doi.org/10.59348/vrt01-f3b49">'
    assert_includes links, '<link rel="describedby"'
  end

  def test_registers_written_files_to_survive_cleanup
    site = run_generator(posts: [post_doc])
    names = site.static_files.map(&:name)
    assert_includes names, ".htaccess"
    assert_includes names, "metadata.json"
  end

  def test_page_without_doi_omits_cite_as_but_still_signposts
    page = FakeDoc.new(url: "/about/", data: { "layout" => "page", "title" => "About" })
    site = run_generator(pages: [page])
    ht = File.read(File.join(@dir, "about", ".htaccess"))
    refute_includes ht, "cite-as"
    assert_includes ht, 'rel=\"author\"'
    assert_includes site.pages.first.data["signposting_links"], '<link rel="author"'
  end

  def test_root_level_file_is_not_given_an_htaccess
    home = FakeDoc.new(url: "/index.html", data: { "layout" => "home", "title" => "Home" })
    site = run_generator(pages: [home])
    refute File.exist?(File.join(@dir, ".htaccess")),
           "must not write a root .htaccess (would clobber the redirects file)"
    # Level 1 fallback is still provided.
    assert_includes site.pages.first.data["signposting_links"], "<link rel="
  end
end
