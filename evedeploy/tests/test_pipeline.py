import os
import subprocess

import pytest

from evedeploy.pipeline import (
    DeployError,
    biron_deposit_new,
    build_site,
    check_preflight,
    commit_sent_state,
    deploy,
    fetch_lastfm,
    fetch_webmentions,
    git_commit_push,
    jekyll_build,
    kcworks_deposit_new,
    posts_missing_marker,
    quick_deploy,
    refresh_cv,
    resize_covers,
    rsync_site,
    send_webmentions,
    sequoia_dry_run,
    serve_site,
    stamp_roguescholar_ids,
)


class FakeRun:
    """A subprocess.run stand-in: records commands, returns scripted results.

    ``outcomes`` maps a command's first tokens (joined) to either an int
    returncode or a (returncode, stdout) pair. Unknown commands succeed.
    """

    def __init__(self, outcomes=None):
        self.calls = []
        self.outcomes = outcomes or {}

    def __call__(self, cmd, cwd=None, check=True, capture=False):
        self.calls.append({"cmd": list(cmd), "cwd": cwd, "check": check})
        outcome = self.outcomes.get(" ".join(cmd[:2]), 0)
        stdout = ""
        if isinstance(outcome, tuple):
            returncode, stdout = outcome
        else:
            returncode = outcome
        if check and returncode != 0:
            raise subprocess.CalledProcessError(returncode, cmd)
        result = subprocess.CompletedProcess(cmd, returncode)
        result.stdout = stdout
        return result

    def commands(self):
        return [" ".join(call["cmd"][:2]) for call in self.calls]


@pytest.fixture
def root(tmp_path):
    blog = tmp_path / "blog"
    blog.mkdir()
    (blog / "resize_covers.py").write_text("# resizer")
    (blog / "_webmentions").mkdir()
    (blog / "_webmentions" / "fetch_webmentions.py").write_text("# fetcher")
    (blog / "_webmentions" / "send_webmentions.py").write_text("# sender")
    (blog / "_lastfm").mkdir()
    (blog / "_lastfm" / "fetch_lastfm.py").write_text("# lastfm fetcher")
    (blog / "_identifiers").mkdir()
    (blog / "_identifiers" / "fetch_roguescholar.py").write_text("# rs fetcher")
    (blog / "kcworks.sh").write_text("# kcworks driver")
    (blog / ".env").write_text("WEBMENTION_IO_TOKEN=test-token")
    return blog


def make_post(root, name, *markers):
    """A minimal _posts entry carrying the given front-matter lines."""
    posts = root / "_posts"
    posts.mkdir(exist_ok=True)
    front = "".join(f"{marker}\n" for marker in markers)
    (posts / name).write_text(f"---\ntitle: x\n{front}---\nbody\n")


def stamp_post(root, name, marker):
    """Insert a front-matter line, as the stamping tools would."""
    path = root / "_posts" / name
    path.write_text(path.read_text().replace(
        "---\nbody", f"{marker}\n---\nbody"))


def stamping(inner, root, trigger, name, marker, once=False):
    """Wrap a run callable: stamp the post when a matching command runs."""
    state = {"done": False}

    def run(cmd, cwd=None, check=True, capture=False):
        result = inner(cmd, cwd=cwd, check=check, capture=capture)
        if trigger(cmd) and not (once and state["done"]):
            stamp_post(root, name, marker)
            state["done"] = True
        return result

    run.inner = inner
    return run


class TestPreflight:
    def test_missing_sequoia_is_fatal(self):
        with pytest.raises(DeployError, match="sequoia"):
            check_preflight(run=FakeRun(), which=lambda name: None)

    def test_sequoia_alone_is_enough_when_node_is_absent(self):
        which = lambda name: "/bin/sequoia" if name == "sequoia" else None
        check_preflight(run=FakeRun(), which=which)

    def test_old_node_is_fatal(self):
        run = FakeRun({"node -p": (0, "18\n")})
        with pytest.raises(DeployError, match="19"):
            check_preflight(run=run, which=lambda name: f"/bin/{name}")

    def test_new_node_passes(self):
        run = FakeRun({"node -p": (0, "24\n")})
        check_preflight(run=run, which=lambda name: f"/bin/{name}")


