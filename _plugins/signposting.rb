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

    def generate(site)
      @site = site
      base_url = site.config["url"].to_s

      (site.posts.docs + site.pages).each do |doc|
        next unless html_output?(doc)

        dir, target_file = location(doc)
        own_directory = target_file == "index.html" && dir != "/"

        page_url = File.join(base_url, dir)
        meta = metadata_for(doc, page_url, own_directory)
        relations = Signposting.relations(meta)

        # Level 1 fallback -- rendered in <head> by the include.
        doc.data["signposting_links"] = Signposting.link_elements(relations).join("\n    ")

        # Level 2 + describedby are only emitted for documents that own their
        # output directory, so we never clobber a shared/root .htaccess (e.g.
        # the site-wide redirects file).
        next unless own_directory

        write_file(dir, DESCRIBEDBY_FILE, json_metadata(doc, page_url))
        write_file(dir, ".htaccess",
                   Signposting.htaccess(relations,
                                        target_file: target_file,
                                        json_file: DESCRIBEDBY_FILE))
      end
    end

    private

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
    # matter as `item:` / `pdf:` (a url/path or a list of them).
    def items_for(doc)
      Array(doc.data["item"] || doc.data["pdf"]).map do |entry|
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

    def json_metadata(doc, page_url)
      data = {
        "@context" => "https://schema.org/",
        "@type" => schema_types(doc).first.sub("https://schema.org/", ""),
        "name" => doc.data["title"],
        "headline" => doc.data["title"],
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
      data["identifier"] = doc.data["doi"] if doc.data["doi"]
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
end
end
