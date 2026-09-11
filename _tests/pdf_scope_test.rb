# Behaviour tests for PDF scope: posts and pages with pretty URLs get PDF
# editions, but a page can opt out with `pdf: false` front matter (the
# /thoughts/ page holds thousands of entries and changes on every thought,
# so rendering it would bloat and churn the cache). Run with:
#   ruby _tests/pdf_scope_test.rb
require "minitest/autorun"
require_relative "../_plugins/pdf_pages"

class PdfScopeTest < Minitest::Test
  def test_pretty_page_urls_are_in_scope
    assert PdfPages.wants_pdf?("/about/", { "layout" => "page" })
    assert PdfPages.wants_pdf?("/2026/09/09/a-post/", { "layout" => "post" })
  end

  def test_non_pretty_or_other_layouts_are_not
    refute PdfPages.wants_pdf?("/feed.xml", { "layout" => "page" })
    refute PdfPages.wants_pdf?("/", { "layout" => "home" })
  end

  def test_pdf_false_front_matter_opts_out
    refute PdfPages.wants_pdf?("/thoughts/", { "layout" => "page", "pdf" => false })
    assert PdfPages.wants_pdf?("/thoughts/", { "layout" => "page", "pdf" => nil })
  end
end
