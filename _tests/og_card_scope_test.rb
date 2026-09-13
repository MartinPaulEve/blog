# Behaviour tests for OG card scoping: cards render for the main content
# layouts unless a page opts out with `og_card: false` front matter (used
# by the generated per-month thoughts archive, where 199 near-identical
# cards would be waste). Run with:
#   ruby _tests/og_card_scope_test.rb
require "minitest/autorun"
require_relative "../_plugins/og_image"

class OgCardScopeTest < Minitest::Test
  def test_scope_layouts_want_cards_by_default
    assert OgImage.wants_card?("page", {})
    assert OgImage.wants_card?("home", {})
    assert OgImage.wants_card?("category", {})
  end

  def test_og_card_false_opts_a_page_out
    refute OgImage.wants_card?("page", { "og_card" => false })
  end

  def test_layouts_outside_the_scope_never_want_cards
    refute OgImage.wants_card?("post", {})
    refute OgImage.wants_card?(nil, {})
  end
end
