# Build-time PDF editions of posts and content pages, rendered headlessly from
# the written site through the print stylesheet, cached in .pdf_cache/ (keyed
# by a build-noise-insensitive content hash) and served from /PDF/<slug>.pdf.
#
# The PdfPages module holds the pure builders (no Jekyll dependency) so they
# can be unit-tested in isolation. Inside Jekyll:
#   * PdfPagesGenerator (priority :normal, so it runs before the :low
#     signposting generator) stamps `pdf_url` on each in-scope document and
#     appends the PDF to its `pdf` data, which signposting turns into a typed
#     rel="item" link; _head.html renders citation_pdf_url, a typed
#     rel="alternate" link, and a schema.org MediaObject encoding from the
#     same value.
#   * A :site :post_write hook serves the freshly written _site over a local
#     HTTP server and prints each page to PDF with headless Chrome (the print
#     stylesheet governs the layout). Renders are cached in .pdf_cache/ so an
#     unchanged page never re-renders; set JEKYLL_SKIP_PDFS=1 to skip the pass
#     entirely (it also skips itself, with a warning, when Chrome is absent).

require_relative "og_image"

require "digest"
require "fileutils"

module PdfPages
  PDF_DIR = "PDF".freeze
  SCOPE_LAYOUTS = %w[post page].freeze

  def self.scope_layout?(layout)
    SCOPE_LAYOUTS.include?(layout.to_s)
  end

  # Same slug convention as the OG card images, so every derivative of a page
  # shares one name.
  def self.slug(url)
    OgImage.slug(url)
  end

  def self.pdf_url(base_url, slug)
    File.join(base_url.to_s, PDF_DIR, "#{slug}.pdf")
  end

  # Cache key for a rendered page, insensitive to build noise that cannot
  # affect the printed output: the ?v= asset cache-busters change every build,
  # and the related-posts sidebar changes whenever any post is published (print
  # CSS hides the sidebar).
  def self.normalize_html(html)
    html.to_s
        .gsub(/\?v=\d+/, "")
        .gsub(%r{<aside class="post-sidebar">.*?</aside>}m, "")
  end

  def self.content_hash(html)
    Digest::SHA256.hexdigest(normalize_html(html))
  end

  # Renders a set of pages through an injectable renderer, keeping a PDF +
  # content-hash pair per slug in cache_dir and copying current PDFs into
  # dest_dir. A failed render leaves no hash behind, so it is retried on the
  # next run.
  class Batch
    def initialize(cache_dir:, dest_dir:, renderer:)
      @cache_dir = cache_dir
      @dest_dir = dest_dir
      @renderer = renderer
      FileUtils.mkdir_p(@cache_dir)
      FileUtils.mkdir_p(@dest_dir)
    end

    def process(pages)
      stats = { rendered: 0, cached: 0, failed: 0 }
      pages.each do |page|
        pdf = File.join(@cache_dir, "#{page[:slug]}.pdf")
        hash_file = File.join(@cache_dir, "#{page[:slug]}.hash")
        hash = PdfPages.content_hash(page[:html])

        if fresh?(pdf, hash_file, hash)
          stats[:cached] += 1
        elsif @renderer.call(page, pdf) && File.exist?(pdf)
          File.write(hash_file, hash)
          stats[:rendered] += 1
        else
          FileUtils.rm_f(hash_file)
          stats[:failed] += 1
          next
        end

        FileUtils.cp(pdf, File.join(@dest_dir, "#{page[:slug]}.pdf"))
      end
      stats
    end

    private

    def fresh?(pdf, hash_file, hash)
      File.exist?(pdf) && File.exist?(hash_file) && File.read(hash_file) == hash
    end
  end
end

if defined?(Jekyll::Generator)
module Jekyll
  # Stamps pdf_url (and the signposting `pdf` item) on every in-scope document
  # so head metadata and Link headers can advertise the PDF edition that the
  # post_write hook will render.
  class PdfPagesGenerator < Generator
    safe false
    priority :normal

    def generate(site)
      base_url = site.config["url"].to_s
      PdfPagesScope.documents(site).each do |doc|
        url = PdfPages.pdf_url(base_url, PdfPages.slug(doc.url))
        doc.data["pdf_url"] = url
        doc.data["pdf"] = Array(doc.data["pdf"]) + [url]
      end
    end
  end

  # Shared scope logic between the generator and the post_write hook: pretty
  # URLs (directory indexes) whose layout opts into the print stylesheet.
  module PdfPagesScope
    def self.documents(site)
      docs = site.posts.docs + site.pages
      docs.select do |doc|
        doc.url.to_s.end_with?("/") && PdfPages.scope_layout?(doc.data["layout"])
      end
    end
  end
