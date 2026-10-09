"""Behavioural tests for the container launcher (evedeploy.container).

The launcher's job is to turn host facts (paths, sockets, uid, tty) into
one `docker run ...` argv. The tests parse that argv back into mounts and
environment rather than asserting on flag order, so the implementation can
move flags around freely as long as the container sees the same world.
"""

from pathlib import Path

import pytest

from evedeploy import container
from evedeploy.container import (
    LauncherError,
    agent_sockets,
    detect_runtime,
    ensure_image,
    env_value,
    git_config_files,
    host_entry,
    hosts_file_for,
    host_timezone,
    image_tag,
    native_command,
    run_command,
    split_args,
    ssh_mounts,
)


# --- argv parsing helpers (test-side, implementation-agnostic) -----------

def mounts_of(cmd):
    """{source: (destination, options)} for every -v/--volume flag."""
    out = {}
    for i, tok in enumerate(cmd):
        if tok in ("-v", "--volume"):
            parts = cmd[i + 1].split(":")
            src, dst = parts[0], parts[1]
            opts = parts[2] if len(parts) > 2 else ""
            out[src] = (dst, opts)
    return out


def all_mounts_of(cmd):
    """[(source, destination)] for every -v/--volume flag, duplicates kept."""
    out = []
    for i, tok in enumerate(cmd):
        if tok in ("-v", "--volume"):
            parts = cmd[i + 1].split(":")
            out.append((parts[0], parts[1]))
    return out


def env_of(cmd):
    """{NAME: value} for every -e/--env flag."""
    out = {}
    for i, tok in enumerate(cmd):
        if tok in ("-e", "--env"):
            name, _, value = cmd[i + 1].partition("=")
            out[name] = value
    return out


def image_index(cmd, image):
    return cmd.index(image)


# --- fixtures -----------------------------------------------------------

ROOT = Path("/home/someone/blog")
HOME = Path("/home/someone")
IMAGE = "evedeploy:abc123"


def exists_in(*present):
    present = {str(p) for p in present}
    return lambda path: str(path) in present


@pytest.fixture
def base_kwargs():
    return dict(runtime="docker", image=IMAGE, root=ROOT, home=HOME,
                uid=1000, gid=100, args=["--quick"], tty=True, env={})


# --- image tag ----------------------------------------------------------

class TestImageTag:
    def test_same_inputs_give_same_tag(self, tmp_path):
        a = tmp_path / "Dockerfile"
        a.write_text("FROM debian")
        assert image_tag([a]) == image_tag([a])

    def test_tag_names_the_evedeploy_image(self, tmp_path):
        a = tmp_path / "Dockerfile"
        a.write_text("FROM debian")
        assert image_tag([a]).startswith("evedeploy:")

    def test_changing_an_input_changes_the_tag(self, tmp_path):
        a = tmp_path / "Dockerfile"
        a.write_text("FROM debian")
        before = image_tag([a])
        a.write_text("FROM debian\nRUN true")
        assert image_tag([a]) != before

    def test_every_input_participates(self, tmp_path):
        a = tmp_path / "Dockerfile"
        b = tmp_path / "Gemfile.lock"
        a.write_text("FROM debian")
        b.write_text("jekyll (4.4.1)")
        before = image_tag([a, b])
        b.write_text("jekyll (4.4.2)")
        assert image_tag([a, b]) != before


# --- runtime detection --------------------------------------------------

class TestDetectRuntime:
    def test_prefers_docker_when_both_present(self):
        which = lambda name: f"/usr/bin/{name}"
        assert detect_runtime(which=which, env={}) == "docker"

    def test_falls_back_to_podman(self):
        which = lambda name: f"/usr/bin/{name}" if name == "podman" else None
        assert detect_runtime(which=which, env={}) == "podman"

    def test_env_override_wins(self):
        which = lambda name: f"/usr/bin/{name}"
        env = {"EVEDEPLOY_RUNTIME": "podman"}
        assert detect_runtime(which=which, env=env) == "podman"

    def test_no_runtime_is_a_launcher_error(self):
        with pytest.raises(LauncherError):
            detect_runtime(which=lambda name: None, env={})


# --- ssh agent sockets --------------------------------------------------

