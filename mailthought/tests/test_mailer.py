"""mailer: Mailgun sends and the wording of reports and receipts."""

from types import SimpleNamespace

import requests

from mailthought.mailer import (
    bad_reply_notice,
    dry_run_report,
    failure_notice,
    missing_draft_notice,
    receipt,
    send_email,
)
from mailthought.publisher import DryRunResult, PublishResult


class PostCollector:
    def __init__(self, status_code=200, raises=None):
        self.status_code = status_code
        self.raises = raises
        self.requests = []

    def __call__(self, url, auth=None, data=None, timeout=None):
        if self.raises:
            raise self.raises
        self.requests.append({"url": url, "auth": auth, "data": data})
        return SimpleNamespace(status_code=self.status_code, text="")


class TestSendEmail:
    def test_posts_to_the_domain_messages_endpoint(self, config):
        post = PostCollector()
        assert send_email(
            config, "martin@eve.gd", "subject", "body",
            in_reply_to="<orig@eve.gd>", post=post,
        )
        (request,) = post.requests
        assert request["url"] == "https://api.mailgun.net/v3/mg.eve.gd/messages"
        assert request["auth"] == ("api", "key-testing")
        assert request["data"]["from"] == "Thoughts <thoughts@mg.eve.gd>"
        assert request["data"]["to"] == "martin@eve.gd"
        assert request["data"]["subject"] == "subject"
        assert request["data"]["text"] == "body"
        assert request["data"]["h:In-Reply-To"] == "<orig@eve.gd>"

    def test_no_reply_header_when_not_a_reply(self, config):
        post = PostCollector()
        send_email(config, "m@e", "s", "b", post=post)
        assert "h:In-Reply-To" not in post.requests[0]["data"]

    def test_api_rejection_returns_false(self, config):
        assert not send_email(
            config, "m@e", "s", "b", post=PostCollector(status_code=401)
        )

    def test_network_failure_returns_false_not_raise(self, config):
        post = PostCollector(raises=requests.ConnectionError("down"))
        assert send_email(config, "m@e", "s", "b", post=post) is False


class TestDryRunReport:
    RESULT = DryRunResult(
        status="310/300 · will thread into 2 posts",
        posts=["first part", "second part"],
    )

    def test_subject_carries_id_and_counts(self):
        subject, _ = dry_run_report("a1b2c3d4", self.RESULT, image_count=1)
        assert subject == "Thought draft [mt-a1b2c3d4]: 2 post(s), 1 image(s)"

    def test_body_explains_the_thread_split(self):
        _, body = dry_run_report("a1b2c3d4", self.RESULT, image_count=0)
        assert "2 posts" in body

    def test_body_mentions_images_on_the_first_post(self):
        _, body = dry_run_report("a1b2c3d4", self.RESULT, image_count=1)
        assert "1 image" in body
        assert "first post" in body

    def test_body_previews_every_post(self):
        _, body = dry_run_report("a1b2c3d4", self.RESULT, image_count=0)
        assert "post 1" in body
        assert "first part" in body
        assert "post 2" in body
        assert "second part" in body

    def test_body_explains_the_post_reply_step(self):
        _, body = dry_run_report("a1b2c3d4", self.RESULT, image_count=0)
        assert "POST" in body
        assert "reply" in body.lower()

    def test_single_post_report_reads_naturally(self):
        result = DryRunResult(status="5/300 · posts as a single post",
                              posts=["hi"])
        subject, body = dry_run_report("a1b2c3d4", result, image_count=0)
        assert "1 post(s)" in subject
        assert "single post" in body


class TestReceipt:
    def test_success_lists_all_three_homes(self):
        result = PublishResult(
            ok=True, thought_id="20260912190000", posts=2,
            bluesky="https://bsky.app/profile/eve.gd/post/3abc",
            mastodon="https://hcommons.social/@mpe/117", pushed=True,
        )
        subject, body = receipt(result)
        assert "published" in subject.lower()
        assert "https://eve.gd/thoughts/#t20260912190000" in body
        assert "https://bsky.app/profile/eve.gd/post/3abc" in body
        assert "https://hcommons.social/@mpe/117" in body

    def test_missing_service_reported_with_its_warning(self):
        result = PublishResult(
            ok=True, thought_id="20260912190000", posts=1,
            bluesky=None, mastodon="https://hcommons.social/@mpe/117",
            warnings=["WARNING: Bluesky post failed: 502"], pushed=True,
        )
        _, body = receipt(result)
        assert "502" in body


class TestNotices:
    def test_failure_notice_carries_the_reason(self):
        subject, body = failure_notice("Empty thought; nothing to do.")
        assert "Empty thought" in body
        assert "fail" in subject.lower()

    def test_bad_reply_notice_explains_the_post_command(self):
        _, body = bad_reply_notice("a1b2c3d4")
        assert "POST" in body
        assert "a1b2c3d4" in body

    def test_missing_draft_notice_names_the_id(self):
        subject, body = missing_draft_notice("deadbeef")
        assert "deadbeef" in subject + body
