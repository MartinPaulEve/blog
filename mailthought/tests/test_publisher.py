"""publisher: command construction, CLI output parsing, and job execution.

Every subprocess is faked: tests assert on the argument vectors issued
and on the results returned, never on internals — the pipeline could
be rewritten and these should still hold.
"""

from types import SimpleNamespace

from mailthought import drafts
from mailthought.publisher import (
    dry_run,
    parse_dry_run_output,
    parse_publish_output,
    process_job,
    publish,
    thought_command,
)

STORED_OK = (
    "Stored thought 20260912190000 (2 post(s)).\n"
    "Bluesky: https://bsky.app/profile/eve.gd/post/3abc\n"
    "Mastodon: https://hcommons.social/@mpe/117\n"
)


class FakeRun:
    """Records (cmd, cwd) and answers via a per-test handler."""

    def __init__(self, handler=None):
        self.calls = []
        self.handler = handler or (lambda cmd: (0, ""))

    def __call__(self, cmd, cwd=None, check=True):
        self.calls.append((list(cmd), cwd))
        returncode, stdout = self.handler(list(cmd))
        return SimpleNamespace(returncode=returncode, stdout=stdout, stderr="")

    def commands(self):
        return [cmd for cmd, _ in self.calls]


def git_commands(fake):
    return [cmd for cmd in fake.commands() if cmd[0] == "git"]


class TestThoughtCommand:
    def test_text_only(self):
        cmd = thought_command("a thought")
        assert cmd == [
            "uv", "run", "--env-file", ".env",
            "--project", "thought_composer", "thought",
            "--text", "a thought",
        ]

    def test_images_ride_as_repeated_flags_with_alts(self):
        cmd = thought_command(
            "t", image_paths=["/tmp/a.jpg", "/tmp/b.png"], alts=["gate", ""]
        )
        assert cmd[cmd.index("--image") + 1] == "/tmp/a.jpg"
        assert cmd.count("--image") == 2
        assert cmd[cmd.index("--alt") + 1] == "gate"

    def test_dry_run_flag(self):
        assert "--dry-run" in thought_command("t", dry_run=True)

    def test_hostile_text_stays_one_argument(self):
        hostile = "nice; rm -rf / #`$(evil)`"
        cmd = thought_command(hostile)
        assert cmd[cmd.index("--text") + 1] == hostile


class TestOutputParsing:
    def test_dry_run_segments_and_status(self):
        stdout = (
            "310/300 · will thread into 2 posts\n"
            "--- post 1 ---\n"
            "first part\nstill first\n"
            "--- post 2 ---\n"
            "second part\n"
        )
        result = parse_dry_run_output(stdout)
        assert result.status == "310/300 · will thread into 2 posts"
        assert result.posts == ["first part\nstill first", "second part"]

    def test_publish_success_with_both_services(self):
        result = parse_publish_output(STORED_OK)
        assert result.ok
        assert result.thought_id == "20260912190000"
        assert result.posts == 2
        assert result.bluesky == "https://bsky.app/profile/eve.gd/post/3abc"
        assert result.mastodon == "https://hcommons.social/@mpe/117"

    def test_partial_syndication_failure_is_still_a_success(self):
        stdout = (
            "Stored thought 20260912190000 (1 post(s)).\n"
            "WARNING: Bluesky post failed: 502 Bad Gateway\n"
            "Mastodon: https://hcommons.social/@mpe/117\n"
        )
        result = parse_publish_output(stdout)
        assert result.ok
        assert result.bluesky is None
        assert result.mastodon == "https://hcommons.social/@mpe/117"
        assert any("Bluesky" in w for w in result.warnings)

    def test_nothing_stored_is_a_failure(self):
        result = parse_publish_output("Empty thought; nothing to do.\n")
        assert not result.ok
        assert result.thought_id is None


class TestDryRun:
    def test_runs_the_cli_in_the_checkout_and_parses(self, tmp_path):
        fake = FakeRun(lambda cmd: (0, "5/300 · posts as a single post\n--- post 1 ---\nhi\n"))
        result = dry_run(tmp_path, "hi", run=fake)
        assert result.posts == ["hi"]
        (cmd, cwd), = fake.calls
        assert "--dry-run" in cmd
        assert cwd == tmp_path

    def test_no_git_commands_run_for_a_dry_run(self, tmp_path):
        fake = FakeRun(lambda cmd: (0, "x\n--- post 1 ---\nhi\n"))
        dry_run(tmp_path, "hi", run=fake)
        assert git_commands(fake) == []


