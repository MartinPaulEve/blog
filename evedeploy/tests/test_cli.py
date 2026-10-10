from pathlib import Path

import pytest
from click.testing import CliRunner

from evedeploy import cli
from evedeploy.cli import find_root, main


@pytest.fixture
def blog_root(tmp_path):
    (tmp_path / "_config.yml").write_text("title: test")
    return tmp_path


@pytest.fixture
def deploy_spy(monkeypatch):
    seen = {}

    def fake_deploy(root, message, resize=True, confirm=None, echo=None,
                    wait_roguescholar=True, sequoia=True, cache_sync=True,
                    cv=True):
        seen.update(
            root=root, message=message, resize=resize, confirm=confirm,
            wait_roguescholar=wait_roguescholar, sequoia=sequoia,
            cache_sync=cache_sync, cv=cv,
        )
        return True

    monkeypatch.setattr(cli, "deploy", fake_deploy)
    return seen


@pytest.fixture
def build_spy(monkeypatch):
    seen = {}

    def fake_build(root, resize=True, echo=None):
        seen.update(root=root, resize=resize)

    monkeypatch.setattr(cli, "build_site", fake_build, raising=False)
    return seen


@pytest.fixture
def serve_spy(monkeypatch):
    seen = {}

    def fake_serve(root, echo=None):
        seen.update(root=root)

    monkeypatch.setattr(cli, "serve_site", fake_serve, raising=False)
    return seen


