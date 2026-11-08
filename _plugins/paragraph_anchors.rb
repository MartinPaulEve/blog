# Per-paragraph and per-heading anchor links for posts. Every <p> and
# <h1>-<h6> in a converted post gets an id and, appended after its text, an
# empty <a class="anchor-link" href="#id"> that assets/css/anchors.css shows
# on hover/focus and assets/js/anchors.js turns into a copy-link button.
#
# Ids must stay put between builds or shared links rot, so a paragraph's id
# is derived from its own text ("p-" + the first ten hex digits of the
# SHA-256 of its tag-stripped, whitespace-collapsed content); a paragraph
# that holds no text (an image) hashes its inner HTML instead. Headings keep
# the id kramdown already gave them (auto_ids), and only an id-less heading
# gets a generated "h-..." one. Identical paragraphs in one post are told
# apart by a positional "-2", "-3" suffix, which is stable as long as their
# order is.
#
# The anchor is appended, never prepended, so the drop-cap ::first-letter on
# a post's opening paragraph still lands on the prose. It carries no text, so
# feeds, the search index, excerpts and the gemtext mirror see nothing new.
# The anchors are print-invisible (display:none in anchors.css) and
# _plugins/pdf_pages.rb strips them, the generated ids and the two asset
# tags from the PDF cache key, so this transform re-renders no PDF.
#
# The hook runs at low priority so it sees the output of the other
# post_convert transforms (content warnings wrap headings in <summary>,
# callouts tag blockquotes) rather than getting in their way.
#
# ParagraphAnchors holds the pure logic (no Jekyll dependency) so it can be
# unit-tested in isolation; the hook below wires it into the build.

require "digest"

module ParagraphAnchors
  ANCHOR_CLASS = "anchor-link".freeze
  ELEMENT = %r{<(p|h[1-6])(\s[^>]*)?>(.*?)</\1>}mi
  ID_ATTR = /\sid="([^"]*)"/i
  HASH_LENGTH = 10

  # Rewrite converted post HTML, giving every paragraph and heading an id
  # and a trailing anchor link. Input with neither is returned as is.
  def self.transform(html)
    text = html.to_s
    taken = text.scan(/\sid="([^"]+)"/i).flatten
    counts = Hash.new(0)

    text.gsub(ELEMENT) do
      tag, attrs, inner = Regexp.last_match.captures
      attrs = attrs.to_s
      id = attrs[ID_ATTR, 1]
      if id.nil? || id.empty?
        id = unique_id(generated_id(tag, inner), taken, counts)
        attrs = attrs.sub(ID_ATTR, "") + " id=\"#{id}\""
      end
      "<#{tag}#{attrs}>#{inner}#{anchor(id, tag)}</#{tag}>"
    end
  end

  # "p-<hash>" for paragraphs, "h-<hash>" for headings; the hash is of the
  # visible text, falling back to the markup when there is none.
  def self.generated_id(tag, inner)
    prefix = tag.downcase.start_with?("h") ? "h" : "p"
    key = plain_text(inner)
    key = inner.strip if key.empty?
    "#{prefix}-#{Digest::SHA256.hexdigest(key)[0, HASH_LENGTH]}"
  end

  def self.plain_text(html)
    html.gsub(/<[^>]+>/, " ").gsub(/\s+/, " ").strip
  end

  # First occurrence keeps the bare id; repeats take -2, -3, ...; anything
  # that would collide with an authored id in the document steps past it.
  def self.unique_id(base, taken, counts)
    counts[base] += 1
    candidate = counts[base] == 1 ? base : "#{base}-#{counts[base]}"
    while taken.include?(candidate)
      counts[base] += 1
      candidate = "#{base}-#{counts[base]}"
    end
    taken << candidate
    candidate
  end

  def self.anchor(id, tag)
    kind = tag.downcase.start_with?("h") ? "heading" : "paragraph"
    "<a class=\"#{ANCHOR_CLASS}\" href=\"##{id}\" " \
      "aria-label=\"Link to this #{kind}\"></a>"
  end
end

if defined?(Jekyll::Hooks)
  Jekyll::Hooks.register :posts, :post_convert, priority: :low do |post|
    post.content = ParagraphAnchors.transform(post.content)
  end
end
