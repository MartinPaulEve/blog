# Callout quotations: large, bold pull-quote blocks that break up the text
# flow of a post. In Markdown, a callout is an ordinary blockquote carrying
# the kramdown class attribute "callout":
#
#   > The whole of the argument hangs on a single comma.
#   >
#   > <cite>Someone Quotable, 1921</cite>
#   {: .callout}
#
# The optional <cite> line becomes the attribution. Styling lives in
# assets/css/callout.css, linked from inside the converted content itself
# just before the first callout — never from _head.html, whose markup takes
# part in every post's PDF cache key — so posts without a callout come out
# byte-identical and no existing PDF is re-rendered. The stylesheet carries
# its own @media print rules, so the PDF edition of a callout post gets a
# print-friendly version of the block.
#
# Callouts holds the pure logic (no Jekyll dependency) so it can be
# unit-tested in isolation; the hook below wires it into the build.

module Callouts
  STYLESHEET = "/assets/css/callout.css".freeze
  # A <blockquote> whose class attribute lists "callout" as a whole token.
  CALLOUT = /<blockquote\b[^>]*\bclass="(?:[^"]*\s)?callout(?:\s[^"]*)?"/

  # Link the callout stylesheet ahead of the first callout blockquote;
  # input without one is returned byte-identical.
  def self.transform(html)
    text = html.to_s
    match = CALLOUT.match(text)
    return html unless match

    text[0...match.begin(0)] +
      "<link rel=\"stylesheet\" href=\"#{STYLESHEET}\">\n" +
      text[match.begin(0)..]
  end
end

if defined?(Jekyll::Hooks)
  Jekyll::Hooks.register :posts, :post_convert do |post|
    post.content = Callouts.transform(post.content)
  end
end
