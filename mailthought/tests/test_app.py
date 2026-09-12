"""The webhook end to end: forged multipart POSTs against the Flask app.

Accepted mail must be durably on disk when the 200 leaves; everything
suspicious must come back 406 with no side effects at all.
"""

import dataclasses
import io
import json
import time

import pytest
from conftest import sign, signed_fields

from mailthought.app import (
    create_app,
    load_pending_jobs,
    persist_job,
    start_worker,
)


def inbound_form(
    config,
    sender="Martin Eve <martin@eve.gd>",
    subject="hello",
    text="a thought",
    token="tok-000001",
    spf="Pass",
    dkim="Pass",
    message_id="<m1@eve.gd>",
    signature_fields=None,
):
    headers = [["Message-Id", message_id]]
    if spf is not None:
        headers.append(["X-Mailgun-Spf", spf])
    if dkim is not None:
        headers.append(["X-Mailgun-Dkim-Check-Result", dkim])
    form = {
        "recipient": "thought@mg.eve.gd",
        "sender": "martin@eve.gd",
        "from": sender,
        "subject": subject,
        "body-plain": text,
        "stripped-text": text,
        "message-headers": json.dumps(headers),
    }
    form.update(
        signature_fields
        if signature_fields is not None
        else signed_fields(config.mailgun_signing_key, token=token)
    )
    return form


@pytest.fixture
def harness(config):
    jobs = []
    app = create_app(config, enqueue=jobs.append)
    return app.test_client(), jobs, config


class TestAcceptance:
    def test_valid_mail_is_queued_with_its_text(self, harness):
        client, jobs, config = harness
        response = client.post("/inbound", data=inbound_form(config))
        assert response.status_code == 200
        assert response.get_json()["status"] == "queued"
        (job,) = jobs
        assert job["kind"] == "publish"
        assert job["text"] == "a thought"
        assert job["sender"] == "martin@eve.gd"
        assert job["message_id"] == "<m1@eve.gd>"

    def test_job_is_on_disk_before_the_200(self, harness):
        client, _jobs, config = harness
        client.post("/inbound", data=inbound_form(config))
        pending = load_pending_jobs(config.inbox_dir)
        assert len(pending) == 1
        assert pending[0]["text"] == "a thought"

    def test_dry_run_subject_classified(self, harness):
        client, jobs, config = harness
        client.post("/inbound", data=inbound_form(config, subject="--dry run"))
        assert jobs[0]["kind"] == "dry_run"

    def test_post_reply_classified_with_its_draft_id(self, harness):
        client, jobs, config = harness
        client.post(
            "/inbound",
            data=inbound_form(
                config,
                subject="Re: Thought draft [mt-a1b2c3d4]: 2 post(s)",
                text="POST",
            ),
        )
        assert jobs[0]["kind"] == "post_draft"
        assert jobs[0]["draft_id"] == "a1b2c3d4"

    def test_reply_without_post_command_is_a_bad_reply(self, harness):
        client, jobs, config = harness
        client.post(
            "/inbound",
            data=inbound_form(
                config,
                subject="Re: Thought draft [mt-a1b2c3d4]: 2 post(s)",
                text="lovely, ship it",
            ),
        )
        assert jobs[0]["kind"] == "bad_reply"

    def test_image_attachment_lands_in_the_job(self, harness):
        client, jobs, config = harness
        data = inbound_form(config)
        data["attachment-1"] = (io.BytesIO(b"JPGBYTES"), "gate.jpg", "image/jpeg")
        client.post("/inbound", data=data)
        (image,) = jobs[0]["images"]
        assert image["mime"] == "image/jpeg"
        assert image["filename"] == "gate.jpg"
        with open(image["path"], "rb") as handle:
            assert handle.read() == b"JPGBYTES"

    def test_non_image_attachment_is_ignored(self, harness):
        client, jobs, config = harness
        data = inbound_form(config)
        data["attachment-1"] = (io.BytesIO(b"%PDF"), "paper.pdf", "application/pdf")
        client.post("/inbound", data=data)
        assert jobs[0]["images"] == []


