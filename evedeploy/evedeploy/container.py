"""Launch evedeploy inside its container image (stdlib only).

deploy.sh runs this file directly with the host's python3 — no uv, no
venv — so the only host requirements are a container runtime (Docker or
Podman), an SSH agent holding the deploy/signing keys, and python3.
Everything the pipeline shells out to (jekyll and its gems, headless
Chromium for the PDF editions and OG cards, exiftool, ImageMagick, uv,
node + sequoia, rsync, git) lives in the image built from
evedeploy/container/Dockerfile.

The container sees the host's world at the host's own paths: the repo is
bind-mounted read-write where it lives (so `.env`, the PDF/OG caches and
`_site` are the same files the native pipeline uses), each ~/.ssh entry
and the git config are mounted read-only at their host paths (from their
resolved locations: home-manager symlinks them into /nix/store) so `Host`
aliases and `IdentityFile` lines keep resolving, sequoia's credential
store is mounted read-write, and every SSH agent socket found is mounted
at its real path too. Git commit signing is redirected to plain
`ssh-keygen` (the host's signing wrapper is a host-specific binary); it
signs with the key the agent offers. uid/gid are passed to the
entrypoint, which creates a matching user so files written into the repo
stay owned by the operator.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

IMAGE_NAME = "evedeploy"
CONTAINER_DIR = Path("evedeploy") / "container"
IMAGE_INPUTS = (
    CONTAINER_DIR / "Dockerfile",
    CONTAINER_DIR / "entrypoint.sh",
    Path("Gemfile"),
    Path("Gemfile.lock"),
)
UV_CACHE_VOLUME = "evedeploy-uv-cache"
UV_CACHE_DIR = "/var/cache/uv"
CV_SOURCE_DIR = Path("../eprintsToCV/output")
# sequoia keeps its ATProto credentials (and refreshed tokens) here.
SEQUOIA_STATE = Path(".config/sequoia")
# Agents we know how to find without any configuration, in order of
# preference for commit signing (the generic SSH_AUTH_SOCK comes last: on a
# desktop it is often a gpg/byobu agent without the deploy key).
KNOWN_AGENTS = (".bitwarden-ssh-agent.sock", ".1password/agent.sock")
# Host variables that may shape the run; forwarded only when set.
PASSTHROUGH_ENV = ("TERM", "COLORTERM", "JEKYLL_SKIP_PDFS",
                   "BUNDLE_SILENCE_DEPRECATIONS", "NO_COLOR")
LAUNCHER_FLAGS = {
    "--native": "native",
    "--shell": "shell",
    "--rebuild-image": "rebuild_image",
}


class LauncherError(RuntimeError):
    """Something on the host stops the container from launching."""


@dataclass
class LauncherOptions:
    native: bool = False
    shell: bool = False
    rebuild_image: bool = False
    passthrough: list = field(default_factory=list)


def repo_root() -> Path:
    """The blog root: this file lives at <root>/evedeploy/evedeploy/."""
    return Path(__file__).resolve().parents[2]


def image_tag(paths) -> str:
    """evedeploy:<digest> — the digest changes when any image input does."""
    digest = hashlib.sha256()
    for path in paths:
        digest.update(Path(path).name.encode())
        digest.update(b"\0")
        digest.update(Path(path).read_bytes())
        digest.update(b"\0")
    return f"{IMAGE_NAME}:{digest.hexdigest()[:12]}"


def detect_runtime(which=shutil.which, env=None) -> str:
    env = os.environ if env is None else env
    forced = env.get("EVEDEPLOY_RUNTIME")
    if forced:
        return forced
    for candidate in ("docker", "podman"):
        if which(candidate):
            return candidate
    raise LauncherError(
        "no container runtime found: install Docker or Podman (or run "
        "with --native to use the host toolchain)")


def _dedupe(paths):
    seen, out = set(), []
    for path in paths:
        if path not in seen:
            seen.add(path)
            out.append(path)
    return out


def agent_sockets(home, env=None, exists=None) -> list:
    """Existing SSH agent sockets, most preferred first."""
    env = os.environ if env is None else env
    exists = exists or (lambda p: Path(p).exists())
    home = Path(home)
    candidates = []
    if env.get("EVEDEPLOY_SSH_AGENT"):
        candidates.append(Path(env["EVEDEPLOY_SSH_AGENT"]))
    candidates += [home / name for name in KNOWN_AGENTS]
    if env.get("SSH_AUTH_SOCK"):
        candidates.append(Path(env["SSH_AUTH_SOCK"]))
    return _dedupe([p for p in candidates if exists(p)])


def ssh_mounts(home, entries=None, realpath=None, exists=None,
               is_socket=None) -> list:
    """(source, destination) for each entry of ~/.ssh, symlinks resolved.

    Mounting the directory itself would carry symlinks across unresolved —
    home-manager, for one, links ~/.ssh/config and the public keys into
    /nix/store, which the container does not have — so every entry is
    mounted on its own from its real location to its host path. Sockets
    (ControlMaster, agents) and dangling links are left out.
    """
    home = Path(home)
    ssh_dir = home / ".ssh"

    def default_entries(directory):
        return sorted(directory.iterdir()) if directory.is_dir() else []

    entries = entries or default_entries
    realpath = realpath or (lambda p: Path(p).resolve())
    exists = exists or (lambda p: Path(p).exists())
    is_socket = is_socket or (lambda p: Path(p).is_socket())
    pairs = []
    for entry in entries(ssh_dir):
        entry = Path(entry)
        if is_socket(entry):
            continue
        source = Path(realpath(entry))
        if not exists(source):
            continue
        pairs.append((source, entry))
    return pairs


def git_config_files(home, env=None, exists=None) -> list:
    """The user's git config file(s): classic ~/.gitconfig and/or XDG."""
    env = os.environ if env is None else env
    exists = exists or (lambda p: Path(p).is_file())
    home = Path(home)
    xdg = Path(env.get("XDG_CONFIG_HOME") or home / ".config")
    candidates = [home / ".gitconfig", xdg / "git" / "config"]
    return [p for p in candidates if exists(p)]


