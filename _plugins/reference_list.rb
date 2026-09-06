# Visible reference lists for posts, rendered at build time from the
# `references:` front matter (see _references/ for how that metadata is
# assembled). The post layout calls the {% reference_list %} tag, which
# emits a "References" section — MHRA by default (also the fixed style in
# the PDF edition, where the picker and alternate styles stay hidden),
# with APA and Chicago author-date variants revealed by a small
# client-side style picker. Bare reference entries render from whatever
# is known: their inline `# label` comment and URL; bare DOIs resolve to
# full citations through the signposting DOI cache (.doi_cache.json).
#
# The section is suppressed on posts that already carry a hand-written
# reference list in the body (a References/Bibliography/Works Cited
# heading), or when the front matter sets `reference_list: false`.
#
# Pure formatting logic lives in the ReferenceList module so it can be
# unit-tested without Jekyll: ruby _tests/reference_list_test.rb

require "cgi"
require "json"

module ReferenceList
  DISCLAIMER =
    "This reference list has been generated, in many cases, through an " \
    "automated process and may therefore contain errors or incomplete " \
    "metadata. It is provided purely as assistance for finding the items " \
    "mentioned within this post."

  STYLES = { "mhra" => "MHRA", "apa" => "APA", "chicago" => "Chicago" }.freeze

  ITALIC_TYPES = %w[Book Report WebSite Periodical Blog].freeze
  DOI_URL_RE = %r{\Ahttps?://(?:dx\.)?doi\.org/(.+)\z}i
  BARE_LABEL_RE = %r{^- (https?://\S+) # (.+?)\s*$}
  MANUAL_HEADING_RE = Regexp.union(
    /^\#{1,6}[ \t]*(references|bibliography|works cited)\b/i,
    /<h[1-6][^>]*>\s*(references|bibliography|works cited)\b/i
  )
  MONTHS = %w[January February March April May June July
              August September October November December].freeze

  # {url => label} from the raw front matter's bare `- url # label` lines.
  def self.parse_labels(raw_text)
    front = raw_text[/\A---\n(.*?\n)---\n/m, 1] || ""
    front.scan(BARE_LABEL_RE).to_h
  end

  # True when the body already carries a hand-written reference list.
  def self.manual_list?(content)
    !!(content =~ MANUAL_HEADING_RE)
  end

  # One front-matter references entry (bare string or mapping) into a
  # normalised citation hash: authors (array), date, title,
  # italic_title, venue, publisher, url. Bare DOIs resolve through
  # doi_store (CSL JSON keyed by bare DOI); bare URLs take their label
  # as a plain description.
  def self.normalize(entry, labels, doi_store)
    return normalize_mapping(entry, doi_store) if entry.respond_to?(:key?)

    text = entry.to_s.strip
    return nil if text.empty?

    if (doi = text[DOI_URL_RE, 1])
      return doi_reference(doi, doi_store)
    end

    {
      authors: [],
      date: nil,
      title: labels[text],
      italic_title: false,
      descriptive: true,
      venue: nil,
      publisher: nil,
      url: text,
    }
  end

  # One normalised citation as an HTML fragment in :mhra, :apa, or
  # :chicago style. Cites whatever fields are present.
  def self.format(ref, style)
    case style
    when :apa then format_apa(ref)
    when :chicago then format_chicago(ref)
    else format_mhra(ref)
    end
  end

  # The full References section (heading, disclaimer, one list per
  # style, hidden picker) or nil when there is nothing to cite.
  def self.render_section(entries, labels, doi_store)
    refs = Array(entries).map { |e| normalize(e, labels, doi_store) }.compact
    return nil if refs.empty?

    refs.sort_by! { |r| sort_key(r) }

    picker_options = STYLES.map do |value, name|
      %(<option value="#{value}">#{name}</option>)
    end.join

    lists = STYLES.keys.map do |style|
      hidden = style == "mhra" ? "" : " hidden"
      items = refs.map { |r| "<li>#{format(r, style.to_sym)}</li>" }.join("\n")
      %(<ol class="post-references-list" data-ref-style="#{style}"#{hidden}>\n#{items}\n</ol>)
    end.join("\n")

    <<~HTML
      <section class="post-references" data-ref-section>
      <h2 id="references">References</h2>
      <p class="post-references-disclaimer">#{DISCLAIMER}</p>
      <p class="post-references-picker" data-ref-picker hidden><label>Citation style: <select data-ref-select>#{picker_options}</select></label></p>
      #{lists}
      </section>
    HTML
  end

  class << self
    private

    def normalize_mapping(entry, doi_store)
      if (doi = bare_doi(entry["doi"]))
        base = doi_reference(doi, doi_store)
        base[:title] = entry["title"].to_s if entry["title"]
        base[:date] = entry["date"].to_s if entry["date"]
        return base
      end

      type = entry["type"].to_s
      {
        authors: author_names(entry["author"]),
        date: entry["date"] ? entry["date"].to_s : nil,
        title: entry["title"] ? entry["title"].to_s : nil,
        italic_title: ITALIC_TYPES.include?(type),
        descriptive: false,
        venue: entry.respond_to?(:dig) ? entry.dig("isPartOf", "name") : nil,
        publisher: entry["publisher"],
        url: entry["url"],
      }
    end

    def doi_reference(doi, doi_store)
      # DOIs are case-insensitive, but the cache preserves the case the
      # signposting plugin saw; keep the reference's own case for display
      # and fall back to a case-insensitive match for the lookup.
      doi = doi.strip
      url = "https://doi.org/#{doi}"
      csl = doi_store[doi]
      if csl.nil?
        target = doi.downcase
        _, csl = doi_store.find { |key, _| key.downcase == target }
      end
      unless csl
        return { authors: [], date: nil, title: nil, italic_title: false,
                 descriptive: false, venue: nil, publisher: nil, url: url }
      end

      venue = first_string(csl["container-title"])
      {
        authors: csl_authors(csl["author"]),
        date: csl_date(csl["issued"] || csl["published"]),
        title: first_string(csl["title"]),
        italic_title: venue.nil?,
        descriptive: false,
        venue: venue,
        publisher: csl["publisher"],
        url: url,
      }
    end

    def bare_doi(value)
      return nil unless value
      text = value.to_s.strip
      text[DOI_URL_RE, 1] || (text =~ %r{\A10\.\d{4,}/} ? text : nil)
    end

    def first_string(value)
      value.is_a?(Array) ? value.first : value
    end

    def csl_authors(list)
      Array(list).map do |a|
        [a["given"], a["family"]].compact.join(" ").strip
      end.reject(&:empty?)
    end

    def csl_date(issued)
      parts = issued && issued["date-parts"] && issued["date-parts"].first
      return nil unless parts && parts.first
      parts.map.with_index { |p, i| i.zero? ? p.to_s : p.to_s.rjust(2, "0") }
           .join("-")
    end

    def author_names(value)
      # A single {name:, orcid:} mapping must not fall into Array(), which
      # would shatter a Hash into [key, value] pairs.
      list = value.respond_to?(:key?) ? [value] : Array(value)
      list.map do |author|
        author.respond_to?(:key?) ? author["name"].to_s : author.to_s
      end.reject(&:empty?)
    end

    def date_parts(date)
      return [] unless date
      date.to_s.split("-").first(3).map(&:to_i).reject(&:zero?)
    end

    def esc(text)
      CGI.escapeHTML(text.to_s)
    end

    # Titles from registration metadata may carry embedded presentational
    # markup (a cited work inside a title, <sub>/<sup> in chemistry, etc.).
    # Escape everything, then restore only that safe whitelist.
    def esc_rich(text)
      esc(text).gsub(%r{&lt;(/?)(i|b|em|strong|sub|sup)&gt;}i) do
        "<#{Regexp.last_match(1)}#{Regexp.last_match(2).downcase}>"
      end
    end

    def invert(name)
      parts = name.split
      return esc(name) if parts.length < 2
      esc("#{parts[-1]}, #{parts[0..-2].join(' ')}")
    end

    def apa_name(name)
      parts = name.split
      return esc(name) if parts.length < 2
      initials = parts[0..-2].map { |p| "#{p[0].upcase}." }.join(" ")
      esc("#{parts[-1]}, #{initials}")
    end

    def surname(name)
      name.split.last.to_s
    end

    def sort_key(ref)
      key = ref[:authors].first ? surname(ref[:authors].first) : (ref[:title] || ref[:url])
      key.to_s.downcase
    end

    def link_html(url)
      %(<a href="#{esc(url)}">#{esc(url)}</a>) if url
    end

    def mhra_authors(authors)
      return nil if authors.empty?
      names = [invert(authors.first)] + authors[1..].map { |a| esc(a) }
      names.length == 1 ? names.first : "#{names[0..-2].join(', ')}, and #{names[-1]}"
    end

    def mhra_date(date)
      y, m, d = date_parts(date)
      return nil unless y
      [d, m && MONTHS[m - 1], y].compact.join(" ")
    end

    def format_mhra(ref)
      title =
        if ref[:title].nil?
          nil
        elsif ref[:italic_title]
          "<i>#{esc_rich(ref[:title])}</i>"
        elsif ref[:descriptive]
          esc_rich(ref[:title])
        else
          "‘#{esc_rich(ref[:title])}’"
        end
      parts = [
        mhra_authors(ref[:authors]),
        title,
        ref[:venue] && "<i>#{esc(ref[:venue])}</i>",
        ref[:publisher] && esc(ref[:publisher]),
        mhra_date(ref[:date]),
      ].compact
      cite = parts.join(", ")
      cite += " &lt;#{link_html(ref[:url])}&gt;" if ref[:url]
      cite.empty? ? link_html(ref[:url]).to_s : cite
    end

    def apa_date(date)
      y, m, d = date_parts(date)
      return "(n.d.)" unless y
      inner = [y, m && MONTHS[m - 1], d].compact
      inner.length == 1 ? "(#{y})" : "(#{y}, #{inner[1]}#{d ? " #{d}" : ''})"
    end

    def format_apa(ref)
      authors = ref[:authors].map { |a| apa_name(a) }
      author_text =
        if authors.empty? then nil
        elsif authors.length == 1 then authors.first
        else "#{authors[0..-2].join(', ')}, &amp; #{authors[-1]}"
        end
      title =
        ref[:title] &&
        (ref[:italic_title] ? "<i>#{esc_rich(ref[:title])}</i>" : esc_rich(ref[:title]))
      parts = [
        author_text && "#{author_text} #{apa_date(ref[:date])}.",
        author_text.nil? && title ? "#{title}. #{apa_date(ref[:date])}." : nil,
        author_text && title ? "#{title}." : nil,
        ref[:venue] && "<i>#{esc(ref[:venue])}</i>.",
        ref[:publisher] && "#{esc(ref[:publisher])}.",
        link_html(ref[:url]),
      ].compact
      parts.join(" ")
    end

    def chicago_authors(authors)
      return nil if authors.empty?
      names = [invert(authors.first)] + authors[1..].map { |a| esc(a) }
      names.length == 1 ? names.first : "#{names[0..-2].join(', ')} and #{names[-1]}"
    end

    def format_chicago(ref)
      y, m, d = date_parts(ref[:date])
      title =
        if ref[:title].nil?
          nil
        elsif ref[:italic_title]
          "<i>#{esc_rich(ref[:title])}</i>."
        elsif ref[:descriptive]
          "#{esc_rich(ref[:title])}."
        else
          "“#{esc_rich(ref[:title])}.”"
        end
      tail_date = m ? "#{MONTHS[m - 1]}#{d ? " #{d}" : ''}" : nil
      parts = [
        chicago_authors(ref[:authors]) && "#{chicago_authors(ref[:authors])}. #{y || 'n.d.'}.",
        chicago_authors(ref[:authors]).nil? && title ? "#{title} #{y || 'n.d.'}." : nil,
        chicago_authors(ref[:authors]) && title ? title : nil,
        ref[:venue] && "<i>#{esc(ref[:venue])}</i>#{tail_date ? ", #{tail_date}" : ''}.",
        ref[:publisher] && "#{esc(ref[:publisher])}.",
        link_html(ref[:url]),
      ].compact
      parts.join(" ")
    end
  end
end

# ---------------------------------------------------------------------------
# Jekyll wiring (skipped under plain ruby, e.g. tests).
# ---------------------------------------------------------------------------
if defined?(Jekyll)
  class ReferenceListTag < Liquid::Tag
    def render(context)
      site = context.registers[:site]
      page = context.registers[:page]
      entries = page["references"]
      return "" if entries.nil? || entries.empty?
      return "" if page["reference_list"] == false

      doc = site.posts.docs.find { |d| d.url == page["url"] }
      return "" if doc.nil?
      return "" if ReferenceList.manual_list?(doc.content)

      labels = ReferenceList.parse_labels(File.read(doc.path))
      html = ReferenceList.render_section(entries, labels, doi_store(site))
      html || ""
    end

    private

    def doi_store(site)
      @@doi_store ||= begin
        path = File.join(site.source, site.config["doi_cache"] || ".doi_cache.json")
        File.exist?(path) ? JSON.parse(File.read(path)) : {}
      rescue JSON::ParserError
        {}
      end
    end
  end

  Liquid::Template.register_tag("reference_list", ReferenceListTag)
end
