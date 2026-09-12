from datetime import UTC, datetime

from thought_composer.importer import (
    assign_id,
    build_thoughts,
    convert,
    existing_rkeys,
    expand_links,
    is_announcement,
    merge_thoughts,
)

DID = "did:plc:me"


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


# --- announcement pruning ----------------------------------------------------


def test_bare_own_domain_links_are_announcements():
    assert is_announcement("https://eve.gd/2026/09/07/a-further-health-update/")
    assert is_announcement("Here's how it's going.\n\nhttps://eve.gd/2026/08/17/x/")
    assert is_announcement(
        "Crossref Member Practices feedback: without digital preservation, "
        "there is no digital persistence https://eve.gd/2026/09/09/x/"
    )
    assert is_announcement("New post: https://www.martineve.com/2014/01/01/y/")


def test_substantive_posts_with_own_links_are_kept():
    assert not is_announcement(
        "If you would ever like a distraction, I wrote a cathartic "
        "self-indulgent blog post last night that explains all of the "
        "gruesome details of what my life has become in medical terms, "
        "and how it might be fixed, and the various things that have to "
        "be weighed against each other https://eve.gd/2026/09/07/x/"
    )
    assert not is_announcement("no links at all here")
    assert not is_announcement("a link https://example.org/x elsewhere")


# --- thread reconstruction ---------------------------------------------------


def reply_record(text, created, parent_rkey, root_rkey, author_did=DID):
    return make_record(
        text=text,
        createdAt=created,
        reply={
            "root": {"uri": f"at://{author_did}/app.bsky.feed.post/{root_rkey}"},
            "parent": {"uri": f"at://{author_did}/app.bsky.feed.post/{parent_rkey}"},
        },
    )


def test_self_thread_continuations_append_to_the_root():
    posts = [
        ("root1", make_record(text="Part one.",
                              createdAt="2025-03-01T12:00:00.000Z")),
        ("cont2", reply_record("Part three.", "2025-03-01T12:02:00.000Z",
                               "cont1", "root1")),
        ("cont1", reply_record("Part two.", "2025-03-01T12:01:00.000Z",
                               "root1", "root1")),
    ]
    thoughts, stats = build_thoughts(posts, "eve.gd", DID, set())
    (thought,) = thoughts
    assert thought["text"] == "Part one.\n\nPart two.\n\nPart three."
    assert thought["bluesky"].endswith("/root1")
    assert stats["threaded"] == 2


def test_replies_to_other_accounts_are_dropped():
    posts = [
        ("r1", reply_record("@someone no, I disagree",
                            "2025-03-01T12:00:00.000Z",
                            "theirs", "theirs", author_did="did:plc:other")),
    ]
    thoughts, stats = build_thoughts(posts, "eve.gd", DID, set())
    assert thoughts == []
    assert stats["replies"] == 1


def test_continuations_of_syndicated_composer_threads_are_dropped():
    # The composer already stored the full unsplit text, so its thread
    # continuations must not be re-appended.
    posts = [
        ("cont1", reply_record("Second segment.", "2025-03-01T12:01:00.000Z",
                               "root1", "root1")),
    ]
    thoughts, stats = build_thoughts(posts, "eve.gd", DID, {"root1"})
    assert thoughts == []
    assert stats["replies"] == 1


def test_pruned_announcement_drops_its_whole_thread():
    posts = [
        ("root1", make_record(text="https://eve.gd/2026/09/07/x/",
                              createdAt="2025-03-01T12:00:00.000Z")),
        ("cont1", reply_record("More on that.", "2025-03-01T12:01:00.000Z",
                               "root1", "root1")),
    ]
    thoughts, stats = build_thoughts(posts, "eve.gd", DID, set())
    assert thoughts == []
    assert stats["announcements"] == 1


def test_thread_continuation_images_merge_into_the_root():
    embed = {
        "$type": "app.bsky.embed.images",
        "images": [{"alt": "late image",
                    "image": {"mimeType": "image/png",
                              "ref": {"$link": "bafylate"}}}],
    }
    posts = [
        ("root1", make_record(text="Part one.",
                              createdAt="2025-03-01T12:00:00.000Z")),
        ("cont1", reply_record("Part two.", "2025-03-01T12:01:00.000Z",
                               "root1", "root1")),
    ]
    posts[1][1]["embed"] = embed
    thoughts, _ = build_thoughts(posts, "eve.gd", DID, set())
    assert thoughts[0]["image_blobs"] == [
        {"cid": "bafylate", "mime": "image/png", "alt": "late image"}
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