def host_timezone(env=None, localtime=None):
    """The host's IANA zone name, or None when it cannot be worked out.

    Jekyll stamps every post with the system zone (unless _config.yml
    pins one), so a container left on UTC shifts dates and can even move
    a post published near midnight to a different day's URL. $TZ wins;
    otherwise the zone is the tail of the /etc/localtime target
    (…/zoneinfo/Europe/London), on glibc and Nix layouts alike.
    """
    env = os.environ if env is None else env
    if env.get("TZ"):
        return env["TZ"]
    if localtime is None:
        def localtime():
            try:
                return str(Path("/etc/localtime").resolve())
            except OSError:
                return None
    target = localtime()
    if not target or "/zoneinfo/" not in target:
        return None
    return target.split("/zoneinfo/", 1)[1]


def split_args(argv) -> LauncherOptions:
    """Peel the launcher's own flags off; the rest goes to evedeploy."""
    opts = LauncherOptions()
    for arg in argv:
        if arg in LAUNCHER_FLAGS:
            setattr(opts, LAUNCHER_FLAGS[arg], True)
        else:
            opts.passthrough.append(arg)
    return opts


def native_command(args) -> list:
    """What deploy.sh used to exec directly on the host."""
    return ["uv", "run", "--env-file", ".env", "--project", "evedeploy",
            "evedeploy", *args]


def run_command(runtime, image, root, home, uid, gid, args, *, tty,
                env=None, sockets=(), identity_files=(), extra_mounts=(),
                state_dirs=(), shell=False, timezone=None) -> list:
    """The full `<runtime> run ...` argv for one evedeploy invocation."""
    env = os.environ if env is None else env
    root, home = Path(root), Path(home)
    cmd = [runtime, "run", "--rm", "-i", "--init",
           "--network", "host", "--shm-size", "1g"]
    if tty:
        cmd.append("-t")
    if runtime == "podman":
        cmd.append("--userns=keep-id")

    def mount(src, dst=None, ro=False):
        spec = f"{src}:{dst or src}" + (":ro" if ro else "")
        cmd.extend(["-v", spec])

    def setenv(name, value):
        cmd.extend(["-e", f"{name}={value}"])

    mount(root)
    cmd.extend(["-w", str(root)])
    for source, destination in identity_files:
        mount(source, destination, ro=True)
    for state in state_dirs:
        mount(state)
    for extra in extra_mounts:
        mount(extra, ro=True)
    mount("/etc/hosts", ro=True)
    for sock in sockets:
        mount(sock)
    if sockets:
        setenv("SSH_AUTH_SOCK", str(sockets[0]))
    mount(UV_CACHE_VOLUME, UV_CACHE_DIR)
    setenv("UV_CACHE_DIR", UV_CACHE_DIR)

    setenv("EVEDEPLOY_UID", str(uid))
    setenv("EVEDEPLOY_GID", str(gid))
    setenv("HOME", str(home))
    if timezone:
        setenv("TZ", timezone)
    # The host's gpg.ssh.program is a host-specific wrapper; plain
    # ssh-keygen signs with whatever the mounted agent offers.
    setenv("GIT_CONFIG_COUNT", "1")
    setenv("GIT_CONFIG_KEY_0", "gpg.ssh.program")
    setenv("GIT_CONFIG_VALUE_0", "ssh-keygen")
    for name in PASSTHROUGH_ENV:
        if name in env:
            setenv(name, env[name])

    cmd.append(image)
    cmd.extend(["bash"] if shell else native_command(args))
    return cmd


def ensure_image(runtime, tag, root, run=subprocess.run, rebuild=False,
                 echo=print) -> None:
    """Build the image when it is missing (or a rebuild is forced)."""
    root = Path(root)
    if not rebuild:
        probe = run([runtime, "image", "inspect", tag],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if probe.returncode == 0:
            return
    echo(f"==> Building container image {tag} (first run on this machine "
         "or the image inputs changed; this takes a few minutes)")
    result = run([runtime, "build", "-f", str(root / CONTAINER_DIR / "Dockerfile"),
                 "-t", tag, str(root)])
    if result.returncode != 0:
        raise LauncherError(f"{runtime} build failed (exit {result.returncode})")


def main(argv=None, exec_=os.execvp) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    opts = split_args(argv)
    root = repo_root()
    os.chdir(root)

    if opts.native:
        cmd = native_command(opts.passthrough)
        exec_(cmd[0], cmd)
        return 0

    try:
        runtime = detect_runtime()
        tag = image_tag([root / p for p in IMAGE_INPUTS])
        ensure_image(runtime, tag, root, rebuild=opts.rebuild_image)
    except LauncherError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    home = Path.home()
    extra = [p for p in [(root / CV_SOURCE_DIR).resolve()] if p.is_dir()]
    identity = ssh_mounts(home) + [
        (cfg.resolve(), cfg) for cfg in git_config_files(home)]
    state = [d for d in [home / SEQUOIA_STATE] if d.is_dir()]
    cmd = run_command(
        runtime, tag, root, home, os.getuid(), os.getgid(),
        opts.passthrough, tty=sys.stdin.isatty() and sys.stdout.isatty(),
        sockets=agent_sockets(home), identity_files=identity,
        extra_mounts=extra, state_dirs=state, shell=opts.shell,
        timezone=host_timezone())
    exec_(cmd[0], cmd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
