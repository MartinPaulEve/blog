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

  def test_content_hash_asset_stamps_do_not_change_the_hash
    with_hex = BASE.sub("?v=123", "?v=3fa9c0de12")
    assert_equal PdfPages.content_hash(BASE), PdfPages.content_hash(with_hex)
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

  def test_activitypub_alternate_link_does_not_change_the_hash
    with_link = with_head_line(
      '<link rel="alternate" type="application/activity+json" ' \
      'href="https://eve.gd/activitypub/posts/some-post.jsonld">'
    )
    assert_equal PdfPages.content_hash(BASE), PdfPages.content_hash(with_link)
  end

  def test_site_header_changes_do_not_change_the_hash
    with_old = BASE.sub(
      "<body>",
      '<body><header class="header"><a href="mailto:martin@eve.gd">Contact</a></header>'
    )
    with_new = BASE.sub(
      "<body>",
      '<body><header class="header"><a href="/accounts/">Contact</a></header>'
    )
    assert_equal PdfPages.content_hash(with_old), PdfPages.content_hash(with_new)
    assert_equal PdfPages.content_hash(BASE), PdfPages.content_hash(with_new)
  end

  def test_body_content_changes_do_change_the_hash
    changed = BASE.sub("Hello.", "Goodbye.")
    refute_equal PdfPages.content_hash(BASE), PdfPages.content_hash(changed)
  end

  def test_print_css_changes_do_change_the_hash
    refute_equal PdfPages.content_hash(BASE, "a{}"), PdfPages.content_hash(BASE, "b{}")
  end
end

class PdfCacheAnchorNormalizationTest < Minitest::Test
  # Paragraph/heading anchors (_plugins/paragraph_anchors.rb) are hidden in
  # print, so neither their markup, their generated ids nor their assets may
  # move a PDF's cache key.
  PLAIN = <<~HTML
    <html><head>
    <link rel="stylesheet" href="/assets/css/blog-post.css?v=1">
    </head><body><article>
    <h2 id="intro">Intro</h2>
    <p>Hello.</p>
    <p class="note">Aside.</p>
    </article></body></html>
  HTML

  ANCHORED = <<~HTML
    <html><head>
    <link rel="stylesheet" href="/assets/css/blog-post.css?v=1">
    <link rel="stylesheet" href="/assets/css/anchors.css?v=abc123">
    </head><body><article>
    <h2 id="intro">Intro<a class="anchor-link" href="#intro" aria-label="Link to this heading"></a></h2>
    <p id="p-3f9a1c2b7d">Hello.<a class="anchor-link" href="#p-3f9a1c2b7d" aria-label="Link to this paragraph"></a></p>
    <p class="note" id="p-00ff00ff00-2">Aside.<a class="anchor-link" href="#p-00ff00ff00-2" aria-label="Link to this paragraph"></a></p>
    <script src="/assets/js/anchors.js?v=abc123"></script>
    </article></body></html>
  HTML

  def test_anchor_markup_ids_and_assets_do_not_change_the_hash
    assert_equal PdfPages.content_hash(PLAIN), PdfPages.content_hash(ANCHORED)
  end

  def test_generated_heading_ids_do_not_change_the_hash
    bare = PLAIN.sub('<h2 id="intro">', "<h2>")
    generated = PLAIN.sub('<h2 id="intro">', '<h2 id="h-9a8b7c6d5e">')
    assert_equal PdfPages.content_hash(bare), PdfPages.content_hash(generated)
  end

  def test_authored_ids_still_count_as_content
    changed = PLAIN.sub('id="intro"', 'id="introduction"')
    refute_equal PdfPages.content_hash(PLAIN), PdfPages.content_hash(changed)
  end

  def test_anchored_text_changes_still_change_the_hash
    changed = ANCHORED.sub("Hello.", "Goodbye.")
    refute_equal PdfPages.content_hash(ANCHORED), PdfPages.content_hash(changed)
  end
end
