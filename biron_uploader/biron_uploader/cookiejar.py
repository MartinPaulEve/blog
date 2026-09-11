"""Harvesting the BIROn session cookie from a controlled browser login.

BIROn's Shibboleth/Microsoft SSO sets a session-only cookie
(secure_eprints_session%3Aeprints.bbk.ac.uk) that lives in browser
memory and never reaches the on-disk cookie store, so it cannot be read
from the user's profile. Instead, a dedicated Chromium profile is
driven over CDP: ``./biron.sh login`` opens a window for the Microsoft
sign-in (first time, with MFA); afterwards the Microsoft session
persisted in that profile normally completes the redirect loop
unattended, so a headless run can refresh the cookie with no
interaction. The harvested cookie is written to ``.biron_cookie``
(gitignored) at the blog root.
"""

import json
import os
import subprocess
import time
from pathlib import Path

COOKIE_PREFIX = "secure_eprints_session"
COOKIE_DOMAIN = "eprints.bbk.ac.uk"
LOGIN_URL = "https://eprints.bbk.ac.uk/cgi/users/home"
COOKIE_FILE = ".biron_cookie"
PROFILE_DIR = "~/.local/state/biron-browser"


class LoginError(RuntimeError):
    """The browser login did not produce a session cookie."""


def cookie_file_path(root: Path) -> Path:
    """The harvested-cookie file: $BIRON_COOKIE_FILE or root/.biron_cookie."""
    override = os.environ.get("BIRON_COOKIE_FILE")
    if override:
        return Path(override)
    return Path(root) / COOKIE_FILE


def read_cookie_file(root: Path) -> str | None:
    """The stored cookie ("name=value"), or None when absent/empty."""
    path = cookie_file_path(root)
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8").strip() or None


def write_cookie_file(root: Path, cookie: str) -> Path:
    """Store the cookie (owner-readable only); return the path written."""
    path = cookie_file_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(mode=0o600, exist_ok=True)
    path.chmod(0o600)
    path.write_text(cookie.strip() + "\n", encoding="utf-8")
    return path


def match_session_cookie(cookies: list[dict]) -> str | None:
    """The BIROn session cookie ("name=value") from a CDP cookie list."""
    for cookie in cookies:
        if cookie.get("name", "").startswith(COOKIE_PREFIX) and (
            COOKIE_DOMAIN in cookie.get("domain", "")
        ):
            return f"{cookie['name']}={cookie['value']}"
    return None


def _browser_websocket_url(profile_dir: Path, deadline: float) -> str:
    """The CDP browser endpoint from Chromium's DevToolsActivePort file."""
    port_file = profile_dir / "DevToolsActivePort"
    while time.monotonic() < deadline:
        if port_file.is_file():
            lines = port_file.read_text().splitlines()
            if len(lines) >= 2:
                return f"ws://127.0.0.1:{lines[0].strip()}{lines[1].strip()}"
        time.sleep(0.2)
    raise LoginError("Chromium did not expose a DevTools endpoint in time")


def _cdp_cookies(ws_url: str) -> list[dict]:
    """All browser cookies (session ones included) via one CDP call."""
    import websocket

    connection = websocket.create_connection(ws_url, timeout=10)
    try:
        for message_id, method in ((1, "Storage.getCookies"),
                                   (2, "Network.getAllCookies")):
            connection.send(json.dumps({"id": message_id, "method": method}))
            while True:
                reply = json.loads(connection.recv())
                if reply.get("id") == message_id:
                    break
            result = reply.get("result") or {}
            if "cookies" in result:
                return result["cookies"]
        return []
    finally:
        connection.close()


def harvest(
    root: Path,
    headless: bool = False,
    timeout: float | None = None,
    chromium: str | None = None,
    echo=print,
) -> str:
    """Drive a Chromium login and return (and store) the session cookie.

    Headful mode waits up to five minutes for the user to finish the
    Microsoft sign-in; headless mode gives the silent redirect loop 45
    seconds. Raises LoginError when no cookie appears in time.
    """
    chromium = chromium or os.environ.get("BIRON_BROWSER", "chromium")
    timeout = timeout or (45 if headless else 300)
    profile_dir = Path(
        os.environ.get("BIRON_BROWSER_PROFILE", PROFILE_DIR)
    ).expanduser()
    profile_dir.mkdir(parents=True, exist_ok=True)
    (profile_dir / "DevToolsActivePort").unlink(missing_ok=True)

    command = [
        chromium,
        f"--user-data-dir={profile_dir}",
        "--remote-debugging-port=0",
        "--no-first-run",
        "--no-default-browser-check",
    ]
    if headless:
        command.append("--headless=new")
    command.append(LOGIN_URL)

    echo(
        "Waiting for the BIROn session cookie "
        + ("(silent Microsoft redirect)…" if headless
           else "— complete the Microsoft sign-in in the browser window…")
    )
    deadline = time.monotonic() + timeout
    process = subprocess.Popen(
        command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    try:
        ws_url = _browser_websocket_url(profile_dir, deadline)
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise LoginError(
                    "the browser exited before a session cookie appeared "
                    "(is another Chromium already using the biron profile?)"
                )
            cookie = match_session_cookie(_cdp_cookies(ws_url))
            if cookie:
                path = write_cookie_file(root, cookie)
                echo(f"Session cookie stored in {path}")
                return cookie
            time.sleep(2)
        raise LoginError(
            "no session cookie after "
            f"{int(timeout)}s — "
            + ("the Microsoft session needs an interactive sign-in; "
               "run ./biron.sh login" if headless
               else "the sign-in was not completed")
        )
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