class TestRejection:
    def test_forged_signature(self, harness):
        client, jobs, config = harness
        form = inbound_form(
            config,
            signature_fields={
                "timestamp": str(int(time.time())),
                "token": "tok-1",
                "signature": "0" * 64,
            },
        )
        response = client.post("/inbound", data=form)
        assert response.status_code == 406
        assert jobs == []
        assert load_pending_jobs(config.inbox_dir) == []

    def test_stale_timestamp(self, harness):
        client, jobs, config = harness
        stale = str(int(time.time()) - 3600)
        form = inbound_form(
            config,
            signature_fields={
                "timestamp": stale,
                "token": "tok-1",
                "signature": sign(config.mailgun_signing_key, stale, "tok-1"),
            },
        )
        assert client.post("/inbound", data=form).status_code == 406
        assert jobs == []

    def test_replayed_token(self, harness):
        client, jobs, config = harness
        fields = signed_fields(config.mailgun_signing_key, token="tok-replay")
        first = client.post(
            "/inbound", data=inbound_form(config, signature_fields=dict(fields))
        )
        second = client.post(
            "/inbound",
            data=inbound_form(
                config, message_id="<m2@eve.gd>", signature_fields=dict(fields)
            ),
        )
        assert first.status_code == 200
        assert second.status_code == 406
        assert len(jobs) == 1

    def test_sender_not_on_the_allowlist(self, harness):
        client, jobs, config = harness
        form = inbound_form(config, sender="Mallory <mallory@evil.example>")
        assert client.post("/inbound", data=form).status_code == 406
        assert jobs == []

    @pytest.mark.parametrize(
        "spf,dkim", [("Fail", "Pass"), ("Pass", "Fail"), (None, None)]
    )
    def test_unauthenticated_mail_rejected(self, harness, spf, dkim):
        client, jobs, config = harness
        form = inbound_form(config, spf=spf, dkim=dkim)
        assert client.post("/inbound", data=form).status_code == 406
        assert jobs == []

    def test_auth_gate_can_be_disabled(self, config):
        jobs = []
        relaxed = dataclasses.replace(config, require_auth=False)
        client = create_app(relaxed, enqueue=jobs.append).test_client()
        form = inbound_form(relaxed, spf="Fail", dkim="Fail")
        assert client.post("/inbound", data=form).status_code == 200
        assert len(jobs) == 1

    def test_duplicate_message_id_is_acknowledged_but_not_requeued(
        self, harness
    ):
        client, jobs, config = harness
        client.post("/inbound", data=inbound_form(config, token="tok-1"))
        response = client.post(
            "/inbound", data=inbound_form(config, token="tok-2")
        )
        assert response.status_code == 200
        assert response.get_json()["status"] == "duplicate"
        assert len(jobs) == 1

    def test_empty_post_is_rejected_not_a_crash(self, harness):
        client, jobs, _config = harness
        assert client.post("/inbound", data={}).status_code == 406
        assert jobs == []


class TestHealth:
    def test_healthz_reports_ok(self, harness):
        client, _, _ = harness
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.get_json()["ok"] is True


class TestJobPersistence:
    def test_persist_and_reload_round_trip(self, config, tmp_path):
        job = persist_job(
            tmp_path / "inbox",
            kind="publish",
            sender="martin@eve.gd",
            message_id="<m@e>",
            subject="s",
            text="the words",
            images=[{"data": b"IMG", "mime": "image/png", "alt": "a",
                     "filename": "s.png"}],
        )
        (loaded,) = load_pending_jobs(tmp_path / "inbox")
        assert loaded["text"] == "the words"
        assert loaded["kind"] == "publish"
        with open(loaded["images"][0]["path"], "rb") as handle:
            assert handle.read() == b"IMG"
        assert loaded["id"] == job["id"]

    def test_empty_inbox_means_no_pending_jobs(self, tmp_path):
        assert load_pending_jobs(tmp_path / "missing") == []


class TestWorker:
    def wait_for(self, predicate, timeout=5.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if predicate():
                return True
            time.sleep(0.01)
        return False

    def test_jobs_are_processed_in_order(self, config):
        processed = []
        enqueue, _thread = start_worker(
            config, process=lambda job, *a, **k: processed.append(job["id"])
        )
        enqueue({"id": "one", "kind": "publish", "dir": None})
        enqueue({"id": "two", "kind": "publish", "dir": None})
        assert self.wait_for(lambda: processed == ["one", "two"])

    def test_pending_jobs_from_a_crash_run_first(self, config):
        persist_job(
            config.inbox_dir, kind="publish", sender="m@e",
            message_id="<m>", subject="s", text="left behind", images=[],
        )
        processed = []
        start_worker(
            config, process=lambda job, *a, **k: processed.append(job["text"])
        )
        assert self.wait_for(lambda: processed == ["left behind"])

    def test_a_failing_job_does_not_kill_the_worker(self, config):
        processed = []

        def process(job, *args, **kwargs):
            if job["id"] == "boom":
                raise RuntimeError("pipeline exploded")
            processed.append(job["id"])

        enqueue, _thread = start_worker(config, process=process)
        enqueue({"id": "boom", "kind": "publish", "dir": None})
        enqueue({"id": "after", "kind": "publish", "dir": None})
        assert self.wait_for(lambda: processed == ["after"])
