# Behaviour tests for blockquote attributions: a blockquote containing a
# <cite> must pull in the attribution stylesheet exactly once, ahead of the
# first such blockquote; everything else must pass through byte-identical so
# no existing PDF's cache key moves. Run with:
#   ruby _tests/quote_attributions_test.rb
require "minitest/autorun"
require_relative "../_plugins/quote_attributions"

class QuoteAttributionsTest < Minitest::Test
  CITED = "<blockquote>\n<p>Words.\n<cite>Gowers, 2000, 1</cite></p>\n</blockquote>"

  def test_content_without_a_cited_blockquote_is_returned_byte_identical
    html = "<p>intro</p>\n<blockquote>\n<p>Plain quote.</p>\n</blockquote>"
    assert_equal html, QuoteAttributions.transform(html)
  end

  def test_a_cite_outside_any_blockquote_does_not_trigger_the_stylesheet
    html = "<p>See <cite>Gowers</cite> for more.</p>\n<blockquote>\n<p>Quote.</p>\n</blockquote>"
    assert_equal html, QuoteAttributions.transform(html)
  end

  def test_a_cite_after_a_closed_blockquote_does_not_trigger_the_stylesheet
    html = "<blockquote>\n<p>Quote.</p>\n</blockquote>\n<p><cite>Later</cite></p>"
    assert_equal html, QuoteAttributions.transform(html)
  end

  def test_a_cited_blockquote_pulls_in_the_stylesheet_before_itself
    out = QuoteAttributions.transform("<p>intro</p>\n#{CITED}\n<p>tail</p>")
    assert_includes out, QuoteAttributions::STYLESHEET
    assert out.index(QuoteAttributions::STYLESHEET) < out.index("<blockquote"),
           "stylesheet link must precede the first cited blockquote"
    assert out.index(QuoteAttributions::STYLESHEET) > out.index("<p>intro</p>"),
           "stylesheet link rides with the quote, not at the top"
  end

  def test_the_quote_markup_itself_is_preserved
    out = QuoteAttributions.transform(CITED)
    assert_includes out, CITED
  end

  def test_the_stylesheet_is_linked_once_for_many_cited_quotes
    two = "<blockquote>\n<p>More.</p>\n<p><cite>Eve, 2026</cite></p>\n</blockquote>"
    out = QuoteAttributions.transform("#{CITED}\n<p>between</p>\n#{two}")
    assert_equal 1, out.scan(QuoteAttributions::STYLESHEET).size
  end

  def test_the_link_lands_before_the_first_cited_quote_not_an_earlier_plain_one
    plain = "<blockquote>\n<p>Plain.</p>\n</blockquote>"
    out = QuoteAttributions.transform("#{plain}\n<p>x</p>\n#{CITED}")
    assert out.index(QuoteAttributions::STYLESHEET) > out.index(plain)
  end

  def test_a_callout_blockquote_with_a_cite_also_counts
    html = "<blockquote class=\"callout\">\n<p>Big.</p>\n<p><cite>Someone</cite></p>\n</blockquote>"
    assert_includes QuoteAttributions.transform(html), QuoteAttributions::STYLESHEET
  end

  def test_the_link_is_a_stylesheet_link_element
    out = QuoteAttributions.transform(CITED)
    assert_match(%r{<link rel="stylesheet" href="#{Regexp.escape(QuoteAttributions::STYLESHEET)}">}, out)
  end
end
