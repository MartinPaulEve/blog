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
