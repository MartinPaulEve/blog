import io
from datetime import UTC, datetime

import pytest
from PIL import Image

from thought_composer.store import (
    add_thought,
    load_image_file,
    load_thoughts,
    save_image,
    set_syndication,
)


@pytest.fixture
def root(tmp_path):
    (tmp_path / "_data").mkdir()
    return tmp_path


def png_bytes(width=10, height=10):
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), "red").save(buffer, format="PNG")
    return buffer.getvalue()


def test_add_thought_prepends_newest_first(root):
    add_thought(root, "first", now=datetime(2026, 9, 10, 9, 0, tzinfo=UTC))
    add_thought(root, "second", now=datetime(2026, 9, 10, 10, 0, tzinfo=UTC))
    thoughts = load_thoughts(root)
    assert [t["text"] for t in thoughts] == ["second", "first"]
    assert thoughts[0]["id"] == "20260910100000"
    assert thoughts[0]["date"].startswith("2026-09-10T10:00:00")


def test_text_is_stored_untouched(root):
    text = 'Raw *markdown* &amp; <tags> stay  exactly\n\nas typed. '
    add_thought(root, text, now=datetime(2026, 9, 10, tzinfo=UTC))
    assert load_thoughts(root)[0]["text"] == text


def test_images_recorded_on_the_entry(root):
    images = [{"src": "/assets/thoughts/x-1.png", "alt": "a red square"}]
    add_thought(
        root, "with image", images=images,
        now=datetime(2026, 9, 10, tzinfo=UTC),
    )
    assert load_thoughts(root)[0]["images"] == images


def test_set_syndication_updates_the_right_entry(root):
    add_thought(root, "first", now=datetime(2026, 9, 10, 9, 0, tzinfo=UTC))
    add_thought(root, "second", now=datetime(2026, 9, 10, 10, 0, tzinfo=UTC))
    set_syndication(
        root, "20260910090000",
        bluesky="https://bsky.app/profile/eve.gd/post/abc",
        mastodon="https://hcommons.social/@mpe/1",
    )
    first = load_thoughts(root)[1]
    assert first["bluesky"].endswith("/abc")
    assert first["mastodon"].endswith("/1")
    assert "bluesky" not in load_thoughts(root)[0]


def test_save_small_image_keeps_bytes_and_format(root):
    data = png_bytes()
    entry, final, mime = save_image(root, data, "image/png", "20260910090000", 1, alt="sq")
    assert entry == {"src": "/assets/thoughts/20260910090000-1.png", "alt": "sq"}
    assert mime == "image/png"
    assert final == data
    assert (root / "assets/thoughts/20260910090000-1.png").read_bytes() == data


def test_save_oversized_image_is_constrained(root):
    data = png_bytes(3000, 500)
    entry, final, mime = save_image(root, data, "image/png", "20260910090000", 1)
    assert mime == "image/jpeg"
    assert entry["src"].endswith(".jpg")
    with Image.open(io.BytesIO(final)) as image:
        assert max(image.size) <= 2000
    assert len(final) < 950_000


def test_load_image_file(root, tmp_path):
    path = tmp_path / "shot.png"
    path.write_bytes(png_bytes())
    data, mime = load_image_file(path)
    assert mime == "image/png"
    assert data == path.read_bytes()


def test_load_image_file_rejects_non_images(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("not an image")
    with pytest.raises(ValueError):
        load_image_file(path)
