# Unit tests for the pure Signposting builders.
# Run with:  ruby test/test_signposting.rb
require "minitest/autorun"
require_relative "../_plugins/signposting"

class TestSignposting < Minitest::Test
  def full_meta
    {
      author: Signposting::AUTHOR_ORCID,
      doi: "https://doi.org/10.59348/vrt01-f3b49",
      license: Signposting::LICENSE_URL,
      types: ["https://schema.org/BlogPosting", "https://schema.org/AboutPage"],
      describedby: {
        url: "https://eve.gd/p/metadata.json",
        type: "application/ld+json",
        profile: "https://schema.org/",
      },
      items: [{ url: "https://eve.gd/p/paper.pdf", type: "application/pdf" }],
    }
  end

  def page_meta
    {
      author: Signposting::AUTHOR_ORCID,
      license: Signposting::LICENSE_URL,
      types: ["https://schema.org/WebPage"],
      describedby: { url: "https://eve.gd/about/metadata.json", type: "application/ld+json" },
    }
  end

  # --- relations -----------------------------------------------------------

  def test_relations_full_order
    rels = Signposting.relations(full_meta)
    assert_equal %w[author cite-as type type license describedby item],
                 rels.map { |r| r[:rel] }
  end

  def test_relations_targets
    rels = Signposting.relations(full_meta)
    assert_equal Signposting::AUTHOR_ORCID, rels[0][:target]
    assert_equal "https://doi.org/10.59348/vrt01-f3b49",
                 rels.find { |r| r[:rel] == "cite-as" }[:target]
    db = rels.find { |r| r[:rel] == "describedby" }
    assert_equal "application/ld+json", db[:params][:type]
    assert_equal "https://schema.org/", db[:params][:profile]
    item = rels.find { |r| r[:rel] == "item" }
    assert_equal "application/pdf", item[:params][:type]
  end

  def test_relations_minimal_omits_cite_as_and_item
    rels = Signposting.relations(page_meta)
    assert_equal %w[author type license describedby], rels.map { |r| r[:rel] }
    refute(rels.any? { |r| r[:rel] == "cite-as" })
    refute(rels.any? { |r| r[:rel] == "item" })
  end

  # --- header_value (RFC 8288) ---------------------------------------------

  def test_header_value_contains_each_link
    hv = Signposting.header_value(Signposting.relations(full_meta))
    assert_includes hv, '<https://orcid.org/0000-0002-5589-8511>; rel="author"'
    assert_includes hv, '<https://doi.org/10.59348/vrt01-f3b49>; rel="cite-as"'
    assert_includes hv, '<https://schema.org/BlogPosting>; rel="type"'
    assert_includes hv, '<https://schema.org/AboutPage>; rel="type"'
    assert_includes hv, '<https://creativecommons.org/licenses/by/4.0/>; rel="license"'
    assert_includes hv, '<https://eve.gd/p/metadata.json>; rel="describedby"; type="application/ld+json"; profile="https://schema.org/"'
    assert_includes hv, '<https://eve.gd/p/paper.pdf>; rel="item"; type="application/pdf"'
  end

  def test_header_value_joins_links_with_comma
    hv = Signposting.header_value(Signposting.relations(full_meta))
    # 7 link-values => 6 ", <" separators between them
    assert_equal 6, hv.scan(", <").length
  end

  # --- htaccess ------------------------------------------------------------

  def test_htaccess_sets_link_on_index_with_escaped_quotes
    ht = Signposting.htaccess(Signposting.relations(full_meta), json_file: "metadata.json")
    assert_includes ht, '<Files "index.html">'
    assert_includes ht, 'Header set Link "'
    assert_includes ht, 'rel=\"author\"'        # inner quotes escaped for Apache
    assert_includes ht, "</Files>"
  end

  def test_htaccess_serves_json_metadata_as_ld_json
    ht = Signposting.htaccess(Signposting.relations(full_meta), json_file: "metadata.json")
    assert_includes ht, '<Files "metadata.json">'
    assert_includes ht, "application/ld+json"
  end

  def test_htaccess_without_json_file_omits_metadata_block
    ht = Signposting.htaccess(Signposting.relations(page_meta))
    refute_includes ht, "ForceType"
    refute_includes ht, '<Files "metadata.json">'
  end

  # --- link_elements (Level 1) ---------------------------------------------

  def test_link_elements_one_per_relation
    els = Signposting.link_elements(Signposting.relations(full_meta))
    assert_equal 7, els.length
  end

  def test_link_elements_render_href_and_type
    joined = Signposting.link_elements(Signposting.relations(full_meta)).join("\n")
    assert_includes joined, '<link rel="author" href="https://orcid.org/0000-0002-5589-8511">'
    assert_includes joined, '<link rel="cite-as" href="https://doi.org/10.59348/vrt01-f3b49">'
    assert_includes joined, '<link rel="describedby" href="https://eve.gd/p/metadata.json" type="application/ld+json">'
  end

  # --- DOI detection / normalisation ---------------------------------------

  def test_normalize_doi_strips_resolver_prefixes
    assert_equal "10.31274/jlsc.16288", Signposting.normalize_doi("10.31274/jlsc.16288")
    assert_equal "10.31274/jlsc.16288", Signposting.normalize_doi("https://doi.org/10.31274/jlsc.16288")
    assert_equal "10.31274/jlsc.16288", Signposting.normalize_doi("http://dx.doi.org/10.31274/jlsc.16288")
    assert_equal "10.31274/jlsc.16288", Signposting.normalize_doi("doi:10.31274/jlsc.16288")
  end

  def test_doi_predicate
    assert Signposting.doi?("10.31274/jlsc.16288")
    assert Signposting.doi?("https://doi.org/10.31274/jlsc.16288")
    refute Signposting.doi?("https://paregorios.org/posts/2018/05/zotero_nikola_harmony/")
    refute Signposting.doi?("just some text")
  end

  # --- CSL-JSON -> schema.org citation --------------------------------------

  def jlsc_csl
    {
      "type" => "journal-article",
      "title" => "Digital Scholarly Journals Are Poorly Preserved: A Study of 7 Million Articles",
      "container-title" => "Journal of Librarianship and Scholarly Communication",
      "publisher" => "Iowa State University",
      "DOI" => "10.31274/jlsc.16288",
      "issued" => { "date-parts" => [[2024, 1, 24]] },
      "author" => [{ "given" => "Martin Paul", "family" => "Eve",
                     "affiliation" => [{ "name" => "Birkbeck, University of London" }] }],
    }
  end

  def test_csl_journal_article_maps_to_scholarly_article
    node = Signposting.csl_to_citation(jlsc_csl)
    assert_equal "ScholarlyArticle", node["@type"]
    assert_equal "https://doi.org/10.31274/jlsc.16288", node["@id"]
    assert_equal "Digital Scholarly Journals Are Poorly Preserved: A Study of 7 Million Articles", node["name"]
    assert_equal "2024-01-24", node["datePublished"]
    assert_equal "Iowa State University", node["publisher"]["name"]
    assert_equal "Periodical", node["isPartOf"]["@type"]
    assert_equal "Journal of Librarianship and Scholarly Communication", node["isPartOf"]["name"]
    assert_equal "Martin Paul Eve", node["author"]["name"]
    assert_equal "Birkbeck, University of London", node["author"]["affiliation"]["name"]
  end

  def test_csl_book_maps_to_book
    node = Signposting.csl_to_citation({ "type" => "book", "title" => "A Book",
                                         "DOI" => "10.5555/book" })
    assert_equal "Book", node["@type"]
  end

  def test_csl_chapter_is_part_of_a_book
    node = Signposting.csl_to_citation({ "type" => "book-chapter", "title" => "A Chapter",
                                         "container-title" => "The Whole Book", "DOI" => "10.5555/ch" })
    assert_equal "Chapter", node["@type"]
    assert_equal "Book", node["isPartOf"]["@type"]
    assert_equal "The Whole Book", node["isPartOf"]["name"]
  end

  def test_csl_dataset_maps_to_dataset
    node = Signposting.csl_to_citation({ "type" => "dataset", "title" => "Some Data",
                                         "DOI" => "10.5555/data" })
    assert_equal "Dataset", node["@type"]
  end

  def test_csl_unknown_type_falls_back_to_creativework
    node = Signposting.csl_to_citation({ "type" => "weird-thing", "title" => "X", "DOI" => "10.5555/x" })
    assert_equal "CreativeWork", node["@type"]
  end

  def test_csl_author_orcid_becomes_identifier
    csl = { "type" => "journal-article", "title" => "X", "DOI" => "10.5555/x",
            "author" => [{ "given" => "Ada", "family" => "Lovelace",
                           "ORCID" => "https://orcid.org/0000-0000-0000-0001" }] }
    author = Signposting.csl_to_citation(csl)["author"]
    assert_equal "https://orcid.org/0000-0000-0000-0001", author["identifier"]
  end

  def test_csl_multiple_authors_become_a_list
    csl = { "type" => "journal-article", "title" => "X", "DOI" => "10.5555/x",
            "author" => [{ "given" => "A", "family" => "One" },
                         { "given" => "B", "family" => "Two" }] }
    authors = Signposting.csl_to_citation(csl)["author"]
    assert_equal 2, authors.length
    assert_equal "A One", authors[0]["name"]
  end

  def test_csl_year_only_date
    node = Signposting.csl_to_citation({ "type" => "book", "title" => "X", "DOI" => "10.5555/x",
                                         "issued" => { "date-parts" => [[1999]] } })
    assert_equal "1999", node["datePublished"]
  end
end
