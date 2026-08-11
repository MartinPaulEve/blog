# Points jekyll-feed at the repo's own copy of its feed template
# (_includes/jekyll-feed/feed.xml) instead of the one bundled inside whichever
# jekyll-feed gem happens to be installed. The stock 0.17.0 template does
# `post.image.path | default: post.image`, which passes this site's `image:`
# front-matter hash straight into `absolute_url` and crashes the build; the
# repo template resolves `post.image.feature` under /images/ instead. Keeping
# the template in-repo makes every build environment (laptop, server) render
# the feed identically without hand-patching installed gems.
#
# The pure FeedTemplateOverride.template_path / #feed_source_path carry no
# Jekyll dependency and are unit-testable; the prepend below wires them in
# only when jekyll-feed is present.
module FeedTemplateOverride
  # Absolute path of the canonical feed template inside this repo.
  def self.template_path
    File.expand_path("../_includes/jekyll-feed/feed.xml", __dir__)
  end

  # Instance override for JekyllFeed::Generator#feed_source_path. Prepended so
  # it wins regardless of gem load order or version.
  def feed_source_path
    @feed_source_path ||= FeedTemplateOverride.template_path
  end
end

begin
  require "jekyll-feed"
  JekyllFeed::Generator.prepend(FeedTemplateOverride)
rescue LoadError
  # jekyll-feed not installed (e.g. plain-Ruby unit tests) — nothing to wire.
end
