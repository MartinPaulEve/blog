# Behaviour tests for the local modification to the vendored ActivityPub
# plugin: the site's static .well-known/webfinger (which aliases the domain
# to @mpe@hcommons.social) must win over the plugin's generated document, so
# webfinger generation is skipped exactly when the source file exists.
require "minitest/autorun"
require "tmpdir"
require "fileutils"
require_relative "../_plugins/activitypub_static"

class ActivityPubSummaryTest < Minitest::Test
  RenderedExcerpt = Struct.new(:output)

  def test_explicit_summary_property_wins
    data = { "description" => "A summary.", "excerpt" => "ignored" }
    assert_equal "A summary.", ActivityPubStaticLocal.summary_from(data, "description")
  end

  def test_plain_string_excerpt_is_returned_as_is
    data = { "excerpt" => "String excerpt." }
    assert_equal "String excerpt.", ActivityPubStaticLocal.summary_from(data, "description")
  end

  def test_rendered_excerpt_object_yields_its_output
    data = { "excerpt" => RenderedExcerpt.new("<p>Rendered.</p>") }
    assert_equal "<p>Rendered.</p>", ActivityPubStaticLocal.summary_from(data, "description")
  end

  def test_no_summary_and_no_excerpt_is_nil
    assert_nil ActivityPubStaticLocal.summary_from({}, "description")
  end
end

class ActivityPubAlsoKnownAsTest < Minitest::Test
  def test_configured_identities_are_returned
    config = { "activitypub" => { "also_known_as" => ["https://hcommons.social/users/mpe"] } }
    assert_equal ["https://hcommons.social/users/mpe"],
                 ActivityPubStaticLocal.also_known_as(config)
  end

  def test_absent_config_yields_nil
    assert_nil ActivityPubStaticLocal.also_known_as({})
  end

  def test_empty_list_yields_nil
    config = { "activitypub" => { "also_known_as" => [] } }
    assert_nil ActivityPubStaticLocal.also_known_as(config)
  end
end

class ActivityPubWebfingerGuardTest < Minitest::Test
  def test_skips_when_source_webfinger_exists
    Dir.mktmpdir do |source|
      FileUtils.mkdir_p(File.join(source, ".well-known"))
      File.write(File.join(source, ".well-known", "webfinger"), "{}")
      assert ActivityPubStaticLocal.skip_webfinger?(source)
    end
  end

  def test_generates_when_source_webfinger_absent
    Dir.mktmpdir do |source|
      refute ActivityPubStaticLocal.skip_webfinger?(source)
    end
  end
end