class TestAgentSockets:
    def test_only_existing_sockets_are_returned(self):
        bw = HOME / ".bitwarden-ssh-agent.sock"
        found = agent_sockets(HOME, env={}, exists=exists_in(bw))
        assert found == [bw]

    def test_known_agents_are_found_without_env(self):
        bw = HOME / ".bitwarden-ssh-agent.sock"
        op = HOME / ".1password/agent.sock"
        found = agent_sockets(HOME, env={}, exists=exists_in(bw, op))
        assert set(found) == {bw, op}

    def test_explicit_override_comes_first(self):
        bw = HOME / ".bitwarden-ssh-agent.sock"
        mine = Path("/run/user/1000/my-agent.sock")
        env = {"EVEDEPLOY_SSH_AGENT": str(mine)}
        found = agent_sockets(HOME, env=env, exists=exists_in(bw, mine))
        assert found[0] == mine
        assert bw in found

    def test_ssh_auth_sock_is_included_last(self):
        bw = HOME / ".bitwarden-ssh-agent.sock"
        generic = Path("/run/user/1000/gnupg/S.gpg-agent.ssh")
        env = {"SSH_AUTH_SOCK": str(generic)}
        found = agent_sockets(HOME, env=env, exists=exists_in(bw, generic))
        assert found == [bw, generic]

    def test_inside_an_ssh_session_the_forwarded_agent_wins(self):
        # Remote session: nobody can approve the desktop agents' prompts,
        # so the agent forwarded from the operator's own machine comes first.
        bw = HOME / ".bitwarden-ssh-agent.sock"
        forwarded = Path("/tmp/ssh-XXXXab12/agent.4242")
        env = {"SSH_AUTH_SOCK": str(forwarded),
               "SSH_CONNECTION": "10.0.0.2 51234 10.0.0.9 22"}
        found = agent_sockets(HOME, env=env, exists=exists_in(bw, forwarded))
        assert found == [forwarded, bw]

    def test_explicit_override_beats_the_forwarded_agent(self):
        forwarded = Path("/tmp/ssh-XXXXab12/agent.4242")
        mine = Path("/run/user/1000/my-agent.sock")
        env = {"SSH_AUTH_SOCK": str(forwarded), "SSH_CONNECTION": "x",
               "EVEDEPLOY_SSH_AGENT": str(mine)}
        found = agent_sockets(HOME, env=env, exists=exists_in(forwarded, mine))
        assert found[0] == mine

    def test_duplicates_collapse(self):
        bw = HOME / ".bitwarden-ssh-agent.sock"
        env = {"SSH_AUTH_SOCK": str(bw), "EVEDEPLOY_SSH_AGENT": str(bw)}
        found = agent_sockets(HOME, env=env, exists=exists_in(bw))
        assert found == [bw]

    def test_nothing_present_gives_empty_list(self):
        assert agent_sockets(HOME, env={}, exists=lambda p: False) == []


# --- ~/.ssh entries, symlinks resolved -----------------------------------

class TestSshMounts:
    def test_plain_files_map_to_themselves(self):
        known = HOME / ".ssh/known_hosts"
        pairs = ssh_mounts(HOME, entries=lambda d: [known],
                           realpath=lambda p: p, exists=lambda p: True)
        assert pairs == [(known, known)]

    def test_symlinks_are_mounted_from_their_target(self):
        link = HOME / ".ssh/config"
        target = Path("/nix/store/abc-home-manager-files/.ssh/config")
        pairs = ssh_mounts(HOME, entries=lambda d: [link],
                           realpath=lambda p: target if p == link else p,
                           exists=lambda p: True)
        assert pairs == [(target, link)]

    def test_dangling_entries_are_skipped(self):
        link = HOME / ".ssh/config"
        target = Path("/nix/store/gone/.ssh/config")
        pairs = ssh_mounts(HOME, entries=lambda d: [link],
                           realpath=lambda p: target if p == link else p,
                           exists=lambda p: p != target)
        assert pairs == []

    def test_sockets_and_control_masters_are_skipped(self):
        sock = HOME / ".ssh/control-abc.sock"
        pairs = ssh_mounts(HOME, entries=lambda d: [sock],
                           realpath=lambda p: p, exists=lambda p: True,
                           is_socket=lambda p: True)
        assert pairs == []

    def test_no_ssh_directory_gives_nothing(self):
        assert ssh_mounts(HOME, entries=lambda d: [], realpath=lambda p: p,
                          exists=lambda p: True) == []


# --- git config discovery -----------------------------------------------

