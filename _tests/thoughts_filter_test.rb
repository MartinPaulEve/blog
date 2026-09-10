# Behaviour tests for the short-thought linkify filter: raw text must be
# HTML-escaped (the writing is stored untouched and must never be
# interpreted), bare URLs become links with trailing punctuation left
# outside, and newlines survive as <br>. Run with:
#   ruby _tests/thoughts_filter_test.rb
require "minitest/autorun"
require_relative "../_plugins/thoughts"

class ThoughtsFilterTest < Minitest::Test
  def test_plain_text_is_escaped
    assert_equal "a &lt;b&gt; &amp; c", ThoughtsFilter.linkify("a <b> & c")
  end

  def test_urls_become_links
    out = ThoughtsFilter.linkify("see https://example.org/x now")
    assert_includes out,
                    '<a href="https://example.org/x">https://example.org/x</a>'
    assert out.start_with?("see ")
    assert out.end_with?(" now")
  end

  def test_trailing_punctuation_stays_outside_the_link
    out = ThoughtsFilter.linkify("go to https://example.org/x.")
    assert_includes out, "</a>."
    refute_includes out, "x.</a>"
  end

  def test_unbalanced_closing_paren_stays_outside
    out = ThoughtsFilter.linkify("(see https://example.org/x)")
    assert_includes out, "</a>)"
  end

  def test_newlines_become_breaks
    out = ThoughtsFilter.linkify("one\ntwo")
    assert_includes out, "<br"
    assert_includes out, "one"
    assert_includes out, "two"
  end

  def test_markup_in_the_text_cannot_inject
    out = ThoughtsFilter.linkify("<script>x</script> not code")
    refute_includes out, "<script>"
    assert_includes out, "&lt;script&gt;"
  end

  def test_ampersands_in_urls_are_escaped_in_output
    out = ThoughtsFilter.linkify("https://example.org/x?a=1&b=2")
    assert_includes out, 'href="https://example.org/x?a=1&amp;b=2"'
  end
end
