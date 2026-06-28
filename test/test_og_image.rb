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
end