class TestResizeCovers:
    def test_runs_resizer_through_uv(self, root):
        run = FakeRun()
        assert resize_covers(root, run=run) is True
        assert run.calls[0]["cmd"] == [
            "uv",
            "run",
            "--with",
            "pillow",
            "--with",
            "python-frontmatter",
            "./resize_covers.py",
        ]
        assert run.calls[0]["cwd"] == root

    def test_skipped_when_disabled(self, root):
        run = FakeRun()
        assert resize_covers(root, run=run, enabled=False) is False
        assert run.calls == []

    def test_skipped_when_resizer_missing(self, root):
        (root / "resize_covers.py").unlink()
        run = FakeRun()
        assert resize_covers(root, run=run) is False
        assert run.calls == []


class TestRefreshCv:
    def test_copies_both_cv_files(self, root, tmp_path):
        source = tmp_path / "eprintsToCV" / "output"
        source.mkdir(parents=True)
        (source / "martin_paul_eve.pdf").write_bytes(b"%PDF cv")
        (source / "martin_paul_eve.html").write_text("<p>cv</p>")
        (root / "c-v").mkdir()
        (root / "_includes").mkdir()

        assert refresh_cv(root) is True
        assert (root / "c-v" / "Eve-CV.pdf").read_bytes() == b"%PDF cv"
        assert (root / "_includes" / "publications.html").read_text() == (
            "<p>cv</p>"
        )

    def test_missing_source_leaves_existing_files_alone(self, root):
        (root / "c-v").mkdir()
        (root / "c-v" / "Eve-CV.pdf").write_bytes(b"old")
        assert refresh_cv(root) is False
        assert (root / "c-v" / "Eve-CV.pdf").read_bytes() == b"old"


class TestGitCommitPush:
    def test_clean_tree_commits_nothing(self, root):
        run = FakeRun({"git diff": 0})
        assert git_commit_push(root, "msg", run=run) is False
        assert "git commit" not in run.commands()
        assert "git push" not in run.commands()

    def test_dirty_tree_commits_and_pushes(self, root):
        run = FakeRun({"git diff": 1})
        assert git_commit_push(root, "the message", run=run) is True
        assert "git add" in run.commands()
        commit = next(
            call["cmd"]
            for call in run.calls
            if call["cmd"][:2] == ["git", "commit"]
        )
        assert "the message" in commit
        assert "git push" in run.commands()


class TestFetchWebmentions:
    def test_runs_the_fetch_script_through_uv_with_env_file(self, root):
        run = FakeRun()
        assert fetch_webmentions(root, run=run, echo=lambda *a, **k: None) is True
        assert run.calls[0]["cmd"] == [
            "uv",
            "run",
            "--env-file",
            ".env",
            "_webmentions/fetch_webmentions.py",
        ]
        assert run.calls[0]["cwd"] == root

    def test_missing_env_file_omits_the_flag(self, root):
        # A checkout without .env must still deploy; the fetch script itself
        # degrades to a no-op without a token.
        (root / ".env").unlink()
        run = FakeRun()
        assert fetch_webmentions(root, run=run, echo=lambda *a, **k: None) is True
        assert run.calls[0]["cmd"] == [
            "uv",
            "run",
            "_webmentions/fetch_webmentions.py",
        ]

    def test_failure_warns_but_does_not_raise(self, root):
        run = FakeRun({"uv run": 1})
        lines = []
        assert fetch_webmentions(root, run=run, echo=lines.append) is False
        assert any("webmention" in line.lower() for line in lines)

    def test_skipped_when_script_absent(self, root):
        # A checkout without the webmention tooling deploys as before.
        run = FakeRun()
        assert fetch_webmentions(root, run=run, echo=lambda *a, **k: None,
                                 present=lambda p: False) is False
        assert run.calls == []


class TestSequoiaDryRun:
    def test_up_to_date_reports_nothing_pending(self):
        run = FakeRun({"sequoia publish":
                       (0, "All posts are up to date. Nothing to publish.")})
        assert sequoia_dry_run(run=run, echo=lambda *a: None) is False

    def test_pending_posts_report_something_to_publish(self):
        run = FakeRun({"sequoia publish": (0, "Would publish: 2026-09-08-new")})
        assert sequoia_dry_run(run=run, echo=lambda *a: None) is True

    def test_the_preview_is_echoed_for_the_operator(self):
        run = FakeRun({"sequoia publish": (0, "Would publish: 2026-09-08-new")})
        lines = []
        sequoia_dry_run(run=run, echo=lines.append)
        assert any("2026-09-08-new" in line for line in lines)

    def test_failure_raises_deploy_error(self):
        run = FakeRun({"sequoia publish": 3})
        with pytest.raises(DeployError):
            sequoia_dry_run(run=run, echo=lambda *a: None)