class TestGitConfigFiles:
    def test_classic_gitconfig_is_found(self):
        classic = HOME / ".gitconfig"
        assert git_config_files(HOME, env={}, exists=exists_in(classic)) == [classic]

    def test_xdg_config_is_found(self):
        xdg = HOME / ".config/git/config"
        assert git_config_files(HOME, env={}, exists=exists_in(xdg)) == [xdg]

    def test_xdg_config_home_is_honoured(self):
        custom = Path("/etc/xdg-home/git/config")
        env = {"XDG_CONFIG_HOME": "/etc/xdg-home"}
        assert git_config_files(HOME, env=env, exists=exists_in(custom)) == [custom]

    def test_missing_files_are_skipped(self):
        assert git_config_files(HOME, env={}, exists=lambda p: False) == []


# --- timezone -----------------------------------------------------------

class TestHostTimezone:
    def test_tz_variable_wins(self):
        env = {"TZ": "Europe/Paris"}
        assert host_timezone(env=env, localtime=lambda: None) == "Europe/Paris"

    def test_zone_is_read_from_the_localtime_link(self):
        target = "/nix/store/abc-tzdata-2026c/share/zoneinfo/Europe/London"
        assert host_timezone(env={}, localtime=lambda: target) == "Europe/London"

    def test_classic_zoneinfo_path_is_handled(self):
        target = "/usr/share/zoneinfo/America/New_York"
        assert host_timezone(env={}, localtime=lambda: target) == "America/New_York"

    def test_unknown_layout_gives_none(self):
        assert host_timezone(env={}, localtime=lambda: "/etc/localtime") is None

    def test_missing_localtime_gives_none(self):
        assert host_timezone(env={}, localtime=lambda: None) is None


# --- argument splitting -------------------------------------------------

class TestSplitArgs:
    def test_plain_args_pass_through_untouched(self):
        opts = split_args(["--quick"])
        assert opts.passthrough == ["--quick"]
        assert opts.native is False
        assert opts.shell is False

    def test_native_flag_is_consumed(self):
        opts = split_args(["--native", "--build-only", "--no-server"])
        assert opts.native is True
        assert opts.passthrough == ["--build-only", "--no-server"]

    def test_shell_flag_is_consumed(self):
        opts = split_args(["--shell"])
        assert opts.shell is True
        assert opts.passthrough == []

    def test_rebuild_image_flag_is_consumed(self):
        opts = split_args(["--rebuild-image", "--quick"])
        assert opts.rebuild_image is True
        assert opts.passthrough == ["--quick"]

    def test_commit_message_survives_with_spaces(self):
        opts = split_args(["--no-resize", "fix the about page"])
        assert opts.passthrough == ["--no-resize", "fix the about page"]


# --- the native (host) command -----------------------------------------

class TestNativeCommand:
    def test_runs_evedeploy_via_uv_with_the_env_file(self):
        cmd = native_command(["--quick"])
        assert cmd == ["uv", "run", "--env-file", ".env", "--project",
                       "evedeploy", "evedeploy", "--quick"]

    def test_no_args_still_runs_evedeploy(self):
        assert native_command([])[-1] == "evedeploy"


# --- the container command ---------------------------------------------

