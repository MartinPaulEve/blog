# Behaviour tests for the image-credit linkify filter: the credit text in a
# post's front matter is displayed untouched apart from bare URLs becoming
# links that open in a new tab (matching the caption's title link), with
# everything HTML-escaped so a credit can never inject markup. Run with:
#   ruby _tests/image_credit_linkify_test.rb
require "minitest/autorun"
require_relative "../_plugins/thoughts"

class ImageCreditLinkifyTest < Minitest::Test
  CREDIT = "Gloria Mendoza / https://betterimagesofai.org / https://creativecommons.org/licenses/by/4.0/"

  def test_plain_credit_is_unchanged_apart_from_escaping
    assert_equal "Jane Doe &amp; Co", ThoughtsFilter.linkify_external("Jane Doe & Co")
  end

  def test_each_url_becomes_a_link_showing_the_address
    out = ThoughtsFilter.linkify_external(CREDIT)
    assert_match %r{<a href="https://betterimagesofai\.org"[^>]*>https://betterimagesofai\.org<}, out
    assert_match %r{<a href="https://creativecommons\.org/licenses/by/4\.0/"[^>]*>https://creativecommons\.org/licenses/by/4\.0/<}, out
  end

  def test_surrounding_text_is_preserved_in_order
    out = ThoughtsFilter.linkify_external(CREDIT)
    assert out.start_with?("Gloria Mendoza / <a ")
    assert_match %r{</a> / <a [^>]+>https://creativecommons}, out
    assert out.end_with?("</a>")
  end

  def test_links_open_in_a_new_tab_safely
    out = ThoughtsFilter.linkify_external("see https://example.org/x")
    assert_match %r{<a [^>]*target="_blank"}, out
    assert_match %r{<a [^>]*rel="noopener"}, out
  end

  def test_trailing_punctuation_stays_outside_the_link
    out = ThoughtsFilter.linkify_external("Library. https://example.org/items/1.")
    assert_includes out, 'href="https://example.org/items/1"'
    assert_includes out, "</a>."
  end

  def test_markup_in_the_credit_cannot_inject
    out = ThoughtsFilter.linkify_external('<img src=x onerror=alert(1)> https://example.org/')
    refute_includes out, "<img"
    assert_includes out, "&lt;img"
    assert_includes out, 'href="https://example.org/"'
  end

  def test_nil_credit_renders_empty
    assert_equal "", ThoughtsFilter.linkify_external(nil)
  end
end
