# Behaviour tests for the Last.fm build-output check: a failure sentinel left
# by fetch_lastfm.py must come out as an error message for the build log, a
# clean tree must stay silent, and a corrupt sentinel must still report the
# failure rather than crash the build. Run with:
#   ruby _tests/lastfm_check_test.rb
require "minitest/autorun"
require "fileutils"
require "json"
require "tmpdir"
require_relative "../_plugins/lastfm_check"

class LastfmCheckTest < Minitest::Test
  def with_root
    Dir.mktmpdir { |root| yield root }
  end

  def write_sentinel(root, body)
    FileUtils.mkdir_p(File.join(root, "_lastfm"))
    File.write(File.join(root, LastfmCheck::SENTINEL), body)
  end

  def test_no_sentinel_stays_silent
    with_root do |root|
      assert_nil LastfmCheck.error_message(root)
    end
  end

  def test_sentinel_yields_a_message_carrying_the_recorded_failure
    with_root do |root|
      write_sentinel(root, JSON.generate(
        "error" => "certificate verify failed",
        "at" => "2026-09-07T16:00:00+00:00"
      ))
      message = LastfmCheck.error_message(root)
      assert_includes message, "certificate verify failed"
      assert_includes message, "2026-09-07"
    end
  end

  def test_corrupt_sentinel_still_reports_a_failure
    with_root do |root|
      write_sentinel(root, "not json{")
      refute_nil LastfmCheck.error_message(root)
    end
  end
end
