# FAIR Signposting (https://signposting.org/FAIR/) for posts and pages.
#
# Emits typed links so machines can navigate the scholarly objects on the site:
#   * Level 2 -- HTTP "Link" headers, generated as a per-directory .htaccess
#     (mod_headers) alongside each rendered page.
#   * Level 1 -- <link> elements in <head>, as a fallback, via the
#     _signposting.html include which calls Signposting.link_elements.
#
# The Signposting module holds the pure builders (no Jekyll dependency) so they
# can be unit-tested in isolation; SignpostingGenerator wires them into the
# build.
#
# Link relations follow the FAIR Signposting profile:
#   author      -> ORCID
#   cite-as     -> DOI (where present)
#   type        -> schema.org type(s)
#   license     -> content licence
#   describedby -> machine-readable metadata representation
#   item        -> content resource(s), where distinct from the landing page

module Signposting
  AUTHOR_ORCID = "https://orcid.org/0000-0002-5589-8511".freeze
  LICENSE_URL  = "https://creativecommons.org/licenses/by/4.0/".freeze

  # Build the ordered list of link relations from a metadata hash.
  #
  # meta keys (all optional):
  #   :author      => ORCID url                       -> author
  #   :doi         => "https://doi.org/..."           -> cite-as
  #   :types       => [schema.org url, ...]            -> one "type" link each
  #   :license     => licence url                      -> license
  #   :describedby => { url:, type:, profile: }         -> describedby
  #   :items       => [{ url:, type: }, ...]            -> one "item" link each
  #
  # Returns an array of { rel:, target:, params: { type:, profile: } } hashes
  # in signposting profile order.
  def self.relations(meta)
    rels = []
    rels << { rel: "author", target: meta[:author], params: {} } if meta[:author]
    rels << { rel: "cite-as", target: meta[:doi], params: {} } if meta[:doi]
    Array(meta[:types]).each do |type_url|
      rels << { rel: "type", target: type_url, params: {} }
    end
    rels << { rel: "license", target: meta[:license], params: {} } if meta[:license]
    if (db = meta[:describedby]) && db[:url]
      params = {}
      params[:type] = db[:type] if db[:type]
      params[:profile] = db[:profile] if db[:profile]
      rels << { rel: "describedby", target: db[:url], params: params }
    end
    Array(meta[:items]).each do |item|
      next unless item[:url]
      params = {}
      params[:type] = item[:type] if item[:type]
      rels << { rel: "item", target: item[:url], params: params }
    end
    rels
  end

  # Render the relations as an RFC 8288 Link header field-value (the value
  # only, without the "Link:" field-name prefix).
  def self.header_value(relations)
    relations.map { |r| link_value(r) }.join(", ")
  end

  # One RFC 8288 link-value: <target>; rel="..."; type="..."; profile="..."
  def self.link_value(rel)
    parts = ["<#{rel[:target]}>", %(rel="#{rel[:rel]}")]
    parts << %(type="#{rel[:params][:type]}") if rel[:params][:type]
    parts << %(profile="#{rel[:params][:profile]}") if rel[:params][:profile]
    parts.join("; ")
  end

  # Render an Apache .htaccess fragment that sets the Link header on the page
  # file (default index.html) and, when json_file is given, serves that file as
  # application/ld+json so the describedby target negotiates correctly.
  def self.htaccess(relations, target_file: "index.html", json_file: nil)
    escaped = header_value(relations).gsub('"', '\\"')
    lines = []
    lines << %(<Files "#{target_file}">)
    lines << %(Header set Link "#{escaped}")
    lines << "</Files>"
    if json_file
      lines << %(<Files "#{json_file}">)
      lines << "ForceType application/ld+json"
      lines << "</Files>"
    end
    lines.join("\n") + "\n"
  end

  # Render the relations as Level 1 <link> elements (an array of HTML strings).
  def self.link_elements(relations)
    relations.map do |r|
      attrs = [%(rel="#{r[:rel]}"), %(href="#{r[:target]}")]
      attrs << %(type="#{r[:params][:type]}") if r[:params][:type]
      "<link #{attrs.join(' ')}>"
    end
  end

  # --- DOI helpers ---------------------------------------------------------
  #
  # References given as a DOI (bare, or as a doi.org/dx.doi.org URL, or `doi:`)
  # are resolved against the registration agency's CSL-JSON content negotiation
  # and mapped to a schema.org citation node. The lookup/caching lives in the
  # generator; the pure helpers below are unit-testable without network access.

  DOI_PATTERN = %r{10\.\d{4,9}/[^\s"<>]+}

  # Strip any resolver prefix (https://doi.org/, dx.doi.org, doi:) so a DOI has
  # one canonical cache key regardless of how it was written.
  def self.normalize_doi(text)
    text.to_s.strip
        .sub(%r{\Ahttps?://(dx\.)?doi\.org/}i, "")
        .sub(%r{\Adoi:}i, "")
  end

  # A front-matter last_modified_at value as a YYYY-MM-DD string, or nil.
  def self.modified_date(value)
    text = value.to_s.strip
    return nil if text.empty?

    text[0, 10]
  end

  # True when the (possibly prefixed) string is a DOI.
  def self.doi?(text)
    normalize_doi(text).match?(/\A#{DOI_PATTERN}\z/)
  end

  # CSL-JSON `type` -> schema.org @type for the work itself.
  CSL_SCHEMA_TYPE = {
    "journal-article"     => "ScholarlyArticle",
    "article-journal"     => "ScholarlyArticle",
    "article"             => "Article",
    "proceedings-article" => "ScholarlyArticle",
    "paper-conference"    => "ScholarlyArticle",
    "posted-content"      => "ScholarlyArticle",
    "book"                => "Book",
    "monograph"           => "Book",
    "reference-book"      => "Book",
    "edited-book"         => "Book",
    "book-chapter"        => "Chapter",
    "chapter"             => "Chapter",
    "dataset"             => "Dataset",
    "report"              => "Report",
    "thesis"              => "Thesis",
    "dissertation"        => "Thesis",
    "webpage"             => "WebPage",
    "post-weblog"         => "BlogPosting",
  }.freeze

  def self.csl_schema_type(csl_type)
    CSL_SCHEMA_TYPE[csl_type] || "CreativeWork"
  end

  # Map a CSL-JSON metadata hash to a schema.org citation node.
  def self.csl_to_citation(csl, doi = nil)
    doi = normalize_doi(doi || csl["DOI"])
    node = { "@type" => csl_schema_type(csl["type"]) }
    node["@id"] = "https://doi.org/#{doi}" unless doi.empty?
    if (name = Array(csl["title"]).first) && !name.to_s.empty?
      node["name"] = name
    end
    node["url"] = "https://doi.org/#{doi}" unless doi.empty?
    if (authors = csl_authors(csl["author"]))
      node["author"] = authors
    end
    if (date = csl_date(csl["issued"] || csl["published"]))
      node["datePublished"] = date
    end
    node["inLanguage"] = csl["language"] if csl["language"]
    if (publisher = csl["publisher"]) && !publisher.to_s.empty?
      node["publisher"] = { "@type" => "Organization", "name" => publisher }
    end
    if (container = Array(csl["container-title"]).first) && !container.to_s.empty?
      node["isPartOf"] = { "@type" => csl_container_type(csl["type"]), "name" => container }
    end
    node
  end

  def self.csl_container_type(csl_type)
    case csl_type
    when "book-chapter", "chapter" then "Book"
    when "dataset" then "DataCatalog"
    else "Periodical"
    end
  end

  # CSL `issued` date-parts -> an ISO date string of the available precision.
  def self.csl_date(issued)
    parts = issued && issued["date-parts"] && issued["date-parts"].first
    return nil unless parts && parts.first

    year, month, day = parts
    out = format("%04d", year.to_i)
    out += format("-%02d", month.to_i) if month
    out += format("-%02d", day.to_i) if month && day
    out
  end

  # CSL authors -> one schema.org Person, or a list when there are several.
  def self.csl_authors(authors)
    nodes = Array(authors).map { |a| csl_person(a) }.compact
    return nil if nodes.empty?

    nodes.length == 1 ? nodes.first : nodes
  end

  def self.csl_person(author)
    name = author["literal"] || [author["given"], author["family"]].compact.join(" ").strip
    return nil if name.empty?

    node = { "@type" => "Person", "name" => name }
    if (orcid = author["ORCID"])
      node["@id"] = orcid
      node["identifier"] = orcid
    end
    if (affiliation = Array(author["affiliation"]).first) && affiliation["name"]
      node["affiliation"] = { "@type" => "Organization", "name" => affiliation["name"] }
    end
    node
  end

  # The repository deposit URL(s) from a document's front-matter `kcworks:`
  # value, ready for a schema.org archivedAt: nil when absent/blank, the
  # single URL as a scalar, or the list when several were given.
  def self.archived_at(value)
    urls = Array(value).map { |v| v.to_s.strip }.reject(&:empty?)
    return nil if urls.empty?

    urls.length == 1 ? urls.first : urls
  end

  CSL_ACCEPT = "application/vnd.citationstyles.csl+json".freeze
  USER_AGENT = "eve.gd-signposting (https://eve.gd; mailto:martin@eve.gd)".freeze

  # Fetch CSL-JSON for a DOI via doi.org content negotiation (works for both
  # Crossref- and DataCite-registered DOIs). Follows redirects to the agency.
  # Returns a parsed hash, or nil on any failure -- a missing reference must
  # never break the build.
  def self.fetch_doi_csl(doi, limit = 6)
    require "net/http"
    require "uri"

    uri = URI("https://doi.org/#{normalize_doi(doi)}")
    limit.times do
      req = Net::HTTP::Get.new(uri)
      req["Accept"] = CSL_ACCEPT
      req["User-Agent"] = USER_AGENT
      res = Net::HTTP.start(uri.hostname, uri.port, use_ssl: uri.scheme == "https") do |http|
        http.open_timeout = 15
        http.read_timeout = 30
        http.request(req)
      end

      case res
      when Net::HTTPSuccess
        return JSON.parse(res.body)
      when Net::HTTPRedirection
        uri = URI(res["location"])
      else
        return nil
      end
    end
    nil
  rescue StandardError, Timeout::Error
    nil
  end
end

require "json"
require "fileutils"

# Only define the Jekyll integration when running inside Jekyll (Jekyll::Generator
# is defined before plugins load). This lets the pure builders above be required
# and unit-tested in plain Ruby without the Jekyll gem.
if defined?(Jekyll::Generator)
module Jekyll
  # Wires the Signposting builders into the build: for every post and page it
  # writes a per-directory .htaccess (Level 2 Link header) and a metadata.json
  # (the describedby target), and stashes the Level 1 <link> HTML on the
  # document so the _signposting.html head include can render it.
  class SignpostingGenerator < Generator
    safe false
    priority :low

    DESCRIBEDBY_FILE = "metadata.json".freeze
    DESCRIBEDBY_TYPE = "application/ld+json".freeze
    SCHEMA_PROFILE   = "https://schema.org/".freeze
    DOI_CACHE_FILE   = ".doi_cache.json".freeze

    # Injectable so tests resolve DOIs without network access; defaults to live
    # doi.org content negotiation.
    attr_writer :doi_fetcher

    def doi_fetcher
      @doi_fetcher ||= ->(doi) { Signposting.fetch_doi_csl(doi) }
    end

    def generate(site)
      @site = site
      base_url = site.config["url"].to_s
      @doi_cache = DoiCache.new(doi_cache_path, doi_fetcher)

      (site.posts.docs + site.pages).each do |doc|
        next unless html_output?(doc)

        dir, target_file = location(doc)
        root_index = dir == "/" && target_file == "index.html"
        own_directory = target_file == "index.html" && dir != "/"

        page_url = File.join(base_url, dir)
        meta = metadata_for(doc, page_url, own_directory || root_index)
        relations = Signposting.relations(meta)

        # Level 1 fallback -- rendered in <head> by the include.
        doc.data["signposting_links"] = Signposting.link_elements(relations).join("\n    ")

        if root_index
          # The apex shares its directory with the site-wide redirects
          # .htaccess, so the signposting directives are appended to that file
          # rather than written fresh (which would drop the redirects).
          emit_root_signposting(dir, target_file, relations, doc, page_url)
        elsif own_directory
          # Documents that own their output directory get their own .htaccess
          # (Level 2 Link header) and metadata.json describedby target.
          write_file(dir, DESCRIBEDBY_FILE, json_metadata(doc, page_url))
          write_file(dir, ".htaccess",
                     Signposting.htaccess(relations,
                                          target_file: target_file,
                                          json_file: DESCRIBEDBY_FILE))
        end
      end

      @doi_cache.flush
    end

    private

    # Where the persistent DOI metadata cache lives (in the source tree, so it
    # is committed and re-used across builds); nil when there is no source.
    def doi_cache_path
      return nil unless @site.respond_to?(:source) && @site.source

      File.join(@site.source, @site.config["doi_cache"] || DOI_CACHE_FILE)
    end

    # Emit the apex (root) signposting: write metadata.json at the site root and
    # append the Link-header directives to the existing redirects .htaccess,
    # preserving the redirects. The source-copied .htaccess StaticFile is dropped
    # so site.write cannot overwrite the combined file we emit here.
    def emit_root_signposting(dir, target_file, relations, doc, page_url)
      write_file(dir, DESCRIBEDBY_FILE, json_metadata(doc, page_url))

      block = Signposting.htaccess(relations,
                                   target_file: target_file,
                                   json_file: DESCRIBEDBY_FILE)
      base = existing_root_htaccess
      combined = base.empty? ? block : "#{base.rstrip}\n\n#{block}"

      @site.static_files.reject! { |f| !f.is_a?(SignpostingFile) && root_htaccess?(f) }
      write_file(dir, ".htaccess", combined)
    end

    # The committed root .htaccess content (the redirects file), or "" if absent.
    def existing_root_htaccess
      return "" unless @site.respond_to?(:source) && @site.source

      path = File.join(@site.source, ".htaccess")
      File.exist?(path) ? File.read(path) : ""
    end

    # True for the site-root .htaccess static file (relative path ".htaccess").
    def root_htaccess?(file)
      rel = if file.respond_to?(:relative_path) && file.relative_path
              file.relative_path
            elsif file.respond_to?(:dir) && file.respond_to?(:name)
              File.join(file.dir.to_s, file.name.to_s)
            else
              ""
            end
      rel.sub(%r{\A/}, "") == ".htaccess"
    end

    def html_output?(doc)
      ext = doc.respond_to?(:output_ext) ? doc.output_ext : File.extname(doc.url)
      ext == ".html" || ext == ".htm"
    end

    # Returns [dir, target_file] for the document's rendered output.
    def location(doc)
      url = doc.url
      if url.end_with?("/")
        [url, "index.html"]
      else
        [File.dirname(url).sub(%r{/?$}, "/"), File.basename(url)]
      end
    end

    def schema_types(doc)
      case doc.data["layout"]
      when "post"
        ["https://schema.org/BlogPosting", "https://schema.org/AboutPage"]
      when "home", "post-index", "category"
        ["https://schema.org/CollectionPage"]
      else
        ["https://schema.org/WebPage"]
      end
    end

    def metadata_for(doc, page_url, own_directory)
      meta = {
        author: Signposting::AUTHOR_ORCID,
        doi: doc.data["doi"],
        license: Signposting::LICENSE_URL,
        types: schema_types(doc),
      }
      if own_directory
        meta[:describedby] = {
          url: File.join(page_url, DESCRIBEDBY_FILE),
          type: DESCRIBEDBY_TYPE,
          profile: SCHEMA_PROFILE,
        }
      end
      meta[:items] = items_for(doc)
      meta
    end

    # Content resources distinct from the landing page, declared in front
    # matter as `item:` and/or `pdf:` (a url/path or a list of them); the
    # pdf_pages generator appends the build's own PDF edition to `pdf`.
    def items_for(doc)
      (Array(doc.data["item"]) + Array(doc.data["pdf"])).map do |entry|
        url = entry.is_a?(Hash) ? entry["url"] : entry
        next nil unless url
        type = entry.is_a?(Hash) ? entry["type"] : guess_type(url)
        { url: url, type: type }
      end.compact
    end

    def guess_type(url)
      case File.extname(url).downcase
      when ".pdf"  then "application/pdf"
      when ".xml"  then "application/xml"
      when ".json" then "application/json"
      end
    end

    # schema.org `citation` nodes for outbound references declared in front
    # matter as `references:` (a list). Each entry may be a bare URL, a free-text
    # citation, or a mapping ({ url:, title:, author:, type: }). References live
    # only in the descriptive metadata -- never in the Signposting Link header or
    # <link> elements.
    def citations_for(doc)
      Array(doc.data["references"]).map { |entry| citation_node(entry) }.compact
    end

    def citation_node(entry)
      if entry.is_a?(Hash)
        if (doi = mapping_doi(entry))
          return doi_citation(doi, entry)
        end
        if (doc = internal_doc(entry["url"], entry["type"]))
          return deduced_citation(doc, entry)
        end
        return mapping_citation(entry)
      end

      text = entry.to_s.strip
      return nil if text.empty?

      # A DOI (bare or as a doi.org URL) is fetched and modelled from its
      # registration metadata; a bare internal URL resolves to the site's own
      # document; otherwise every reference is a proper schema.org CreativeWork:
      # an external URL is a dereferenceable node, free text becomes its `name`.
      if Signposting.doi?(text)
        doi_citation(text, {})
      elsif (doc = internal_doc(text))
        deduced_citation(doc, {})
      elsif url?(text)
        { "@type" => "CreativeWork", "@id" => text, "url" => text }
      else
        { "@type" => "CreativeWork", "name" => text }
      end
    end

    # A mapping is auto-resolved only when it carries an explicit `doi:` key;
    # a hand-written mapping that merely links to doi.org keeps its own metadata.
    def mapping_doi(entry)
      entry["doi"]
    end

    # Resolve a DOI to a citation node via the cache (fetching once on a miss),
    # then apply any explicitly-given reference keys on top. A DOI that cannot
    # be resolved still yields a minimal, dereferenceable node.
    def doi_citation(doi_text, overrides)
      doi = Signposting.normalize_doi(doi_text)
      csl = @doi_cache.csl(doi)
      node = if csl
               Signposting.csl_to_citation(csl, doi)
             else
               { "@type" => "CreativeWork",
                 "@id" => "https://doi.org/#{doi}",
                 "url" => "https://doi.org/#{doi}" }
             end
      apply_reference_overrides(node, overrides)
    end

    INTERNAL_MARKERS = %w[internal self].freeze

    # Resolve an internal reference (a URL on this site, or one flagged with
    # `type: Internal`) to the Jekyll document it points at, or nil.
    def internal_doc(url, type = nil)
      return nil unless url
      return nil unless internal_url?(url) || INTERNAL_MARKERS.include?(type.to_s.downcase)

      doc = doc_index[canonical_path(url)]
      if doc.nil? && defined?(Jekyll) && Jekyll.respond_to?(:logger)
        Jekyll.logger.warn "Signposting:", "unresolved internal reference #{url}"
      end
      doc
    end

    # A reference is internal when it is site-relative or sits under site.url.
    def internal_url?(url)
      return true if url.start_with?("/")

      base = @site.config["url"].to_s
      return false if base.empty?
      url == base || url.start_with?("#{base}/")
    end

    # Index of every rendered document keyed by a host/slash-insensitive path,
    # so an absolute or relative reference resolves to the same entry.
    def doc_index
      @doc_index ||= (@site.posts.docs + @site.pages).each_with_object({}) do |doc, idx|
        idx[canonical_path(doc.url)] = doc if html_output?(doc)
      end
    end

    def canonical_path(url)
      url.sub(%r{\Ahttps?://[^/]+}, "")
         .sub(%r{index\.html\z}, "")
         .sub(%r{\A/}, "")
         .sub(%r{/\z}, "")
    end

    # Build a citation node from a resolved site document: schema.org type,
    # title, canonical URL, DOI/identifier, date, language, licence, the site
    # author (with ORCID), and the blog it belongs to. Any keys set explicitly
    # in the reference mapping override the deduced values.
    def deduced_citation(doc, overrides)
      page_url = File.join(@site.config["url"].to_s, doc.url)
      node = { "@type" => schema_types(doc).first.sub("https://schema.org/", "") }
      node["@id"] = doc.data["doi"] || page_url
      node["name"] = doc.data["title"] if doc.data["title"]
      node["url"] = page_url
      if doc.respond_to?(:date) && doc.date
        node["datePublished"] = doc.date.strftime("%Y-%m-%d")
      end
      node["inLanguage"] = "en-GB"
      node["license"] = Signposting::LICENSE_URL
      node["author"] = {
        "@type" => "Person",
        "name" => "Martin Paul Eve",
        "@id" => Signposting::AUTHOR_ORCID,
        "identifier" => Signposting::AUTHOR_ORCID,
      }
      node["isPartOf"] = {
        "@type" => "Blog",
        "name" => @site.config["title"],
        "url" => @site.config["url"],
      }
      apply_reference_overrides(node, overrides)
    end

    # Let explicit reference keys override deduced values. The `type: Internal`
    # resolver flag is consumed here, never emitted as a schema.org @type.
    def apply_reference_overrides(node, entry)
      type = entry["type"]
      node["@type"] = type if type && !INTERNAL_MARKERS.include?(type.to_s.downcase)
      node["@id"] = entry["doi"] if entry["doi"]
      node["name"] = entry["title"] if entry["title"]
      node["datePublished"] = entry["date"].to_s if entry["date"]
      node["inLanguage"] = entry["language"] if entry["language"]
      node["license"] = entry["license"] if entry["license"]
      node["author"] = author_nodes(entry["author"]) if entry["author"]
      if (part = entry["isPartOf"] || entry["container"])
        node["isPartOf"] = part_of_node(part)
      end
      node
    end

    def mapping_citation(entry)
      node = { "@type" => entry["type"] || "CreativeWork" }
      identifier = entry["doi"] || entry["url"]
      node["@id"] = identifier if identifier
      node["name"] = entry["title"] if entry["title"]
      node["url"] = entry["url"] if entry["url"]
      node["datePublished"] = entry["date"].to_s if entry["date"]
      node["inLanguage"] = entry["language"] if entry["language"]
      node["license"] = entry["license"] if entry["license"]
      node["author"] = author_nodes(entry["author"]) if entry["author"]
      if (publisher = entry["publisher"])
        node["publisher"] = { "@type" => "Organization", "name" => publisher }
      end
      if (part = entry["isPartOf"] || entry["container"])
        node["isPartOf"] = part_of_node(part)
      end
      node
    end

    # One Person node, or a list when several authors are given.
    def author_nodes(authors)
      list = authors.is_a?(Array) ? authors : [authors]
      nodes = list.map { |a| person_node(a) }.compact
      nodes.length == 1 ? nodes.first : nodes
    end

    def person_node(author)
      if author.is_a?(Hash)
        name = author["name"]
        return nil unless name
        node = { "@type" => "Person", "name" => name }
        if (orcid = author["orcid"])
          node["@id"] = orcid
          node["identifier"] = orcid
        end
        node["url"] = author["url"] if author["url"]
        node
      else
        text = author.to_s.strip
        text.empty? ? nil : { "@type" => "Person", "name" => text }
      end
    end

    # The work a reference belongs to (e.g. the blog a post appeared in).
    def part_of_node(part)
      return { "@type" => "CreativeWork", "name" => part.to_s } unless part.is_a?(Hash)

      node = { "@type" => part["type"] || "CreativeWork" }
      node["name"] = part["name"] if part["name"]
      node["url"] = part["url"] if part["url"]
      node
    end

    def url?(value)
      value.start_with?("http://", "https://")
    end

    def json_metadata(doc, page_url)
      title = doc.data["title"] || @site.config["title"]
      data = {
        "@context" => "https://schema.org/",
        "@type" => schema_types(doc).first.sub("https://schema.org/", ""),
        "name" => title,
        "headline" => title,
        "url" => page_url,
        "inLanguage" => "en-GB",
        "license" => Signposting::LICENSE_URL,
        "author" => {
          "@type" => "Person",
          "name" => "Martin Paul Eve",
          "url" => "https://eve.gd",
          "identifier" => Signposting::AUTHOR_ORCID,
        },
      }
      if doc.respond_to?(:date) && doc.date
        data["datePublished"] = doc.date.strftime("%Y-%m-%d")
      end
      if (modified = Signposting.modified_date(doc.data["last_modified_at"]))
        data["dateModified"] = modified
      end
      data["identifier"] = doc.data["doi"] if doc.data["doi"]
      # A repository deposit of this post (front-matter `kcworks:`), e.g. on
      # KC Works, advertised as the place the post is archived.
      if (archived = Signposting.archived_at(doc.data["kcworks"]))
        data["archivedAt"] = archived
      end
      if (pdf = doc.data["pdf_url"])
        data["encoding"] = {
          "@type" => "MediaObject",
          "contentUrl" => pdf,
          "encodingFormat" => "application/pdf",
        }
      end
      citations = citations_for(doc)
      data["citation"] = citations unless citations.empty?
      JSON.pretty_generate(data) + "\n"
    end

    # Write a generated file straight into the output dir and register it as a
    # no-op static file so the cleaner keeps it (same approach as AliasFile).
    def write_file(dir, name, content)
      fs_dir = File.join(@site.dest, dir)
      FileUtils.mkdir_p(fs_dir)
      File.open(File.join(fs_dir, name), "w") { |f| f.write(content) }
      @site.static_files << SignpostingFile.new(@site, @site.dest, dir, name)
    end
  end

  class SignpostingFile < StaticFile
    def modified?
      false
    end

    def write(_dest)
      true
    end
  end

  # A persistent, on-disk cache of DOI CSL-JSON metadata so each DOI is fetched
  # at most once. Successful lookups are stored; failures are not cached, so a
  # transient network error is retried on the next build rather than poisoning
  # the cache.
  class DoiCache
    def initialize(path, fetcher)
      @path = path
      @fetcher = fetcher
      @store = load_store
      @dirty = false
    end

    def csl(doi)
      return @store[doi] if @store.key?(doi)

      data = @fetcher.call(doi)
      if data
        @store[doi] = data
        @dirty = true
      end
      data
    end

    def flush
      return unless @path && @dirty

      File.write(@path, JSON.pretty_generate(@store) + "\n")
    end

    private

    def load_store
      return {} unless @path && File.exist?(@path)

      JSON.parse(File.read(@path))
    rescue JSON::ParserError
      {}
    end
  end
end
end