class TestRunCommand:
    def test_uses_the_detected_runtime(self, base_kwargs):
        cmd = run_command(**base_kwargs)
        assert cmd[:2] == ["docker", "run"]

    def test_container_is_removed_afterwards(self, base_kwargs):
        assert "--rm" in run_command(**base_kwargs)

    def test_tty_is_allocated_when_the_host_has_one(self, base_kwargs):
        cmd = run_command(**base_kwargs)
        assert "-t" in cmd or "--tty" in cmd

    def test_no_tty_when_the_host_has_none(self, base_kwargs):
        base_kwargs["tty"] = False
        cmd = run_command(**base_kwargs)
        assert "-t" not in cmd and "--tty" not in cmd

    def test_stdin_is_always_connected_for_the_confirm_gate(self, base_kwargs):
        cmd = run_command(**base_kwargs)
        assert "-i" in cmd or "--interactive" in cmd

    def test_repo_is_mounted_read_write_at_its_host_path(self, base_kwargs):
        mounts = mounts_of(run_command(**base_kwargs))
        dst, opts = mounts[str(ROOT)]
        assert dst == str(ROOT)
        assert "ro" not in opts.split(",")

    def test_working_directory_is_the_repo(self, base_kwargs):
        cmd = run_command(**base_kwargs)
        i = cmd.index("-w") if "-w" in cmd else cmd.index("--workdir")
        assert cmd[i + 1] == str(ROOT)

    def test_evedeploy_runs_after_the_image_with_the_passthrough_args(
            self, base_kwargs):
        cmd = run_command(**base_kwargs)
        tail = cmd[image_index(cmd, IMAGE) + 1:]
        assert tail == native_command(["--quick"])

    def test_shell_mode_opens_bash_instead(self, base_kwargs):
        cmd = run_command(**base_kwargs, shell=True)
        assert cmd[image_index(cmd, IMAGE) + 1:] == ["bash"]

    def test_chosen_agent_is_mounted_at_its_host_path(self, base_kwargs):
        forwarded = Path("/tmp/ssh-XXXXab12/agent.4242")
        mounts = all_mounts_of(run_command(**base_kwargs, agent=forwarded))
        assert (str(forwarded), str(forwarded)) in mounts

    def test_chosen_agent_also_answers_at_the_desktop_agents_paths(
            self, base_kwargs):
        # ~/.ssh/config pins IdentityAgent to a desktop agent's socket; the
        # chosen agent has to be what those lines reach inside the container.
        forwarded = Path("/tmp/ssh-XXXXab12/agent.4242")
        mounts = all_mounts_of(run_command(**base_kwargs, agent=forwarded))
        assert (str(forwarded), str(HOME / ".bitwarden-ssh-agent.sock")) in mounts
        assert (str(forwarded), str(HOME / ".1password/agent.sock")) in mounts

    def test_only_the_chosen_agent_is_mounted(self, base_kwargs):
        bw = HOME / ".bitwarden-ssh-agent.sock"
        mounts = all_mounts_of(run_command(**base_kwargs, agent=bw))
        sources = {src for src, _ in mounts if src.endswith(".sock") or "/agent." in src}
        assert sources == {str(bw)}

    def test_chosen_agent_becomes_ssh_auth_sock(self, base_kwargs):
        bw = HOME / ".bitwarden-ssh-agent.sock"
        env = env_of(run_command(**base_kwargs, agent=bw))
        assert env["SSH_AUTH_SOCK"] == str(bw)

    def test_no_agent_means_no_ssh_auth_sock_and_no_agent_mounts(
            self, base_kwargs):
        cmd = run_command(**base_kwargs, agent=None)
        assert "SSH_AUTH_SOCK" not in env_of(cmd)
        assert not any("agent" in src for src, _ in all_mounts_of(cmd))

    def test_identity_files_are_mounted_read_only_at_their_host_paths(
            self, base_kwargs):
        # (resolved source, host path): a home-manager symlink in ~/.ssh
        # points into /nix/store, which does not exist in the container.
        src = Path("/nix/store/abc-home-manager-files/.ssh/config")
        dst = HOME / ".ssh/config"
        mounts = mounts_of(run_command(**base_kwargs,
                                       identity_files=[(src, dst)]))
        mounted_dst, opts = mounts[str(src)]
        assert mounted_dst == str(dst)
        assert "ro" in opts.split(",")

    def test_the_ssh_directory_itself_is_not_mounted(self, base_kwargs):
        # Mounting the directory would carry the dangling symlinks across.
        src = Path("/nix/store/abc/.ssh/config")
        mounts = mounts_of(run_command(**base_kwargs,
                                       identity_files=[(src, HOME / ".ssh/config")]))
        assert str(HOME / ".ssh") not in mounts

    def test_state_dirs_are_mounted_read_write_at_their_host_paths(
            self, base_kwargs):
        creds = HOME / ".config/sequoia"
        mounts = mounts_of(run_command(**base_kwargs, state_dirs=[creds]))
        dst, opts = mounts[str(creds)]
        assert dst == str(creds)
        assert "ro" not in opts.split(",")

    def test_commit_signing_uses_plain_ssh_keygen_inside(self, base_kwargs):
        env = env_of(run_command(**base_kwargs))
        pairs = {}
        n = int(env.get("GIT_CONFIG_COUNT", "0"))
        for i in range(n):
            pairs[env[f"GIT_CONFIG_KEY_{i}"]] = env[f"GIT_CONFIG_VALUE_{i}"]
        assert pairs.get("gpg.ssh.program") == "ssh-keygen"

    def test_hosts_file_is_shared_read_only(self, base_kwargs):
        mounts = mounts_of(run_command(**base_kwargs))
        assert mounts["/etc/hosts"] == ("/etc/hosts", "ro")

    def test_extra_mounts_are_read_only_at_their_host_paths(self, base_kwargs):
        cv = Path("/home/someone/eprintsToCV/output")
        mounts = mounts_of(run_command(**base_kwargs, extra_mounts=[cv]))
        dst, opts = mounts[str(cv)]
        assert dst == str(cv)
        assert "ro" in opts.split(",")

    def test_uv_cache_persists_in_a_named_volume(self, base_kwargs):
        cmd = run_command(**base_kwargs)
        env = env_of(cmd)
        cache_dir = env["UV_CACHE_DIR"]
        volumes = {dst: src for src, (dst, _) in mounts_of(cmd).items()}
        assert cache_dir in volumes
        assert not volumes[cache_dir].startswith("/")  # a named volume

    def test_identity_is_passed_for_the_entrypoint(self, base_kwargs):
        env = env_of(run_command(**base_kwargs))
        assert env["EVEDEPLOY_UID"] == "1000"
        assert env["EVEDEPLOY_GID"] == "100"
        assert env["HOME"] == str(HOME)

    def test_uses_the_host_network(self, base_kwargs):
        cmd = run_command(**base_kwargs)
        assert "--network" in cmd and cmd[cmd.index("--network") + 1] == "host"

    def test_terminal_variables_pass_through_when_set(self, base_kwargs):
        base_kwargs["env"] = {"TERM": "xterm-256color", "COLORTERM": "truecolor"}
        env = env_of(run_command(**base_kwargs))
        assert env["TERM"] == "xterm-256color"
        assert env["COLORTERM"] == "truecolor"

    def test_build_switches_pass_through_when_set(self, base_kwargs):
        base_kwargs["env"] = {"JEKYLL_SKIP_PDFS": "1"}
        assert env_of(run_command(**base_kwargs))["JEKYLL_SKIP_PDFS"] == "1"

    def test_unset_switches_are_not_invented(self, base_kwargs):
        env = env_of(run_command(**base_kwargs))
        assert "JEKYLL_SKIP_PDFS" not in env
        assert "TERM" not in env

    def test_unrelated_host_variables_do_not_leak(self, base_kwargs):
        base_kwargs["env"] = {"AWS_SECRET_ACCESS_KEY": "nope"}
        assert "AWS_SECRET_ACCESS_KEY" not in env_of(run_command(**base_kwargs))

    def test_timezone_is_forwarded_so_post_dates_do_not_shift(self, base_kwargs):
        env = env_of(run_command(**base_kwargs, timezone="Europe/London"))
        assert env["TZ"] == "Europe/London"

    def test_no_known_timezone_sets_none(self, base_kwargs):
        assert "TZ" not in env_of(run_command(**base_kwargs, timezone=None))

    def test_podman_keeps_the_host_uid(self, base_kwargs):
        base_kwargs["runtime"] = "podman"
        cmd = run_command(**base_kwargs)
        assert cmd[:2] == ["podman", "run"]
        assert "--userns=keep-id" in cmd

    def test_docker_does_not_use_podman_user_namespaces(self, base_kwargs):
        assert "--userns=keep-id" not in run_command(**base_kwargs)


