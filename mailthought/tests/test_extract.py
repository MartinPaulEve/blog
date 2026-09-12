"""extract: classification, body selection and attachment collection."""

import io
import json

from mailthought.extract import (
    KIND_BAD_REPLY,
    KIND_DRY_RUN,
    KIND_POST_DRAFT,
    KIND_PUBLISH,
    classify,
    collect_images,
    find_draft_id,
    first_line_is_post,
    html_to_text,
    select_body,
    strip_signature,
    unwrap_flowed,
    wants_dry_run,
)


class TestSubjectParsing:
    def test_draft_id_found_in_a_reply_subject(self):
        subject = "Re: Thought draft [mt-a1b2c3d4]: 3 post(s), 1 image(s)"
        assert find_draft_id(subject) == "a1b2c3d4"

    def test_no_draft_id_in_an_ordinary_subject(self):
        assert find_draft_id("a passing thought") is None

    def test_malformed_ids_are_not_matched(self):
        assert find_draft_id("[mt-xyz] nope") is None
        assert find_draft_id("[mt-a1b2c3] too short") is None

    def test_dry_run_flag_variants(self):
        assert wants_dry_run("--dry run")
        assert wants_dry_run("--Dry Run")
        assert wants_dry_run("--dry-run")
        assert wants_dry_run("please --dry run this")

    def test_dry_run_not_triggered_by_ordinary_words(self):
        assert not wants_dry_run("thoughts on laundry drying")
        assert not wants_dry_run("a dry run of the marathon")


class TestPostCommand:
    def test_post_as_first_line(self):
        assert first_line_is_post("POST\n\nquoted reply below")

    def test_post_with_surrounding_whitespace(self):
        assert first_line_is_post("  POST  \nrest")

    def test_blank_lines_before_post_are_skipped(self):
        assert first_line_is_post("\n\nPOST\n")

    def test_lowercase_post_is_not_a_command(self):
        assert not first_line_is_post("post\n")

    def test_post_embedded_in_a_sentence_is_not_a_command(self):
        assert not first_line_is_post("Sure, POST it\n")
        assert not first_line_is_post("POSTED\n")

    def test_empty_body_is_not_a_command(self):
        assert not first_line_is_post("")


class TestClassify:
    def test_plain_mail_publishes(self):
        action = classify("hello", "a thought")
        assert action.kind == KIND_PUBLISH

    def test_dry_run_subject_previews(self):
        action = classify("--dry run", "a thought")
        assert action.kind == KIND_DRY_RUN

    def test_post_reply_publishes_the_draft(self):
        action = classify("Re: Thought draft [mt-a1b2c3d4]: 2 post(s)", "POST\n")
        assert action.kind == KIND_POST_DRAFT
        assert action.draft_id == "a1b2c3d4"

    def test_draft_id_wins_over_a_quoted_dry_run_flag(self):
        action = classify("Re: --dry run Thought draft [mt-a1b2c3d4]", "POST")
        assert action.kind == KIND_POST_DRAFT

    def test_reply_without_post_first_line_is_a_bad_reply(self):
        action = classify(
            "Re: Thought draft [mt-a1b2c3d4]: 2 post(s)", "looks good!"
        )
        assert action.kind == KIND_BAD_REPLY
        assert action.draft_id == "a1b2c3d4"


class TestSelectBody:
    def test_stripped_text_is_preferred(self):
        form = {
            "stripped-text": "the thought",
            "body-plain": "the thought\n-- \nMartin\n",
            "body-html": "<p>the thought</p>",
        }
        assert select_body(form) == "the thought"

    def test_crlf_normalised_and_outer_whitespace_trimmed(self):
        form = {"stripped-text": "line one\r\nline two\r\n\r\n"}
        assert select_body(form) == "line one\nline two"

    def test_html_used_when_no_plain_text(self):
        form = {
            "stripped-html": (
                "<div>see <a href=\"https://eve.gd/x\">this post</a></div>"
            )
        }
        assert select_body(form) == "see this post https://eve.gd/x"

    def test_plain_body_falls_back_with_signature_stripped(self):
        form = {"body-plain": "just a thought\n-- \nProf M P Eve\n"}
        assert select_body(form) == "just a thought"

    def test_flowed_plain_text_is_unwrapped_when_declared(self):
        headers = json.dumps(
            [["Content-Type", "text/plain; charset=utf-8; format=flowed"]]
        )
        form = {
            "body-plain": "a line that was \nsoft wrapped\n",
            "message-headers": headers,
        }
        assert select_body(form) == "a line that was soft wrapped"

    def test_empty_mail_yields_empty_string(self):
        assert select_body({}) == ""


