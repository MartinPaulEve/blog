# Attribution styling for <cite> inside blockquotes. In Markdown, a quote's
# source goes on its own line at the end of the blockquote:
#
#   > (i) the point of solving problems is to understand mathematics better.
#   > <cite>Gowers, 2000, 1</cite>
#
# assets/css/quote-cite.css sets that <cite> off as an attribution line (a
# red dash, then the source in the site's mono eyebrow style). The
# stylesheet is linked from inside the converted content itself, just before
# the first blockquote that contains a <cite> — never from _head.html, whose
# markup takes part in every post's PDF cache key — so posts without such a
# quote come out byte-identical and no existing PDF is re-rendered.
#
# QuoteAttributions holds the pure logic (no Jekyll dependency) so it can be
# unit-tested in isolation; the hook below wires it into the build.

module QuoteAttributions
  STYLESHEET = "/assets/css/quote-cite.css".freeze
  # A <blockquote> whose body (up to its own closing tag) contains a <cite>.
  CITED_QUOTE = %r{<blockquote\b[^>]*>(?:(?!</blockquote>).)*?<cite\b}m

  # Link the attribution stylesheet ahead of the first cited blockquote;
  # input without one is returned byte-identical.
  def self.transform(html)
    text = html.to_s
    match = CITED_QUOTE.match(text)
    return html unless match

    text[0...match.begin(0)] +
      "<link rel=\"stylesheet\" href=\"#{STYLESHEET}\">\n" +
      text[match.begin(0)..]
  end
end

if defined?(Jekyll::Hooks)
  Jekyll::Hooks.register :posts, :post_convert do |post|
    post.content = QuoteAttributions.transform(post.content)
  end
end
