# Generates one page per post category at /categories/<slug>/, rendered with
# the `category` layout. Slugs come from Jekyll::Utils.slugify — the same
# function behind the Liquid `slugify` filter — so URLs generated here always
# match anchors and links built in templates. Runs at :normal priority so the
# og_image generator (:low) picks the pages up and renders their social cards.
module Jekyll
  class CategoryPage < Page
    def initialize(site, category)
      @site = site
      @base = site.source
      @dir  = File.join("categories", Utils.slugify(category))
      @name = "index.html"
      process(@name)
      self.data = {
        "layout"          => "category",
        "title"           => category,
        "category"        => category,
        "og_card_snippet" => "Posts filed under #{category} on eve.gd.",
      }
    end
  end

  class CategoryPageGenerator < Generator
    safe false
    priority :normal

    def generate(site)
      seen = {}
      site.categories.each_key do |category|
        slug = Utils.slugify(category)
        if seen[slug]
          Jekyll.logger.warn "Categories:",
            "slug collision: '#{category}' and '#{seen[slug]}' both map to '#{slug}'; skipping '#{category}'"
          next
        end
        seen[slug] = category
        site.pages << CategoryPage.new(site, category)
      end
    end
  end
end
