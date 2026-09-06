# Behaviour tests for the repository-deposit (archivedAt) mapping: a post's
# front-matter `kcworks:` value must come through as a schema.org-ready
# archivedAt value — absent stays absent, one URL stays a scalar, several
# stay a list, and blank noise is dropped.
require "minitest/autorun"
require_relative "../_plugins/signposting"

class SignpostingArchivedAtTest < Minitest::Test
  RECORD = "https://works.hcommons.org/records/abc12-xyz34".freeze
  OTHER = "https://works.hcommons.org/records/def56-uvw78".freeze

  def test_absent_value_is_nil
    assert_nil Signposting.archived_at(nil)
  end

  def test_blank_value_is_nil
    assert_nil Signposting.archived_at("")
    assert_nil Signposting.archived_at("   ")
    assert_nil Signposting.archived_at([])
  end

  def test_single_url_stays_a_scalar
    assert_equal RECORD, Signposting.archived_at(RECORD)
  end

  def test_single_url_in_a_list_becomes_a_scalar
    assert_equal RECORD, Signposting.archived_at([RECORD])
  end

  def test_several_urls_stay_a_list
    assert_equal [RECORD, OTHER], Signposting.archived_at([RECORD, OTHER])
  end

  def test_blank_entries_are_dropped
    assert_equal RECORD, Signposting.archived_at(["", RECORD, nil])
  end

  def test_surrounding_whitespace_is_stripped
    assert_equal RECORD, Signposting.archived_at("  #{RECORD}  ")
  end
end

# Behaviour tests for the last_modified_at -> dateModified normalisation:
# absent and blank values stay absent; Date objects and ISO strings come
# through as YYYY-MM-DD; datetime strings are truncated to the date.
require "date"

class SignpostingModifiedDateTest < Minitest::Test
  def test_absent_and_blank_are_nil
    assert_nil Signposting.modified_date(nil)
    assert_nil Signposting.modified_date("")
    assert_nil Signposting.modified_date("   ")
  end

  def test_date_object_becomes_iso_string
    assert_equal "2026-09-06", Signposting.modified_date(Date.new(2026, 9, 6))
  end

  def test_iso_string_passes_through
    assert_equal "2026-09-06", Signposting.modified_date("2026-09-06")
  end

  def test_datetime_string_is_truncated_to_the_date
    assert_equal "2026-09-06", Signposting.modified_date("2026-09-06 20:28:53 +0100")
  end
end
