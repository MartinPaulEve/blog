# Unit tests for the pure OgImage builders. Run: ruby test/test_og_image.rb
require "minitest/autorun"
require_relative "../_plugins/og_image"

class TestOgImage < Minitest::Test
  def test_slug_from_post_url
    assert_equal "2026-06-23-harvestable", OgImage.slug("/2026/06/23/harvestable/")
  end

  def test_slug_from_page_url
    assert_equal "about", OgImage.slug("/about/")
  end

  def test_slug_for_apex_is_index
    assert_equal "index", OgImage.slug("/")
  end

  def test_slug_strips_host_and_index_and_html
    assert_equal "books", OgImage.slug("https://eve.gd/books/index.html")
    assert_equal "404", OgImage.slug("/404.html")
  end

  def test_scope_layout
    assert OgImage.scope_layout?("page")
    assert OgImage.scope_layout?("home")
    refute OgImage.scope_layout?("redirect")
    refute OgImage.scope_layout?(nil)
  end

  def test_button_label
    assert_equal "Read post", OgImage.button_label(true)
    assert_equal "Read more", OgImage.button_label(false)
  end

  def test_title_for_falls_back_to_site_title
    assert_equal "About", OgImage.title_for("About", "Martin Paul Eve")
    assert_equal "Martin Paul Eve", OgImage.title_for("", "Martin Paul Eve")
    assert_equal "Martin Paul Eve", OgImage.title_for(nil, "Martin Paul Eve")
  end

  def test_asset_url
    assert_equal "https://eve.gd/images/og/about.png",
                 OgImage.asset_url("https://eve.gd", "about")
    assert_equal "https://eve.gd/images/og/about.twitter.png",
                 OgImage.asset_url("https://eve.gd", "about", twitter: true)
  end

  def test_excerpt_strips_html_and_collapses_whitespace
    raw = "<p>Hello   <strong>there</strong>\n\nworld</p>"
    assert_equal "Hello there world", OgImage.excerpt_text(raw)
  end

  def test_excerpt_truncates_on_word_boundary_with_ellipsis
    raw = "one two three four five six seven eight nine ten eleven twelve"
    out = OgImage.excerpt_text(raw, 20)
    assert out.length <= 21, "truncated to ~limit plus ellipsis"
    assert out.end_with?("…")
    refute_includes out, "  "
  end

  def test_excerpt_blank
    assert_equal "", OgImage.excerpt_text(nil)
    assert_equal "", OgImage.excerpt_text("   ")
  end

  def test_data_uri_from_png_fixture
    require "tmpdir"
    Dir.mktmpdir do |d|
      path = File.join(d, "x.png")
      File.binwrite(path, "\x89PNG\r\n\x1a\nDATA")
      uri = OgImage.data_uri(path)
      assert uri.start_with?("data:image/png;base64,")
      assert_equal "\x89PNG\r\n\x1a\nDATA".b,
                   Base64.decode64(uri.sub("data:image/png;base64,", "")).b
    end
  end

  def test_data_uri_missing_file_is_nil
    assert_nil OgImage.data_uri("/no/such/file.png")
    assert_nil OgImage.data_uri(nil)
  end

  def test_html_escape
    assert_equal "a &amp; b &lt;c&gt; &quot;d&quot;", OgImage.html_escape('a & b <c> "d"')
  end

  def png_bytes(w, h)
    "\x89PNG\r\n\x1a\n".b + [13].pack("N") + "IHDR".b + [w].pack("N") + [h].pack("N") + ("\x00" * 5).b
  end

  def jpeg_bytes(w, h)
    "\xFF\xD8".b + "\xFF\xC0".b + [17].pack("n") + "\x08".b + [h].pack("n") + [w].pack("n") + ("\x00" * 10).b
  end

  def test_image_dimensions_png
    require "tmpdir"
    Dir.mktmpdir do |d|
      p = File.join(d, "b.png"); File.binwrite(p, png_bytes(1902, 353))
      assert_equal [1902, 353], OgImage.image_dimensions(p)
    end
  end

  def test_image_dimensions_jpeg
    require "tmpdir"
    Dir.mktmpdir do |d|
      p = File.join(d, "a.jpg"); File.binwrite(p, jpeg_bytes(945, 630))
      assert_equal [945, 630], OgImage.image_dimensions(p)
    end
  end

  def test_image_dimensions_unknown_is_nil
    require "tmpdir"
    Dir.mktmpdir do |d|
      p = File.join(d, "x.bin"); File.binwrite(p, "not an image")
      assert_nil OgImage.image_dimensions(p)
    end
    assert_nil OgImage.image_dimensions("/no/such/file")
  end

  def test_wide_banner_detection
    require "tmpdir"
    Dir.mktmpdir do |d|
      wide = File.join(d, "w.png"); File.binwrite(wide, png_bytes(1902, 353))
      ok = File.join(d, "o.png"); File.binwrite(ok, png_bytes(945, 630))
      assert OgImage.wide_banner?(wide)
      refute OgImage.wide_banner?(ok)
      refute OgImage.wide_banner?("/no/file.png") # unknown => not treated as banner
    end
  end

  def render(image_uri: "data:image/png;base64,AAA", fonts: {})
    OgImage.render_html(pill: OgImage::SITE_AUTHOR, title: "My <Post>",
                        snippet: "A snippet & more", button: "Read post",
                        image_uri: image_uri, fonts: fonts)
  end

  def test_render_html_contains_core_content_escaped
    html = render
    assert_includes html, "eve.gd: Martin Paul Eve"
    assert_includes html, "My &lt;Post&gt;"          # title escaped
    assert_includes html, "A snippet &amp; more"      # snippet escaped
    assert_includes html, "Read post"
    assert_includes html, "1200px"
    assert_includes html, "#b3122a"
  end

  def test_render_html_includes_image_card_when_image_present
    html = render(image_uri: "data:image/png;base64,ZZZ")
    assert_includes html, "data:image/png;base64,ZZZ"
    assert_includes html, 'class="right"'
  end

  def test_render_html_omits_image_card_when_absent
    html = render(image_uri: nil)
    refute_includes html, 'class="right"'
    assert_includes html, "og-full"                   # full-width modifier
  end

  def test_render_html_embeds_fonts_when_provided
    html = render(fonts: { fraunces: "data:font/ttf;base64,FFF",
                           mono_regular: "data:font/ttf;base64,MMM",
                           mono_semibold: "data:font/ttf;base64,SSS" })
    assert_includes html, "@font-face"
    assert_includes html, "data:font/ttf;base64,FFF"
    assert_includes html, "Fraunces"
  end
end
