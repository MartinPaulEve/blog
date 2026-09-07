# Behaviour tests for content-warning disclosures: a heading carrying a
# [content warning: ...] marker must collapse its section behind a
# clickable summary that shows the heading and the warning text; everything
# else must pass through byte-identical. Run with:
#   ruby _tests/content_warnings_test.rb
require "minitest/autorun"
require_relative "../_plugins/content_warnings"

class ContentWarningsTest < Minitest::Test
  MARKED = '<h3 id="severe">Severe bowel dysmotility (~2019-) ' \
           "[content warning: discusses bowels]</h3>"

  def test_unmarked_content_is_returned_byte_identical
    html = %(<h3 id="a">Plain heading</h3>\n<p>Some [bracketed] text.</p>)
    assert_equal html, ContentWarnings.transform(html)
  end

  def test_marked_section_collapses_behind_a_summary
    out = ContentWarnings.transform("#{MARKED}\n<p>One.</p>\n<p>Two.</p>")
    assert_includes out, '<details class="content-warning">'
    assert_includes out,
                    '<h3 id="severe">Severe bowel dysmotility (~2019-)</h3>'
    refute_includes out, "[content warning:"
    assert_includes out, "Content warning: discusses bowels"
    assert out.index("<p>One.</p>") > out.index("<summary>"),
           "section body must sit inside the details"
    assert out.index("</details>") > out.index("<p>Two.</p>")
  end

  def test_section_ends_at_the_next_heading_of_the_same_level
    out = ContentWarnings.transform(
      "#{MARKED}\n<p>warned</p>\n<h3 id=\"n\">Next</h3>\n<p>open</p>")
    closed = out.index("</details>")
    assert out.index('<h3 id="n">Next</h3>') > closed
    assert out.index("<p>open</p>") > closed
  end

  def test_section_ends_at_a_higher_level_heading
    out = ContentWarnings.transform(
      "#{MARKED}\n<p>warned</p>\n<h2 id=\"big\">Chapter</h2>\n<p>open</p>")
    assert out.index('<h2 id="big">Chapter</h2>') > out.index("</details>")
  end

  def test_sub_headings_stay_inside_the_section
    out = ContentWarnings.transform(
      "#{MARKED}\n<p>a</p>\n<h4 id=\"sub\">Detail</h4>\n<p>b</p>")
    assert out.index('<h4 id="sub">Detail</h4>') < out.index("</details>")
    assert out.index("<p>b</p>") < out.index("</details>")
  end

  def test_marked_section_at_the_end_runs_to_the_end
    out = ContentWarnings.transform("<p>intro</p>\n#{MARKED}\n<p>tail</p>")
    assert out.index("<p>tail</p>") < out.index("</details>")
    assert out.index("<p>intro</p>") < out.index("<details")
  end

  def test_multiple_sections_each_collapse
    two = '<h3 id="other">Other section [Content Warning: also marked]</h3>'
    out = ContentWarnings.transform(
      "#{MARKED}\n<p>one</p>\n#{two}\n<p>two</p>")
    assert_equal 2, out.scan('<details class="content-warning">').size
    assert_includes out, "Content warning: also marked"
  end

  def test_stylesheet_link_is_injected_once_before_the_first_details
    two = '<h3 id="other">Other [content warning: x]</h3>'
    out = ContentWarnings.transform("#{MARKED}\n<p>a</p>\n#{two}\n<p>b</p>")
    links = out.scan(ContentWarnings::STYLESHEET).size
    assert_equal 1, links
    assert out.index(ContentWarnings::STYLESHEET) < out.index("<details")
  end

  def test_toc_labels_lose_the_marker
    toc = '<ul id="markdown-toc"><li><a href="#severe" ' \
          'id="markdown-toc-severe">Severe bowel dysmotility (~2019-) ' \
          "[content warning: discusses bowels]</a></li></ul>"
    out = ContentWarnings.transform("#{toc}\n#{MARKED}\n<p>x</p>")
    assert_includes out, ">Severe bowel dysmotility (~2019-)</a>"
    refute_includes out, "[content warning:"
  end
end