class TestHtmlToText:
    def test_links_survive_with_their_urls(self):
        html = '<p>Hello <a href="https://x.example/y">a link</a></p>'
        assert html_to_text(html) == "Hello a link https://x.example/y"

    def test_url_not_duplicated_when_anchor_text_is_the_url(self):
        html = '<p><a href="https://x.example/">https://x.example/</a></p>'
        assert html_to_text(html) == "https://x.example/"

    def test_paragraphs_become_blank_lines(self):
        assert html_to_text("<p>one</p><p>two</p>") == "one\n\ntwo"

    def test_br_becomes_a_newline(self):
        assert html_to_text("one<br>two") == "one\ntwo"

    def test_style_and_script_contents_disappear(self):
        html = "<style>p{color:red}</style><p>kept</p><script>x()</script>"
        assert html_to_text(html) == "kept"

    def test_entities_are_decoded(self):
        assert html_to_text("<p>bread &amp; butter</p>") == "bread & butter"


class TestStripSignature:
    def test_rfc3676_delimiter(self):
        assert strip_signature("body\n-- \nMartin Eve\n") == "body"

    def test_bare_double_dash_delimiter(self):
        assert strip_signature("body\n--\nMartin Eve\n") == "body"

    def test_mobile_signoffs(self):
        assert strip_signature("body\nSent from my iPhone\n") == "body"
        assert strip_signature("body\nGet Outlook for Android\n") == "body"

    def test_dashes_inside_the_body_are_not_a_delimiter(self):
        text = "an em-dash -- like this -- stays\nmore text"
        assert strip_signature(text) == text

    def test_body_without_signature_is_untouched(self):
        assert strip_signature("just words\nacross lines") == (
            "just words\nacross lines"
        )


class TestUnwrapFlowed:
    FLOWED = "text/plain; charset=utf-8; format=flowed"

    def test_soft_wrapped_lines_are_joined(self):
        text = "wrapped at the \nboundary here\n\nnew paragraph\n"
        assert unwrap_flowed(text, self.FLOWED) == (
            "wrapped at the boundary here\n\nnew paragraph\n"
        )

    def test_delsp_removes_the_soft_break_space(self):
        content_type = self.FLOWED + "; delsp=yes"
        assert unwrap_flowed("hy \nphen", content_type) == "hyphen"

    def test_space_stuffed_lines_are_unstuffed(self):
        assert unwrap_flowed(" From here\n", self.FLOWED) == "From here\n"

    def test_signature_delimiter_is_never_joined(self):
        text = "body\n-- \nsig\n"
        assert unwrap_flowed(text, self.FLOWED) == text

    def test_non_flowed_content_is_untouched(self):
        text = "kept \nexactly\n"
        assert unwrap_flowed(text, "text/plain; charset=utf-8") == text


class FakeUpload:
    def __init__(self, filename, mimetype, data):
        self.filename = filename
        self.mimetype = mimetype
        self._stream = io.BytesIO(data)

    def read(self):
        return self._stream.read()


class TestCollectImages:
    def test_images_collected_in_attachment_order(self):
        files = {
            "attachment-2": FakeUpload("b.png", "image/png", b"PNG2"),
            "attachment-1": FakeUpload("a.jpg", "image/jpeg", b"JPG1"),
        }
        images = collect_images(files)
        assert [i["filename"] for i in images] == ["a.jpg", "b.png"]
        assert images[0]["data"] == b"JPG1"
        assert images[0]["mime"] == "image/jpeg"

    def test_non_image_attachments_are_ignored(self):
        files = {
            "attachment-1": FakeUpload("doc.pdf", "application/pdf", b"%PDF"),
            "attachment-2": FakeUpload("c.webp", "image/webp", b"WEBP"),
        }
        images = collect_images(files)
        assert [i["mime"] for i in images] == ["image/webp"]

    def test_filename_stem_becomes_default_alt_text(self):
        files = {"attachment-1": FakeUpload("garden gate.jpg", "image/jpeg", b"x")}
        assert collect_images(files)[0]["alt"] == "garden gate"

    def test_at_most_four_images_survive(self):
        files = {
            f"attachment-{n}": FakeUpload(f"{n}.png", "image/png", b"x")
            for n in range(1, 7)
        }
        assert len(collect_images(files)) == 4

    def test_no_attachments_is_fine(self):
        assert collect_images({}) == []
