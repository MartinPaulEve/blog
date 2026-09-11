from datetime import UTC, datetime

from thought_composer.importer import (
    assign_id,
    convert,
    existing_rkeys,
    expand_links,
    merge_thoughts,
)


def link_facet(byte_start, byte_end, uri):
    return {
        "index": {"byteStart": byte_start, "byteEnd": byte_end},
        "features": [{"$type": "app.bsky.richtext.facet#link", "uri": uri}],
    }


# --- link expansion ----------------------------------------------------------


def test_truncated_display_text_is_restored_to_the_full_url():
    text = "read example.com/a-very-long... now"
    display = "example.com/a-very-long..."
    start = len("read ")
    facets = [link_facet(start, start + len(display.encode()),
                         "https://example.com/a-very-long-path")]
    assert expand_links(text, facets) == (
        "read https://example.com/a-very-long-path now"
    )


def test_full_urls_and_facetless_text_pass_through():
    text = "see https://example.org/x now"
    facets = [link_facet(4, 4 + len("https://example.org/x"),
                         "https://example.org/x")]
    assert expand_links(text, facets) == text
    assert expand_links("no links here", None) == "no links here"


def test_byte_offsets_respect_multibyte_characters():
    text = "café → example.com/x..."
    prefix = len("café → ".encode())
    facets = [link_facet(prefix, prefix + len(b"example.com/x..."),
                         "https://example.com/xyz")]
    assert expand_links(text, facets) == "café → https://example.com/xyz"


# --- conversion --------------------------------------------------------------


def make_record(**overrides):
    record = {
        "$type": "app.bsky.feed.post",
        "text": "An old thought from Bluesky",
        "createdAt": "2025-03-01T12:30:45.123Z",
    }
    record.update(overrides)
    return record


def test_convert_builds_a_thought_entry():
    thought = convert(make_record(), "rkey123", "eve.gd")
    assert thought["text"] == "An old thought from Bluesky"
    assert thought["bluesky"] == "https://bsky.app/profile/eve.gd/post/rkey123"
    assert thought["date"].startswith("2025-03-01T")
    assert thought["image_blobs"] == []


def test_convert_skips_replies():
    record = make_record(reply={"root": {"uri": "at://x"}, "parent": {"uri": "at://x"}})
    assert convert(record, "rkey123", "eve.gd") is None


def test_convert_collects_image_blobs():
    embed = {
        "$type": "app.bsky.embed.images",
        "images": [
            {
                "alt": "a chart",
                "image": {"$type": "blob", "mimeType": "image/jpeg",
                          "ref": {"$link": "bafyabc"}},
            }
        ],
    }
    thought = convert(make_record(embed=embed), "rkey123", "eve.gd")
    assert thought["image_blobs"] == [
        {"cid": "bafyabc", "mime": "image/jpeg", "alt": "a chart"}
    ]


def test_convert_finds_images_inside_record_with_media():
    embed = {
        "$type": "app.bsky.embed.recordWithMedia",
        "record": {"record": {"uri": "at://quoted"}},
        "media": {
            "$type": "app.bsky.embed.images",
            "images": [
                {"alt": "", "image": {"mimeType": "image/png",
                                      "ref": {"$link": "bafyxyz"}}}
            ],
        },
    }
    thought = convert(make_record(embed=embed), "rkey123", "eve.gd")
    assert thought["image_blobs"] == [
        {"cid": "bafyxyz", "mime": "image/png", "alt": ""}
    ]


# --- ids, dedup and merging --------------------------------------------------


def test_assign_id_bumps_seconds_on_collision():
    taken = {"20250301123045"}
    date = datetime(2025, 3, 1, 12, 30, 45, tzinfo=UTC)
    new_id = assign_id(date, taken)
    assert new_id == "20250301123046"
    assert new_id in taken  # recorded so the next collision bumps again


def test_existing_rkeys_read_from_bluesky_urls():
    thoughts = [
        {"id": "1", "bluesky": "https://bsky.app/profile/eve.gd/post/abc"},
        {"id": "2"},
    ]
    assert existing_rkeys(thoughts) == {"abc"}


def test_merge_orders_newest_first():
    existing = [
        {"id": "3", "date": "2026-09-11T20:00:00+01:00", "text": "newest"},
        {"id": "1", "date": "2026-09-01T09:00:00+01:00", "text": "older"},
    ]
    imported = [
        {"id": "2", "date": "2026-09-05T12:00:00+01:00", "text": "between"},
        {"id": "0", "date": "2025-01-01T00:00:00+00:00", "text": "ancient"},
    ]
    merged = merge_thoughts(existing, imported)
    assert [t["id"] for t in merged] == ["3", "2", "1", "0"]
