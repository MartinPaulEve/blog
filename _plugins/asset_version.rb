# Deterministic cache-busting for static assets.
#
# Stylesheet and script links carry a `?v=` stamp so browsers fetch a fresh
# copy after a change. Deriving the stamp from the build clock made every
# page differ on every build, which (a) forced visitors to re-download all
# CSS after each deploy and (b) made the deploy's rsync list every page as
# changed. The `asset_version` filter instead stamps an asset with a short
# digest of its content, so pages only change when the asset does:
#
#   <link rel="stylesheet" href="/assets/css/x.css?v={{ '/assets/css/x.css' | asset_version }}">
#
# A missing asset gets a fixed stamp (and a build warning) rather than
# failing the build. The PDF cache key strips `?v=` stamps (see
# pdf_pages.rb#normalize_html), so changing a stamp never re-renders PDFs.

require "digest"

module AssetVersion
  STAMP_LENGTH = 10
  MISSING = "0" * STAMP_LENGTH

  def self.version(source_dir, path)
    file = File.join(source_dir.to_s, path.to_s.sub(%r{\A/+}, ""))
    return MISSING unless File.file?(file)

    Digest::SHA256.file(file).hexdigest[0, STAMP_LENGTH]
  end
end

if defined?(Liquid)
  module Jekyll
    module AssetVersionLiquidFilter
      def asset_version(path)
        site = @context.registers[:site]
        stamp = AssetVersion.version(site.source, path)
        if stamp == AssetVersion::MISSING && Jekyll.respond_to?(:logger)
          Jekyll.logger.warn "AssetVersion:", "no such asset #{path}"
        end
        stamp
      end
    end
  end
  Liquid::Template.register_filter(Jekyll::AssetVersionLiquidFilter)
end