class TestFetchLastfm:
    def test_runs_the_fetch_script_through_uv_with_env_file(self, root):
        run = FakeRun()
        assert fetch_lastfm(root, run=run, echo=lambda *a, **k: None) is True
        assert run.calls[0]["cmd"] == [
            "uv",
            "run",
            "--env-file",
            ".env",
            "_lastfm/fetch_lastfm.py",
        ]
        assert run.calls[0]["cwd"] == root

    def test_failure_warns_but_does_not_raise(self, root):
        run = FakeRun({"uv run": 1})
        lines = []
        assert fetch_lastfm(root, run=run, echo=lines.append) is False
        assert any("last.fm" in line.lower() for line in lines)

    def test_failure_is_reported_as_an_error(self, root):
        # The step is tolerant, but the failure must be unmissable in the
        # deploy output — a warning proved too quiet in practice.
        run = FakeRun({"uv run": 1})
        lines = []
        fetch_lastfm(root, run=run, echo=lines.append)
        assert any("error" in line.lower() for line in lines)

    def test_skipped_when_script_absent(self, root):
        # A checkout without the Last.fm tooling deploys as before.
        run = FakeRun()
        assert fetch_lastfm(root, run=run, echo=lambda *a, **k: None,
                            present=lambda p: False) is False
        assert run.calls == []


class TestPostsMissingMarker:
    def test_lists_posts_lacking_the_marker(self, root):
        make_post(root, "2026-01-01-a.md")
        make_post(root, "2026-01-02-b.md", "kcworks: https://works/x")
        assert posts_missing_marker(root, "kcworks:") == [
            "_posts/2026-01-01-a.md"]

    def test_marker_in_the_body_does_not_count(self, root):
        make_post(root, "2026-01-01-a.md")
        path = root / "_posts" / "2026-01-01-a.md"
        path.write_text(path.read_text() + "kcworks: mentioned in prose\n")
        assert posts_missing_marker(root, "kcworks:") == [
            "_posts/2026-01-01-a.md"]

    def test_no_posts_directory_is_empty(self, tmp_path):
        assert posts_missing_marker(tmp_path, "kcworks:") == []


class TestStampRoguescholarIds:
    def test_runs_the_fetcher_over_the_pending_posts(self, root):
        make_post(root, "2026-01-01-a.md", "kcworks: k")
        run = FakeRun()
        stamp_roguescholar_ids(root, ["_posts/2026-01-01-a.md"], run=run,
                               echo=lambda *a, **k: None)
        assert run.calls[0]["cmd"] == [
            "uv", "run", "--with", "pyyaml", "--with", "certifi",
            "_identifiers/fetch_roguescholar.py", "_posts/2026-01-01-a.md",
        ]
        assert run.calls[0]["cwd"] == root
        # Exit 1 just means "not harvested yet" and must not raise.
        assert run.calls[0]["check"] is False

    def test_polling_arguments_are_passed_when_waiting(self, root):
        make_post(root, "2026-01-01-a.md")
        run = FakeRun()
        stamp_roguescholar_ids(root, ["_posts/2026-01-01-a.md"], run=run,
                               echo=lambda *a, **k: None,
                               attempts=8, interval=120.0)
        cmd = run.calls[0]["cmd"]
        assert "--attempts" in cmd and "8" in cmd
        assert "--interval" in cmd and "120" in cmd

    def test_returns_the_posts_the_fetcher_stamped(self, root):
        make_post(root, "2026-01-01-a.md")
        make_post(root, "2026-01-02-b.md")
        run = stamping(FakeRun(), root,
                       lambda cmd: "fetch_roguescholar" in " ".join(cmd),
                       "2026-01-01-a.md", "roguescholar: https://rs/x")
        stamped = stamp_roguescholar_ids(
            root, ["_posts/2026-01-01-a.md", "_posts/2026-01-02-b.md"],
            run=run, echo=lambda *a, **k: None)
        assert stamped == ["_posts/2026-01-01-a.md"]

    def test_nothing_pending_runs_nothing(self, root):
        run = FakeRun()
        assert stamp_roguescholar_ids(root, [], run=run,
                                      echo=lambda *a, **k: None) == []
        assert run.calls == []

    def test_skipped_when_fetcher_absent(self, root):
        make_post(root, "2026-01-01-a.md")
        run = FakeRun()
        assert stamp_roguescholar_ids(root, ["_posts/2026-01-01-a.md"],
                                      run=run, echo=lambda *a, **k: None,
                                      present=lambda p: False) == []
        assert run.calls == []


