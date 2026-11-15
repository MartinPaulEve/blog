# Behaviour tests for callout quotations: a blockquote carrying the
# "callout" class must pull in the callout stylesheet exactly once, ahead of
# the first callout; everything else must pass through byte-identical so no
# existing PDF's cache key moves. Run with:
#   ruby _tests/callouts_test.rb
require "minitest/autorun"
require_relative "../_plugins/callouts"

class CalloutsTest < Minitest::Test
  CALLOUT = "<blockquote class=\"callout\">\n<p>Big words.</p>\n</blockquote>"

  def test_content_without_callouts_is_returned_byte_identical
    html = "<p>intro</p>\n<blockquote>\n<p>Ordinary quote.</p>\n</blockquote>"
    assert_equal html, Callouts.transform(html)
  end

  def test_the_word_callout_in_prose_does_not_trigger_the_stylesheet
    html = "<p>I like a good callout now and then.</p>"
    assert_equal html, Callouts.transform(html)
  end

  def test_a_callout_class_on_another_element_does_not_trigger_it
    html = '<p class="callout">not a quote</p>'
    assert_equal html, Callouts.transform(html)
  end

  def test_callout_blockquote_pulls_in_the_stylesheet_before_itself
    out = Callouts.transform("<p>intro</p>\n#{CALLOUT}\n<p>tail</p>")
    assert_includes out, Callouts::STYLESHEET
    assert out.index(Callouts::STYLESHEET) < out.index("<blockquote"),
           "stylesheet link must precede the first callout"
    assert out.index(Callouts::STYLESHEET) > out.index("<p>intro</p>"),
           "stylesheet link rides with the callout, not at the top"
  end

  def test_the_quote_markup_itself_is_preserved
    out = Callouts.transform(CALLOUT)
    assert_includes out, CALLOUT
  end

  def test_the_stylesheet_is_linked_once_for_many_callouts
    two = "<blockquote class=\"callout\">\n<p>Again.</p>\n</blockquote>"
    out = Callouts.transform("#{CALLOUT}\n<p>between</p>\n#{two}")
    assert_equal 1, out.scan(Callouts::STYLESHEET).size
    assert_equal 2, out.scan('<blockquote class="callout">').size
  end

  def test_callout_among_other_classes_still_counts
    html = "<blockquote class=\"wide callout\">\n<p>x</p>\n</blockquote>"
    out = Callouts.transform(html)
    assert_includes out, Callouts::STYLESHEET
  end

  def test_a_class_merely_containing_the_word_does_not_count
    html = "<blockquote class=\"callouts-list\">\n<p>x</p>\n</blockquote>"
    assert_equal html, Callouts.transform(html)
  end

  def test_the_link_is_a_stylesheet_link_element
    out = Callouts.transform(CALLOUT)
    assert_match(%r{<link rel="stylesheet" href="#{Regexp.escape(Callouts::STYLESHEET)}">},
                 out)
  end
end
