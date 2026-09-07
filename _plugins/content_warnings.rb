# Content-warning disclosures for post sections. A heading that ends with a
# bracketed marker:
#
#   ### Severe bowel dysmotility (~2019-) [content warning: discusses bowels]
#
# comes out of the build as a native <details>/<summary> block: the heading
# and a "Content warning: discusses bowels" label stay visible, and the
# section below (up to the next heading of the same or higher level) is
# collapsed until the reader clicks the heading. No JavaScript is involved.
#
# The PDF edition prints through assets/css/content-warning.css, whose
# @media print rules keep the warning label visible but expand the section
# (via ::details-content, verified against the site's headless-Chromium
# print pipeline). The stylesheet is linked from inside the transformed
# content itself and stays outside the PDF-hashed stylesheet set, and the
# transform returns unmarked posts byte-identical, so no existing PDF's
# cache key moves.
#
# ContentWarnings holds the pure logic (no Jekyll dependency) so it can be
# unit-tested in isolation; the hook below wires it into the build.

module ContentWarnings
  STYLESHEET = "/assets/css/content-warning.css".freeze
  MARKER = /\s*\[content warning:\s*([^\]]+)\]\s*\z/i
  HEADING = %r{<h([1-6])([^>]*)>(.*?)</h\1>}mi
  TOC_LINK = %r{(<a href="#[^"]*" id="markdown-toc-[^"]*">)(.*?)(</a>)}m

  # Rewrite converted post HTML, collapsing marked sections; unmarked
  # input is returned byte-identical.
  def self.transform(html)
    text = html.to_s
    return html unless text =~ /\[content warning:/i

    result = +""
    pos = 0
    changed = false
    while (heading = HEADING.match(text, pos))
      marker = heading[3].match(MARKER)
      unless marker
        result << text[pos...heading.end(0)]
        pos = heading.end(0)
        next
      end
      changed = true
      title = heading[3].sub(MARKER, "")
      section_end = section_end(text, heading.end(0), heading[1].to_i)
      result << text[pos...heading.begin(0)]
      result << disclosure(heading[1], heading[2], title,
                           marker[1].strip,
                           text[heading.end(0)...section_end])
      pos = section_end
    end
    result << text[pos..]
    return html unless changed

    inject_stylesheet(clean_toc(result))
  end

  # Where a marked section stops: the next heading at the same or a higher
  # level, or the end of the post.
  def self.section_end(text, from, level)
    pos = from
    while (heading = HEADING.match(text, pos))
      return heading.begin(0) if heading[1].to_i <= level

      pos = heading.end(0)
    end
    text.length
  end

  def self.disclosure(level, attrs, title, warning, body)
    "<details class=\"content-warning\">\n" \
      "<summary><h#{level}#{attrs}>#{title}</h#{level}> " \
      "<span class=\"cw-label\">Content warning: #{warning}</span>" \
      "</summary>\n" \
      "<div class=\"cw-body\">\n#{body.strip}\n</div>\n" \
      "</details>\n"
  end

  # The kramdown {:toc} renders before this transform, so its link labels
  # carry the marker text; strip it there too.
  def self.clean_toc(html)
    html.gsub(TOC_LINK) do
      open_tag, label, close_tag = Regexp.last_match.captures
      "#{open_tag}#{label.sub(MARKER, '')}#{close_tag}"
    end
  end

  # One stylesheet link, riding inside the content just before the first
  # disclosure — never in _head.html, whose markup is PDF-cache-hashed.
  def self.inject_stylesheet(html)
    html.sub(
      '<details class="content-warning">',
      "<link rel=\"stylesheet\" href=\"#{STYLESHEET}\">\n" \
      '<details class="content-warning">')
  end
end

if defined?(Jekyll::Hooks)
  Jekyll::Hooks.register :posts, :post_convert do |post|
    post.content = ContentWarnings.transform(post.content)
  end
end
