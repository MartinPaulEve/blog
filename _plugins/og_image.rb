# Build-time Open Graph / Twitter card images (1200x630 / 1200x628) for posts
# and main content pages. The pure builders below carry no Jekyll dependency so
# they can be unit-tested in plain Ruby; Jekyll::OgImageGenerator (defined only
# inside Jekyll) wires them into the build.
module OgImage
  CARD_W = 1200
  CARD_H = 630
  TW_W   = 1200
  TW_H   = 628

  SITE_AUTHOR   = "eve.gd: Martin Paul Eve".freeze
  SCOPE_LAYOUTS = %w[home page post-index category].freeze

  # Filesystem-safe cache slug from a document's output URL.
  def self.slug(url)
    s = url.to_s
           .sub(%r{\Ahttps?://[^/]+}, "")
           .sub(%r{index\.html\z}, "")
           .sub(%r{\.html\z}, "")
           .gsub(%r{\A/|/\z}, "")
    s = "index" if s.empty?
    s.gsub(%r{[^a-zA-Z0-9._-]+}, "-")
  end

  def self.scope_layout?(layout)
    SCOPE_LAYOUTS.include?(layout.to_s)
  end

  def self.button_label(is_post)
    is_post ? "Read post" : "Read more"
  end

  def self.title_for(doc_title, site_title)
    t = doc_title.to_s.strip
    t.empty? ? site_title.to_s : t
  end

  def self.asset_url(base_url, slug, twitter: false)
    name = twitter ? "#{slug}.twitter.png" : "#{slug}.png"
    File.join(base_url.to_s, "images", "og", name)
  end

  IMAGE_MIME = {
    ".png" => "image/png", ".jpg" => "image/jpeg", ".jpeg" => "image/jpeg",
    ".gif" => "image/gif", ".webp" => "image/webp", ".svg" => "image/svg+xml"
  }.freeze

  # Plain-text snippet: strip tags/entities, collapse whitespace, truncate on a
  # word boundary with an ellipsis.
  def self.excerpt_text(raw, limit = 160)
    text = raw.to_s.gsub(/<[^>]+>/, " ").gsub(/&[#a-zA-Z0-9]+;/, " ").gsub(/\s+/, " ").strip
    return "" if text.empty?
    return text if text.length <= limit

    text[0, limit].sub(/\s+\S*\z/, "").rstrip + "…"
  end

  # base64 data URI for a local file, or nil when absent.
  def self.data_uri(path, mime = nil)
    return nil unless path && File.exist?(path)

    mime ||= IMAGE_MIME[File.extname(path).downcase] || "application/octet-stream"
    "data:#{mime};base64,#{Base64.strict_encode64(File.binread(path))}"
  end

  def self.html_escape(text)
    text.to_s.gsub("&", "&amp;").gsub("<", "&lt;").gsub(">", "&gt;").gsub('"', "&quot;")
  end
end

require "json"
require "base64"
require "fileutils"
