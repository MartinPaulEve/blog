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

# The render cache must be sensitive to the print stylesheet, not just the
# page HTML: a print-CSS-only change alters the rendered PDF, so it has to
# produce a different content hash or cached PDFs go silently stale.
class PdfCacheKeyTest < Minitest::Test
  HTML = "<html><body><p>post</p></body></html>"

  def test_css_change_changes_the_hash
    refute_equal PdfPages.content_hash(HTML, "a { color: red }"),
                 PdfPages.content_hash(HTML, "a { color: blue }")
  end

  def test_same_html_and_css_hash_equal
    assert_equal PdfPages.content_hash(HTML, "a { color: red }"),
                 PdfPages.content_hash(HTML, "a { color: red }")
  end

  def test_build_noise_in_html_still_normalized_away
    noisy = HTML.sub("<body>", "<body><link href=\"/assets/css/blog-post.css?v=123\">")
    stable = HTML.sub("<body>", "<body><link href=\"/assets/css/blog-post.css?v=456\">")

    assert_equal PdfPages.content_hash(noisy, "css"), PdfPages.content_hash(stable, "css")
  end

  def test_screen_only_pdf_link_does_not_affect_the_hash
    # The on-screen "Download PDF" line lives in the post header, which is
    # display:none in print — it cannot change the rendered PDF, so it must
    # not invalidate the cache.
    with_link = HTML.sub("<p>post</p>",
                         '<p class="post-description post-pdf"><a href="/PDF/x.pdf">PDF</a></p><p>post</p>')

    assert_equal PdfPages.content_hash(with_link, "css"), PdfPages.content_hash(HTML, "css")
  end
end
