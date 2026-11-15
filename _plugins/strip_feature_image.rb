# Strips a post's feature image from its already-rendered ({{ content }}) HTML,
# so a layout can show the feature once (in its own hero slot) without the same
# image appearing again inline in the body. The pure StripFeatureImage.strip
# method carries no Jekyll dependency and is unit-testable in plain Ruby; a thin
# Liquid filter (registered only when Liquid is present) wires it into the build.
module StripFeatureImage
  # Remove every <img> whose src ends with `feature`, then clean up the empty
  # <a>/<p> wrappers kramdown and Markdown links leave behind.
  def self.strip(html, feature)
    return html if feature.nil? || feature.to_s.strip.empty?

    # Remove any <img> whose src ends with the (full) feature value. Matching is
    # attribute-order independent and quote-agnostic; anchoring the feature to
    # the end of the src keeps sub-paths precise (won't hit a same-named file in
    # another folder).
    img = /<img\b[^>]*\bsrc=["'][^"']*#{Regexp.escape(feature.to_s)}["'][^>]*\/?>/i
    out = html.to_s.gsub(img, "")

    # Collapse the now-empty wrappers left behind, but only when whitespace-only:
    # anchors first (they sit inside paragraphs), then paragraphs. An empty
    # anchor whose href is a fragment is not an image wrapper but a paragraph
    # anchor link (_plugins/paragraph_anchors.rb) and stays; a paragraph left
    # holding nothing but such anchors was the image's own and goes with it.
    out = out.gsub(/<a\b(?![^>]*\bhref=["']#)[^>]*>\s*<\/a>/i, "")
    out.gsub(/<p\b[^>]*>(?:\s*<a\b[^>]*\bhref=["']#[^>]*>\s*<\/a>)*\s*<\/p>/i, "")
  end
end

if defined?(Liquid)
  module StripFeatureImageFilter
    def strip_feature_image(html, feature)
      StripFeatureImage.strip(html.to_s, feature)
    end
  end

  Liquid::Template.register_filter(StripFeatureImageFilter)
end