class TestKcworksDepositNew:
    def test_deposits_pending_posts_through_the_driver(self, root):
        make_post(root, "2026-01-01-a.md")
        run = stamping(FakeRun(), root,
                       lambda cmd: cmd[0] == "./kcworks.sh",
                       "2026-01-01-a.md", "kcworks: https://works/x")
        stamped = kcworks_deposit_new(root, run=run,
                                      echo=lambda *a, **k: None)
        assert stamped == ["_posts/2026-01-01-a.md"]
        assert run.inner.calls[0]["cmd"] == ["./kcworks.sh", "backfill"]
        assert run.inner.calls[0]["cwd"] == root

    def test_nothing_pending_runs_nothing(self, root):
        make_post(root, "2026-01-01-a.md", "kcworks: k")
        run = FakeRun()
        assert kcworks_deposit_new(root, run=run,
                                   echo=lambda *a, **k: None) == []
        assert run.calls == []

    def test_failure_is_reported_as_an_error_and_does_not_raise(self, root):
        make_post(root, "2026-01-01-a.md")
        run = FakeRun({"./kcworks.sh backfill": 1})
        lines = []
        assert kcworks_deposit_new(root, run=run, echo=lines.append) == []
        assert any("error" in line.lower() for line in lines)
        assert any("kc works" in line.lower() for line in lines)

    def test_skipped_when_driver_absent(self, root):
        make_post(root, "2026-01-01-a.md")
        run = FakeRun()
        assert kcworks_deposit_new(root, run=run,
                                   echo=lambda *a, **k: None,
                                   present=lambda p: False) == []
        assert run.calls == []


class TestQuickDeploy:
    def test_builds_then_rsyncs(self, root):
        run = FakeRun()
        assert quick_deploy(root, run=run, echo=lambda *a, **k: None) is True
        cmds = run.commands()
        assert "jekyll build" in cmds
        assert "rsync -avz" in cmds
        assert cmds.index("jekyll build") < cmds.index("rsync -avz")

    def test_touches_nothing_else(self, root):
        # No sequoia, git, deposits, or feed fetches — a thought must
        # ship in seconds without any repository or publishing work.
        run = FakeRun()
        quick_deploy(root, run=run, echo=lambda *a, **k: None)
        joined = " ".join(" ".join(call["cmd"]) for call in run.calls)
        for forbidden in ("sequoia", "git", "kcworks", "biron",
                          "webmention", "lastfm", "resize"):
            assert forbidden not in joined


class TestBironDepositNew:
    def _enable(self, root):
        (root / "biron.sh").write_text("# biron driver")
        (root / ".env").write_text(
            "WEBMENTION_IO_TOKEN=test-token\n"
            "BIRON_USERNAME=user\nBIRON_PASSWORD=pass\n")

    def test_runs_backfill_through_the_driver(self, root):
        self._enable(root)
        run = FakeRun()
        assert biron_deposit_new(root, run=run,
                                 echo=lambda *a, **k: None) is True
        assert run.calls[0]["cmd"] == ["./biron.sh", "backfill"]
        assert run.calls[0]["cwd"] == root

    def test_skipped_without_credentials_in_env(self, root):
        (root / "biron.sh").write_text("# biron driver")
        run = FakeRun()
        assert biron_deposit_new(root, run=run,
                                 echo=lambda *a, **k: None) is False
        assert run.calls == []

    def test_cookie_auto_configuration_enables_the_step(self, root):
        # Session-cookie auth: BIRON_COOKIE=auto (no username) must count
        # as configured.
        (root / "biron.sh").write_text("# biron driver")
        (root / ".env").write_text("BIRON_COOKIE=auto\n")
        run = FakeRun()
        assert biron_deposit_new(root, run=run,
                                 echo=lambda *a, **k: None) is True
        assert run.calls[0]["cmd"] == ["./biron.sh", "backfill"]

    def test_skipped_when_driver_absent(self, root):
        run = FakeRun()
        assert biron_deposit_new(root, run=run, echo=lambda *a, **k: None,
                                 present=lambda p: False) is False
        assert run.calls == []

    def test_failure_is_reported_as_an_error_and_does_not_raise(self, root):
        self._enable(root)
        run = FakeRun({"./biron.sh backfill": 1})
        lines = []
        assert biron_deposit_new(root, run=run, echo=lines.append) is False
        assert any("error" in line.lower() for line in lines)
        assert any("biron" in line.lower() for line in lines)

    def test_deploy_runs_the_backfill_after_shipping(self, root):
        self._enable(root)
        run = FakeRun({"git diff": 1})
        result = deploy(root=root, message="msg", confirm=lambda: True,
                        run=run, echo=lambda *a, **k: None,
                        which=lambda name: None, sequoia=False)
        assert result is True
        cmds = run.commands()
        assert "./biron.sh backfill" in cmds
        assert cmds.index("./biron.sh backfill") > cmds.index("rsync -avz")


