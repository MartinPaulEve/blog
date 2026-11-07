# /activity/: one chronological log of everything that happens on the
# site — posts, short thoughts, TILs and listening — split into per-month
# pages like /thoughts/ (each month at /activity/<YYYY-MM>/, the index
# carrying the newest month), with whole-log search through
# /activity/search.json (plus a pregzipped twin) that activity-search.js
# fetches on first use. A thought that is a TIL appears once, as the TIL.
# Runs of plays with nothing else between them on a day fold into one
# listening entry on the page (search still finds each play).
#
# ActivityPages holds the pure helpers (no Jekyll dependency, unit-tested
# in _tests/activity_pages_test.rb); the Jekyll wiring is at the bottom.

require "cgi"
require "json"
require "time"
require "zlib"
require_relative "thoughts"
require_relative "thoughts_pages"
require_relative "listening_pages"

module ActivityPages
  BASE_DIR = "activity".freeze
  EXCERPT_LENGTH = 300

  # Seconds since the epoch for an ISO 8601 string (fractions and all) or
  # a Time: the one key every kind of entry sorts on.
  def self.epoch(date)
    return date.to_i if date.respond_to?(:to_time) && !date.is_a?(String)

    Time.iso8601(date.to_s).to_i
  end

  def self.iso(date)
    date.is_a?(String) ? date : date.iso8601
  end

  # The first paragraph of a markdown excerpt as plain text, shortened
  # to EXCERPT_LENGTH characters with an ellipsis.
  def self.excerpt_text(markdown)
    text = markdown.to_s.strip
    paragraphs = text.split(/\n\s*\n/).map(&:strip).reject do |para|
      para.empty? || para.start_with?("#")
    end
    para = paragraphs.first.to_s
    para = para.gsub(/\{%.*?%\}/m, "").gsub(/\{\{.*?\}\}/m, "")
    para = para.gsub(/<[^>]+>/, "")
    para = para.gsub(/!\[([^\]]*)\]\([^)]*\)/, "\\1")
    para = para.gsub(/\[([^\]]+)\]\([^)]*\)/, "\\1")
    para = para.gsub(/(\*\*|__)(.*?)\1/, "\\2")
    para = para.gsub(/(\*|_)(.*?)\1/, "\\2")
    para = para.gsub(/`([^`]*)`/, "\\1")
    para = para.gsub(/\s+/, " ").strip
    return para if para.length <= EXCERPT_LENGTH

    para[0, EXCERPT_LENGTH].sub(/\s+\S*\z/, "") + "…"
  end

  # --- one shape per kind ----------------------------------------------

  def self.post_entry(post)
    date = post["date"]
    {
      "kind" => "post",
      "date" => iso(date),
      "epoch" => epoch(date),
      "url" => post["url"].to_s,
      "title" => post["title"].to_s,
      "excerpt" => excerpt_text(post["excerpt"]),
    }
  end

  def self.thought_entry(thought)
    id = thought["id"].to_s
    text = thought["text"].to_s
    til = ThoughtsFilter.til?(text)
    entry = {
      "kind" => til ? "til" : "thought",
      "date" => thought["date"].to_s,
      "epoch" => epoch(thought["date"]),
      "id" => id,
      "text" => til ? ThoughtsFilter.til_strip(text) : text,
      "url" => til ? "/til/#t#{id}" : "#{ThoughtsPages.month_url(ThoughtsPages.month_of_id(id))}#t#{id}",
    }
    entry["raw"] = text if til
    images = thought["images"]
    entry["images"] = images unless images.nil? || images.empty?
    ThoughtsPages::SYNDICATION_KEYS.each_key do |source|
      entry[source] = thought[source] if thought[source]
    end
    entry
  end

  def self.play_entry(play)
    date = play["date"].to_s
    entry = {
      "kind" => "play",
      "date" => date,
      "epoch" => epoch(date),
      "ts" => play["ts"],
      "url" => "#{ListeningPages.month_url(date[0, 7])}##{ListeningPages.anchor(play)}",
      "track" => play["track"].to_s,
      "artist" => play["artist"].to_s,
      "track_url" => play["url"].to_s,
      "artist_url" => play["artist_url"].to_s,
    }
    entry["album"] = play["album"] if play["album"] && !play["album"].to_s.empty?
    entry["n"] = play["n"] if play["n"]
    entry
  end

  # Every entry, newest first; ties keep their input order (posts, then
  # thoughts, then plays).
  def self.entries(posts: [], thoughts: [], plays: [])
    all = (posts || []).map { |p| post_entry(p) } +
          (thoughts || []).map { |t| thought_entry(t) } +
          (plays || []).map { |p| play_entry(p) }
    all.each_with_index.sort_by { |entry, i| [-entry["epoch"], i] }.map(&:first)
  end

  def self.month_url(month)
    "/#{BASE_DIR}/#{month}/"
  end

  def self.month_title(month)
    ThoughtsPages.month_title(month)
  end

  def self.group_by_month(entries)
    ThoughtsPages.group_by_month(entries)
  end

  # --- what the page shows ---------------------------------------------

  # Consecutive plays on the same day (newest-first input) become one
  # "listening" entry carrying the plays, the span of their times and
  # the number of plays including repeats.
  def self.display(entries)
    shown = []
    (entries || []).each do |entry|
      unless entry["kind"] == "play"
        shown << entry
        next
      end
      last = shown.last
      if last && last["kind"] == "listening" && last["date"][0, 10] == entry["date"][0, 10]
        last["plays"] << entry
        last["first_date"] = entry["date"]
        last["count"] += entry["n"] || 1
      else
        shown << {
          "kind" => "listening",
          "date" => entry["date"],
          "first_date" => entry["date"],
          "epoch" => entry["epoch"],
          "url" => entry["url"],
          "plays" => [entry],
          "count" => entry["n"] || 1,
        }
      end
    end
    shown
  end

  # --- search ----------------------------------------------------------

  KIND_KEYS = { "post" => "p", "thought" => "t", "til" => "i", "play" => "s" }.freeze

  # One compact hash per entry. A thought's or TIL's URL is left out:
  # the client derives it from the kind and id (27k of them, a megabyte
  # of payload otherwise).
  def self.search_index(entries)
    (entries || []).map do |entry|
      indexed = { "k" => KIND_KEYS.fetch(entry["kind"]), "d" => entry["date"] }
      case entry["kind"]
      when "post"
        indexed["u"] = entry["url"]
        indexed["t"] = entry["title"]
        indexed["e"] = entry["excerpt"]
      when "thought", "til"
        indexed["id"] = entry["id"]
        indexed["t"] = entry["text"]
        if entry["images"]
          indexed["i"] = entry["images"].map { |image| [image["src"].to_s, image["alt"].to_s] }
        end
        ThoughtsPages::SYNDICATION_KEYS.each do |source, key|
          indexed[key] = entry[source] if entry[source]
        end
      when "play"
        indexed["u"] = entry["url"]
        indexed["t"] = entry["track"]
        indexed["a"] = entry["artist"]
        indexed["l"] = entry["album"] if entry["album"]
        indexed["n"] = entry["n"] if entry["n"]
        indexed["tu"] = entry["track_url"]
        indexed["au"] = entry["artist_url"]
      end
      indexed
    end
  end

  # The entries for a site: its posts as plain hashes, its thoughts and
  # its plays.
  def self.site_entries(site)
    posts = site.posts.docs.map do |doc|
      excerpt = doc.data["excerpt"]
      {
        "title" => doc.data["title"],
        "url" => doc.url,
        "date" => doc.date,
        "excerpt" => excerpt.respond_to?(:content) ? excerpt.content : excerpt,
      }
    end
    entries(posts: posts, thoughts: site.data["thoughts"],
            plays: ListeningPages.plays(site.data))
  end
end

if defined?(Jekyll)
  module Jekyll
    class ActivityMonthPage < PageWithoutAFile
      def initialize(site, month, entries, nav)
        super(site, site.source,
              File.join(ActivityPages::BASE_DIR, month), "index.html")
        display = ActivityPages.month_title(month)
        self.content = "{% include _activity_page.html %}\n"
        self.data = {
          "layout" => "page",
          "title" => "Activity: #{display}",
          "excerpt" => "Everything on this site from #{display}: posts, " \
                       "short thoughts, TILs and listening.",
          "og_card" => false,
          "pdf" => false,
          "feed" => "/#{ActivityPages::BASE_DIR}/feed.atom",
          "month" => month,
          "month_display" => display,
          "month_entries" => ActivityPages.display(entries),
          "activity_nav" => nav,
        }
      end
    end

    class ActivitySearchIndexPage < PageWithoutAFile
      def initialize(site, entries)
        super(site, site.source, ActivityPages::BASE_DIR, "search.json")
        self.content = JSON.generate(ActivityPages.search_index(entries))
        self.data = {
          "layout" => nil,
          "render_with_liquid" => false,
          "sitemap" => false,
          "pdf" => false,
          "og_card" => false,
        }
      end
    end

    # :low so that the posts are all read and the thoughts/listening
    # generators (:normal) have run; the og_image generator is :low too
    # but these pages carry og_card: false.
    class ActivityPagesGenerator < Generator
      safe false
      priority :low

      def generate(site)
        entries = ActivityPages.site_entries(site)
        return if entries.empty?

        groups = ActivityPages.group_by_month(entries)
        nav = groups.map do |month, _entries|
          {
            "name" => month,
            "url" => ActivityPages.month_url(month),
            "display" => ActivityPages.month_title(month),
          }
        end

        groups.each do |month, month_entries|
          site.pages << ActivityMonthPage.new(site, month, month_entries, nav)
        end
        site.pages << ActivitySearchIndexPage.new(site, entries)

        index = site.pages.find { |page| page.url == "/#{ActivityPages::BASE_DIR}/" }
        return unless index

        month, month_entries = groups.first
        index.data.merge!(
          "month" => month,
          "month_display" => ActivityPages.month_title(month),
          "month_entries" => ActivityPages.display(month_entries),
          "activity_nav" => nav,
          "activity_index" => true,
          "entry_count" => entries.length,
        )
      end
    end
  end

  Jekyll::Hooks.register :site, :post_write do |site|
    source = File.join(site.dest, ActivityPages::BASE_DIR, "search.json")
    next unless File.exist?(source)

    Zlib::GzipWriter.open("#{source}.gz") do |gz|
      gz.mtime = 0
      gz.write(File.binread(source))
    end
  end
end
