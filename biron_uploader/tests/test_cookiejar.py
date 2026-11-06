import io
import time

import pytest

from biron_uploader import cookiejar
from biron_uploader.cookiejar import (
    LoginError,
    LoginSkipped,
    browser_websocket_url,
    cookie_file_path,
    find_extensions,
    harvest,
    launch_command,
    match_session_cookie,
    prepare_profile,
    read_cookie_file,
    read_keypress,
    write_cookie_file,
)


def test_match_finds_the_encoded_session_cookie():
    cookies = [
        {"name": "JSESSIONID", "domain": "login.microsoftonline.com", "value": "x"},
        {
            "name": "secure_eprints_session%3Aeprints.bbk.ac.uk",
            "domain": "eprints.bbk.ac.uk",
            "value": "abc123",
        },
    ]
    assert match_session_cookie(cookies) == (
        "secure_eprints_session%3Aeprints.bbk.ac.uk=abc123"
    )


def test_match_requires_the_right_domain_and_prefix():
    assert match_session_cookie(
        [{"name": "secure_eprints_session%3Aother.example", "domain": "other.example", "value": "x"}]
    ) is None
    assert match_session_cookie(
        [{"name": "other_cookie", "domain": "eprints.bbk.ac.uk", "value": "x"}]
    ) is None
    assert match_session_cookie([]) is None


def test_launch_command_permits_devtools_connections():
    command = launch_command("chromium", "/tmp/profile", headless=True)
    assert command[0] == "chromium"
    assert "--user-data-dir=/tmp/profile" in command
    assert "--remote-debugging-port=0" in command
    # Chromium >= 111 rejects DevTools websockets from unlisted origins.
    assert "--remote-allow-origins=*" in command
    assert "--headless=new" in command
    assert command[-1].startswith("https://eprints.bbk.ac.uk/")
    assert "--headless=new" not in launch_command("chromium", "/p", headless=False)


def test_find_extensions_picks_the_newest_installed_version(tmp_path):
    ext = tmp_path / "Default" / "Extensions" / "aeblfdkhhhdcdjpifhhbdiojplfjncoa"
    (ext / "8.9.1_0").mkdir(parents=True)
    (ext / "8.12.36.40_0").mkdir()
    (found,) = find_extensions(tmp_path)
    assert found == ext / "8.12.36.40_0"


def test_find_extensions_empty_when_nothing_installed(tmp_path):
    assert find_extensions(tmp_path) == []
    assert find_extensions(tmp_path / "missing") == []


def test_headful_launch_loads_extensions_headless_does_not():
    command = launch_command(
        "chromium", "/p", headless=False, extensions=["/e/one", "/e/two"]
    )
    assert "--load-extension=/e/one,/e/two" in command
    command = launch_command(
        "chromium", "/p", headless=True, extensions=["/e/one"]
    )
    assert not any(arg.startswith("--load-extension") for arg in command)


def test_prepare_profile_copies_native_messaging_manifests(tmp_path):
    daily = tmp_path / "chromium"
    (daily / "NativeMessagingHosts").mkdir(parents=True)
    manifest = daily / "NativeMessagingHosts" / "com.1password.1password.json"
    manifest.write_text('{"name": "com.1password.1password"}')
    profile = tmp_path / "biron-profile"
    prepare_profile(profile, daily)
    copied = profile / "NativeMessagingHosts" / "com.1password.1password.json"
    assert copied.read_text() == manifest.read_text()
    # idempotent, and fine when the source has nothing to offer
    prepare_profile(profile, daily)
    prepare_profile(profile, tmp_path / "nowhere")


def test_cookie_file_round_trip(tmp_path):
    assert read_cookie_file(tmp_path) is None
    path = write_cookie_file(tmp_path, "secure_eprints_session%3Ax=abc")
    assert path == tmp_path / ".biron_cookie"
    assert read_cookie_file(tmp_path) == "secure_eprints_session%3Ax=abc"
    assert (path.stat().st_mode & 0o777) == 0o600


def test_cookie_file_env_override(tmp_path, monkeypatch):
    override = tmp_path / "elsewhere" / "cookie"
    monkeypatch.setenv("BIRON_COOKIE_FILE", str(override))
    assert cookie_file_path(tmp_path) == override
    write_cookie_file(tmp_path, "name=val")
    assert override.read_text().strip() == "name=val"
    assert read_cookie_file(tmp_path) == "name=val"


def test_empty_cookie_file_reads_as_none(tmp_path):
    (tmp_path / ".biron_cookie").write_text("\n")
    assert read_cookie_file(tmp_path) is None


# --- driving the login browser ---------------------------------------------

SESSION = [
    {
        "name": "secure_eprints_session%3Aeprints.bbk.ac.uk",
        "domain": "eprints.bbk.ac.uk",
        "value": "abc",
    }
]
SESSION_COOKIE = "secure_eprints_session%3Aeprints.bbk.ac.uk=abc"


