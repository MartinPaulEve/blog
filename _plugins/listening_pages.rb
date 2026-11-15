# Splitting /listening/ — the Last.fm play log that _lastfm/fetch_lastfm.py
# keeps in _data/listening.json — into per-month pages, exactly as
# thoughts_pages.rb does for /thoughts/: each month gets its own page at
# /listening/<YYYY-MM>/ and the index carries only the newest month,
# while search spans the whole log through /listening/search.json (plus
# a pregzipped twin) that listening-search.js fetches on first use.
# Months, titles and grouping are ThoughtsPages' own (both data sets
# carry an ISO "date"); only the URL base, the anchors and the index
# payload differ.

require "json"
require "zlib"
require_relative "thoughts_pages"

module ListeningPages
  BASE_DIR = "listening".freeze

  # The newest-first play list from site.data, or [] without a data file.
  def self.plays(site_data)
    listening = (site_data || {})["listening"]
    return [] unless listening.is_a?(Hash)

    listening["plays"] || []
  end

  # "/listening/2026-10/" for "2026-10".
  def self.month_url(month)
    "/#{BASE_DIR}/#{month}/"
  end

  def self.month_title(month)
    ThoughtsPages.month_title(month)
  end

  def self.group_by_month(plays)
    ThoughtsPages.group_by_month(plays)
  end

  # The fragment id of a play on its month page: its timestamp is unique.
  def self.anchor(play)
    "s#{play['ts']}"
  end

  # The whole-log search payload: one compact hash per play — timestamp,
  # ISO date ("d"), track ("t"), artist ("a"), their Last.fm URLs ("u",
  # "au") and, only when present, the album ("l") and the run count ("n").
  def self.search_index(plays)
    (plays || []).map do |play|
      entry = {
        "ts" => play["ts"],
        "d" => play["date"].to_s,
        "t" => play["track"].to_s,
        "a" => play["artist"].to_s,
        "u" => play["url"].to_s,
        "au" => play["artist_url"].to_s,
      }
      entry["l"] = play["album"] if play["album"] && !play["album"].to_s.empty?
      entry["n"] = play["n"] if play["n"]
      entry
    end
  end
end

if defined?(Jekyll)
  module Jekyll
    class ListeningMonthPage < PageWithoutAFile
      def initialize(site, month, entries, nav)
        super(site, site.source,
              File.join(ListeningPages::BASE_DIR, month), "index.html")
        display = ListeningPages.month_title(month)
        self.content = "{% include _listening_page.html %}\n"
        self.data = {
          "layout" => "page",
          "title" => "Listening: #{display}",
          "excerpt" => "Everything I listened to in #{display}, " \
                       "scrobbled from Last.fm.",
          "og_card" => false,
          "pdf" => false,
          "feed" => "/#{ListeningPages::BASE_DIR}/feed.atom",
          "month" => month,
          "month_display" => display,
          "month_plays" => entries,
          "listening_nav" => nav,
        }
      end
    end

    class ListeningSearchIndexPage < PageWithoutAFile
      def initialize(site, plays)
        super(site, site.source, ListeningPages::BASE_DIR, "search.json")
        self.content = JSON.generate(ListeningPages.search_index(plays))
        self.data = {
          "layout" => nil,
          "render_with_liquid" => false,
          "sitemap" => false,
          "pdf" => false,
          "og_card" => false,
        }
      end
    end

    class ListeningPagesGenerator < Generator
      safe false
      priority :normal

      def generate(site)
        plays = ListeningPages.plays(site.data)
        return if plays.empty?

        groups = ListeningPages.group_by_month(plays)
        nav = groups.map do |month, _entries|
          {
            "name" => month,
            "url" => ListeningPages.month_url(month),
            "display" => ListeningPages.month_title(month),
          }
        end

        groups.each do |month, entries|
          site.pages << ListeningMonthPage.new(site, month, entries, nav)
        end
        site.pages << ListeningSearchIndexPage.new(site, plays)

        index = site.pages.find { |page| page.url == "/#{ListeningPages::BASE_DIR}/" }
        return unless index

        month, entries = groups.first
        index.data.merge!(
          "month" => month,
          "month_display" => ListeningPages.month_title(month),
          "month_plays" => entries,
          "listening_nav" => nav,
          "listening_index" => true,
          "play_count" => plays.length,
        )
      end
    end
  end

  Jekyll::Hooks.register :site, :post_write do |site|
    source = File.join(site.dest, ListeningPages::BASE_DIR, "search.json")
    next unless File.exist?(source)

    Zlib::GzipWriter.open("#{source}.gz") do |gz|
      gz.mtime = 0
      gz.write(File.binread(source))
    end
  end
end
