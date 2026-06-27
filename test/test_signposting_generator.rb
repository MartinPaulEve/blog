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
  attr_reader :dest, :config, :static_files, :pages, :source
  def initialize(dest:, posts: [], pages: [], source: nil, static_files: [])
    @dest = dest
    @source = source
    @config = { "url" => "https://eve.gd", "title" => "Martin Paul Eve" }
    @static_files = static_files
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

  def run_generator(posts: [], pages: [], source: nil, static_files: [])
    site = FakeSite.new(dest: @dir, posts: posts, pages: pages,
                        source: source, static_files: static_files)
    Jekyll::SignpostingGenerator.new.generate(site)
    site
  end

  def home_doc
    FakeDoc.new(url: "/", data: { "layout" => "home", "title" => "Martin Paul Eve" })
  end

  # A source tree containing the site-wide redirects .htaccess, plus the
  # StaticFile entry Jekyll would have created for it during `read`.
  def with_root_htaccess
    src = Dir.mktmpdir
    File.write(File.join(src, ".htaccess"),
               "RewriteEngine On\nRewriteRule ^feed$ /feed.xml [R=301,L]\n")
    original = Jekyll::StaticFile.new(nil, src, "/", ".htaccess")
    yield(src, original)
  ensure
    FileUtils.remove_entry(src) if src
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

  def referencing_post(refs)
    FakeDoc.new(
      url: "/2026/06/23/making-blog-harvestable/",
      data: { "layout" => "post", "title" => "Making blog harvestable",
              "references" => refs },
      date: Time.new(2026, 6, 23),
    )
  end

  def citation_for(refs)
    run_generator(posts: [referencing_post(refs)])
    json = JSON.parse(
      File.read(File.join(@dir, "2026/06/23/making-blog-harvestable", "metadata.json"))
    )
    json["citation"]
  end

  def test_bare_url_reference_becomes_dereferenceable_creativework
    citation = citation_for(["https://paregorios.org/posts/2018/05/zotero_nikola_harmony/"])
    assert_equal 1, citation.length
    node = citation.first
    assert_equal "CreativeWork", node["@type"]
    assert_equal "https://paregorios.org/posts/2018/05/zotero_nikola_harmony/", node["@id"]
    assert_equal "https://paregorios.org/posts/2018/05/zotero_nikola_harmony/", node["url"]
  end

  def test_mapping_reference_becomes_typed_node_with_author
    citation = citation_for([{
      "url" => "https://doi.org/10.1045/january2016-vandesompel",
      "title" => "A Perspective on Resource Synchronization",
      "author" => "Herbert Van de Sompel",
      "type" => "ScholarlyArticle",
    }])
    node = citation.first
    assert_equal "ScholarlyArticle", node["@type"]
    assert_equal "https://doi.org/10.1045/january2016-vandesompel", node["@id"]
    assert_equal "A Perspective on Resource Synchronization", node["name"]
    assert_equal "Herbert Van de Sompel", node["author"]["name"]
  end

  def test_rich_mapping_reference_models_full_creativework
    citation = citation_for([{
      "type" => "BlogPosting",
      "title" => "Zotero-Nikola Harmony (One Simple Trick)",
      "url" => "https://paregorios.org/posts/2018/05/zotero_nikola_harmony/",
      "author" => { "name" => "Tom Elliott",
                    "orcid" => "https://orcid.org/0000-0002-4114-6677" },
      "date" => "2018-05-08",
      "language" => "en",
      "license" => "https://creativecommons.org/licenses/by/4.0/",
      "isPartOf" => { "type" => "Blog", "name" => "paregorios.org",
                      "url" => "https://paregorios.org/" },
    }])
    node = citation.first
    assert_equal "BlogPosting", node["@type"]
    assert_equal "https://paregorios.org/posts/2018/05/zotero_nikola_harmony/", node["@id"]
    assert_equal "Zotero-Nikola Harmony (One Simple Trick)", node["name"]
    assert_equal "2018-05-08", node["datePublished"]
    assert_equal "en", node["inLanguage"]
    assert_equal "https://creativecommons.org/licenses/by/4.0/", node["license"]
    assert_equal "Tom Elliott", node["author"]["name"]
    assert_equal "https://orcid.org/0000-0002-4114-6677", node["author"]["identifier"]
    assert_equal "Blog", node["isPartOf"]["@type"]
    assert_equal "paregorios.org", node["isPartOf"]["name"]
    assert_equal "https://paregorios.org/", node["isPartOf"]["url"]
  end

  def test_doi_reference_prefers_doi_as_id
    node = citation_for([{ "title" => "X", "url" => "https://eg.org/x",
                           "doi" => "https://doi.org/10.5555/x" }]).first
    assert_equal "https://doi.org/10.5555/x", node["@id"]
    assert_equal "https://eg.org/x", node["url"]
  end

  def test_multiple_authors_become_a_list
    authors = citation_for([{
      "title" => "Co-authored",
      "author" => ["Ada Lovelace",
                   { "name" => "Alan Turing", "orcid" => "https://orcid.org/0000-0001-0000-0000" }],
    }]).first["author"]
    assert_equal 2, authors.length
    assert_equal "Ada Lovelace", authors[0]["name"]
    assert_equal "https://orcid.org/0000-0001-0000-0000", authors[1]["@id"]
  end

  def test_free_text_reference_becomes_named_creativework
    citation = citation_for(["Elliott, T. (2018). Zotero, Nikola, and Harmony. Blog post."])
    assert_equal 1, citation.length
    node = citation.first
    assert_equal "CreativeWork", node["@type"]
    assert_equal "Elliott, T. (2018). Zotero, Nikola, and Harmony. Blog post.", node["name"]
    refute node.key?("url"), "a text-only reference has no url"
  end

  def test_post_without_references_omits_citation_key
    run_generator(posts: [post_doc])
    json = JSON.parse(
      File.read(File.join(@dir, "2026/06/23/making-blog-harvestable", "metadata.json"))
    )
    refute json.key?("citation"), "must not emit an empty citation key"
  end

  def test_references_do_not_leak_into_link_header_or_level1
    site = run_generator(posts: [referencing_post(["https://example.org/x"])])
    ht = File.read(File.join(@dir, "2026/06/23/making-blog-harvestable", ".htaccess"))
    refute_includes ht, "example.org"
    refute_includes site.posts.docs.first.data["signposting_links"], "example.org"
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

  def test_root_index_appends_signposting_to_existing_htaccess
    with_root_htaccess do |src, original|
      run_generator(pages: [home_doc], source: src, static_files: [original])
      ht = File.read(File.join(@dir, ".htaccess"))
      # The site-wide redirects must be preserved...
      assert_includes ht, "RewriteRule ^feed$ /feed.xml [R=301,L]"
      # ...and the signposting directives appended.
      assert_includes ht, '<Files "index.html">'
      assert_includes ht, "Header set Link"
      assert_includes ht, 'rel=\"author\"'
      assert_includes ht, 'rel=\"describedby\"'
      assert_includes ht, '<Files "metadata.json">'
    end
  end

  def test_root_index_writes_jsonld_metadata
    site = run_generator(pages: [home_doc])
    path = File.join(@dir, "metadata.json")
    assert File.exist?(path), "expected apex metadata.json to be written"
    json = JSON.parse(File.read(path))
    assert_equal "CollectionPage", json["@type"]
    assert_equal "https://eve.gd/", json["url"]
  end

  def test_root_index_drops_source_htaccess_so_it_is_not_reclobbered
    with_root_htaccess do |src, original|
      site = run_generator(pages: [home_doc], source: src, static_files: [original])
      # The source-copied root .htaccess StaticFile must be removed so that
      # site.write cannot overwrite the combined file we emitted...
      refute_includes site.static_files, original
      # ...while a replacement root .htaccess is registered to survive cleanup.
      root = site.static_files.select { |f| f.name == ".htaccess" && f.dir == "/" }
      assert_equal 1, root.length
    end
  end

  def test_root_handling_keeps_nested_post_htaccess
    with_root_htaccess do |src, original|
      site = run_generator(posts: [post_doc], pages: [home_doc],
                           source: src, static_files: [original])
      assert File.exist?(
        File.join(@dir, "2026/06/23/making-blog-harvestable", ".htaccess")
      ), "nested post .htaccess must still be written"
      nested = site.static_files.select { |f| f.name == ".htaccess" }
      assert_operator nested.length, :>=, 2,
                      "both the nested and the apex .htaccess should be registered"
    end
  end

  def test_metadata_falls_back_to_site_title_when_doc_has_no_title
    titleless = FakeDoc.new(url: "/", data: { "layout" => "home" })
    run_generator(pages: [titleless])
    json = JSON.parse(File.read(File.join(@dir, "metadata.json")))
    assert_equal "Martin Paul Eve", json["name"]
    assert_equal "Martin Paul Eve", json["headline"]
  end

  def test_root_index_still_sets_level1_links
    site = run_generator(pages: [home_doc])
    assert_includes site.pages.first.data["signposting_links"],
                    '<link rel="author"'
  end
end
