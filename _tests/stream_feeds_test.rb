# Behaviour tests for the stream Atom feeds: an ActivityPages entry of
# any kind becomes a feed entry with a title, link and HTML body, and the
# feed itself is well-formed Atom with absolute links, the newest entry's
# time as its own, and everything escaped.
#   ruby _tests/stream_feeds_test.rb
require "minitest/autorun"
require "rexml/document"
require_relative "../_plugins/stream_feeds"

class StreamFeedsTest < Minitest::Test
  SITE = "https://eve.gd".freeze

  def post_entry
    ActivityPages.post_entry("title" => "A <post>", "url" => "/2026/10/15/a-post/",
                             "date" => "2026-10-15T00:00:00+01:00", "excerpt" => "Hello & welcome.")
  end

  def thought_entry(text = "A thought with https://example.org/x in it")
    ActivityPages.thought_entry("id" => "20261107080338", "date" => "2026-11-07T08:03:38+00:00",
                                "text" => text)
  end

  def listening_entry
    entries = ActivityPages.entries(plays: [
      { "ts" => 2, "date" => "2026-10-04T15:09:08+01:00", "track" => "B", "artist" => "Fluke",
        "url" => "https://www.last.fm/music/Fluke/_/B", "artist_url" => "https://www.last.fm/music/Fluke" },
      { "ts" => 1, "date" => "2026-10-04T15:01:00+01:00", "track" => "A", "artist" => "Fluke",
        "url" => "https://www.last.fm/music/Fluke/_/A", "artist_url" => "https://www.last.fm/music/Fluke", "n" => 2 },
    ])
    ActivityPages.display(entries)[0]
  end

  def test_post_feed_entry
    entry = StreamFeeds.entry_for(post_entry, SITE)
    assert_equal "A <post>", entry["title"]
    assert_equal "https://eve.gd/2026/10/15/a-post/", entry["url"]
    assert_equal "2026-10-15T00:00:00+01:00", entry["date"]
    assert_includes entry["html"], "Hello &amp; welcome."
  end

  def test_thought_feed_entry_titles_from_the_text_and_links_urls
    entry = StreamFeeds.entry_for(thought_entry, SITE)
    assert_equal "A thought with https://example.org/x in it", entry["title"]
    assert_equal "https://eve.gd/thoughts/2026-11/#t20261107080338", entry["url"]
    assert_includes entry["html"], '<a href="https://example.org/x">'
  end

  def test_long_thought_titles_are_shortened
    entry = StreamFeeds.entry_for(thought_entry("word " * 40), SITE)
    assert entry["title"].length < 100
    assert entry["title"].end_with?("…")
  end

  def test_til_feed_entry_is_marked_as_one
    entry = StreamFeeds.entry_for(thought_entry("TIL: that bees sleep"), SITE)
    assert entry["title"].start_with?("TIL"), entry["title"]
    assert_includes entry["title"], "Bees sleep"
    assert_equal "https://eve.gd/til/#t20261107080338", entry["url"]
  end

  def test_listening_feed_entry_lists_the_tracks
    entry = StreamFeeds.entry_for(listening_entry, SITE)
    assert_includes entry["title"], "3"
    assert_equal "https://eve.gd/listening/2026-10/#s2", entry["url"]
    assert_includes entry["html"], "B"
    assert_includes entry["html"], "A"
    assert_includes entry["html"], "Fluke"
  end

  def test_single_play_feed_entry_names_the_track
    entries = ActivityPages.entries(plays: [
      { "ts" => 1, "date" => "2026-10-04T15:01:00+01:00", "track" => "A", "artist" => "Fluke",
        "url" => "https://www.last.fm/music/Fluke/_/A", "artist_url" => "https://www.last.fm/music/Fluke" },
    ])
    entry = StreamFeeds.entry_for(ActivityPages.display(entries)[0], SITE)
    assert_includes entry["title"], "A"
    assert_includes entry["title"], "Fluke"
  end

  def feed(entries = [post_entry, thought_entry], **options)
    StreamFeeds.atom(title: "Activity & more", site_url: SITE, page_url: "/activity/",
                     author: "Martin Paul Eve",
                     entries: entries.map { |e| StreamFeeds.entry_for(e, SITE) }, **options)
  end

  def test_feed_is_well_formed_atom_with_absolute_links
    doc = REXML::Document.new(feed)
    root = doc.root
    assert_equal "feed", root.name
    assert_equal "http://www.w3.org/2005/Atom", root.namespace
    assert_equal "Activity & more", root.elements["title"].text
    assert_equal "https://eve.gd/activity/feed.atom", root.elements["link[@rel='self']"].attributes["href"]
    assert_equal "https://eve.gd/activity/", root.elements["link[@rel='alternate']"].attributes["href"]
    assert_equal "https://eve.gd/activity/", root.elements["id"].text
    assert_equal "Martin Paul Eve", root.elements["author/name"].text
    assert_equal 2, root.elements.to_a("entry").length
  end

  def test_feed_updated_is_the_newest_entry_time_and_entries_carry_theirs
    doc = REXML::Document.new(feed)
    assert_equal "2026-11-07T08:03:38+00:00", doc.root.elements["updated"].text
    entries = doc.root.elements.to_a("entry")
    assert_equal "2026-11-07T08:03:38+00:00", entries[0].elements["updated"].text
    assert_equal "https://eve.gd/thoughts/2026-11/#t20261107080338", entries[0].elements["id"].text
    assert_equal "https://eve.gd/thoughts/2026-11/#t20261107080338",
                 entries[0].elements["link"].attributes["href"]
    assert_equal "html", entries[0].elements["content"].attributes["type"]
    assert_equal "A <post>", entries[1].elements["title"].text
  end

  def test_feed_limits_the_entries
    doc = REXML::Document.new(feed(limit: 1))
    assert_equal 1, doc.root.elements.to_a("entry").length
  end

  def test_empty_feed_is_still_well_formed
    doc = REXML::Document.new(feed([]))
    assert_equal 0, doc.root.elements.to_a("entry").length
    refute_nil doc.root.elements["updated"].text
  end
end
