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

  def self.linkify(text)
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
      escaped_url = CGI.escape_html(url)
      out << CGI.escape_html(text[last...match.begin(0)])
      out << %(<a href="#{escaped_url}">#{escaped_url}</a>)
      out << CGI.escape_html(trail)
      last = match.begin(0) + match[0].length
    end
    out << CGI.escape_html(text[last..] || "")
    out.gsub("\n", "<br>\n")
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

      def til_entries(input)
        ThoughtsFilter.til_entries(input)
      end
    end
  end
  Liquid::Template.register_filter(Jekyll::ThoughtsLiquidFilter)
end
