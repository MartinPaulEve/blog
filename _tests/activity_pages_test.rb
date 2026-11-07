# Behaviour tests for the /activity/ log: entries of every kind normalise
# to one shape, sort newest first, group by month, fold runs of plays into
# one listening entry for display, and index for client-side search.
#   ruby _tests/activity_pages_test.rb
require "minitest/autorun"
require_relative "../_plugins/activity_pages"

class ActivityPagesTest < Minitest::Test
  def post(title: "A post", url: "/2026/10/15/a-post/", date: "2026-10-15T00:00:00+01:00",
           excerpt: "First *paragraph* here.")
    { "title" => title, "url" => url, "date" => date, "excerpt" => excerpt }
  end

  def thought(id: "20261107080338", date: "2026-11-07T08:03:38.882953+00:00",
              text: "hello there", images: nil, bluesky: nil)
    entry = { "id" => id, "date" => date, "text" => text }
    entry["images"] = images if images
    entry["bluesky"] = bluesky if bluesky
    entry
  end

  def play(ts: 1791122948, date: "2026-10-04T15:09:08+01:00", track: "Bullet",
           artist: "Fluke", album: nil, n: nil)
    entry = { "ts" => ts, "date" => date, "track" => track, "artist" => artist,
              "artist_url" => "https://www.last.fm/music/Fluke",
              "url" => "https://www.last.fm/music/Fluke/_/Bullet" }
    entry["album"] = album if album
    entry["n"] = n if n
    entry
  end

  def kinds(entries)
    entries.map { |e| e["kind"] }
  end

  # --- normalising -----------------------------------------------------

  def test_epoch_handles_iso_strings_with_fractions_and_time_objects
    expected = Time.utc(2026, 11, 7, 8, 3, 38).to_i
    assert_equal expected, ActivityPages.epoch("2026-11-07T08:03:38.882953+00:00")
    assert_equal expected, ActivityPages.epoch(Time.at(expected))
  end

  def test_post_entry
    entry = ActivityPages.post_entry(post)
    assert_equal "post", entry["kind"]
    assert_equal "A post", entry["title"]
    assert_equal "/2026/10/15/a-post/", entry["url"]
    assert_equal "2026-10-15T00:00:00+01:00", entry["date"]
    assert_equal "First paragraph here.", entry["excerpt"]
    assert_equal ActivityPages.epoch("2026-10-15T00:00:00+01:00"), entry["epoch"]
  end

  def test_post_entry_accepts_a_time_for_the_date
    entry = ActivityPages.post_entry(post(date: Time.new(2026, 10, 15, 0, 0, 0, "+01:00")))
    assert_equal "2026-10-15T00:00:00+01:00", entry["date"]
  end

  def test_excerpt_text_strips_markdown_and_html_and_keeps_the_first_paragraph
    text = "## Heading\n\nA [link](https://x) with **bold**, _it_ and <em>tags</em>.\n\nSecond para."
    assert_equal "A link with bold, it and tags.", ActivityPages.excerpt_text(text)
    assert_equal "", ActivityPages.excerpt_text(nil)
  end

  def test_excerpt_text_drops_liquid_tags
    text = "{% highlight python %}\nprint(1)\n{% endhighlight %} Then {{ page.title }} words."
    assert_equal "print(1) Then words.", ActivityPages.excerpt_text(text)
  end

  def test_excerpt_text_truncates_long_paragraphs
    text = "word " * 100
    got = ActivityPages.excerpt_text(text)
    assert got.length <= ActivityPages::EXCERPT_LENGTH + 1
    assert got.end_with?("…")
  end

  def test_thought_entry_links_to_its_month_page
    entry = ActivityPages.thought_entry(thought(bluesky: "https://bsky.app/x"))
    assert_equal "thought", entry["kind"]
    assert_equal "20261107080338", entry["id"]
    assert_equal "hello there", entry["text"]
    assert_equal "/thoughts/2026-11/#t20261107080338", entry["url"]
    assert_equal "https://bsky.app/x", entry["bluesky"]
    refute entry.key?("images")
  end

  def test_a_til_thought_becomes_a_til_entry_with_the_prefix_stripped
    entry = ActivityPages.thought_entry(thought(text: "TIL: that bees sleep"))
    assert_equal "til", entry["kind"]
    assert_equal "Bees sleep", entry["text"]
    assert_equal "TIL: that bees sleep", entry["raw"]
    assert_equal "/til/#t20261107080338", entry["url"]
  end

  def test_play_entry_links_to_its_listening_month_page
    entry = ActivityPages.play_entry(play(album: "The Second Bite", n: 2))
    assert_equal "play", entry["kind"]
    assert_equal 1791122948, entry["ts"]
    assert_equal "Bullet", entry["track"]
    assert_equal "Fluke", entry["artist"]
    assert_equal "The Second Bite", entry["album"]
    assert_equal 2, entry["n"]
    assert_equal "/listening/2026-10/#s1791122948", entry["url"]
    assert_equal "https://www.last.fm/music/Fluke/_/Bullet", entry["track_url"]
    assert_equal "https://www.last.fm/music/Fluke", entry["artist_url"]
  end

  # --- the merged log --------------------------------------------------

  def test_entries_merges_every_kind_newest_first
    entries = ActivityPages.entries(
      posts: [post(date: "2026-10-15T00:00:00+01:00")],
      thoughts: [thought(date: "2026-11-07T08:03:38+00:00"),
                 thought(id: "20261004120000", date: "2026-10-04T12:00:00+01:00", text: "TIL: x")],
      plays: [play(date: "2026-10-04T15:09:08+01:00")],
    )
    assert_equal %w[thought post play til], kinds(entries)
  end

  def test_entries_with_the_same_time_keep_their_input_order
    entries = ActivityPages.entries(
      posts: [post(date: "2026-10-04T12:00:00+01:00")],
      thoughts: [thought(date: "2026-10-04T12:00:00+01:00")],
    )
    assert_equal %w[post thought], kinds(entries)
  end

  def test_entries_of_nothing_is_empty
    assert_equal [], ActivityPages.entries
    assert_equal [], ActivityPages.entries(posts: nil, thoughts: nil, plays: nil)
  end

  def test_month_url_and_grouping
    assert_equal "/activity/2026-10/", ActivityPages.month_url("2026-10")
    entries = ActivityPages.entries(
      posts: [post(date: "2026-10-15T00:00:00+01:00")],
      thoughts: [thought(date: "2026-11-07T08:03:38+00:00")],
    )
    groups = ActivityPages.group_by_month(entries)
    assert_equal ["2026-11", "2026-10"], groups.map(&:first)
    assert_equal [], ActivityPages.group_by_month(nil)
  end

  # --- display ---------------------------------------------------------

  def test_display_folds_consecutive_plays_on_a_day_into_one_listening_entry
    entries = ActivityPages.entries(
      plays: [play(ts: 3, date: "2026-10-04T15:09:08+01:00", track: "C"),
              play(ts: 2, date: "2026-10-04T15:01:00+01:00", track: "B"),
              play(ts: 1, date: "2026-10-04T14:53:00+01:00", track: "A")],
    )
    shown = ActivityPages.display(entries)
    assert_equal ["listening"], kinds(shown)
    assert_equal %w[C B A], shown[0]["plays"].map { |p| p["track"] }
    assert_equal "2026-10-04T15:09:08+01:00", shown[0]["date"]
    assert_equal "2026-10-04T14:53:00+01:00", shown[0]["first_date"]
    assert_equal 3, shown[0]["count"]
  end

  def test_display_counts_repeats_in_a_run
    entries = ActivityPages.entries(plays: [play(n: 4)])
    assert_equal 4, ActivityPages.display(entries)[0]["count"]
  end

  def test_display_splits_plays_around_other_activity_and_across_days
    entries = ActivityPages.entries(
      plays: [play(ts: 4, date: "2026-10-05T01:00:00+01:00", track: "D"),
              play(ts: 3, date: "2026-10-04T23:00:00+01:00", track: "C"),
              play(ts: 1, date: "2026-10-04T14:00:00+01:00", track: "A")],
      thoughts: [thought(date: "2026-10-04T15:00:00+01:00")],
    )
    shown = ActivityPages.display(entries)
    assert_equal %w[listening listening thought listening], kinds(shown)
    assert_equal [["D"], ["C"], nil, ["A"]],
                 shown.map { |e| e["plays"]&.map { |p| p["track"] } }
  end

  def test_display_leaves_other_kinds_untouched
    entries = ActivityPages.entries(posts: [post], thoughts: [thought])
    assert_equal entries, ActivityPages.display(entries)
  end

  # --- search ----------------------------------------------------------

  def test_search_index_shapes_each_kind
    entries = ActivityPages.entries(
      posts: [post(date: "2026-10-15T00:00:00+01:00")],
      thoughts: [thought(date: "2026-11-07T08:03:38+00:00", images: [{ "src" => "/i.png", "alt" => "pic" }]),
                 thought(id: "20261004120000", date: "2026-10-04T12:00:00+01:00", text: "TIL: that x")],
      plays: [play(date: "2026-10-04T15:09:08+01:00", album: "Bite", n: 2)],
    )
    by_kind = ActivityPages.search_index(entries).group_by { |e| e["k"] }
    post_idx = by_kind["p"][0]
    assert_equal({ "k" => "p", "d" => "2026-10-15T00:00:00+01:00", "u" => "/2026/10/15/a-post/",
                   "t" => "A post", "e" => "First paragraph here." }, post_idx)
    thought_idx = by_kind["t"][0]
    assert_equal "hello there", thought_idx["t"]
    assert_equal "20261107080338", thought_idx["id"]
    refute thought_idx.key?("u"), "a thought's URL derives from its id client-side"
    assert_equal [["/i.png", "pic"]], thought_idx["i"]
    til_idx = by_kind["i"][0]
    assert_equal "X", til_idx["t"]
    assert_equal "20261004120000", til_idx["id"]
    refute til_idx.key?("u")
    play_idx = by_kind["s"][0]
    assert_equal({ "k" => "s", "d" => "2026-10-04T15:09:08+01:00", "u" => "/listening/2026-10/#s1791122948",
                   "t" => "Bullet", "a" => "Fluke", "l" => "Bite", "n" => 2,
                   "tu" => "https://www.last.fm/music/Fluke/_/Bullet",
                   "au" => "https://www.last.fm/music/Fluke" }, play_idx)
  end

  def test_search_index_omits_what_an_entry_lacks
    entries = ActivityPages.entries(thoughts: [thought], plays: [play])
    entries.each { |e| refute ActivityPages.search_index([e])[0].key?("i") }
    play_idx = ActivityPages.search_index(entries)[1]
    refute play_idx.key?("l")
    refute play_idx.key?("n")
  end
end
