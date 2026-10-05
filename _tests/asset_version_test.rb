# Behaviour tests for the asset_version filter: the cache-busting stamp for
# an asset must depend only on the asset's content, so two builds of an
# unchanged site produce byte-identical pages and only a real edit to the
# asset changes the stamp. Run with:
#   ruby _tests/asset_version_test.rb
require "minitest/autorun"
require "tmpdir"
require_relative "../_plugins/asset_version"

class AssetVersionTest < Minitest::Test
  def with_site
    Dir.mktmpdir do |dir|
      Dir.mkdir(File.join(dir, "assets"))
      File.write(File.join(dir, "assets", "a.css"), "body { color: red }")
      yield dir
    end
  end

  def test_same_content_gives_the_same_stamp_across_calls
    with_site do |dir|
      first = AssetVersion.version(dir, "/assets/a.css")
      second = AssetVersion.version(dir, "/assets/a.css")
      assert_equal first, second
    end
  end

  def test_stamp_is_short_lowercase_hex
    with_site do |dir|
      assert_match(/\A[0-9a-f]{8,16}\z/, AssetVersion.version(dir, "/assets/a.css"))
    end
  end

  def test_changing_the_asset_changes_the_stamp
    with_site do |dir|
      before = AssetVersion.version(dir, "/assets/a.css")
      File.write(File.join(dir, "assets", "a.css"), "body { color: blue }")
      refute_equal before, AssetVersion.version(dir, "/assets/a.css")
    end
  end

  def test_stamp_depends_on_content_not_on_clock_or_path
    with_site do |dir|
      File.write(File.join(dir, "assets", "b.css"), "body { color: red }")
      assert_equal AssetVersion.version(dir, "/assets/a.css"),
                   AssetVersion.version(dir, "/assets/b.css")
    end
  end

  def test_path_without_leading_slash_resolves_the_same_asset
    with_site do |dir|
      assert_equal AssetVersion.version(dir, "/assets/a.css"),
                   AssetVersion.version(dir, "assets/a.css")
    end
  end

  def test_missing_asset_gives_a_stable_stamp_rather_than_failing
    with_site do |dir|
      first = AssetVersion.version(dir, "/assets/missing.css")
      assert_kind_of String, first
      assert_match(/\A[0-9a-f]+\z/, first)
      assert_equal first, AssetVersion.version(dir, "/assets/missing.css")
    end
  end
end
