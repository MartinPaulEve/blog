import io

import pytest
from PIL import Image

from thought_composer import cli
from thought_composer.store import add_thought, load_thoughts, set_syndication


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


# --- resyndicating a stored thought --------------------------------------



class RecordingBluesky:
    def __init__(self):
        self.calls = []

    def post_thread(self, segments, images=None, card=None):
        self.calls.append({"segments": segments, "images": images})
        return ["https://bsky.app/profile/eve.gd/post/rkey9"]


class RecordingMastodon:
    def __init__(self):
        self.uploads = []
        self.calls = []

    def upload_media(self, data, mime, alt=""):
        self.uploads.append({"data": data, "mime": mime, "alt": alt})
        return f"m{len(self.uploads)}"

    def post_thread(self, segments, media_ids=None):
        self.calls.append({"segments": segments, "media_ids": media_ids})
        return ["https://hcommons.social/@mpe/999"]


@pytest.fixture
def services(monkeypatch):
    bluesky, mastodon = RecordingBluesky(), RecordingMastodon()
    monkeypatch.setattr(cli, "_bluesky_client", lambda: bluesky)
    monkeypatch.setattr(cli, "_mastodon_client", lambda: mastodon)
    return bluesky, mastodon


def stored_with_image(root, text="Tea, delivered."):
    (root / "assets" / "thoughts").mkdir(parents=True)
    (root / "assets" / "thoughts" / "x-1.png").write_bytes(png_bytes())
    entry = add_thought(
        root, text,
        images=[{"src": "/assets/thoughts/x-1.png", "alt": "a box of tea"}],
    )
    return entry["id"]


def test_resyndicate_posts_only_to_the_missing_service(root, services):
    bluesky, mastodon = services
    thought_id = stored_with_image(root)
    set_syndication(root, thought_id, bluesky="https://bsky.app/profile/eve.gd/post/old")

    result = cli.resyndicate(root, thought_id, echo=lambda *a: None)

    assert bluesky.calls == []
    assert mastodon.calls and mastodon.calls[0]["segments"] == ["Tea, delivered."]
    assert result["mastodon"] == "https://hcommons.social/@mpe/999"
    (entry,) = load_thoughts(root)
    assert entry["mastodon"] == "https://hcommons.social/@mpe/999"
    assert entry["bluesky"] == "https://bsky.app/profile/eve.gd/post/old"


def test_resyndicate_reuploads_the_stored_images(root, services):
    _bluesky, mastodon = services
    thought_id = stored_with_image(root)
    cli.resyndicate(root, thought_id, services=["mastodon"], echo=lambda *a: None)
    (upload,) = mastodon.uploads
    assert upload["data"] == png_bytes()
    assert upload["mime"] == "image/png"
    assert upload["alt"] == "a box of tea"
    assert mastodon.calls[0]["media_ids"] == ["m1"]


def test_resyndicate_can_be_limited_to_one_service(root, services):
    bluesky, mastodon = services
    entry = add_thought(root, "no links yet")
    cli.resyndicate(root, entry["id"], services=["bluesky"], echo=lambda *a: None)
    assert bluesky.calls and not mastodon.calls
    assert load_thoughts(root)[0]["bluesky"].startswith("https://bsky.app/")


def test_resyndicate_does_nothing_when_both_copies_exist(root, services):
    bluesky, mastodon = services
    entry = add_thought(root, "done already")
    set_syndication(root, entry["id"], bluesky="https://bsky.app/x", mastodon="https://hcommons.social/y")
    assert cli.resyndicate(root, entry["id"], echo=lambda *a: None) == {}
    assert not bluesky.calls and not mastodon.calls


def test_resyndicate_unknown_id_is_an_error(root, services):
    with pytest.raises(KeyError):
        cli.resyndicate(root, "19990101000000", echo=lambda *a: None)


def test_resyndicate_main_reports_the_new_link(root, services, capsys):
    entry = add_thought(root, "cli path")
    set_syndication(root, entry["id"], bluesky="https://bsky.app/x")
    assert cli.resyndicate_main([entry["id"], "--root", str(root)]) == 0
    assert "https://hcommons.social/@mpe/999" in capsys.readouterr().out


def test_resyndicate_main_unknown_id_fails(root, services, capsys):
    assert cli.resyndicate_main(["19990101000000", "--root", str(root)]) == 1
    assert "19990101000000" in capsys.readouterr().err
