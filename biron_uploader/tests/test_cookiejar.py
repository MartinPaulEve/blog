
from biron_uploader.cookiejar import (
    cookie_file_path,
    match_session_cookie,
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
