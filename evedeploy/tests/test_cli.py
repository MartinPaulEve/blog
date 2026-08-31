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

    def fake_deploy(root, message, resize=True, confirm=None, echo=None):
        seen.update(
            root=root, message=message, resize=resize, confirm=confirm
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
    def test_builds_without_deploying(self, blog_root, deploy_spy, build_spy):
        result = CliRunner().invoke(
            main, ["--root", str(blog_root), "--build-only"]
        )
        assert result.exit_code == 0
        assert Path(build_spy["root"]) == blog_root
        assert deploy_spy == {}

    def test_no_resize_is_respected(self, blog_root, deploy_spy, build_spy):
        CliRunner().invoke(
            main, ["--root", str(blog_root), "--build-only", "--no-resize"]
        )
        assert build_spy["resize"] is False

    def test_needs_no_confirmation_or_message(
        self, blog_root, deploy_spy, build_spy
    ):
        # No --yes and no stdin: a local build must never prompt.
        result = CliRunner().invoke(
            main, ["--root", str(blog_root), "--build-only"]
        )
        assert result.exit_code == 0
        assert deploy_spy == {}
