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
end