# --- image build --------------------------------------------------------

class FakeRuntime:
    """Records every runtime invocation; `present` says if the image exists."""

    def __init__(self, present):
        self.present = present
        self.calls = []

    def __call__(self, cmd, **kwargs):
        self.calls.append(list(cmd))

        class Result:
            pass

        result = Result()
        if "inspect" in cmd:
            result.returncode = 0 if self.present else 1
        else:
            result.returncode = 0
            self.present = True
        return result

    def builds(self):
        return [c for c in self.calls if "build" in c]


class TestEnsureImage:
    def test_existing_image_is_not_rebuilt(self):
        rt = FakeRuntime(present=True)
        ensure_image("docker", IMAGE, ROOT, run=rt, echo=lambda *a: None)
        assert rt.builds() == []

    def test_missing_image_is_built_with_the_tag(self):
        rt = FakeRuntime(present=False)
        ensure_image("docker", IMAGE, ROOT, run=rt, echo=lambda *a: None)
        (build,) = rt.builds()
        assert build[0] == "docker"
        assert IMAGE in build

    def test_build_context_is_the_repo(self):
        rt = FakeRuntime(present=False)
        ensure_image("docker", IMAGE, ROOT, run=rt, echo=lambda *a: None)
        (build,) = rt.builds()
        assert build[-1] == str(ROOT)

    def test_rebuild_forces_a_build_even_when_present(self):
        rt = FakeRuntime(present=True)
        ensure_image("docker", IMAGE, ROOT, run=rt, rebuild=True,
                     echo=lambda *a: None)
        assert len(rt.builds()) == 1

    def test_failed_build_is_a_launcher_error(self):
        class Failing(FakeRuntime):
            def __call__(self, cmd, **kwargs):
                result = super().__call__(cmd, **kwargs)
                if "build" in cmd:
                    result.returncode = 1
                return result

        with pytest.raises(LauncherError):
            ensure_image("docker", IMAGE, ROOT, run=Failing(present=False),
                         echo=lambda *a: None)


