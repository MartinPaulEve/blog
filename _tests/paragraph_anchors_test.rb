# Behaviour tests for paragraph/heading anchors: every <p> and <h1>-<h6> in a
# post must end up with an id and a trailing anchor link pointing at it. Ids
# derive from the element's text so they survive rebuilds unchanged; existing
# ids (kramdown's heading ids) are kept. Run with:
#   ruby _tests/paragraph_anchors_test.rb
require "minitest/autorun"
require_relative "../_plugins/paragraph_anchors"

class ParagraphAnchorsTest < Minitest::Test
  ANCHOR = %r{<a class="#{ParagraphAnchors::ANCHOR_CLASS}" href="#([^"]+)"[^>]*></a>}

  def anchors(html)
    html.scan(ANCHOR).flatten
  end

  def test_a_paragraph_gains_an_id_and_a_matching_anchor
    out = ParagraphAnchors.transform("<p>Hello world.</p>")
    assert_match(/<p id="([a-z0-9-]+)">Hello world\.<a class="anchor-link" href="#\1"[^>]*><\/a><\/p>/, out)
  end

  def test_the_anchor_sits_after_the_text_so_the_first_letter_is_untouched
    out = ParagraphAnchors.transform("<p>Lorem ipsum.</p>")
    assert_match(/<p[^>]*>Lorem ipsum\.<a /, out)
  end

  def test_ids_are_stable_across_calls_and_for_identical_text
    a = ParagraphAnchors.transform("<p>Same text.</p>")
    b = ParagraphAnchors.transform("<p>Same text.</p>")
    assert_equal a, b
  end

  def test_different_text_gives_different_ids
    a = anchors(ParagraphAnchors.transform("<p>One.</p>")).first
    b = anchors(ParagraphAnchors.transform("<p>Two.</p>")).first
    refute_equal a, b
  end

  def test_id_depends_on_text_not_on_surrounding_markup_or_position
    alone = anchors(ParagraphAnchors.transform("<p>Steady.</p>")).first
    later = anchors(ParagraphAnchors.transform(
      "<p>Intro.</p>\n<h2 id=\"x\">H</h2>\n<p>Steady.</p>")).last
    assert_equal alone, later
  end

  def test_inline_markup_inside_the_paragraph_does_not_change_the_id
    plain = anchors(ParagraphAnchors.transform("<p>Some bold words.</p>")).first
    marked = anchors(ParagraphAnchors.transform("<p>Some <strong>bold</strong> words.</p>")).first
    assert_equal plain, marked
  end

  def test_whitespace_differences_do_not_change_the_id
    a = anchors(ParagraphAnchors.transform("<p>Two  words\nhere.</p>")).first
    b = anchors(ParagraphAnchors.transform("<p>Two words here.</p>")).first
    assert_equal a, b
  end

  def test_an_existing_paragraph_id_is_kept_and_linked
    out = ParagraphAnchors.transform('<p id="keep-me">Text.</p>')
    assert_includes out, '<p id="keep-me">Text.<a class="anchor-link" href="#keep-me"'
    assert_equal 1, out.scan(/ id="/).size
  end

  def test_other_paragraph_attributes_are_preserved
    out = ParagraphAnchors.transform('<p class="note">Text.</p>')
    assert_match(/<p class="note" id="[a-z0-9-]+">Text\.<a /, out)
  end

  def test_a_heading_with_an_id_gets_an_anchor_to_that_id
    out = ParagraphAnchors.transform('<h2 id="my-heading">My heading</h2>')
    assert_includes out,
                    '<h2 id="my-heading">My heading<a class="anchor-link" href="#my-heading"'
    assert out.end_with?("</a></h2>")
  end

  def test_a_heading_without_an_id_gets_a_generated_one
    out = ParagraphAnchors.transform("<h3>Bare heading</h3>")
    assert_match(%r{<h3 id="([a-z0-9-]+)">Bare heading<a class="anchor-link" href="#\1"}, out)
  end

  def test_every_heading_level_is_handled
    (1..6).each do |n|
      out = ParagraphAnchors.transform("<h#{n} id=\"h\">T</h#{n}>")
      assert_equal ["h"], anchors(out), "h#{n} should carry an anchor"
    end
  end

  def test_duplicate_paragraphs_get_distinct_ids_deterministically
    html = "<p>Repeat.</p>\n<p>Repeat.</p>\n<p>Repeat.</p>"
    ids = anchors(ParagraphAnchors.transform(html))
    assert_equal 3, ids.uniq.size
    assert_equal ids, anchors(ParagraphAnchors.transform(html))
  end

  def test_generated_ids_avoid_ids_already_in_the_document
    out = ParagraphAnchors.transform("<p>Repeat.</p>\n<p id=\"dup\">x</p>\n<p>Repeat.</p>")
    ids = out.scan(/ id="([^"]+)"/).flatten
    assert_equal ids.size, ids.uniq.size
  end

  def test_image_only_paragraphs_with_different_sources_get_different_ids
    a = anchors(ParagraphAnchors.transform('<p><img src="/a.png" alt=""></p>')).first
    b = anchors(ParagraphAnchors.transform('<p><img src="/b.png" alt=""></p>')).first
    refute_equal a, b
  end

  def test_anchors_are_accessible_links
    out = ParagraphAnchors.transform("<p>Text.</p>\n<h2 id=\"h\">Head</h2>")
    assert_match(/<a class="anchor-link" href="#[^"]+" aria-label="[^"]*paragraph[^"]*"/, out)
    assert_match(/<a class="anchor-link" href="#h" aria-label="[^"]*heading[^"]*"/, out)
  end

  def test_ids_are_url_fragment_safe
    out = ParagraphAnchors.transform("<p>Ünïcödé & symbols!</p>\n<h2>Spaced out?</h2>")
    out.scan(/ id="([^"]+)"/).flatten.each do |id|
      assert_match(/\A[a-z][a-z0-9-]*\z/, id)
    end
  end

  def test_content_without_paragraphs_or_headings_is_unchanged
    html = "<ul><li>one</li></ul>\n<pre><code>&lt;p&gt;not a p&lt;/p&gt;</code></pre>"
    assert_equal html, ParagraphAnchors.transform(html)
  end

  def test_pre_and_param_tags_are_not_mistaken_for_paragraphs
    html = "<pre>code</pre><param name=\"x\" value=\"y\">"
    assert_equal html, ParagraphAnchors.transform(html)
  end

  def test_empty_input_is_returned_as_is
    assert_equal "", ParagraphAnchors.transform("")
  end

  def test_paragraphs_inside_blockquotes_and_lists_are_anchored
    out = ParagraphAnchors.transform(
      "<blockquote>\n<p>Quoted.</p>\n</blockquote>\n<ul>\n<li><p>Item.</p></li>\n</ul>")
    assert_equal 2, anchors(out).size
  end

  def test_headings_inside_a_summary_are_anchored_without_breaking_the_markup
    html = "<details class=\"content-warning\">\n<summary><h3 id=\"s\">Title</h3> " \
           "<span class=\"cw-label\">Content warning: x</span></summary>\n</details>"
    out = ParagraphAnchors.transform(html)
    assert_includes out, '<h3 id="s">Title<a class="anchor-link" href="#s"'
    assert_includes out, '</a></h3> <span class="cw-label">'
  end
end