class FakeProcess:
    """A Popen stand-in: alive until terminated, or dead from the start."""

    def __init__(self, exit_code=None):
        self.returncode = exit_code
        self.terminated = False

    def poll(self):
        return self.returncode

    def terminate(self):
        self.terminated = True
        if self.returncode is None:
            self.returncode = -15

    def wait(self, timeout=None):
        return self.returncode

    def kill(self):
        self.returncode = -9


def test_websocket_wait_fails_fast_when_the_browser_has_exited(tmp_path):
    started = time.monotonic()
    with pytest.raises(LoginError):
        browser_websocket_url(
            tmp_path, deadline=time.monotonic() + 60, process=FakeProcess(1)
        )
    assert time.monotonic() - started < 5


def test_websocket_wait_reads_the_devtools_port_file(tmp_path):
    (tmp_path / "DevToolsActivePort").write_text("9222\n/devtools/browser/abc\n")
    url = browser_websocket_url(
        tmp_path, deadline=time.monotonic() + 5, process=FakeProcess()
    )
    assert url == "ws://127.0.0.1:9222/devtools/browser/abc"


def test_keypress_is_none_when_stdin_is_not_a_terminal():
    assert read_keypress(io.StringIO("c")) is None


@pytest.fixture
def driven_browser(monkeypatch, tmp_path):
    """harvest() against a fake Chromium: no process, no CDP, no window.

    ``cookies`` is the sequence of cookie lists successive CDP polls
    return (empty once exhausted).
    """
    state = {"cookies": [], "process": FakeProcess(), "launches": []}

    def fake_popen(command, **kwargs):
        state["launches"].append(command)
        return state["process"]

    monkeypatch.setattr(cookiejar.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(
        cookiejar, "browser_websocket_url", lambda *a, **k: "ws://127.0.0.1:1/x"
    )
    monkeypatch.setattr(
        cookiejar, "_cdp_cookies",
        lambda ws: state["cookies"].pop(0) if state["cookies"] else [],
    )
    monkeypatch.setattr(cookiejar, "find_extensions", lambda *a, **k: [])
    monkeypatch.setattr(cookiejar, "prepare_profile", lambda *a, **k: None)
    monkeypatch.setenv("BIRON_BROWSER_PROFILE", str(tmp_path / "profile"))
    return state


def quiet(*args, **kwargs):
    pass


def test_harvest_returns_and_stores_the_cookie_once_it_appears(
        driven_browser, tmp_path):
    driven_browser["cookies"] = [[], SESSION]
    cookie = harvest(tmp_path, headless=True, timeout=10, interval=0, echo=quiet)
    assert cookie == SESSION_COOKIE
    assert read_cookie_file(tmp_path) == SESSION_COOKIE
    assert driven_browser["process"].terminated


def test_headful_wait_stops_on_the_continue_key(driven_browser, tmp_path):
    with pytest.raises(LoginSkipped):
        harvest(tmp_path, headless=False, timeout=30, interval=0,
                keypress=lambda: "c", echo=quiet)
    assert driven_browser["process"].terminated
    assert read_cookie_file(tmp_path) is None


def test_the_continue_key_is_case_insensitive(driven_browser, tmp_path):
    with pytest.raises(LoginSkipped):
        harvest(tmp_path, headless=False, timeout=30, interval=0,
                keypress=lambda: "C", echo=quiet)


def test_other_keys_do_not_interrupt_the_wait(driven_browser, tmp_path):
    driven_browser["cookies"] = [[], [], SESSION]
    keys = iter(["x", "q"])
    cookie = harvest(tmp_path, headless=False, timeout=10, interval=0,
                     keypress=lambda: next(keys, None), echo=quiet)
    assert cookie == SESSION_COOKIE


def test_headless_runs_ignore_the_keyboard(driven_browser, tmp_path):
    driven_browser["cookies"] = [[], SESSION]
    cookie = harvest(tmp_path, headless=True, timeout=10, interval=0,
                     keypress=lambda: "c", echo=quiet)
    assert cookie == SESSION_COOKIE


def test_a_browser_that_dies_is_a_login_error_not_a_hang(
        driven_browser, tmp_path):
    driven_browser["process"] = FakeProcess(1)
    started = time.monotonic()
    with pytest.raises(LoginError) as excinfo:
        harvest(tmp_path, headless=True, timeout=60, interval=0, echo=quiet)
    assert not isinstance(excinfo.value, LoginSkipped)
    assert time.monotonic() - started < 5


def test_the_wait_times_out_with_a_login_error(driven_browser, tmp_path):
    with pytest.raises(LoginError) as excinfo:
        harvest(tmp_path, headless=True, timeout=0.2, interval=0, echo=quiet)
    assert not isinstance(excinfo.value, LoginSkipped)
    assert driven_browser["process"].terminated