# --- main ---------------------------------------------------------------

class TestMain:
    def test_native_mode_execs_uv_on_the_host(self, monkeypatch, tmp_path):
        seen = {}

        def fake_exec(prog, argv):
            seen["prog"], seen["argv"] = prog, argv

        monkeypatch.setattr(container, "repo_root", lambda: tmp_path)
        container.main(["--native", "--quick"], exec_=fake_exec)
        assert seen["prog"] == "uv"
        assert seen["argv"] == native_command(["--quick"])

    def test_container_mode_execs_the_runtime(self, monkeypatch, tmp_path):
        seen = {}

        def fake_exec(prog, argv):
            seen["prog"], seen["argv"] = prog, argv

        (tmp_path / "evedeploy" / "container").mkdir(parents=True)
        (tmp_path / "evedeploy" / "container" / "Dockerfile").write_text("FROM x")
        (tmp_path / "evedeploy" / "container" / "entrypoint.sh").write_text("#!/bin/sh")
        (tmp_path / "Gemfile").write_text("")
        (tmp_path / "Gemfile.lock").write_text("")
        monkeypatch.setattr(container, "repo_root", lambda: tmp_path)
        monkeypatch.setattr(container, "detect_runtime",
                            lambda **kw: "docker")
        monkeypatch.setattr(container, "ensure_image",
                            lambda *a, **kw: None)
        container.main(["--quick"], exec_=fake_exec)
        assert seen["prog"] == "docker"
        assert seen["argv"][:2] == ["docker", "run"]
        assert seen["argv"][-1] == "--quick"

    def test_missing_runtime_reports_and_fails(self, monkeypatch, tmp_path,
                                               capsys):
        monkeypatch.setattr(container, "repo_root", lambda: tmp_path)

        def no_runtime(**kw):
            raise LauncherError("no container runtime found")

        monkeypatch.setattr(container, "detect_runtime", no_runtime)
        code = container.main(["--quick"], exec_=lambda *a: None)
        assert code != 0
        assert "runtime" in capsys.readouterr().err


# --- the remote build host's name inside the container -------------------


class TestEnvValue:
    def test_reads_a_plain_assignment(self, tmp_path):
        env = tmp_path / ".env"
        env.write_text("FOO=1\nREMOTE_BUILD_HOST=waldorf\n")
        assert env_value(env, "REMOTE_BUILD_HOST") == "waldorf"

    def test_strips_quotes_and_whitespace(self, tmp_path):
        env = tmp_path / ".env"
        env.write_text('REMOTE_BUILD_HOST = "waldorf" \n')
        assert env_value(env, "REMOTE_BUILD_HOST") == "waldorf"

    def test_ignores_comments_and_commented_out_lines(self, tmp_path):
        env = tmp_path / ".env"
        env.write_text("# REMOTE_BUILD_HOST=old\nREMOTE_BUILD_HOST=waldorf # live\n")
        assert env_value(env, "REMOTE_BUILD_HOST") == "waldorf"

    def test_missing_key_or_file_gives_none(self, tmp_path):
        env = tmp_path / ".env"
        env.write_text("FOO=1\n")
        assert env_value(env, "REMOTE_BUILD_HOST") is None
        assert env_value(tmp_path / "absent", "REMOTE_BUILD_HOST") is None

    def test_empty_value_gives_none(self, tmp_path):
        env = tmp_path / ".env"
        env.write_text("REMOTE_BUILD_HOST=\n")
        assert env_value(env, "REMOTE_BUILD_HOST") is None


