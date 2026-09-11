
from biron_uploader.cookiejar import (
    cookie_file_path,
    find_extensions,
    launch_command,
    match_session_cookie,
    prepare_profile,
    read_cookie_file,
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
