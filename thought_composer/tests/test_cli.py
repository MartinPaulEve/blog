import io

import pytest
from PIL import Image

from thought_composer import cli
from thought_composer.store import load_thoughts


@pytest.fixture
def root(tmp_path):
    (tmp_path / "_data").mkdir()
    return tmp_path


def png_bytes():
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), "blue").save(buffer, format="PNG")
    return buffer.getvalue()


def test_dry_run_shows_segments_and_stores_nothing(root, capsys):
    long_text = " ".join(f"word{i}" for i in range(80))
    cli.main(["--dry-run", "--text", long_text, "--root", str(root)])
    out = capsys.readouterr().out
    assert "2" in out  # it would thread
    assert load_thoughts(root) == []


def test_dry_run_shows_each_service_when_they_split_differently(root, capsys):
    long_text = " ".join(f"word{i}" for i in range(80))
    cli.main(["--dry-run", "--text", long_text, "--root", str(root)])
    out = capsys.readouterr().out
    assert "Bluesky post 1" in out
    assert "Bluesky post 2" in out
    assert "Mastodon post 1" in out
    assert "Mastodon post 2" not in out


def test_dry_run_shows_one_set_when_they_split_the_same(root, capsys):
    cli.main(["--dry-run", "--text", "just a short one", "--root", str(root)])
    out = capsys.readouterr().out
    assert "--- post 1 ---" in out
    assert "Bluesky post" not in out


def test_local_flow_stores_the_thought_untouched(root):
    text = "A thought with a link https://example.org/x in it. "
    cli.main(["--text", text, "--no-post", "--no-deploy", "--root", str(root)])
    (entry,) = load_thoughts(root)
    assert entry["text"] == text
    assert "bluesky" not in entry


def test_local_flow_saves_attached_images(root, tmp_path):
    shot = tmp_path / "shot.png"
    shot.write_bytes(png_bytes())
    cli.main([
        "--text", "with a picture", "--no-post", "--no-deploy",
        "--image", str(shot), "--alt", "a blue square",
        "--root", str(root),
    ])
    (entry,) = load_thoughts(root)
    (image,) = entry["images"]
    assert image["alt"] == "a blue square"
    assert (root / image["src"].lstrip("/")).is_file()


def test_syndicate_records_urls_and_survives_one_service_failing(root, monkeypatch):
    cli_calls = {}

    class FakeBluesky:
        def post_thread(self, segments, images=None, card=None):
            cli_calls["bluesky"] = segments
            return ["https://bsky.app/profile/eve.gd/post/rkey1"]

    class FakeMastodon:
        def upload_media(self, data, mime, alt=""):
            return "314"

        def post_thread(self, segments, media_ids=None):
            raise RuntimeError("mastodon is down")

    monkeypatch.setattr(cli, "_bluesky_client", lambda: FakeBluesky())
    monkeypatch.setattr(cli, "_mastodon_client", lambda: FakeMastodon())
    from thought_composer.store import add_thought

    add_thought(root, "hello")
    stored = load_thoughts(root)[0]
    result = cli.syndicate(
        root, stored, ["hello"], ["hello"], [], echo=lambda *a: None
    )
    assert result["bluesky"] == "https://bsky.app/profile/eve.gd/post/rkey1"
    assert result["mastodon"] is None
    assert load_thoughts(root)[0]["bluesky"] == result["bluesky"]
    assert "mastodon" not in load_thoughts(root)[0]


def test_syndicate_sends_each_service_its_own_segments(root, monkeypatch):
    received = {}

    class FakeBluesky:
        def post_thread(self, segments, images=None, card=None):
            received["bluesky"] = segments
            return ["https://bsky.app/profile/eve.gd/post/rkey1"]

    class FakeMastodon:
        def upload_media(self, data, mime, alt=""):
            return "314"

        def post_thread(self, segments, media_ids=None):
            received["mastodon"] = segments
            return ["https://hcommons.social/@mpe/1"]

    monkeypatch.setattr(cli, "_bluesky_client", lambda: FakeBluesky())
    monkeypatch.setattr(cli, "_mastodon_client", lambda: FakeMastodon())
    from thought_composer.store import add_thought

    add_thought(root, "part one part two")
    stored = load_thoughts(root)[0]
    cli.syndicate(
        root,
        stored,
        ["part one", "part two"],
        ["part one part two"],
        [],
        echo=lambda *a: None,
    )
    assert received["bluesky"] == ["part one", "part two"]
    assert received["mastodon"] == ["part one part two"]