end
end

# The rendering pass proper: only wired up inside a real Jekyll build.
if defined?(Jekyll::Hooks)
module Jekyll
  module PdfPagesRunner
    CACHE_DIR = ".pdf_cache".freeze
    THREADS = 4

    CHROME_BINS = %w[google-chrome google-chrome-stable chromium chromium-browser].freeze

    def self.run(site)
      return if ENV["JEKYLL_SKIP_PDFS"]
      return unless site.respond_to?(:source) && site.source

      chrome = CHROME_BINS.find { |b| system("command -v #{b} >/dev/null 2>&1") }
      cache_dir = File.join(site.source, CACHE_DIR)
      dest_dir = File.join(site.dest, PdfPages::PDF_DIR)

      pages = collect_pages(site)
      unless chrome
        copy_cache_only(cache_dir, dest_dir, pages)
        Jekyll.logger.warn "PdfPages:", "Chrome not found; served cached PDFs only"
        return
      end

      with_server(site.dest) do |port|
        renderer = chrome_renderer(chrome, port)
        pool = ThreadPoolBatch.new(cache_dir: cache_dir, dest_dir: dest_dir,
                                   renderer: renderer, threads: THREADS)
        stats = pool.process(pages)
        Jekyll.logger.info "PdfPages:",
                           "#{stats[:rendered]} rendered, #{stats[:cached]} cached" \
                           "#{stats[:failed].positive? ? ", #{stats[:failed]} FAILED" : ''}"
      end
    end

    def self.collect_pages(site)
      PdfPagesScope.documents(site).map do |doc|
        path = File.join(site.dest, doc.url, "index.html")
        next nil unless File.exist?(path)

        { slug: PdfPages.slug(doc.url), url: doc.url, html: File.read(path) }
      end.compact
    end

    def self.copy_cache_only(cache_dir, dest_dir, pages)
      FileUtils.mkdir_p(dest_dir)
      pages.each do |page|
        pdf = File.join(cache_dir, "#{page[:slug]}.pdf")
        FileUtils.cp(pdf, File.join(dest_dir, "#{page[:slug]}.pdf")) if File.exist?(pdf)
      end
    end

    # Serve the written site so the pages render with their real asset URLs.
    def self.with_server(dest)
      require "socket"
      port = TCPServer.open("127.0.0.1", 0) { |s| s.addr[1] }
      pid = Process.spawn("python3", "-m", "http.server", port.to_s,
                          "--bind", "127.0.0.1", "--directory", dest,
                          out: File::NULL, err: File::NULL)
      wait_for_port(port)
      yield port
    ensure
      if pid
        Process.kill("TERM", pid)
        Process.wait(pid)
      end
    end

    def self.wait_for_port(port, tries = 50)
      tries.times do
        TCPSocket.new("127.0.0.1", port).close
        return true
      rescue Errno::ECONNREFUSED
        sleep 0.1
      end
      raise "PDF server did not start on port #{port}"
    end

    def self.chrome_renderer(chrome, port)
      require "open3"
      lambda do |page, out_path|
        cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
               "--no-pdf-header-footer",
               "--print-to-pdf=#{out_path}",
               "http://127.0.0.1:#{port}#{page[:url]}"]
        _out, err, status = Open3.capture3(*cmd)
        ok = status.success? && File.exist?(out_path)
        Jekyll.logger.warn "PdfPages:", "render failed for #{page[:slug]}: #{err.lines.last}" unless ok
        ok
      end
    end

    # A Batch that fans page renders out over a small thread pool (Chrome
    # start-up dominates the cost); cache bookkeeping stays in PdfPages::Batch,
    # one instance per thread over a disjoint slice of the pages.
    class ThreadPoolBatch
      def initialize(cache_dir:, dest_dir:, renderer:, threads:)
        @cache_dir = cache_dir
        @dest_dir = dest_dir
        @renderer = renderer
        @threads = threads
      end

      def process(pages)
        slices = pages.each_slice((pages.length / @threads.to_f).ceil.clamp(1, pages.length)).to_a
        totals = { rendered: 0, cached: 0, failed: 0 }
        return totals if pages.empty?

        slices.map do |slice|
          Thread.new do
            PdfPages::Batch.new(cache_dir: @cache_dir, dest_dir: @dest_dir,
                                renderer: @renderer).process(slice)
          end
        end.each do |t|
          stats = t.value
          totals.merge!(stats) { |_k, a, b| a + b }
        end
        totals
      end
    end
  end

  Hooks.register :site, :post_write do |site|
    PdfPagesRunner.run(site)
  end
end
end
