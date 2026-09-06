# Behaviour tests for the visible reference list: front-matter references
# entries must come out as citation fragments in each supported style,
# citing whatever metadata exists — full structured entries, bare labelled
# URLs, and DOI-cache-resolved DOIs alike. Run with:
#   ruby _tests/reference_list_test.rb
require "minitest/autorun"
require_relative "../_plugins/reference_list"

RAW_POST = <<~RAW
  ---
  title: "A post"
  references:
  - http://www.researchinfonet.org/publish/finch/ # Finch report on open access
  - http://dx.doi.org/10.7766/orbit.v1.1.38 # Eve, Orbit article
  - author: Kerry Eustice
    date: '2011-12-28'
    title: 'Higher education review of 2011: the 10 best blogs of the year'
    type: NewsArticle
    url: http://www.guardian.co.uk/higher-education-network/blog/2011/dec/28/top-higher-education-blogs-2011
    isPartOf:
      name: The Guardian
      type: Periodical
  ---
  Body.
RAW

DOI_STORE = {
  "10.7766/orbit.v1.1.38" => {
    "title" => "Whole Earth to Gravity's Rainbow",
    "author" => [
      { "family" => "Eve", "given" => "Martin Paul" },
    ],
    "container-title" => "Orbit: A Journal of American Literature",
    "issued" => { "date-parts" => [[2012, 5, 10]] },
    "publisher" => "Open Library of Humanities",
    "type" => "journal-article",
  },
}.freeze

STRUCTURED = {
  "author" => "Kerry Eustice",
  "date" => "2011-12-28",
  "title" => "Higher education review of 2011: the 10 best blogs of the year",
  "type" => "NewsArticle",
  "url" => "http://example.org/review",
  "isPartOf" => { "name" => "The Guardian", "type" => "Periodical" },
}.freeze

BOOK = {
  "author" => ["Janice Newson", "Claire Polster"],
  "title" => "Academic Callings",
  "type" => "Book",
  "url" => "http://example.org/book",
}.freeze

describe "ReferenceList.parse_labels" do
  it "maps bare reference urls to their inline labels" do
    labels = ReferenceList.parse_labels(RAW_POST)
    _(labels["http://www.researchinfonet.org/publish/finch/"])
      .must_equal "Finch report on open access"
  end

  it "ignores structured entries" do
    labels = ReferenceList.parse_labels(RAW_POST)
    _(labels.keys.length).must_equal 2
  end
end

describe "ReferenceList.manual_list?" do
  it "detects markdown reference headings" do
    _(ReferenceList.manual_list?("Text\n\n## References\n\n- one\n")).must_equal true
    _(ReferenceList.manual_list?("Text\n\n### Bibliography\n")).must_equal true
    _(ReferenceList.manual_list?("Text\n\n## Works Cited\n")).must_equal true
  end

  it "detects html reference headings" do
    _(ReferenceList.manual_list?("<h2>References</h2>")).must_equal true
  end

  it "does not trigger on prose mentions" do
    _(ReferenceList.manual_list?("I checked the references in the report.")).must_equal false
  end
end

describe "ReferenceList.normalize" do
  it "resolves bare dois through the cache" do
    ref = ReferenceList.normalize(
      "http://dx.doi.org/10.7766/orbit.v1.1.38", {}, DOI_STORE
    )
    _(ref[:authors]).must_equal ["Martin Paul Eve"]
    _(ref[:title]).must_equal "Whole Earth to Gravity's Rainbow"
    _(ref[:venue]).must_equal "Orbit: A Journal of American Literature"
    _(ref[:date]).must_equal "2012-05-10"
    _(ref[:url]).must_equal "https://doi.org/10.7766/orbit.v1.1.38"
  end

  it "resolves dois case-insensitively against the cache" do
    store = {
      "10.1080/0950236X.2013.840113" => {
        "title" => "Textual practice article",
        "author" => [{ "family" => "Eve", "given" => "Martin Paul" }],
      },
    }
    ref = ReferenceList.normalize(
      "https://doi.org/10.1080/0950236x.2013.840113", {}, store
    )
    _(ref[:title]).must_equal "Textual practice article"
  end

  it "keeps the doi's original case in the rendered url" do
    ref = ReferenceList.normalize(
      "https://doi.org/10.1080/0950236X.2013.840113", {}, {}
    )
    _(ref[:url]).must_equal "https://doi.org/10.1080/0950236X.2013.840113"
  end

  it "uses the label as a plain description for unresolved bare urls" do
    ref = ReferenceList.normalize(
      "http://x.example/y",
      { "http://x.example/y" => "A useful page" },
      {}
    )
    _(ref[:title]).must_equal "A useful page"
    _(ref[:italic_title]).must_equal false
    _(ref[:authors]).must_equal []
  end

  it "carries structured entry fields across" do
    ref = ReferenceList.normalize(STRUCTURED, {}, {})
    _(ref[:authors]).must_equal ["Kerry Eustice"]
    _(ref[:venue]).must_equal "The Guardian"
    _(ref[:date]).must_equal "2011-12-28"
  end

  it "treats book titles as italic" do
    _(ReferenceList.normalize(BOOK, {}, {})[:italic_title]).must_equal true
    _(ReferenceList.normalize(STRUCTURED, {}, {})[:italic_title]).must_equal false
  end

  it "reads a single author mapping with name and orcid keys" do
    entry = {
      "author" => {
        "name" => "Brennan Kenneth Brown",
        "orcid" => "https://orcid.org/0009-0004-6725-8425",
      },
      "title" => "Publishing My Eleventy Blog",
      "url" => "https://brennan.day/x",
    }
    _(ReferenceList.normalize(entry, {}, {})[:authors])
      .must_equal ["Brennan Kenneth Brown"]
  end

  it "reads a list of author mappings" do
    entry = {
      "author" => [
        { "name" => "Ada One" },
        { "name" => "Bea Two", "orcid" => "https://orcid.org/x" },
      ],
      "title" => "T",
      "url" => "https://example.org/x",
    }
    _(ReferenceList.normalize(entry, {}, {})[:authors])
      .must_equal ["Ada One", "Bea Two"]
  end
