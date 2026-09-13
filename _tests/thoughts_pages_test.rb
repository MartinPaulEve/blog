# Behaviour tests for the per-month thoughts pagination helpers: months
# group newest-first preserving entry order, URLs and titles derive from
# the month key, an entry's month derives from its compact id, and the
# search index carries exactly what client-side search needs. Run with:
#   ruby _tests/thoughts_pages_test.rb
require "minitest/autorun"
require_relative "../_plugins/thoughts_pages"

class ThoughtsPagesTest < Minitest::Test
  def thought(id:, date:, text: "hello", images: nil)
    entry = { "id" => id, "date" => date, "text" => text }
    entry["images"] = images if images
    entry
  end

  def test_month_of_uses_the_date_prefix
    entry = thought(id: "20120516182000", date: "2012-05-16T18:20:00+01:00")
    assert_equal "2012-05", ThoughtsPages.month_of(entry)
  end

  def test_month_of_id_derives_from_the_compact_timestamp
    assert_equal "2012-05", ThoughtsPages.month_of_id("20120516182000")
    assert_equal "2026-09", ThoughtsPages.month_of_id("20260912232746")
  end

  def test_month_url
    assert_equal "/thoughts/2012-05/", ThoughtsPages.month_url("2012-05")
  end

  def test_month_title_is_the_english_month_and_year
    assert_equal "May 2012", ThoughtsPages.month_title("2012-05")
    assert_equal "January 2026", ThoughtsPages.month_title("2026-01")
  end

  def test_group_by_month_keeps_months_and_entries_newest_first
    newest = thought(id: "20260901120000", date: "2026-09-01T12:00:00+01:00")
    late_may = thought(id: "20120530090000", date: "2012-05-30T09:00:00+01:00")
    early_may = thought(id: "20120501090000", date: "2012-05-01T09:00:00+01:00")
    groups = ThoughtsPages.group_by_month([newest, late_may, early_may])

    assert_equal [["2026-09", [newest]], ["2012-05", [late_may, early_may]]],
                 groups
  end

  def test_group_by_month_of_nothing_is_empty
    assert_equal [], ThoughtsPages.group_by_month([])
    assert_equal [], ThoughtsPages.group_by_month(nil)
  end

  def test_search_index_carries_id_date_and_untouched_text
    entry = thought(
      id: "20120516182000",
      date: "2012-05-16T18:20:00+01:00",
      text: "raw <b>text</b> stays raw\nwith newlines",
    )
    index = ThoughtsPages.search_index([entry])

    assert_equal 1, index.length
    assert_equal "20120516182000", index[0]["id"]
    assert_equal "2012-05-16T18:20:00+01:00", index[0]["d"]
    assert_equal "raw <b>text</b> stays raw\nwith newlines", index[0]["t"]
  end

  def test_search_index_includes_image_src_and_alt_pairs_only_when_present
    with_images = thought(
      id: "20120516182000",
      date: "2012-05-16T18:20:00+01:00",
      images: [
        { "src" => "/assets/thoughts/20120516182000-1.jpg", "alt" => "a cat" },
        { "src" => "/assets/thoughts/20120516182000-2.jpg" },
      ],
    )
    bare = thought(id: "20120601090000", date: "2012-06-01T09:00:00+01:00")
    index = ThoughtsPages.search_index([with_images, bare])

    assert_equal [["/assets/thoughts/20120516182000-1.jpg", "a cat"],
                  ["/assets/thoughts/20120516182000-2.jpg", ""]],
                 index[0]["i"]
    refute index[1].key?("i")
  end
end
