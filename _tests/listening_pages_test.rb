# Behaviour tests for the per-month listening log pages: plays come from
# the data file's "plays" list, months group newest-first, URLs and
# anchors derive from the month and timestamp, and the search index
# carries exactly what client-side search needs. Run with:
#   ruby _tests/listening_pages_test.rb
require "minitest/autorun"
require_relative "../_plugins/listening_pages"

class ListeningPagesTest < Minitest::Test
  def play(ts:, date:, track: "Atom Bomb", artist: "Fluke", album: nil, n: nil)
    entry = {
      "ts" => ts, "date" => date, "track" => track, "artist" => artist,
      "artist_url" => "https://www.last.fm/music/Fluke",
      "url" => "https://www.last.fm/music/Fluke/_/Atom+Bomb",
    }
    entry["album"] = album if album
    entry["n"] = n if n
    entry
  end

  def test_plays_come_from_the_data_file
    entry = play(ts: 1, date: "2026-10-04T14:09:08+01:00")
    assert_equal [entry], ListeningPages.plays("listening" => { "plays" => [entry] })
  end

  def test_no_data_file_means_no_plays
    assert_equal [], ListeningPages.plays({})
    assert_equal [], ListeningPages.plays("listening" => {})
    assert_equal [], ListeningPages.plays(nil)
  end

  def test_month_url
    assert_equal "/listening/2026-10/", ListeningPages.month_url("2026-10")
  end

  def test_anchor_is_the_timestamp
    assert_equal "s1791122948", ListeningPages.anchor(play(ts: 1791122948, date: "x"))
  end

  def test_group_by_month_keeps_months_and_entries_newest_first
    newest = play(ts: 3, date: "2026-10-04T14:09:08+01:00")
    late = play(ts: 2, date: "2026-09-30T09:00:00+01:00")
    early = play(ts: 1, date: "2026-09-01T09:00:00+01:00")
    groups = ListeningPages.group_by_month([newest, late, early])
    assert_equal [["2026-10", [newest]], ["2026-09", [late, early]]], groups
    assert_equal [], ListeningPages.group_by_month(nil)
  end

  def test_search_index_carries_what_the_client_renders
    entry = play(ts: 1791122948, date: "2026-10-04T14:09:08+01:00",
                 album: "The Second Bite", n: 3)
    indexed = ListeningPages.search_index([entry]).first
    assert_equal 1791122948, indexed["ts"]
    assert_equal "2026-10-04T14:09:08+01:00", indexed["d"]
    assert_equal "Atom Bomb", indexed["t"]
    assert_equal "Fluke", indexed["a"]
    assert_equal "The Second Bite", indexed["l"]
    assert_equal 3, indexed["n"]
    assert_equal "https://www.last.fm/music/Fluke/_/Atom+Bomb", indexed["u"]
    assert_equal "https://www.last.fm/music/Fluke", indexed["au"]
  end

  def test_search_index_omits_what_a_play_lacks
    indexed = ListeningPages.search_index([play(ts: 1, date: "2026-10-04T14:09:08+01:00")]).first
    refute indexed.key?("l")
    refute indexed.key?("n")
  end

  def test_search_index_of_nothing_is_empty
    assert_equal [], ListeningPages.search_index(nil)
  end
end