class TestHostEntry:
    RESOLVES = {"waldorf": "100.64.128.23",
                "waldorf.example.net": "100.64.128.23"}

    def resolve(self, name):
        if name not in self.RESOLVES:
            raise OSError("no such host")
        return self.RESOLVES[name]

    def test_resolves_the_name_ssh_will_actually_use(self):
        # `Host waldorf` may map to another HostName; that is what the
        # ssh inside the container looks up.
        entry = host_entry("waldorf", ssh_hostname=lambda n: "waldorf.example.net",
                           resolve=self.resolve, hosts_text="")
        assert entry == "100.64.128.23 waldorf.example.net"

    def test_plain_name_maps_to_itself(self):
        entry = host_entry("waldorf", ssh_hostname=lambda n: n,
                           resolve=self.resolve, hosts_text="")
        assert entry == "100.64.128.23 waldorf"

    def test_no_host_configured_gives_none(self):
        assert host_entry(None, ssh_hostname=lambda n: n,
                          resolve=self.resolve, hosts_text="") is None

    def test_ip_literals_need_no_entry(self):
        assert host_entry("100.64.128.23", ssh_hostname=lambda n: n,
                          resolve=self.resolve, hosts_text="") is None
        assert host_entry("waldorf", ssh_hostname=lambda n: "100.64.128.23",
                          resolve=self.resolve, hosts_text="") is None

    def test_names_already_in_etc_hosts_need_no_entry(self):
        hosts = "127.0.0.1 localhost\n100.64.128.23 waldorf waldorf.lan\n"
        assert host_entry("waldorf", ssh_hostname=lambda n: n,
                          resolve=self.resolve, hosts_text=hosts) is None

    def test_a_commented_hosts_line_does_not_count(self):
        hosts = "#100.64.128.23 waldorf\n"
        entry = host_entry("waldorf", ssh_hostname=lambda n: n,
                           resolve=self.resolve, hosts_text=hosts)
        assert entry == "100.64.128.23 waldorf"

    def test_unresolvable_name_gives_none(self):
        assert host_entry("nowhere", ssh_hostname=lambda n: n,
                          resolve=self.resolve, hosts_text="") is None

    def test_ssh_hostname_failure_falls_back_to_the_name(self):
        def broken(name):
            raise OSError("no ssh")
        entry = host_entry("waldorf", ssh_hostname=broken,
                           resolve=self.resolve, hosts_text="")
        assert entry == "100.64.128.23 waldorf"


class TestHostsFileFor:
    def test_without_an_entry_the_system_hosts_file_is_used(self, tmp_path):
        path = hosts_file_for(tmp_path / "home", entry=None,
                              system_hosts=tmp_path / "hosts")
        assert path == tmp_path / "hosts"

    def test_with_an_entry_an_augmented_copy_is_written_under_home(
            self, tmp_path):
        system = tmp_path / "hosts"
        system.write_text("127.0.0.1 localhost\n")
        home = tmp_path / "home"
        path = hosts_file_for(home, entry="100.64.128.23 waldorf",
                              system_hosts=system)
        assert path != system
        assert str(path).startswith(str(home))
        text = path.read_text()
        assert "127.0.0.1 localhost" in text
        assert text.rstrip().endswith("100.64.128.23 waldorf")

    def test_the_copy_is_rewritten_each_time(self, tmp_path):
        system = tmp_path / "hosts"
        system.write_text("127.0.0.1 localhost\n")
        home = tmp_path / "home"
        hosts_file_for(home, entry="10.0.0.1 waldorf", system_hosts=system)
        path = hosts_file_for(home, entry="10.0.0.2 waldorf", system_hosts=system)
        assert "10.0.0.1" not in path.read_text()
        assert "10.0.0.2 waldorf" in path.read_text()


class TestRunCommandHosts:
    def test_a_given_hosts_file_is_mounted_as_etc_hosts(self, base_kwargs):
        mounts = mounts_of(run_command(**base_kwargs,
                                       hosts="/home/someone/.cache/evedeploy/hosts"))
        assert mounts["/home/someone/.cache/evedeploy/hosts"] == ("/etc/hosts", "ro")
        assert "/etc/hosts" not in mounts

    def test_default_is_the_system_hosts_file(self, base_kwargs):
        mounts = mounts_of(run_command(**base_kwargs))
        assert mounts["/etc/hosts"] == ("/etc/hosts", "ro")