class TestFindRoot:
    def test_finds_config_in_start_dir(self, blog_root):
        assert find_root(blog_root) == blog_root

    def test_walks_up_to_ancestor(self, blog_root):
        nested = blog_root / "a" / "b"
        nested.mkdir(parents=True)
        assert find_root(nested) == blog_root

    def test_no_config_anywhere_is_an_error(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            find_root(tmp_path / "nowhere")


class TestMain:
    def test_default_message_is_publish_plus_timestamp(
        self, blog_root, deploy_spy
    ):
        result = CliRunner().invoke(
            main, ["--root", str(blog_root), "--yes"]
        )
        assert result.exit_code == 0
        assert deploy_spy["message"].startswith("Publish 2")

    def test_explicit_message_is_passed_through(self, blog_root, deploy_spy):
        CliRunner().invoke(
            main, ["--root", str(blog_root), "--yes", "my words"]
        )
        assert deploy_spy["message"] == "my words"

    def test_no_resize_flag_disables_resize(self, blog_root, deploy_spy):
        CliRunner().invoke(
            main, ["--root", str(blog_root), "--yes", "--no-resize"]
        )
        assert deploy_spy["resize"] is False

    def test_rs_wait_is_on_by_default(self, blog_root, deploy_spy):
        CliRunner().invoke(
            main, ["--root", str(blog_root), "--yes", "msg"])
        assert deploy_spy["wait_roguescholar"] is True

    def test_no_rs_wait_flag_disables_the_wait(self, blog_root, deploy_spy):
        CliRunner().invoke(
            main, ["--root", str(blog_root), "--yes", "--no-rs-wait", "msg"])
        assert deploy_spy["wait_roguescholar"] is False

    def test_sequoia_is_on_by_default(self, blog_root, deploy_spy):
        CliRunner().invoke(
            main, ["--root", str(blog_root), "--yes", "msg"])
        assert deploy_spy["sequoia"] is True

    def test_no_sequoia_flag_disables_the_publish(self, blog_root, deploy_spy):
        CliRunner().invoke(
            main, ["--root", str(blog_root), "--yes", "--no-sequoia", "msg"])
        assert deploy_spy["sequoia"] is False

    def test_yes_flag_confirms_without_prompting(self, blog_root, deploy_spy):
        CliRunner().invoke(main, ["--root", str(blog_root), "--yes"])
        assert deploy_spy["confirm"]() is True

    def test_banner_is_shown(self, blog_root, deploy_spy):
        result = CliRunner().invoke(
            main, ["--root", str(blog_root), "--yes"]
        )
        # The banner goes to stderr; depending on the click version that is
        # captured separately or mixed into output.
        combined = result.output
        try:
            combined += result.stderr
        except (ValueError, AttributeError):
            pass
        assert "██" in combined

    def test_root_is_resolved_from_cwd_when_not_given(
        self, blog_root, deploy_spy, monkeypatch
    ):
        monkeypatch.chdir(blog_root)
        CliRunner().invoke(main, ["--yes"])
        assert Path(deploy_spy["root"]) == blog_root


class TestBuildOnly:
    def test_builds_without_deploying(
        self, blog_root, deploy_spy, build_spy, serve_spy
    ):
        result = CliRunner().invoke(
            main, ["--root", str(blog_root), "--build-only"]
        )
        assert result.exit_code == 0
        assert Path(build_spy["root"]) == blog_root
        assert deploy_spy == {}

    def test_no_resize_is_respected(
        self, blog_root, deploy_spy, build_spy, serve_spy
    ):
        CliRunner().invoke(
            main, ["--root", str(blog_root), "--build-only", "--no-resize"]
        )
        assert build_spy["resize"] is False

    def test_needs_no_confirmation_or_message(
        self, blog_root, deploy_spy, build_spy, serve_spy
    ):
        # No --yes and no stdin: a local build must never prompt.
        result = CliRunner().invoke(
            main, ["--root", str(blog_root), "--build-only"]
        )
        assert result.exit_code == 0
        assert deploy_spy == {}

    def test_serves_the_preview_by_default(
        self, blog_root, deploy_spy, build_spy, serve_spy
    ):
        result = CliRunner().invoke(
            main, ["--root", str(blog_root), "--build-only"]
        )
        assert result.exit_code == 0
        assert Path(serve_spy["root"]) == blog_root

    def test_no_server_skips_the_preview_server(
        self, blog_root, deploy_spy, build_spy, serve_spy
    ):
        result = CliRunner().invoke(
            main, ["--root", str(blog_root), "--build-only", "--no-server"]
        )
        assert result.exit_code == 0
        assert serve_spy == {}
        assert Path(build_spy["root"]) == blog_root

    def test_server_launches_after_a_successful_build(
        self, blog_root, deploy_spy, serve_spy, monkeypatch
    ):
        # A failed build must not leave a server running on a stale site.
        def failing_build(root, resize=True, echo=None):
            raise cli.DeployError("jekyll build failed")

        monkeypatch.setattr(cli, "build_site", failing_build, raising=False)
        result = CliRunner().invoke(
            main, ["--root", str(blog_root), "--build-only"]
        )
        assert result.exit_code != 0
        assert serve_spy == {}


@pytest.fixture
def remote_spy(monkeypatch):
    seen = {}

    def fake_remote(root, host, remote_dir, message, args, run=None,
                    echo=None, resize=True, quick=False, home=None):
        seen.update(root=root, host=host, remote_dir=remote_dir,
                    message=message, args=list(args), resize=resize,
                    quick=quick)
        return True

    monkeypatch.setattr(cli, "remote_deploy", fake_remote, raising=False)
    return seen


@pytest.fixture
def check_spy(monkeypatch):
    seen = {}

    def fake_check(root, host, remote_dir, run=None, echo=None):
        seen.update(root=root, host=host, remote_dir=remote_dir)
        return True

    monkeypatch.setattr(cli, "remote_check", fake_check, raising=False)
    return seen


class TestRemoteBuildHost:
    def test_host_in_env_routes_the_deploy_to_the_remote(
            self, blog_root, deploy_spy, remote_spy, monkeypatch):
        monkeypatch.setenv("REMOTE_BUILD_HOST", "waldorf")
        monkeypatch.delenv("REMOTE_BUILD_DIR", raising=False)
        result = CliRunner().invoke(
            main, ["--root", str(blog_root), "--no-sequoia", "Hello"])
        assert result.exit_code == 0, result.output
        assert remote_spy["host"] == "waldorf"
        assert remote_spy["remote_dir"] == "~/build/martineve/blog"
        assert remote_spy["message"] == "Hello"
        assert "--no-sequoia" in remote_spy["args"]
        assert remote_spy["quick"] is False
        assert "root" not in deploy_spy

    def test_remote_dir_can_be_set(self, blog_root, remote_spy, monkeypatch):
        monkeypatch.setenv("REMOTE_BUILD_HOST", "waldorf")
        monkeypatch.setenv("REMOTE_BUILD_DIR", "/srv/blog")
        CliRunner().invoke(main, ["--root", str(blog_root)])
        assert remote_spy["remote_dir"] == "/srv/blog"

    def test_local_flag_overrides_the_host(
            self, blog_root, deploy_spy, remote_spy, monkeypatch):
        monkeypatch.setenv("REMOTE_BUILD_HOST", "waldorf")
        result = CliRunner().invoke(
            main, ["--root", str(blog_root), "--local", "--yes"])
        assert result.exit_code == 0, result.output
        assert deploy_spy["root"] == blog_root
        assert "host" not in remote_spy

    def test_build_only_always_stays_local(
            self, blog_root, build_spy, remote_spy, monkeypatch):
        monkeypatch.setenv("REMOTE_BUILD_HOST", "waldorf")
        CliRunner().invoke(
            main, ["--root", str(blog_root), "--build-only", "--no-server"])
        assert build_spy["root"] == blog_root
        assert "host" not in remote_spy

    def test_quick_goes_remote_too(self, blog_root, remote_spy, monkeypatch):
        monkeypatch.setenv("REMOTE_BUILD_HOST", "waldorf")
        result = CliRunner().invoke(main, ["--root", str(blog_root), "--quick"])
        assert result.exit_code == 0, result.output
        assert remote_spy["quick"] is True
        assert "--quick" in remote_spy["args"]

    def test_no_resize_is_honoured_remotely(
            self, blog_root, remote_spy, monkeypatch):
        monkeypatch.setenv("REMOTE_BUILD_HOST", "waldorf")
        CliRunner().invoke(main, ["--root", str(blog_root), "--no-resize"])
        assert remote_spy["resize"] is False

    def test_yes_and_rs_wait_flags_are_forwarded(
            self, blog_root, remote_spy, monkeypatch):
        monkeypatch.setenv("REMOTE_BUILD_HOST", "waldorf")
        CliRunner().invoke(
            main, ["--root", str(blog_root), "--yes", "--no-rs-wait"])
        assert "--yes" in remote_spy["args"]
        assert "--no-rs-wait" in remote_spy["args"]

    def test_without_a_host_the_deploy_is_local(
            self, blog_root, deploy_spy, remote_spy, monkeypatch):
        monkeypatch.delenv("REMOTE_BUILD_HOST", raising=False)
        CliRunner().invoke(main, ["--root", str(blog_root), "--yes"])
        assert deploy_spy["root"] == blog_root
        assert "host" not in remote_spy

    def test_remote_check_runs_the_doctor_and_nothing_else(
            self, blog_root, deploy_spy, remote_spy, check_spy, monkeypatch):
        monkeypatch.setenv("REMOTE_BUILD_HOST", "waldorf")
        result = CliRunner().invoke(
            main, ["--root", str(blog_root), "--remote-check"])
        assert result.exit_code == 0, result.output
        assert check_spy["host"] == "waldorf"
        assert "root" not in deploy_spy and "host" not in remote_spy

    def test_remote_check_without_a_host_is_an_error(
            self, blog_root, check_spy, monkeypatch):
        monkeypatch.delenv("REMOTE_BUILD_HOST", raising=False)
        result = CliRunner().invoke(
            main, ["--root", str(blog_root), "--remote-check"])
        assert result.exit_code != 0
        assert "REMOTE_BUILD_HOST" in result.output


class TestCacheAndCvFlags:
    def test_cache_sync_is_on_by_default(self, blog_root, deploy_spy):
        CliRunner().invoke(main, ["--root", str(blog_root), "--yes"])
        assert deploy_spy["cache_sync"] is True
        assert deploy_spy["cv"] is True

    def test_no_cache_sync_flag(self, blog_root, deploy_spy):
        CliRunner().invoke(
            main, ["--root", str(blog_root), "--yes", "--no-cache-sync"])
        assert deploy_spy["cache_sync"] is False

    def test_no_cv_flag(self, blog_root, deploy_spy):
        CliRunner().invoke(main, ["--root", str(blog_root), "--yes", "--no-cv"])
        assert deploy_spy["cv"] is False


@pytest.fixture
def banner_spy(monkeypatch):
    seen = {}

    def fake_banner(stream=None, color=None, words=None):
        seen["words"] = words

    monkeypatch.setattr(cli, "print_banner", fake_banner)
    return seen


class TestRemotePhase:
    def test_remote_phase_runs_here_with_the_host_side_flags(
            self, blog_root, deploy_spy, remote_spy, monkeypatch):
        monkeypatch.setenv("REMOTE_BUILD_HOST", "waldorf")
        result = CliRunner().invoke(
            main, ["--root", str(blog_root), "--remote-phase", "--yes"])
        assert result.exit_code == 0, result.output
        assert deploy_spy["root"] == blog_root
        assert deploy_spy["resize"] is False
        assert deploy_spy["cv"] is False
        assert "host" not in remote_spy

    def test_remote_phase_shows_the_remote_build_server_wordmark(
            self, blog_root, deploy_spy, banner_spy):
        CliRunner().invoke(
            main, ["--root", str(blog_root), "--remote-phase", "--yes"])
        assert banner_spy["words"] == ("REMOTE", "BUILD", "SERVER")

    def test_ordinary_runs_keep_the_eve_gd_wordmark(
            self, blog_root, deploy_spy, banner_spy):
        CliRunner().invoke(main, ["--root", str(blog_root), "--yes"])
        assert banner_spy["words"] in (None, ("EVE.GD",))

    def test_remote_phase_quick_commits_the_ledger(
            self, blog_root, banner_spy, monkeypatch):
        seen = {}

        def fake_quick(root, echo=None, cache_sync=True, commit_ledger=False):
            seen.update(commit_ledger=commit_ledger)
            return True

        monkeypatch.setattr(cli, "quick_deploy", fake_quick)
        CliRunner().invoke(
            main, ["--root", str(blog_root), "--remote-phase", "--quick"])
        assert seen["commit_ledger"] is True
