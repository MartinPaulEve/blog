import subprocess

import pytest

from evedeploy.pipeline import (
    DeployError,
    check_preflight,
    deploy,
    git_commit_push,
    jekyll_build,
    refresh_cv,
    resize_covers,
    rsync_site,
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
    return blog


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


class TestBuildAndRsync:
    def test_jekyll_build_runs_plain_jekyll_at_root(self, root):
        run = FakeRun()
        jekyll_build(root, run=run)
        assert run.calls[0]["cmd"] == ["jekyll", "build"]
        assert run.calls[0]["cwd"] == root

    def test_rsync_pushes_site_dir_to_server(self, root):
        run = FakeRun()
        rsync_site(root, run=run)
        assert run.calls[0]["cmd"] == [
            "rsync",
            "-avz",
            f"{root}/_site/",
            "evegd@reclaim:/home/evegd/blog/_site/",
        ]


class TestDeploy:
    def deploy_kwargs(self, root, run, confirm=lambda: True):
        return dict(
            root=root,
            message="msg",
            confirm=confirm,
            run=run,
            echo=lambda *a, **k: None,
            which=lambda name: f"/bin/{name}" if name == "sequoia" else None,
        )

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

    def test_full_deploy_runs_steps_in_script_order(self, root):
        run = FakeRun({"git diff": 1})
        result = deploy(**self.deploy_kwargs(root, run))
        assert result is True
        commands = run.commands()
        # Faithful to newdeploy.sh: resize, dry run, publish, build, git,
        # rsync — in that order.
        expected_order = [
            "uv run",
            "sequoia publish",  # dry run
            "sequoia publish",  # real publish
            "jekyll build",
            "git add",
            "git diff",
            "git commit",
            "git push",
            "rsync -avz",
        ]
        positions = []
        cursor = 0
        for expected in expected_order:
            cursor = commands.index(expected, cursor)
            positions.append(cursor)
            cursor += 1
        assert positions == sorted(positions)

    def test_step_failure_raises_deploy_error(self, root):
        run = FakeRun({"jekyll build": 1})
        with pytest.raises(DeployError, match="jekyll"):
            deploy(**self.deploy_kwargs(root, run))
