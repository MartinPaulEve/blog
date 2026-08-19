# Behaviour tests for the PDF metadata embedding: given a page's bibliographic
# data, PdfPages.metadata_args must produce exiftool tag assignments that carry
# the title, author, date, DOI and canonical URL into the PDF's Info dictionary
# and XMP packet. Only the resulting tag set is asserted, not how it is applied.
require "minitest/autorun"
require_relative "../_plugins/pdf_pages"

class PdfMetadataTest < Minitest::Test
  FULL = {
    title: "Feed, Infection Control, Fluid Overload",
    date: Time.utc(2026, 8, 17),
    doi: "https://doi.org/10.59348/pahpe-g7w52",
    url: "https://eve.gd/2026/08/17/feed-infection-control-fluid-overload/",
  }.freeze

  def args(meta = FULL)
    PdfPages.metadata_args(meta)
  end

  def assert_tag(args, tag, value)
    assert_includes args, "-#{tag}=#{value}"
  end

  def test_carries_title_into_info_and_xmp
    assert_tag args, "Title", FULL[:title]
    assert_tag args, "XMP-dc:Title", FULL[:title]
  end

  def test_carries_author_into_info_and_xmp
    assert_tag args, "Author", "Martin Paul Eve"
    assert_tag args, "XMP-dc:Creator", "Eve, Martin Paul"
  end

  def test_carries_date
    assert_tag args, "XMP-dc:Date", "2026-08-17"
    assert_tag args, "CreateDate", "2026:08:17 00:00:00"
  end

  def test_carries_doi_as_bare_doi_and_identifier
    assert_tag args, "XMP-prism:DOI", "10.59348/pahpe-g7w52"
    assert_tag args, "XMP-dc:Identifier", FULL[:doi]
  end

  def test_carries_canonical_url
    # prism:URL is a structured tag in PRISM 3.0 and fails to write; the
    # simple-text tags carry the canonical web URL instead.
    assert_tag args, "XMP-dc:Source", FULL[:url]
    assert_tag args, "XMP-prism:Link", FULL[:url]
  end

  def test_omits_absent_fields_without_blank_assignments
    a = args(title: "About Martin Eve", url: "https://eve.gd/about/")

    assert_tag a, "Title", "About Martin Eve"
    refute(a.any? { |arg| arg.end_with?("=") }, "no empty tag assignments")
    refute(a.any? { |arg| arg.include?("DOI") }, "no DOI tags without a DOI")
    refute(a.any? { |arg| arg.include?("Date") }, "no date tags without a date")
  end

  def test_every_arg_is_a_tag_assignment_or_flag
    args.each do |arg|
      assert arg.start_with?("-"), "#{arg} should be an exiftool switch"
    end
  end
end
