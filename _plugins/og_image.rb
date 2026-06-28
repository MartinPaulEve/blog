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
  def self.excerpt_text(raw, limit = 240)
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

  # [width, height] for a PNG/JPEG/GIF file, parsed from its header, or nil.
  def self.image_dimensions(path)
    return nil unless path && File.exist?(path)

    data = File.binread(path)
    if data[0, 8] == "\x89PNG\r\n\x1a\n".b
      [data[16, 4].unpack1("N"), data[20, 4].unpack1("N")]
    elsif data[0, 6] == "GIF87a".b || data[0, 6] == "GIF89a".b
      [data[6, 2].unpack1("v"), data[8, 2].unpack1("v")]
    elsif data[0, 2] == "\xFF\xD8".b
      jpeg_dimensions(data)
    end
  end

  def self.jpeg_dimensions(data)
    i = 2
    while i < data.bytesize - 8
      return nil unless data.getbyte(i) == 0xFF

      marker = data.getbyte(i + 1)
      if marker >= 0xC0 && marker <= 0xCF && ![0xC4, 0xC8, 0xCC].include?(marker)
        return [data[i + 7, 2].unpack1("n"), data[i + 5, 2].unpack1("n")]
      end

      seg_len = data[i + 2, 2].unpack1("n")
      break unless seg_len

      i += 2 + seg_len
    end
    nil
  end

  # A wide hero banner (aspect >= max_aspect) does not suit the portrait card
  # slot, so it is dropped in favour of the full-width text layout. Unknown
  # dimensions => not a banner (show the image).
  def self.wide_banner?(path, max_aspect = 2.0)
    dims = image_dimensions(path)
    return false unless dims

    w, h = dims
    h.to_i.positive? && (w.to_f / h) >= max_aspect
  end

  # Assemble the 1200x630 card HTML. image_uri nil => full-width text layout.
  def self.render_html(pill:, title:, snippet:, button:, image_uri:, image_aspect: nil, fonts:)
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
    # A portrait image gets a taller card sized to its own aspect ratio so the
    # whole image shows (no crop, no letterbox); landscape/square keep the
    # standard landscape card.
    portrait = has_image && image_aspect && image_aspect < 0.9
    card_style = portrait ? "width:#{(534 * image_aspect).round}px;height:534px" : "width:100%;height:454px"
    snippet_html = snippet.to_s.empty? ? "" :
      %(<p class="snippet">#{html_escape(snippet)}</p>)
    right_html = has_image ?
      %(<div class="right"><div class="imgcard" style="#{card_style}"><img src="#{image_uri}" alt=""></div></div>) : ""

    <<~HTML
      <!doctype html><html><head><meta charset="utf-8"><style>
      #{faces}
      *{margin:0;padding:0;box-sizing:border-box}
      html,body{width:1200px;height:630px}
      .card{position:relative;width:1200px;height:630px;background:#0b0b0b;
        overflow:hidden;font-family:'IBM Plex Mono',ui-monospace,monospace}
      .bg{position:absolute;inset:0;overflow:hidden}
      .wedge{position:absolute;top:-12%;right:-6%;width:56%;height:124%;
        background:linear-gradient(160deg,#b3122a,#8c0d20);
        transform:skewX(-4deg);transform-origin:top right}
      .line{position:absolute;left:-30%;width:160%;height:3px;background:#e63946;
        opacity:.55;transform:rotate(-4deg)}
      .line1{top:16%}.line2{top:84%}
      .content{position:relative;display:flex;width:1200px;height:630px}
      .left{width:50%;padding:72px 64px;display:flex;flex-direction:column;
        justify-content:center}
      .og-full .left{width:50%}
      .pill{align-self:flex-start;background:#b3122a;color:#fff;font-weight:600;
        font-size:22px;padding:11px 24px;border-radius:999px;letter-spacing:.01em}
      .title{font-family:'Fraunces',Georgia,serif;font-weight:600;color:#fff;
        font-size:60px;line-height:1.07;margin:30px 0 20px;
        display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
      .snippet{color:#f6f4f0;font-size:20px;line-height:1.4;max-width:94%;
        display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
      .btn{align-self:flex-start;margin-top:36px;background:#b3122a;color:#fff;
        font-weight:600;font-size:22px;padding:16px 32px;border-radius:10px}
      .right{width:50%;position:relative;display:flex;align-items:center;
        justify-content:center;padding:48px 56px 48px 0}
      .imgcard{border-radius:24px;overflow:hidden;
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
require "open3"
require "tmpdir"

if defined?(Jekyll::Generator)
module Jekyll
  # Renders one social card per in-scope document, caches it outside _site, and
  # serves a copy from <dest>/images/og/. The renderer (headless Chrome) and
  # cropper (ImageMagick) are injectable so the wiring tests run without them.
  class OgImageGenerator < Generator
    safe false
    priority :low

    OG_DEST_DIR = "images/og".freeze
    CACHE_DIR   = ".og_cache".freeze

    attr_writer :renderer, :cropper

    def renderer
      @renderer ||= method(:chrome_render)
    end

    def cropper
      @cropper ||= method(:imagemagick_crop)
    end

    def generate(site)
      @site = site
      @fonts = load_fonts
      base_url = site.config["url"].to_s

      documents(site).each do |doc, is_post|
        next unless html_output?(doc)

        slug = OgImage.slug(doc.url)
        og_cache = cache_path("#{slug}.png")
        tw_cache = cache_path("#{slug}.twitter.png")
        next unless og_cache && tw_cache

        ensure_cached(doc, is_post, og_cache, tw_cache)
        next unless File.exist?(og_cache)

        copy_to_dest(og_cache, "#{slug}.png")
        copy_to_dest(tw_cache, "#{slug}.twitter.png") if File.exist?(tw_cache)

        doc.data["og_image"] = OgImage.asset_url(base_url, slug)
        doc.data["og_image_twitter"] = OgImage.asset_url(base_url, slug, twitter: true)
      end
    end

    private

    # [doc, is_post] for every post and in-scope page.
    def documents(site)
      pairs = site.posts.docs.map { |d| [d, true] }
      site.pages.each do |p|
        pairs << [p, false] if OgImage.scope_layout?(p.data["layout"])
      end
      pairs
    end

    def html_output?(doc)
      ext = doc.respond_to?(:output_ext) ? doc.output_ext : File.extname(doc.url)
      ext == ".html" || ext == ".htm"
    end

    def cache_path(name)
      return nil unless @site.respond_to?(:source) && @site.source

      File.join(@site.source, CACHE_DIR, name)
    end

    def ensure_cached(doc, is_post, og_cache, tw_cache)
      unless File.exist?(og_cache)
        html = build_html(doc, is_post)
        FileUtils.mkdir_p(File.dirname(og_cache))
        renderer.call(html, OgImage::CARD_W, OgImage::CARD_H, og_cache)
      end
      return unless File.exist?(og_cache) && !File.exist?(tw_cache)

      cropper.call(og_cache, tw_cache, OgImage::TW_W, OgImage::TW_H)
    end

    def build_html(doc, is_post)
      image_uri, image_aspect = feature_image(doc)
      OgImage.render_html(
        pill: OgImage::SITE_AUTHOR,
        title: OgImage.title_for(doc.data["title"], @site.config["title"]),
        snippet: OgImage.excerpt_text(snippet_source(doc)),
        button: OgImage.button_label(is_post),
        image_uri: image_uri,
        image_aspect: image_aspect,
        fonts: @fonts,
      )
    end

    # The snippet text. The home page, and any document whose front matter sets
    # `og_card_snippet: job`, use the site owner's job title; `og_card_snippet`
    # may also be any literal string. Otherwise posts use their auto-excerpt and
    # pages fall back to their content.
    def snippet_source(doc)
      custom = doc.data["og_card_snippet"]
      if custom == "job" || doc.data["layout"] == "home"
        owner = @site.config["owner"]
        return owner["job"] if owner.is_a?(Hash) && owner["job"]
      end
      return custom if custom.is_a?(String) && custom != "job" && !custom.strip.empty?

      excerpt = doc.data["excerpt"].to_s
      return excerpt unless excerpt.strip.empty?

      doc.respond_to?(:content) ? doc.content.to_s : ""
    end

    # [data_uri, aspect] for the card image, or [nil, nil] for full-width text.
    def feature_image(doc)
      path = feature_path(doc)
      return [nil, nil] unless path

      dims = OgImage.image_dimensions(path)
      aspect = dims && dims[1].to_i.positive? ? dims[0].to_f / dims[1] : nil
      [OgImage.data_uri(path), aspect]
    end

    # Absolute path of the image to embed, or nil for the full-width layout.
    def feature_path(doc)
      override = doc.data["og_card_image"]
      if override.is_a?(String) && !override.empty? && !override.include?("http")
        return File.join(@site.source, "images", override)
      end

      feature = doc.data["image"] && doc.data["image"]["feature"]
      return nil unless feature.is_a?(String) && !feature.empty?
      return nil if feature.include?("http") # only embed local files

      path = File.join(@site.source, "images", feature)
      return nil if OgImage.wide_banner?(path) # banners suit the full-width layout

      path
    end

    def load_fonts
      return {} unless @site.respond_to?(:source) && @site.source

      dir = File.join(@site.source, "_og", "fonts")
      {
        fraunces: OgImage.data_uri(File.join(dir, "Fraunces.ttf"), "font/ttf"),
        mono_regular: OgImage.data_uri(File.join(dir, "IBMPlexMono-Regular.ttf"), "font/ttf"),
        mono_semibold: OgImage.data_uri(File.join(dir, "IBMPlexMono-SemiBold.ttf"), "font/ttf"),
      }
    end

    def copy_to_dest(src, name)
      dest_dir = File.join(@site.dest, OG_DEST_DIR)
      FileUtils.mkdir_p(dest_dir)
      FileUtils.cp(src, File.join(dest_dir, name))
      @site.static_files << OgImageFile.new(@site, @site.dest, OG_DEST_DIR, name)
    end

    CHROME_BINS = %w[google-chrome google-chrome-stable chromium chromium-browser].freeze

    def chrome_render(html, width, height, out_path)
      bin = CHROME_BINS.find { |b| system("command -v #{b} >/dev/null 2>&1") }
      raise "no Chrome binary found (tried: #{CHROME_BINS.join(', ')})" unless bin

      Dir.mktmpdir("og") do |tmp|
        html_path = File.join(tmp, "card.html")
        File.write(html_path, html)
        cmd = [bin, "--headless=new", "--disable-gpu", "--no-sandbox",
               "--hide-scrollbars", "--force-device-scale-factor=1",
               "--default-background-color=00000000",
               "--window-size=#{width},#{height}",
               "--screenshot=#{out_path}", "file://#{html_path}"]
        _out, err, status = Open3.capture3(*cmd)
        unless status.success? && File.exist?(out_path)
          Jekyll.logger.warn "OgImage:", "render failed for #{out_path}: #{err.lines.last}"
        end
      end
    end

    def imagemagick_crop(src_path, out_path, width, height)
      cmd = ["convert", src_path, "-gravity", "center",
             "-crop", "#{width}x#{height}+0+0", "+repage", out_path]
      _out, err, status = Open3.capture3(*cmd)
      unless status.success? && File.exist?(out_path)
        Jekyll.logger.warn "OgImage:", "crop failed for #{out_path}: #{err.lines.last}"
        FileUtils.cp(src_path, out_path) # fall back to the uncropped image
      end
    end
  end

  class OgImageFile < StaticFile
    def modified?; false; end
    def write(_dest); true; end
  end
end
end
