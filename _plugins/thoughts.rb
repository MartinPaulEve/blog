# Rendering support for short thoughts (_data/thoughts.yml).
#
# The thought text is the author's untouched writing, stored raw; display
# must escape it (never interpret it as HTML or markdown) while making
# bare URLs clickable and preserving line breaks. The `linkify_urls`
# Liquid filter does exactly that and nothing more.
#
# Thoughts beginning "TIL:" also feed /til/. The `til_entries` filter
# selects them from the data and rewrites each text for display there:
# the prefix goes, and a leading "about"/"that" goes with it (the next
# word taking its capital). The stored text is never touched — the
# rewrite happens on a copy at render time, so /thoughts/ and the
# syndicated posts keep the original wording.

require "cgi"

module ThoughtsFilter
  URL_RE = %r{https?://[^\s<]+}
  TRAILING_PUNCTUATION = /[.,;:!?…'"”’]\z/

  EXTERNAL_ATTRS = ' target="_blank" rel="noopener"'
  EXTERNAL_HINT = '<span class="sr-only"> (opens in new tab)</span>'

  def self.linkify(text)
    linkify_with(text) { |url| %(<a href="#{url}">#{url}</a>) }.gsub("\n", "<br>\n")
  end

  # Image credits are stored as plain text in front matter and must never be
  # rewritten there; at render time any bare URL in the credit becomes a
  # link that opens in a new tab, matching the caption's existing title link.
  def self.linkify_external(text)
    linkify_with(text) do |url|
      %(<a href="#{url}"#{EXTERNAL_ATTRS}>#{url}#{EXTERNAL_HINT}</a>)
    end
  end

  # Escape the whole text and hand each bare URL (already escaped, with
  # trailing punctuation and unbalanced parens left outside) to the block,
  # which returns the anchor markup to emit in its place.
  def self.linkify_with(text)
    text = text.to_s
    out = +""
    last = 0
    text.scan(URL_RE) do
      match = Regexp.last_match
      url = match[0]
      trail = +""
      loop do
        if url =~ TRAILING_PUNCTUATION
          trail.prepend(url[-1])
          url = url[0..-2]
        elsif url.end_with?(")") && url.count("(") < url.count(")")
          trail.prepend(")")
          url = url[0..-2]
        else
          break
        end
      end
      out << CGI.escape_html(text[last...match.begin(0)])
      out << yield(CGI.escape_html(url))
      out << CGI.escape_html(trail)
      last = match.begin(0) + match[0].length
    end
    out << CGI.escape_html(text[last..] || "")
  end

  TIL_PREFIX = /\ATIL:\s*/
  TIL_LEADER = /\A(?:about|that)\s+/i

  def self.til?(text)
    text.to_s.match?(TIL_PREFIX)
  end

  def self.til_strip(text)
    stripped = text.to_s.sub(TIL_PREFIX, "")
    return stripped unless stripped =~ TIL_LEADER

    stripped.sub(TIL_LEADER, "").sub(/\A[[:lower:]]/) { |c| c.upcase }
  end

  def self.til_entries(thoughts)
    (thoughts || [])
      .select { |thought| til?(thought["text"]) }
      .map { |thought| thought.merge("text" => til_strip(thought["text"])) }
  end
end

if defined?(Liquid)
  module Jekyll
    module ThoughtsLiquidFilter
      def linkify_urls(input)
        ThoughtsFilter.linkify(input)
      end

      def linkify_urls_external(input)
        ThoughtsFilter.linkify_external(input)
      end

      def til_entries(input)
        ThoughtsFilter.til_entries(input)
      end
    end
  end
  Liquid::Template.register_filter(Jekyll::ThoughtsLiquidFilter)
end