class TestSendWebmentions:
    def test_runs_the_send_script_through_uv_with_env_file(self, root):
        run = FakeRun()
        assert send_webmentions(root, run=run, echo=lambda *a, **k: None) is True
        assert run.calls[0]["cmd"] == [
            "uv",
            "run",
            "--env-file",
            ".env",
            "_webmentions/send_webmentions.py",
        ]
        assert run.calls[0]["cwd"] == root

    def test_failure_warns_but_does_not_raise(self, root):
        run = FakeRun({"uv run": 1})
        lines = []
        assert send_webmentions(root, run=run, echo=lines.append) is False
        assert any("webmention" in line.lower() for line in lines)


class TestCommitSentState:
    def test_clean_state_commits_nothing(self, root):
        run = FakeRun({"git diff": 0})
        assert commit_sent_state(root, run=run) is False
        assert "git commit" not in run.commands()

    def test_changed_state_is_committed_and_pushed(self, root):
        run = FakeRun({"git diff": 1})
        assert commit_sent_state(root, run=run) is True
        add = next(c["cmd"] for c in run.calls if c["cmd"][:2] == ["git", "add"])
        assert "_webmentions/sent.json" in add
        commit = next(
            c["cmd"] for c in run.calls if c["cmd"][:2] == ["git", "commit"]
        )
        assert any("webmention" in part for part in commit)
        assert "git push" in run.commands()


class TestBuildAndRsync:
    def test_jekyll_build_runs_plain_jekyll_at_root(self, root):
        run = FakeRun()
        jekyll_build(root, run=run)
        assert run.calls[0]["cmd"] == ["jekyll", "build"]
        assert run.calls[0]["cwd"] == root

    def test_jekyll_build_silences_the_nix_gemfile_deprecation(
            self, root, monkeypatch):
        # The nix-wrapped jekyll runs Bundler.setup against its own read-only
        # Gemfile, which still uses the legacy :mingw/:mswin platform symbols.
        # We can't edit that file, so the build must quiet the deprecation.
        monkeypatch.delenv("BUNDLE_SILENCE_DEPRECATIONS", raising=False)
        jekyll_build(root, run=FakeRun())
        assert os.environ.get("BUNDLE_SILENCE_DEPRECATIONS") == "true"

    def test_jekyll_build_respects_an_existing_silence_setting(
            self, root, monkeypatch):
        monkeypatch.setenv("BUNDLE_SILENCE_DEPRECATIONS", "false")
        jekyll_build(root, run=FakeRun())
        assert os.environ.get("BUNDLE_SILENCE_DEPRECATIONS") == "false"

    def test_rsync_pushes_site_dir_to_server(self, root):
        run = FakeRun()
        rsync_site(root, run=run)
        assert run.calls[0]["cmd"] == [
            "rsync",
            "-avz",
            f"{root}/_site/",
            "evegd@reclaim:/home/evegd/blog/_site/",
        ]


class TestBuildSite:
    def test_resizes_covers_then_builds_and_nothing_else(self, root):
        run = FakeRun()
        build_site(root, run=run, echo=lambda *a, **k: None)
        assert run.commands() == ["uv run", "jekyll build"]

    def test_no_resize_runs_only_the_build(self, root):
        run = FakeRun()
        build_site(root, resize=False, run=run, echo=lambda *a, **k: None)
        assert run.commands() == ["jekyll build"]

    def test_never_publishes_commits_or_deploys(self, root):
        run = FakeRun()
        build_site(root, run=run, echo=lambda *a, **k: None)
        commands = run.commands()
        assert not any(c.startswith("sequoia") for c in commands)
        assert not any(c.startswith("git") for c in commands)
        assert not any(c.startswith("rsync") for c in commands)

    def test_works_without_sequoia_on_path(self, root):
        # No preflight: a local build must not demand the publish toolchain.
        run = FakeRun()
        build_site(root, run=run, echo=lambda *a, **k: None)
        assert "jekyll build" in run.commands()

    def test_build_failure_raises_deploy_error(self, root):
        run = FakeRun({"jekyll build": 1})
        with pytest.raises(DeployError, match="jekyll"):
            build_site(root, run=run, echo=lambda *a, **k: None)

    def test_tells_the_user_where_the_site_is(self, root):
        lines = []
        build_site(root, run=FakeRun(), echo=lines.append)
        assert any("_site" in line for line in lines)


