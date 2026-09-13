# Splitting /thoughts/ into per-month pages (_data/thoughts.yml).
#
# One 22MB page for 27k thoughts is unshippable, so each month gets its
# own page at /thoughts/<YYYY-MM>/ and the index carries only the newest
# month. Search still spans the whole archive: the generator emits
# /thoughts/search.json (and a pregzipped .json.gz twin, so the 6MB
# payload costs ~2MB even where the server never learned to compress)
# that the search script fetches on first use. Thought ids are compact
# local timestamps (YYYYMMDDHHMMSS), so an entry's month page is
# derivable from its id alone — which keeps old /thoughts/#t<id>
# permalinks redirectable and gives templates the `thought_month_url`
# Liquid filter.

require "date"
require "json"
require "zlib"

module ThoughtsPages
  BASE_DIR = "thoughts".freeze

  # "2012-05" for a thought hash (from its ISO date).
  def self.month_of(thought)
    thought["date"].to_s[0, 7]
  end

  # "2012-05" for a compact thought id like "20120516182000".
  def self.month_of_id(id)
    "#{id[0, 4]}-#{id[4, 2]}"
  end

  # "/thoughts/2012-05/" for "2012-05".
  def self.month_url(month)
    "/#{BASE_DIR}/#{month}/"
  end

  # "May 2012" for "2012-05".
  def self.month_title(month)
    year, mm = month.split("-")
    "#{Date::MONTHNAMES[mm.to_i]} #{year}"
  end

  # Newest-first [month, entries] pairs preserving the data file's own
  # (newest-first) order within each month.
  def self.group_by_month(thoughts)
    groups = []
    positions = {}
    (thoughts || []).each do |thought|
      month = month_of(thought)
      unless positions.key?(month)
        positions[month] = groups.length
        groups << [month, []]
      end
      groups[positions[month]][1] << thought
    end
    groups
  end

  # The whole-archive search payload: one compact hash per thought —
  # id, ISO date ("d"), untouched text ("t") and, only when present,
  # image [src, alt] pairs ("i").
  def self.search_index(thoughts)
    (thoughts || []).map do |thought|
      entry = {
        "id" => thought["id"].to_s,
        "d" => thought["date"].to_s,
        "t" => thought["text"].to_s,
      }
      images = thought["images"]
      unless images.nil? || images.empty?
        entry["i"] = images.map { |image| [image["src"].to_s, image["alt"].to_s] }
      end
      entry
    end
  end
end

if defined?(Liquid)
  module Jekyll
    module ThoughtsPagesLiquidFilter
      # The month page holding a thought, straight from its id.
      def thought_month_url(id)
        ThoughtsPages.month_url(ThoughtsPages.month_of_id(id.to_s))
      end
    end
  end
  Liquid::Template.register_filter(Jekyll::ThoughtsPagesLiquidFilter)
end

if defined?(Jekyll)
  module Jekyll
    class ThoughtsMonthPage < PageWithoutAFile
      def initialize(site, month, entries, nav)
        super(site, site.source,
              File.join(ThoughtsPages::BASE_DIR, month), "index.html")
        display = ThoughtsPages.month_title(month)
        self.content = "{% include _thoughts_page.html %}\n"
        self.data = {
          "layout" => "page",
          "title" => "Short Thoughts: #{display}",
          "excerpt" => "Short thoughts from #{display} — " \
                       "micro-posts syndicated to Bluesky and Mastodon.",
          "og_card" => false,
          "pdf" => false,
          "month" => month,
          "month_display" => display,
          "month_thoughts" => entries,
          "thoughts_nav" => nav,
        }
      end
    end

    class ThoughtsSearchIndexPage < PageWithoutAFile
      def initialize(site, thoughts)
        super(site, site.source, ThoughtsPages::BASE_DIR, "search.json")
        self.content = JSON.generate(ThoughtsPages.search_index(thoughts))
        self.data = {
          "layout" => nil,
          "sitemap" => false,
          "pdf" => false,
          "og_card" => false,
        }
      end
    end

    # Runs at :normal priority like the category pages; the og_image
    # generator (:low) would then card every month page, hence their
    # og_card: false.
    class ThoughtsPagesGenerator < Generator
      safe false
      priority :normal

      def generate(site)
        thoughts = site.data["thoughts"]
        return if thoughts.nil? || thoughts.empty?

        groups = ThoughtsPages.group_by_month(thoughts)
        nav = groups.map do |month, _entries|
          {
            "name" => month,
            "url" => ThoughtsPages.month_url(month),
            "display" => ThoughtsPages.month_title(month),
          }
        end

        groups.each do |month, entries|
          site.pages << ThoughtsMonthPage.new(site, month, entries, nav)
        end
        site.pages << ThoughtsSearchIndexPage.new(site, thoughts)

        index = site.pages.find { |page| page.url == "/#{ThoughtsPages::BASE_DIR}/" }
        return unless index

        month, entries = groups.first
        index.data.merge!(
          "month" => month,
          "month_display" => ThoughtsPages.month_title(month),
          "month_thoughts" => entries,
          "thoughts_nav" => nav,
          "thoughts_index" => true,
        )
      end
    end
  end

  # The pregzipped twin ships alongside the JSON so the client can avoid
  # the uncompressed transfer without any server configuration. mtime 0
  # keeps the bytes stable across identical builds.
  Jekyll::Hooks.register :site, :post_write do |site|
    source = File.join(site.dest, ThoughtsPages::BASE_DIR, "search.json")
    next unless File.exist?(source)

    Zlib::GzipWriter.open("#{source}.gz") do |gz|
      gz.mtime = 0
      gz.write(File.binread(source))
    end
  end
end
