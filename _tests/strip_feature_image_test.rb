# Behaviour tests for StripFeatureImage.strip. These exercise the returned
# string only (what gets rendered), never call counts or implementation detail,
# so the regex/parse strategy can change freely as long as behaviour holds.
require "minitest/autorun"
require_relative "../_plugins/strip_feature_image"

class StripFeatureImageTest < Minitest::Test
  # A raw <img> embed (authored as HTML, or Markdown that rendered to one) with
  # the feature src is removed entirely.
  def test_removes_raw_img_embed
    html = %(<p>Intro</p><img src="/images/microphone.png" alt="A microphone" style="width:100%"/><p>Body</p>)
    out = StripFeatureImage.strip(html, "microphone.png")

    refute_includes out, "microphone.png"
    refute_includes out, "<img"
    assert_includes out, "<p>Intro</p>"
    assert_includes out, "<p>Body</p>"
  end

  # kramdown wraps a lone image in its own paragraph; once the img goes the
  # emptied <p> must go too.
  def test_removes_kramdown_paragraph_wrapped_image
    html = %(<p>Text before</p><p><img src="/images/oa.png" alt="oa"></p><p>Text after</p>)
    out = StripFeatureImage.strip(html, "oa.png")

    refute_includes out, "oa.png"
    refute_includes out, "<img"
    refute_includes out, "<p></p>"
    assert_includes out, "<p>Text before</p>"
    assert_includes out, "<p>Text after</p>"
  end

  # A linked image ([![](img)](href)) renders to <a><img></a>; removing the img
  # leaves an empty anchor that must also be cleaned up.
  def test_removes_linked_image_and_empty_anchor
    html = %(<a href="http://doi.org/x"><img src="/images/Stemma.png" alt="Stemma"></a>)
    out = StripFeatureImage.strip(html, "Stemma.png")

    refute_includes out, "Stemma.png"
    refute_includes out, "<img"
    refute_includes out, "<a "
    refute_includes out, "</a>"
  end

  # A different image must be left completely intact.
  def test_leaves_other_images_untouched
    html = %(<img src="/images/SH2.png"><img src="/images/microphone.png" alt="mic"/>)
    out = StripFeatureImage.strip(html, "microphone.png")

    refute_includes out, "microphone.png"
    assert_includes out, %(<img src="/images/SH2.png">)
  end

  # Feature values can carry a sub-path; the full path must match precisely.
  def test_matches_subpath_feature
    html = %(<p><img src="/images/post_images/Birkbeck.jpg" alt="bbk"></p>)
    out = StripFeatureImage.strip(html, "post_images/Birkbeck.jpg")

    refute_includes out, "Birkbeck.jpg"
    refute_includes out, "<img"
    refute_includes out, "<p></p>"
  end

  # nil / blank feature is a no-op.
  def test_nil_feature_returns_input_unchanged
    html = %(<img src="/images/microphone.png"><p>hi</p>)
    assert_equal html, StripFeatureImage.strip(html, nil)
  end

  def test_empty_feature_returns_input_unchanged
    html = %(<img src="/images/microphone.png"><p>hi</p>)
    assert_equal html, StripFeatureImage.strip(html, "")
  end

  # Feature is set but never appears in the body -> body is unchanged.
  def test_absent_feature_returns_body_unchanged
    html = %(<p>Just words</p><img src="/images/other.png" alt="other">)
    assert_equal html, StripFeatureImage.strip(html, "microphone.png")
  end

  # When the feature img shares a paragraph with real text, only the img is
  # stripped; the surrounding paragraph and its text survive.
  def test_keeps_paragraph_with_trailing_text
    html = %(<p><img src="/images/oa.png" alt="oa">Some caption text</p>)
    out = StripFeatureImage.strip(html, "oa.png")

    refute_includes out, "oa.png"
    refute_includes out, "<img"
    assert_includes out, "Some caption text"
    assert_includes out, "<p>"
    assert_includes out, "</p>"
  end
end
