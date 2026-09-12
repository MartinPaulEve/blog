"""drafts: what a dry run leaves behind for the POST reply to publish."""

from datetime import UTC, datetime, timedelta

from mailthought.drafts import (
    delete_draft,
    load_draft,
    new_draft_id,
    prune_drafts,
    save_draft,
)

IMAGES = [
    {"data": b"JPGBYTES", "mime": "image/jpeg", "alt": "a gate", "filename": "gate.jpg"},
    {"data": b"PNGBYTES", "mime": "image/png", "alt": "", "filename": "shot.png"},
]


def test_new_id_is_eight_hex_characters():
    draft_id = new_draft_id()
    assert len(draft_id) == 8
    assert all(c in "0123456789abcdef" for c in draft_id)


def test_new_id_uses_injected_randomness():
    assert new_draft_id(rand=lambda: "a1b2c3d4e5") == "a1b2c3d4"


def test_two_default_ids_differ():
    assert new_draft_id() != new_draft_id()


def test_saved_draft_round_trips(tmp_path):
    save_draft(
        tmp_path,
        "a1b2c3d4",
        text="the drafted thought",
        images=IMAGES,
        sender="martin@eve.gd",
        message_id="<msg-1@eve.gd>",
    )
    draft = load_draft(tmp_path, "a1b2c3d4")
    assert draft["text"] == "the drafted thought"
    assert draft["sender"] == "martin@eve.gd"
    assert draft["message_id"] == "<msg-1@eve.gd>"
    assert [i["data"] for i in draft["images"]] == [b"JPGBYTES", b"PNGBYTES"]
    assert draft["images"][0]["mime"] == "image/jpeg"
    assert draft["images"][0]["alt"] == "a gate"


def test_unknown_draft_is_none(tmp_path):
    assert load_draft(tmp_path, "deadbeef") is None


def test_delete_removes_and_is_idempotent(tmp_path):
    save_draft(
        tmp_path, "a1b2c3d4", text="x", images=[], sender="m@e", message_id="<m>"
    )
    delete_draft(tmp_path, "a1b2c3d4")
    assert load_draft(tmp_path, "a1b2c3d4") is None
    delete_draft(tmp_path, "a1b2c3d4")  # no error the second time


def test_prune_removes_only_expired_drafts(tmp_path):
    t0 = datetime(2026, 1, 1, tzinfo=UTC)
    save_draft(
        tmp_path, "old00001", text="old", images=[], sender="m@e",
        message_id="<old>", now=t0,
    )
    save_draft(
        tmp_path, "fresh001", text="fresh", images=[], sender="m@e",
        message_id="<fresh>", now=t0 + timedelta(days=29),
    )
    removed = prune_drafts(tmp_path, ttl_days=30, now=t0 + timedelta(days=31))
    assert removed == ["old00001"]
    assert load_draft(tmp_path, "old00001") is None
    assert load_draft(tmp_path, "fresh001") is not None
