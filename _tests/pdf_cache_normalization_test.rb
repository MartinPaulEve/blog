# Behaviour tests for the PDF render cache key: head links that are invisible
# in print (webmention plumbing, identity rel=me, the human.json declaration)
# must not perturb the content hash, or a site-wide head tweak re-renders every
# PDF. Real content changes must still change the hash.
require "minitest/autorun"
require_relative "../_plugins/pdf_pages"

class PdfCacheNormalizationTest < Minitest::Test
  BASE = <<~HTML
    <html><head>
    <link rel="stylesheet" href="/assets/css/styles.css?v=123">
    </head><body><article><p>Hello.</p></article></body></html>
  HTML

  def with_head_line(line)
    BASE.sub("</head>", "#{line}\n</head>")
  end

  def test_human_json_link_does_not_change_the_hash
    with_link = with_head_line('<link rel="human-json" href="/human.json">')
    assert_equal PdfPages.content_hash(BASE), PdfPages.content_hash(with_link)
  end

  def test_webmention_and_me_links_do_not_change_the_hash
    with_links = with_head_line(
      '<link rel="webmention" href="https://webmention.io/eve.gd/webmention" />' \
      '<link rel="me" href="https://github.com/MartinPaulEve" />'
    )
    assert_equal PdfPages.content_hash(BASE), PdfPages.content_hash(with_links)
  end

  def test_footer_changes_do_not_change_the_hash
    with_old = BASE.sub("</body>", '<footer class="footer"><ul><li>old</li></ul></footer></body>')
    with_new = BASE.sub("</body>", '<footer class="footer"><ul><li>new link</li></ul></footer></body>')
    assert_equal PdfPages.content_hash(with_old), PdfPages.content_hash(with_new)
  end

  def test_body_content_changes_do_change_the_hash
    changed = BASE.sub("Hello.", "Goodbye.")
    refute_equal PdfPages.content_hash(BASE), PdfPages.content_hash(changed)
  end

  def test_print_css_changes_do_change_the_hash
    refute_equal PdfPages.content_hash(BASE, "a{}"), PdfPages.content_hash(BASE, "b{}")
  end
end