class TestServeSite:
    def test_serves_the_site_dir_on_localhost(self, root):
        run = FakeRun()
        serve_site(
            root,
            run=run,
            echo=lambda *a, **k: None,
            port_free=lambda p: True,
        )
        assert run.calls[0]["cmd"] == [
            "python3",
            "-m",
            "http.server",
            "--bind",
            "127.0.0.1",
            "-d",
            f"{root}/_site",
            "8000",
        ]

    def test_tells_the_user_the_preview_url(self, root):
        lines = []
        serve_site(
            root,
            run=FakeRun(),
            echo=lines.append,
            port_free=lambda p: True,
        )
        assert any("http://127.0.0.1:8000" in line for line in lines)

    def test_busy_port_falls_over_to_the_next_free_one(self, root):
        run = FakeRun()
        lines = []
        serve_site(
            root,
            run=run,
            echo=lines.append,
            port_free=lambda p: p != 8000,
        )
        assert run.calls[0]["cmd"][-1] == "8001"
        assert any("http://127.0.0.1:8001" in line for line in lines)

    def test_no_free_port_at_all_is_a_deploy_error(self, root):
        run = FakeRun()
        with pytest.raises(DeployError, match="port"):
            serve_site(
                root,
                run=run,
                echo=lambda *a, **k: None,
                port_free=lambda p: False,
            )
        assert run.calls == []

    def test_ctrl_c_stops_the_server_cleanly(self, root):
        def interrupted(cmd, cwd=None, check=True, capture=False):
            raise KeyboardInterrupt

        serve_site(
            root,
            run=interrupted,
            echo=lambda *a, **k: None,
            port_free=lambda p: True,
        )


