# Date-aware institutional affiliations for the PDF title pages. The print
# cover shows the affiliation(s) Martin held when a piece was written, not the
# current ones, so each document is stamped with the entries in force on its
# date (undated content pages get the present-day entries).
#
# The Affiliations module holds the pure lookup (no Jekyll dependency) so it
# can be unit-tested in isolation; the generator below stamps
# `doc.data["affiliations"]` for _print_cover.html to render.

require "date"

module Affiliations
  BIRKBECK_PROFESSOR = {
    "role" => "Professor of Literature, Technology and Publishing",
    "institution" => "Birkbeck, University of London",
  }.freeze

  # Each period runs from its `from` date until the next period begins; the
  # last runs indefinitely. Dual affiliations are deliberately ordered with
  # Birkbeck first and rendered side by side, not stacked, on the cover.
  TIMELINE = [
    {
      from: Date.new(2009, 1, 1),
      affiliations: [{ "institution" => "University of Sussex" }],
    },
    {
      from: Date.new(2013, 1, 1),
      affiliations: [
        {
          "role" => "Lecturer in English",
          "institution" => "University of Lincoln",
        },
      ],
    },
    {
      from: Date.new(2015, 1, 1),
      affiliations: [
        {
          "role" => "Senior Lecturer in Literature, Technology and Publishing",
          "institution" => "Birkbeck, University of London",
        },
      ],
    },
    {
      from: Date.new(2016, 1, 1),
      affiliations: [BIRKBECK_PROFESSOR],
    },
    {
      from: Date.new(2023, 1, 1),
      affiliations: [
        BIRKBECK_PROFESSOR,
        { "role" => "Principal R&D Developer", "institution" => "Crossref" },
      ],
    },
    {
      from: Date.new(2025, 1, 1),
      affiliations: [
        BIRKBECK_PROFESSOR,
        {
          "role" => "Technical Lead of Knowledge Commons",
          "institution" => "Michigan State University",
        },
      ],
    },
    {
      from: Date.new(2026, 6, 1),
      affiliations: [
        BIRKBECK_PROFESSOR,
        {
          "role" => "Associate Director of Knowledge Commons",
          "institution" => "Michigan State University",
        },
      ],
    },
  ].freeze

  # Returns the affiliations in force on `date` (a Date, Time or nil; nil
  # means "now") as an array of {"role" => ..., "institution" => ...} hashes
  # with string keys, so Liquid templates can read them. "role" is absent
  # when only an institution should be shown; the array is empty for dates
  # before any affiliation began.
  def self.for_date(date)
    date = date.nil? ? Date.today : date
    date = date.to_date if date.respond_to?(:to_date)
    period = TIMELINE.reverse_each.find { |entry| date >= entry[:from] }
    period ? period[:affiliations].map(&:dup) : []
  end
end

if defined?(Jekyll::Generator)
  module Affiliations
    # Runs at :normal priority alongside the PDF generator; only the print
    # cover reads the stamped data, so ordering against it does not matter.
    class Generator < Jekyll::Generator
      priority :normal

      def generate(site)
        (site.posts.docs + site.pages).each do |doc|
          doc.data["affiliations"] = Affiliations.for_date(doc.data["date"])
        end
      end
    end
  end
end
