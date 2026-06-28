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

  # Assemble the 1200x630 card HTML. image_uri nil => full-width text layout.
  def self.render_html(pill:, title:, snippet:, button:, image_uri:, fonts:)
    faces = +""
    if fonts[:fraunces]
      faces << "@font-face{font-family:'Fraunces';font-weight:100 900;" \
               "src:url(#{fonts[:fraunces]}) format('truetype')}"
    end
    if fonts[:mono_regular]
      faces << "@font-face{font-family:'IBM Plex Mono';font-weight:400;" \
               "src:url(#{fonts[:mono_regular]}) format('truetype')}"
    end
    if fonts[:mono_semibold]
      faces << "@font-face{font-family:'IBM Plex Mono';font-weight:600;" \
               "src:url(#{fonts[:mono_semibold]}) format('truetype')}"
    end

    has_image = !image_uri.nil? && !image_uri.empty?
    full = has_image ? "" : " og-full"
    snippet_html = snippet.to_s.empty? ? "" :
      %(<p class="snippet">#{html_escape(snippet)}</p>)
    right_html = has_image ?
      %(<div class="right"><div class="imgcard"><img src="#{image_uri}" alt=""></div></div>) : ""

    <<~HTML
      <!doctype html><html><head><meta charset="utf-8"><style>
      #{faces}
      *{margin:0;padding:0;box-sizing:border-box}
      html,body{width:1200px;height:630px}
      .card{position:relative;width:1200px;height:630px;background:#0b0b0b;
        overflow:hidden;font-family:'IBM Plex Mono',ui-monospace,monospace}
      .bg{position:absolute;inset:0;overflow:hidden}
      .wedge{position:absolute;top:-12%;right:-6%;width:54%;height:124%;
        background:linear-gradient(160deg,#b3122a,#8c0d20);
        transform:skewX(-4deg);transform-origin:top right}
      .line{position:absolute;left:-30%;width:160%;height:3px;background:#e63946;
        opacity:.55;transform:rotate(-4deg)}
      .line1{top:16%}.line2{top:84%}
      .content{position:relative;display:flex;width:1200px;height:630px}
      .left{width:62%;padding:72px 64px;display:flex;flex-direction:column;
        justify-content:center}
      .og-full .left{width:100%}
      .pill{align-self:flex-start;background:#b3122a;color:#fff;font-weight:600;
        font-size:22px;padding:11px 24px;border-radius:999px;letter-spacing:.01em}
      .title{font-family:'Fraunces',Georgia,serif;font-weight:600;color:#fff;
        font-size:60px;line-height:1.07;margin:30px 0 20px;
        display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
      .snippet{color:#b3ada3;font-size:24px;line-height:1.45;max-width:94%;
        display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
      .btn{align-self:flex-start;margin-top:36px;background:#b3122a;color:#fff;
        font-weight:600;font-size:22px;padding:16px 32px;border-radius:10px}
      .right{width:38%;position:relative;display:flex;align-items:center;
        justify-content:center;padding:48px 56px 48px 0}
      .imgcard{width:100%;height:454px;border-radius:24px;overflow:hidden;
        box-shadow:0 28px 60px rgba(0,0,0,.55);background:#1a1a1a}
      .imgcard img{width:100%;height:100%;object-fit:cover;display:block}
      </style></head>
      <body><div class="card#{full}">
      <div class="bg"><div class="wedge"></div>
        <div class="line line1"></div><div class="line line2"></div></div>
      <div class="content">
        <div class="left">
          <span class="pill">#{html_escape(pill)}</span>
          <h1 class="title">#{html_escape(title)}</h1>
          #{snippet_html}
          <span class="btn">#{html_escape(button)}</span>
        </div>
        #{right_html}
      </div>
      </div></body></html>
    HTML
  end
end

require "json"
require "base64"
require "fileutils"