class TestDeploy:
    def deploy_kwargs(self, root, run, confirm=lambda: True):
        return {
            "root": root,
            "message": "msg",
            "confirm": confirm,
            "run": run,
            "echo": lambda *a, **k: None,
            "which": lambda name: (
                f"/bin/{name}" if name == "sequoia" else None
            ),
        }

    def test_declining_the_gate_aborts_before_any_publish(self, root):
        run = FakeRun()
        result = deploy(**self.deploy_kwargs(root, run, confirm=lambda: False))
        assert result is False
        assert "sequoia publish" in run.commands()  # the dry run only
        publishes = [
            call["cmd"]
            for call in run.calls
            if call["cmd"][:2] == ["sequoia", "publish"]
        ]
        assert publishes == [["sequoia", "publish", "--dry-run"]]
        assert "jekyll build" not in run.commands()
        assert "rsync -avz" not in run.commands()

    def test_nothing_to_publish_skips_the_confirmation_prompt(self, root):
        # When the dry run reports the repo is up to date there is no
        # irreversible publish to guard, so the deploy proceeds without
        # asking — but still builds and ships any edits.
        run = FakeRun({"sequoia publish":
                       (0, "All posts are up to date. Nothing to publish."),
                       "git diff": 1})
        asked = []
        kwargs = self.deploy_kwargs(
            root, run, confirm=lambda: asked.append(True) or True)
        result = deploy(**kwargs)
        assert result is True
        assert asked == [], "must not prompt when nothing is pending"
        assert "jekyll build" in run.commands()
        assert "rsync -avz" in run.commands()

    def test_pending_posts_still_prompt(self, root):
        # Something to publish → the gate is honoured; declining aborts.
        run = FakeRun({"sequoia publish": (0, "Would publish: 2026-09-08-new")})
        asked = []

        def confirm():
            asked.append(True)
            return False

        result = deploy(**self.deploy_kwargs(root, run, confirm=confirm))
        assert asked == [True], "must prompt when a post is pending"
        assert result is False
        assert "jekyll build" not in run.commands()

    def test_no_sequoia_skips_dry_run_publish_and_gate(self, root):
        # sequoia=False must run no sequoia command at all, and with no
        # irreversible ATProto publish to guard there is nothing to
        # confirm — but the site still builds and ships.
        run = FakeRun({"git diff": 1})
        asked = []
        kwargs = self.deploy_kwargs(
            root, run, confirm=lambda: asked.append(True) or True)
        result = deploy(sequoia=False, **kwargs)
        assert result is True
        assert "sequoia publish" not in run.commands()
        assert asked == [], "must not prompt when sequoia is skipped"
        assert "jekyll build" in run.commands()
        assert "rsync -avz" in run.commands()

    def test_no_sequoia_needs_no_sequoia_on_path(self, root):
        # The preflight exists only to guard the sequoia publish, so a
        # sequoia-less deploy must not demand the tool be installed.
        run = FakeRun({"git diff": 1})
        kwargs = self.deploy_kwargs(root, run)
        kwargs["which"] = lambda name: None
        result = deploy(sequoia=False, **kwargs)
        assert result is True

    def test_full_deploy_runs_steps_in_script_order(self, root):
        run = FakeRun({"git diff": 1})
        result = deploy(**self.deploy_kwargs(root, run))
        assert result is True
        commands = run.commands()
        # resize, dry run, publish, fetch webmentions (so the build renders
        # fresh mentions), fetch Last.fm stats (so the sidebar widget renders
        # fresh listening data), build, git, rsync, THEN send webmentions
        # (their receivers verify the live source page) and commit the sent
        # state.
        expected_order = [
            "uv run",  # resize covers
            "sequoia publish",  # dry run
            "sequoia publish",  # real publish
            "uv run",  # fetch webmentions
            "uv run",  # fetch Last.fm stats
            "jekyll build",
            "git add",
            "git diff",
            "git commit",
            "git push",
            "rsync -avz",
            "uv run",  # send webmentions
            "git add",  # commit sent state
            "git commit",
            "git push",
        ]
        positions = []
        cursor = 0
        for expected in expected_order:
            cursor = commands.index(expected, cursor)
            positions.append(cursor)
            cursor += 1
        assert positions == sorted(positions)

    def test_deploy_fetches_lastfm_stats_before_the_build(self, root):
        run = FakeRun({"git diff": 1})
        deploy(**self.deploy_kwargs(root, run))
        scripts = [call["cmd"][-1] for call in run.calls
                   if call["cmd"][:2] == ["uv", "run"]]
        assert "_lastfm/fetch_lastfm.py" in scripts
        lastfm_at = next(i for i, call in enumerate(run.calls)
                         if call["cmd"][-1] == "_lastfm/fetch_lastfm.py")
        build_at = next(i for i, call in enumerate(run.calls)
                        if call["cmd"][:2] == ["jekyll", "build"])
        assert lastfm_at < build_at

    def test_new_post_is_deposited_after_the_build_and_rendered_by_a_second(
            self, root):
        # The deposit needs the built PDF, and the built pages need the
        # freshly stamped kcworks: link — so build, deposit, build again.
        make_post(root, "2026-09-08-new.md", "roguescholar: r")
        run = stamping(FakeRun({"git diff": 1}), root,
                       lambda cmd: cmd[0] == "./kcworks.sh",
                       "2026-09-08-new.md", "kcworks: https://works/x")
        assert deploy(**self.deploy_kwargs(root, run)) is True
        commands = run.inner.commands()
        deposit_at = commands.index("./kcworks.sh backfill")
        builds = [i for i, c in enumerate(commands) if c == "jekyll build"]
        assert len(builds) == 2
        assert builds[0] < deposit_at < builds[1]
        assert builds[1] < commands.index("rsync -avz")

    def test_no_new_posts_means_one_build_and_no_deposit(self, root):
        make_post(root, "2026-01-01-old.md", "kcworks: k", "roguescholar: r")
        run = FakeRun({"git diff": 1})
        assert deploy(**self.deploy_kwargs(root, run)) is True
        commands = run.commands()
        assert "./kcworks.sh backfill" not in commands
        assert commands.count("jekyll build") == 1

    def test_pending_roguescholar_links_are_stamped_before_the_build(
            self, root):
        # A post published in an earlier deploy picks its link up at the
        # start of the next one — no dedicated second deploy run needed.
        make_post(root, "2026-01-01-old.md", "kcworks: k")
        run = stamping(FakeRun({"git diff": 1}), root,
                       lambda cmd: "fetch_roguescholar" in " ".join(cmd),
                       "2026-01-01-old.md", "roguescholar: https://rs/x")
        assert deploy(**self.deploy_kwargs(root, run)) is True
        commands = run.inner.commands()
        fetch_at = next(
            i for i, call in enumerate(run.inner.calls)
            if "fetch_roguescholar" in " ".join(call["cmd"]))
        assert fetch_at < commands.index("jekyll build")
        assert commands.count("jekyll build") == 1

    def test_deploy_waits_for_roguescholar_then_redeploys_the_links(
            self, root):
        # The tail: a brand-new post goes live in the rsync, Rogue Scholar
        # harvests it, and the same deploy run stamps, rebuilds, commits and
        # rsyncs again — the "second deployment" folded into one command.
        make_post(root, "2026-09-08-new.md")
        inner = FakeRun({"git diff": 1})
        with_kc = stamping(inner, root,
                           lambda cmd: cmd[0] == "./kcworks.sh",
                           "2026-09-08-new.md", "kcworks: https://works/x")
        with_rs = stamping(with_kc, root,
                           lambda cmd: "--attempts" in cmd,
                           "2026-09-08-new.md", "roguescholar: https://rs/x")
        with_rs.inner = inner
        assert deploy(**self.deploy_kwargs(root, with_rs)) is True
        commands = inner.commands()
        assert commands.count("jekyll build") == 3
        assert commands.count("rsync -avz") == 2
        poll_at = next(
            i for i, call in enumerate(inner.calls)
            if "--attempts" in call["cmd"])
        first_rsync = commands.index("rsync -avz")
        assert poll_at > first_rsync
        assert commands.index("rsync -avz", first_rsync + 1) > poll_at

    def test_wait_roguescholar_false_skips_the_tail(self, root):
        make_post(root, "2026-09-08-new.md")
        run = stamping(FakeRun({"git diff": 1}), root,
                       lambda cmd: cmd[0] == "./kcworks.sh",
                       "2026-09-08-new.md", "kcworks: https://works/x")
        kwargs = self.deploy_kwargs(root, run)
        kwargs["wait_roguescholar"] = False
        assert deploy(**kwargs) is True
        assert not any("--attempts" in call["cmd"]
                       for call in run.inner.calls)
        assert run.inner.commands().count("rsync -avz") == 1

    def test_roguescholar_wait_budget_is_at_most_ten_minutes(self):
        from evedeploy.pipeline import RS_WAIT_ATTEMPTS, RS_WAIT_INTERVAL
        assert (RS_WAIT_ATTEMPTS - 1) * RS_WAIT_INTERVAL <= 600

    def test_interrupting_the_wait_finishes_the_deploy_cleanly(self, root):
        # Ctrl+C during the Rogue Scholar wait must not crash or redeploy:
        # the site is already live, so the deploy ends normally and the
        # pre-build sweep picks the links up next time.
        make_post(root, "2026-09-08-new.md")
        inner = FakeRun({"git diff": 1})
        with_kc = stamping(inner, root,
                           lambda cmd: cmd[0] == "./kcworks.sh",
                           "2026-09-08-new.md", "kcworks: https://works/x")

        def run(cmd, cwd=None, check=True, capture=False):
            if "--attempts" in cmd:
                raise KeyboardInterrupt
            return with_kc(cmd, cwd=cwd, check=check, capture=capture)

        assert deploy(**self.deploy_kwargs(root, run)) is True
        commands = inner.commands()
        assert commands.count("rsync -avz") == 1
        assert commands.count("jekyll build") == 2

    def test_unharvested_roguescholar_gives_up_without_a_second_rsync(
            self, root):
        make_post(root, "2026-09-08-new.md")
        run = stamping(FakeRun({"git diff": 1}), root,
                       lambda cmd: cmd[0] == "./kcworks.sh",
                       "2026-09-08-new.md", "kcworks: https://works/x")
        assert deploy(**self.deploy_kwargs(root, run)) is True
        commands = run.inner.commands()
        assert commands.count("rsync -avz") == 1
        assert commands.count("jekyll build") == 2

    def test_webmention_failures_do_not_abort_the_deploy(self, root):
        # With cover resize disabled, the only "uv run" commands left are the
        # webmention fetch/send and the Last.fm fetch; all of them failing
        # must still deploy the site.
        run = FakeRun({"uv run": 1})
        kwargs = self.deploy_kwargs(root, run)
        kwargs["resize"] = False
        result = deploy(**kwargs)
        assert result is True
        assert "jekyll build" in run.commands()
        assert "rsync -avz" in run.commands()

    def test_step_failure_raises_deploy_error(self, root):
        run = FakeRun({"jekyll build": 1})
        with pytest.raises(DeployError, match="jekyll"):
            deploy(**self.deploy_kwargs(root, run))