end

describe "ReferenceList.format" do
  before do
    @article = ReferenceList.normalize(STRUCTURED, {}, {})
    @book = ReferenceList.normalize(BOOK, {}, {})
  end

  it "renders mhra with inverted first author, quoted title, italic venue and full date" do
    html = ReferenceList.format(@article, :mhra)
    _(html).must_include "Eustice, Kerry"
    _(html).must_include "‘Higher education review of 2011: the 10 best blogs of the year’"
    _(html).must_include "<i>The Guardian</i>"
    _(html).must_include "28 December 2011"
    _(html).must_include 'href="http://example.org/review"'
  end

  it "renders mhra books with italic titles and natural-order later authors" do
    html = ReferenceList.format(@book, :mhra)
    _(html).must_include "Newson, Janice"
    _(html).must_include "and Claire Polster"
    _(html).must_include "<i>Academic Callings</i>"
  end

  it "renders apa with initials and a dated parenthetical" do
    html = ReferenceList.format(@article, :apa)
    _(html).must_include "Eustice, K."
    _(html).must_include "(2011, December 28)"
    _(html).must_include "<i>The Guardian</i>"
  end

  it "renders apa n.d. when no date is known" do
    html = ReferenceList.format(@book, :apa)
    _(html).must_include "(n.d.)"
  end

  it "renders chicago author-date with the year after the author" do
    html = ReferenceList.format(@article, :chicago)
    _(html).must_include "Eustice, Kerry. 2011."
  end

  it "cites what it can for a label-only reference" do
    bare = ReferenceList.normalize(
      "http://x.example/y", { "http://x.example/y" => "A useful page" }, {}
    )
    html = ReferenceList.format(bare, :mhra)
    _(html).must_include "A useful page"
    _(html).must_include 'href="http://x.example/y"'
  end

  it "escapes html in metadata" do
    ref = ReferenceList.normalize({ "title" => "a <script>bad</script> title", "url" => "http://x.example" }, {}, {})
    html = ReferenceList.format(ref, :mhra)
    _(html).wont_include "<script>"
    _(html).must_include "&lt;script&gt;"
  end

  it "preserves italic markup embedded in titles" do
    ref = ReferenceList.normalize(
      { "title" => "Reading Redaction: Erasure Poetry and Mark Blacklock’s <i>I’m Jack</i>",
        "url" => "https://doi.org/10.1080/00111619.2019.1568960" },
      {}, {}
    )
    %i[mhra apa chicago].each do |style|
      html = ReferenceList.format(ref, style)
      _(html).must_include "<i>I’m Jack</i>"
      _(html).wont_include "&lt;i&gt;"
    end
  end
end

describe "ReferenceList.render_section" do
  before do
    @entries = [
      STRUCTURED,
      BOOK,
      "http://www.researchinfonet.org/publish/finch/",
    ]
    @labels = { "http://www.researchinfonet.org/publish/finch/" => "Finch report" }
    @html = ReferenceList.render_section(@entries, @labels, {})
  end

  it "returns nil when there is nothing to cite" do
    _(ReferenceList.render_section([], {}, {})).must_be_nil
  end

  it "carries the heading and the disclaimer" do
    _(@html).must_include ">References</h2>"
    _(@html).must_include "automated process"
    _(@html).must_include "purely as assistance"
  end

  it "renders one list per style with only mhra visible" do
    _(@html).must_include 'data-ref-style="mhra"'
    _(@html).must_include 'data-ref-style="apa" hidden'
    _(@html).must_include 'data-ref-style="chicago" hidden'
    _(@html).wont_include 'data-ref-style="mhra" hidden'
  end

  it "sorts entries by first author surname then title" do
    mhra = @html[/data-ref-style="mhra".*?<\/ol>/m]
    eustice = mhra.index("Eustice")
    finch = mhra.index("Finch report")
    newson = mhra.index("Newson")
    _(eustice).must_be :<, finch
    _(finch).must_be :<, newson
  end

  it "keeps the style picker hidden until scripted" do
    _(@html).must_include "data-ref-picker hidden"
  end
end
