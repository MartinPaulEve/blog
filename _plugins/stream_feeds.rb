# Atom feeds for the site's streams: /activity/, /thoughts/, /til/ and
# /listening/ each get a feed.atom beside the site's own /feed/feed.atom
# (jekyll-feed's, posts only). StreamFeeds.atom renders a feed from plain
# entry hashes and StreamFeeds.entry_for turns an ActivityPages entry of
# any kind into one — both pure, unit-tested in _tests/stream_feeds_test.rb.
# The generator at the bottom builds the four feeds from the same unified
# log the /activity/ pages use.

require "cgi"
require "time"
require_relative "activity_pages"

module StreamFeeds
  FEED_NAME = "feed.atom".freeze
  LIMIT = 50
  TITLE_LENGTH = 90

  def self.absolute(site_url, url)
    url.to_s.start_with?("http") ? url.to_s : "#{site_url.to_s.chomp('/')}#{url}"
  end

  def self.shorten(text)
    text = text.to_s.gsub(/\s+/, " ").strip
    return text if text.length <= TITLE_LENGTH

    text[0, TITLE_LENGTH].sub(/\s+\S*\z/, "") + "…"
  end

  def self.play_html(play)
    track = %(<a href="#{CGI.escape_html(play['track_url'])}">#{CGI.escape_html(play['track'])}</a>)
    artist = %(<a href="#{CGI.escape_html(play['artist_url'])}">#{CGI.escape_html(play['artist'])}</a>)
    line = "#{track} by #{artist}"
    line += " on #{CGI.escape_html(play['album'])}" if play["album"]
    line += " (×#{play['n']})" if play["n"]
    line
  end

  # A feed entry — {"title", "url" (absolute), "date", "html"} — for an
  # ActivityPages entry (a post, thought, TIL, or a display "listening"
  # group).
  def self.entry_for(entry, site_url)
    url = absolute(site_url, entry["url"])
    case entry["kind"]
    when "post"
      title = entry["title"]
      html = "<p>#{CGI.escape_html(entry['excerpt'].to_s)}</p>" +
             %(<p><a href="#{CGI.escape_html(url)}">Read the post</a></p>)
    when "thought", "til"
      title = shorten(entry["text"])
      title = "TIL: #{title}" if entry["kind"] == "til"
      html = "<p>#{ThoughtsFilter.linkify(entry['text'])}</p>"
      (entry["images"] || []).each do |image|
        html += %(<p><img src="#{CGI.escape_html(absolute(site_url, image['src']))}" ) +
                %(alt="#{CGI.escape_html(image['alt'].to_s)}"></p>)
      end
    when "listening"
      plays = entry["plays"]
      title = if plays.length == 1 && !plays[0]["n"]
                "Listened to #{plays[0]['track']} by #{plays[0]['artist']}"
              else
                "Listened to #{entry['count']} tracks"
              end
      html = "<ul>" + plays.map { |play| "<li>#{play_html(play)}</li>" }.join + "</ul>"
    when "play"
      title = "Listened to #{entry['track']} by #{entry['artist']}"
      html = "<p>#{play_html(entry)}</p>"
    else
      raise ArgumentError, "unknown activity kind #{entry['kind'].inspect}"
    end
    { "title" => title, "url" => url, "date" => entry["date"], "html" => html }
  end

  # An Atom document for ``entries`` (newest first; at most ``limit``).
  def self.atom(title:, site_url:, page_url:, author:, entries:, subtitle: nil,
                limit: LIMIT)
    entries = (entries || []).each_with_index
                             .sort_by { |entry, i| [-ActivityPages.epoch(entry["date"]), i] }
                             .map(&:first).first(limit)
    page = absolute(site_url, page_url)
    self_url = "#{page.chomp('/')}/#{FEED_NAME}"
    updated = entries.first ? entries.first["date"] : Time.now.utc.iso8601
    xml = +%(<?xml version="1.0" encoding="utf-8"?>\n)
    xml << %(<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="en">\n)
    xml << "  <title>#{CGI.escape_html(title)}</title>\n"
    xml << "  <subtitle>#{CGI.escape_html(subtitle)}</subtitle>\n" if subtitle
    xml << %(  <link href="#{CGI.escape_html(self_url)}" rel="self" type="application/atom+xml" />\n)
    xml << %(  <link href="#{CGI.escape_html(page)}" rel="alternate" type="text/html" />\n)
    xml << "  <updated>#{CGI.escape_html(updated)}</updated>\n"
    xml << "  <id>#{CGI.escape_html(page)}</id>\n"
    xml << "  <author><name>#{CGI.escape_html(author)}</name></author>\n"
    entries.each do |entry|
      url = CGI.escape_html(entry["url"])
      xml << "  <entry>\n"
      xml << "    <title>#{CGI.escape_html(entry['title'])}</title>\n"
      xml << %(    <link href="#{url}" rel="alternate" type="text/html" />\n)
      xml << "    <id>#{url}</id>\n"
      xml << "    <updated>#{CGI.escape_html(entry['date'])}</updated>\n"
      xml << "    <published>#{CGI.escape_html(entry['date'])}</published>\n"
      xml << %(    <content type="html">#{CGI.escape_html(entry['html'])}</content>\n)
      xml << "  </entry>\n"
    end
    xml << "</feed>\n"
  end
end

if defined?(Jekyll)
  module Jekyll
    class StreamFeedPage < PageWithoutAFile
      def initialize(site, dir, xml)
        super(site, site.source, dir, StreamFeeds::FEED_NAME)
        self.content = xml
        self.data = {
          "layout" => nil,
          "render_with_liquid" => false,
          "sitemap" => false,
          "pdf" => false,
          "og_card" => false,
        }
      end
    end

    # Which of the unified entries each stream's feed carries.
    STREAM_FEEDS = [
      ["activity", "Activity", "Everything on this site: posts, short thoughts, TILs and listening.",
       ->(entries) { ActivityPages.display(entries) }],
      ["thoughts", "Short Thoughts", "Short thoughts, TILs included, as posted.",
       ->(entries) { entries.select { |e| %w[thought til].include?(e["kind"]) } }],
      ["til", "Today I Learned", "TIL micro-posts drawn from the short thoughts stream.",
       ->(entries) { entries.select { |e| e["kind"] == "til" } }],
      ["listening", "Listening", "Everything I listen to, scrobbled from Last.fm.",
       ->(entries) { ActivityPages.display(entries.select { |e| e["kind"] == "play" }) }],
    ].freeze

    class StreamFeedsGenerator < Generator
      safe false
      priority :lowest

      def generate(site)
        entries = ActivityPages.site_entries(site)
        site_url = site.config["url"].to_s
        author = (site.config["owner"] || {})["name"] || site.config["author"].to_s
        site_title = site.config["title"].to_s
        STREAM_FEEDS.each do |dir, name, subtitle, select|
          chosen = select.call(entries).first(StreamFeeds::LIMIT)
          # The thoughts feed shows a TIL as the thought it was posted as.
          feed_entries = chosen.map do |entry|
            entry = entry.merge("kind" => "thought", "text" => entry["raw"]) if dir == "thoughts" && entry["kind"] == "til"
            StreamFeeds.entry_for(entry, site_url)
          end
          xml = StreamFeeds.atom(
            title: "#{site_title}: #{name}", subtitle: subtitle,
            site_url: site_url, page_url: "/#{dir}/", author: author,
            entries: feed_entries,
          )
          site.pages << StreamFeedPage.new(site, dir, xml)
        end
      end
    end
  end
end
