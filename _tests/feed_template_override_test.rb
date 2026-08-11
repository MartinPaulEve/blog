# Behaviour tests for FeedTemplateOverride. These check what the override
# resolves to — an existing, image.feature-aware template inside the repo —
# not how it is wired into jekyll-feed, so the hook mechanism can change
# freely as long as builds keep using the repo template.
require "minitest/autorun"
require_relative "../_plugins/feed_template_override"

class FeedTemplateOverrideTest < Minitest::Test
  def test_template_path_points_at_repo_copy
    path = FeedTemplateOverride.template_path

    assert path.end_with?(File.join("_includes", "jekyll-feed", "feed.xml")),
           "expected repo template path, got #{path}"
    assert File.file?(path), "template should exist at #{path}"
  end

  def test_template_resolves_feature_key_not_raw_image_hash
    content = File.read(FeedTemplateOverride.template_path)

    assert_includes content, "post.image.feature"
    refute_includes content, "post.image.path"
  end

  def test_feed_source_path_returns_template_path
    generator = Class.new { include FeedTemplateOverride }.new

    assert_equal FeedTemplateOverride.template_path, generator.feed_source_path
  end
end