class TestPublish:
    def make_handler(self, seen_images, push_failures=0):
        state = {"pushes": 0}

        def handler(cmd):
            if cmd[0] == "uv":
                for index, part in enumerate(cmd):
                    if part == "--image":
                        with open(cmd[index + 1], "rb") as handle:
                            seen_images.append(handle.read())
                return 0, STORED_OK
            if cmd[:3] == ["git", "diff", "--cached"]:
                return 1, ""  # something staged
            if cmd[:2] == ["git", "push"]:
                state["pushes"] += 1
                if state["pushes"] <= push_failures:
                    return 1, ""
                return 0, ""
            return 0, ""

        return handler

    def test_pull_thought_commit_push_in_order(self, tmp_path):
        fake = FakeRun(self.make_handler([]))
        result = publish(tmp_path / "blog", "a thought", [], run=fake,
                         workdir=tmp_path / "work")
        assert result.ok
        assert result.pushed
        cmds = fake.commands()
        assert cmds[0] == ["git", "pull", "--rebase"]
        assert cmds[1][0] == "uv" and "--text" in cmds[1]
        add = next(c for c in cmds if c[:2] == ["git", "add"])
        assert "_data/thoughts.yml" in add
        assert "assets/thoughts" not in add  # no images this time
        commit = next(c for c in cmds if c[:2] == ["git", "commit"])
        assert commit[-1] == "chore(thoughts): add 20260912190000 via mail gateway"
        assert ["git", "push"] in cmds

    def test_image_bytes_reach_the_cli_as_files(self, tmp_path):
        seen = []
        fake = FakeRun(self.make_handler(seen))
        images = [
            {"data": b"JPGBYTES", "mime": "image/jpeg", "alt": "gate",
             "filename": "gate.jpg"}
        ]
        publish(tmp_path / "blog", "t", images, run=fake,
                workdir=tmp_path / "work")
        assert seen == [b"JPGBYTES"]
        add = next(c for c in fake.commands() if c[:2] == ["git", "add"])
        assert "assets/thoughts" in add

    def test_rejected_push_is_retried_after_a_rebase(self, tmp_path):
        fake = FakeRun(self.make_handler([], push_failures=1))
        result = publish(tmp_path / "blog", "t", [], run=fake,
                         workdir=tmp_path / "work")
        assert result.pushed
        cmds = fake.commands()
        assert cmds.count(["git", "push"]) == 2
        # a rebase happens between the two pushes
        between = cmds[cmds.index(["git", "push"]) + 1:]
        assert ["git", "pull", "--rebase"] in between

    def test_failed_store_means_no_commit(self, tmp_path):
        def handler(cmd):
            if cmd[0] == "uv":
                return 1, "Empty thought; nothing to do.\n"
            return 0, ""

        fake = FakeRun(handler)
        result = publish(tmp_path / "blog", "", [], run=fake,
                         workdir=tmp_path / "work")
        assert not result.ok
        assert not any(c[:2] == ["git", "commit"] for c in fake.commands())

    def test_stored_but_deploy_failed_still_commits_and_warns(self, tmp_path):
        def handler(cmd):
            if cmd[0] == "uv":
                return 1, STORED_OK  # CLI exits 1 when the quick deploy fails
            if cmd[:3] == ["git", "diff", "--cached"]:
                return 1, ""
            return 0, ""

        fake = FakeRun(handler)
        result = publish(tmp_path / "blog", "t", [], run=fake,
                         workdir=tmp_path / "work")
        assert result.ok
        assert any(c[:2] == ["git", "commit"] for c in fake.commands())
        assert result.warnings  # the deploy failure is reported


def make_job(tmp_path, kind, text="a thought", draft_id=None, images=()):
    job_dir = tmp_path / "inbox" / "job-1"
    job_dir.mkdir(parents=True, exist_ok=True)
    image_entries = []
    for index, (name, mime, data) in enumerate(images, 1):
        path = job_dir / f"image-{index}"
        path.write_bytes(data)
        image_entries.append(
            {"path": str(path), "mime": mime, "alt": "", "filename": name}
        )
    return {
        "id": "job-1",
        "kind": kind,
        "draft_id": draft_id,
        "sender": "martin@eve.gd",
        "message_id": "<original@eve.gd>",
        "subject": "s",
        "text": text,
        "images": image_entries,
        "dir": str(job_dir),
    }


