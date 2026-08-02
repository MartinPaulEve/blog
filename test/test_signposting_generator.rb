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

  def run_generator(posts: [], pages: [], source: nil, static_files: [], doi_fetcher: nil)
    site = FakeSite.new(dest: @dir, posts: posts, pages: pages,
                        source: source, static_files: static_files)
    gen = Jekyll::SignpostingGenerator.new
    gen.doi_fetcher = doi_fetcher if doi_fetcher
    gen.generate(site)
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
    # These cases must never reach the network; a fetch here is a test bug.
    no_fetch = ->(doi) { raise "unexpected DOI fetch: #{doi}" }
    run_generator(posts: [referencing_post(refs)], doi_fetcher: no_fetch)
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

  # --- internal references (auto-resolved from the site) -------------------

  def target_post
    FakeDoc.new(
      url: "/2026/06/23/harvestable/",
      data: { "layout" => "post", "title" => "Making blog posts harvestable",
              "doi" => "https://doi.org/10.59348/vrt01-f3b49" },
      date: Time.new(2026, 6, 23),
    )
  end

  def citing_post(refs)
    FakeDoc.new(
      url: "/2026/07/01/citing/",
      data: { "layout" => "post", "title" => "Citing", "references" => refs },
      date: Time.new(2026, 7, 1),
    )
  end

  def internal_citation(refs)
    run_generator(posts: [target_post, citing_post(refs)])
    json = JSON.parse(File.read(File.join(@dir, "2026/07/01/citing", "metadata.json")))
    json["citation"].first
  end

  def test_internal_absolute_url_is_resolved_from_the_site
    node = internal_citation(["https://eve.gd/2026/06/23/harvestable/"])
    assert_equal "BlogPosting", node["@type"]
    assert_equal "https://doi.org/10.59348/vrt01-f3b49", node["@id"] # DOI preferred
    assert_equal "Making blog posts harvestable", node["name"]
    assert_equal "https://eve.gd/2026/06/23/harvestable/", node["url"]
    assert_equal "2026-06-23", node["datePublished"]
    assert_equal "Martin Paul Eve", node["author"]["name"]
    assert_equal Signposting::AUTHOR_ORCID, node["author"]["identifier"]
    assert_equal "Blog", node["isPartOf"]["@type"]
    assert_equal "Martin Paul Eve", node["isPartOf"]["name"]
  end

  def test_internal_relative_path_is_resolved
    node = internal_citation(["/2026/06/23/harvestable/"])
    assert_equal "BlogPosting", node["@type"]
    assert_equal "Making blog posts harvestable", node["name"]
  end

  def test_internal_marker_type_does_not_leak_as_schema_type
    node = internal_citation([{ "type" => "Internal",
                                "url" => "https://eve.gd/2026/06/23/harvestable/" }])
    assert_equal "BlogPosting", node["@type"]
  end

  def test_internal_reference_allows_explicit_field_override
    node = internal_citation([{ "url" => "/2026/06/23/harvestable/",
                                "title" => "A Better Title" }])
    assert_equal "A Better Title", node["name"]      # overridden
    assert_equal "2026-06-23", node["datePublished"] # still deduced
  end

  def test_unresolved_internal_link_falls_back_to_plain_node
    node = internal_citation(["https://eve.gd/2026/06/23/does-not-exist/"])
    assert_equal "CreativeWork", node["@type"]
    assert_equal "https://eve.gd/2026/06/23/does-not-exist/", node["url"]
  end

  def test_external_reference_is_not_auto_resolved
    node = internal_citation(["https://paregorios.org/posts/2018/05/zotero_nikola_harmony/"])
    assert_equal "CreativeWork", node["@type"]
    assert_equal "https://paregorios.org/posts/2018/05/zotero_nikola_harmony/", node["@id"]
  end

  # --- DOI references (fetched + cached) -----------------------------------

  JLSC_CSL = {
    "type" => "journal-article",
    "title" => "Digital Scholarly Journals Are Poorly Preserved: A Study of 7 Million Articles",
    "container-title" => "Journal of Librarianship and Scholarly Communication",
    "publisher" => "Iowa State University",
    "DOI" => "10.31274/jlsc.16288",
    "issued" => { "date-parts" => [[2024, 1, 24]] },
    "author" => [{ "given" => "Martin Paul", "family" => "Eve" }],
  }.freeze

  # A fetcher that records the DOIs it was asked for and returns canned CSL.
  def counting_fetcher(csl = JLSC_CSL)
    calls = []
    fetcher = ->(doi) { calls << doi; csl }
    [fetcher, calls]
  end

  def doi_citation(refs, fetcher)
    run_generator(posts: [referencing_post(refs)], doi_fetcher: fetcher)
    json = JSON.parse(File.read(File.join(@dir, "2026/06/23/making-blog-harvestable", "metadata.json")))
    json["citation"].first
  end

  def test_bare_doi_reference_is_fetched_and_modelled
    fetcher, calls = counting_fetcher
    node = doi_citation(["10.31274/jlsc.16288"], fetcher)
    assert_equal ["10.31274/jlsc.16288"], calls
    assert_equal "ScholarlyArticle", node["@type"]
    assert_equal "https://doi.org/10.31274/jlsc.16288", node["@id"]
    assert_equal "Martin Paul Eve", node["author"]["name"]
    assert_equal "2024-01-24", node["datePublished"]
  end

  def test_doi_org_url_reference_normalises_to_same_key
    fetcher, calls = counting_fetcher
    node = doi_citation(["https://doi.org/10.31274/jlsc.16288"], fetcher)
    assert_equal ["10.31274/jlsc.16288"], calls
    assert_equal "ScholarlyArticle", node["@type"]
  end

  def test_same_doi_is_fetched_only_once_within_a_build
    fetcher, calls = counting_fetcher
    run_generator(
      posts: [referencing_post(["10.31274/jlsc.16288",
                                "https://doi.org/10.31274/jlsc.16288"])],
      doi_fetcher: fetcher,
    )
    assert_equal 1, calls.length, "the DOI should be fetched once and reused"
  end

  def test_doi_metadata_is_cached_to_disk_and_reused_across_builds
    src = Dir.mktmpdir
    begin
      fetcher, calls = counting_fetcher
      run_generator(posts: [referencing_post(["10.31274/jlsc.16288"])],
                    source: src, doi_fetcher: fetcher)
      assert_equal 1, calls.length
      assert File.exist?(File.join(src, ".doi_cache.json")), "cache file should be written"

      # A second build with a fetcher that explodes must still resolve the DOI
      # from the on-disk cache.
      boom = ->(_doi) { raise "must not fetch -- should be cached" }
      node = doi_citation_in(src, ["10.31274/jlsc.16288"], boom)
      assert_equal "ScholarlyArticle", node["@type"]
    ensure
      FileUtils.remove_entry(src)
    end
  end

  def doi_citation_in(src, refs, fetcher)
    run_generator(posts: [referencing_post(refs)], source: src, doi_fetcher: fetcher)
    json = JSON.parse(File.read(File.join(@dir, "2026/06/23/making-blog-harvestable", "metadata.json")))
    json["citation"].first
  end

  def test_doi_mapping_allows_field_override
    fetcher, = counting_fetcher
    node = doi_citation([{ "doi" => "10.31274/jlsc.16288", "title" => "Short title" }], fetcher)
    assert_equal "Short title", node["name"]            # overridden
    assert_equal "ScholarlyArticle", node["@type"]      # still from CSL
  end

  def test_unresolved_doi_falls_back_to_dereferenceable_node
    boom = ->(_doi) { nil }
    node = doi_citation(["10.31274/jlsc.16288"], boom)
    assert_equal "CreativeWork", node["@type"]
    assert_equal "https://doi.org/10.31274/jlsc.16288", node["@id"]
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

  # --- PDF versions (populated by the pdf_pages generator) ------------------

  def pdf_post
    FakeDoc.new(
      url: "/2026/08/02/voyager/",
      data: { "layout" => "post", "title" => "Voyager",
              "pdf" => ["https://eve.gd/PDF/2026-08-02-voyager.pdf"],
              "pdf_url" => "https://eve.gd/PDF/2026-08-02-voyager.pdf",
              "item" => ["https://eve.gd/files/slides.key"] },
      date: Time.new(2026, 8, 2),
    )
  end

  def test_item_and_pdf_front_matter_both_become_item_links
    site = run_generator(posts: [pdf_post])
    links = site.posts.docs.first.data["signposting_links"]
    assert_includes links,
                    '<link rel="item" href="https://eve.gd/PDF/2026-08-02-voyager.pdf" type="application/pdf">'
    assert_includes links, '<link rel="item" href="https://eve.gd/files/slides.key"'
  end

  def test_pdf_appears_in_link_header
    run_generator(posts: [pdf_post])
    ht = File.read(File.join(@dir, "2026/08/02/voyager", ".htaccess"))
    assert_includes ht, "PDF/2026-08-02-voyager.pdf"
    assert_includes ht, 'rel=\"item\"'
  end

  def test_pdf_encoding_node_in_describedby_metadata
    run_generator(posts: [pdf_post])
    json = JSON.parse(File.read(File.join(@dir, "2026/08/02/voyager", "metadata.json")))
    enc = json["encoding"]
    assert_equal "MediaObject", enc["@type"]
    assert_equal "https://eve.gd/PDF/2026-08-02-voyager.pdf", enc["contentUrl"]
    assert_equal "application/pdf", enc["encodingFormat"]
  end
end