class SendCollector:
    def __init__(self):
        self.sent = []

    def __call__(self, config, to, subject, body, in_reply_to=None):
        self.sent.append(
            {"to": to, "subject": subject, "body": body,
             "in_reply_to": in_reply_to}
        )
        return True


class TestProcessJob:
    def test_publish_job_sends_a_receipt_to_the_sender(self, config, tmp_path):
        fake = FakeRun(lambda cmd: (
            (0, STORED_OK) if cmd[0] == "uv"
            else (1, "") if cmd[:3] == ["git", "diff", "--cached"]
            else (0, "")
        ))
        send = SendCollector()
        job = make_job(tmp_path, "publish",
                       images=[("gate.jpg", "image/jpeg", b"JPG")])
        process_job(job, config, run=fake, send=send)
        (mail,) = send.sent
        assert mail["to"] == "martin@eve.gd"
        assert mail["in_reply_to"] == "<original@eve.gd>"
        assert "https://bsky.app/profile/eve.gd/post/3abc" in mail["body"]
        assert "https://hcommons.social/@mpe/117" in mail["body"]

    def test_dry_run_job_saves_a_draft_and_previews(self, config, tmp_path):
        fake = FakeRun(lambda cmd: (
            0, "5/300 · posts as a single post\n--- post 1 ---\na thought\n"
        ))
        send = SendCollector()
        job = make_job(tmp_path, "dry_run")
        process_job(job, config, run=fake, send=send)

        assert git_commands(fake) == []
        (mail,) = send.sent
        assert "[mt-" in mail["subject"]

        draft_dirs = list(config.drafts_dir.iterdir())
        assert len(draft_dirs) == 1
        saved = drafts.load_draft(config.drafts_dir, draft_dirs[0].name)
        assert saved["text"] == "a thought"
        assert draft_dirs[0].name in mail["subject"]
        assert "a thought" in mail["body"]

    def test_post_draft_job_publishes_the_draft_then_deletes_it(
        self, config, tmp_path
    ):
        drafts.save_draft(
            config.drafts_dir, "a1b2c3d4", text="drafted words",
            images=[{"data": b"IMG", "mime": "image/png", "alt": "",
                     "filename": "s.png"}],
            sender="martin@eve.gd", message_id="<draft@eve.gd>",
        )
        captured = []

        def handler(cmd):
            if cmd[0] == "uv":
                assert cmd[cmd.index("--text") + 1] == "drafted words"
                for index, part in enumerate(cmd):
                    if part == "--image":
                        with open(cmd[index + 1], "rb") as handle:
                            captured.append(handle.read())
                return 0, STORED_OK
            if cmd[:3] == ["git", "diff", "--cached"]:
                return 1, ""
            return 0, ""

        send = SendCollector()
        job = make_job(tmp_path, "post_draft", text="POST", draft_id="a1b2c3d4")
        process_job(job, config, run=FakeRun(handler), send=send)

        assert captured == [b"IMG"]
        assert drafts.load_draft(config.drafts_dir, "a1b2c3d4") is None
        (mail,) = send.sent
        assert "https://bsky.app" in mail["body"]

    def test_post_draft_with_unknown_id_reports_and_touches_nothing(
        self, config, tmp_path
    ):
        fake = FakeRun()
        send = SendCollector()
        job = make_job(tmp_path, "post_draft", text="POST", draft_id="deadbeef")
        process_job(job, config, run=fake, send=send)
        assert fake.calls == []
        (mail,) = send.sent
        assert "deadbeef" in mail["subject"] or "deadbeef" in mail["body"]

    def test_bad_reply_gets_instructions_and_no_pipeline_runs(
        self, config, tmp_path
    ):
        fake = FakeRun()
        send = SendCollector()
        job = make_job(tmp_path, "bad_reply", draft_id="a1b2c3d4")
        process_job(job, config, run=fake, send=send)
        assert fake.calls == []
        (mail,) = send.sent
        assert "POST" in mail["body"]

    def test_failed_publish_sends_a_failure_notice(self, config, tmp_path):
        fake = FakeRun(lambda cmd: (
            (1, "Empty thought; nothing to do.\n") if cmd[0] == "uv" else (0, "")
        ))
        send = SendCollector()
        job = make_job(tmp_path, "publish", text="")
        process_job(job, config, run=fake, send=send)
        (mail,) = send.sent
        assert "Empty thought" in mail["body"]
