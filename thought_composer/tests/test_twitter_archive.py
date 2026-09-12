
from thought_composer.twitter_archive import (
    build_tweet_thoughts,
    existing_tweet_ids,
    expand_tco,
    media_files,
    parse_created_at,
    strip_js_preamble,
)

OWN_ID = "12345"


def make_tweet(tweet_id, text, created="Wed Aug 27 13:08:45 +0000 2008",
               **overrides):
    tweet = {
        "id_str": tweet_id,
        "full_text": text,
        "created_at": created,
        "entities": {},
    }
    tweet.update(overrides)
    return tweet


# --- archive file parsing ----------------------------------------------------


def test_strip_js_preamble_returns_the_json_payload():
    payload = 'window.YTD.tweets.part0 = [\n  {"tweet": {"id_str": "1"}}\n]'
    assert strip_js_preamble(payload) == [{"tweet": {"id_str": "1"}}]


def test_parse_created_at_converts_to_local_time():
    parsed = parse_created_at("Wed Aug 27 13:08:45 +0000 2008")
    assert parsed.year == 2008
    assert parsed.tzinfo is not None
    assert parsed.utcoffset() is not None


# --- t.co expansion ----------------------------------------------------------


def test_urls_are_expanded_and_media_stubs_removed():
    entities = {
        "urls": [
            {"url": "https://t.co/abc", "expanded_url": "https://example.org/full"}
        ],
        "media": [{"url": "https://t.co/img"}],
    }
    text = "read https://t.co/abc please https://t.co/img"
    assert expand_tco(text, entities) == "read https://example.org/full please"


def test_text_without_entities_passes_through():
    assert expand_tco("plain words", None) == "plain words"
    assert expand_tco("plain words", {}) == "plain words"


# --- media ------------------------------------------------------------------


def test_media_files_use_the_archive_naming_convention():
    tweet = make_tweet("99", "with pic", extended_entities={
        "media": [
            {"type": "photo",
             "media_url_https": "https://pbs.twimg.com/media/AbC12.jpg"},
            {"type": "video",
             "media_url_https": "https://pbs.twimg.com/media/Vid.mp4"},
        ]
    })
    (photo,) = media_files(tweet)
    assert photo == {"name": "99-AbC12.jpg", "mime": "image/jpeg", "alt": ""}


# --- thread and filter rules -------------------------------------------------


def reply_tweet(tweet_id, text, parent_id, reply_user=OWN_ID, **overrides):
    return make_tweet(
        tweet_id, text,
        in_reply_to_status_id_str=parent_id,
        in_reply_to_user_id_str=reply_user,
        **overrides,
    )


def test_plain_tweets_become_thoughts():
    thoughts, _stats = build_tweet_thoughts(
        [make_tweet("1", "An ancient thought")], "martin_eve", OWN_ID, set()
    )
    (thought,) = thoughts
    assert thought["text"] == "An ancient thought"
    assert thought["twitter"] == "https://twitter.com/martin_eve/status/1"
    assert thought["date"].startswith("2008-08-27T")


def test_retweets_and_mention_openers_are_dropped():
    thoughts, stats = build_tweet_thoughts(
        [
            make_tweet("1", "RT @someone: their words"),
            make_tweet("2", "@someone I disagree entirely"),
        ],
        "martin_eve", OWN_ID, set(),
    )
    assert thoughts == []
    assert stats["retweets"] == 1
    assert stats["replies"] == 1


def test_replies_to_others_are_dropped():
    thoughts, stats = build_tweet_thoughts(
        [reply_tweet("2", "no, wrong", "1", reply_user="999")],
        "martin_eve", OWN_ID, set(),
    )
    assert thoughts == []
    assert stats["replies"] == 1


def test_self_threads_append_to_the_root_chronologically():
    tweets = [
        make_tweet("1", "Part one.", created="Wed Aug 27 13:00:00 +0000 2008"),
        reply_tweet("3", "Part three.", "2",
                    created="Wed Aug 27 13:02:00 +0000 2008"),
        reply_tweet("2", "Part two.", "1",
                    created="Wed Aug 27 13:01:00 +0000 2008"),
    ]
    thoughts, stats = build_tweet_thoughts(tweets, "martin_eve", OWN_ID, set())
    (thought,) = thoughts
    assert thought["text"] == "Part one.\n\nPart two.\n\nPart three."
    assert thought["twitter"].endswith("/status/1")
    assert stats["threaded"] == 2


def test_broken_chains_and_chains_rooted_in_conversations_are_dropped():
    tweets = [
        # parent tweet absent from the archive entirely
        reply_tweet("2", "orphan continuation", "404"),
        # chain roots in a reply to someone else
        reply_tweet("10", "@other actually…", "9", reply_user="999"),
        reply_tweet("11", "and another thing", "10"),
    ]
    thoughts, stats = build_tweet_thoughts(tweets, "martin_eve", OWN_ID, set())
    assert thoughts == []
    assert stats["replies"] == 3


def test_blog_announcements_are_pruned_after_tco_expansion():
    entities = {
        "urls": [
            {"url": "https://t.co/xyz",
             "expanded_url": "https://www.martineve.com/2014/01/01/a-post/"}
        ]
    }
    tweets = [
        make_tweet("1", "New blog post: https://t.co/xyz", entities=entities),
    ]
    thoughts, stats = build_tweet_thoughts(tweets, "martin_eve", OWN_ID, set())
    assert thoughts == []
    assert stats["announcements"] == 1


def test_known_tweets_are_skipped():
    thoughts, stats = build_tweet_thoughts(
        [make_tweet("1", "already imported")], "martin_eve", OWN_ID, {"1"}
    )
    assert thoughts == []
    assert stats["known"] == 1


def test_existing_tweet_ids_read_from_twitter_urls():
    thoughts = [
        {"id": "a", "twitter": "https://twitter.com/martin_eve/status/42"},
        {"id": "b", "bluesky": "https://bsky.app/profile/eve.gd/post/xyz"},
    ]
    assert existing_tweet_ids(thoughts) == {"42"}


# --- archive reader ----------------------------------------------------------


def make_archive_dir(tmp_path):
    data = tmp_path / "archive" / "data"
    data.mkdir(parents=True)
    (data / "account.js").write_text(
        'window.YTD.account.part0 = [ {"account": '
        '{"username": "martin_eve", "accountId": "12345"}} ]'
    )
    (data / "tweets.js").write_text(
        'window.YTD.tweets.part0 = [ {"tweet": {"id_str": "1", '
        '"full_text": "one", "created_at": "Wed Aug 27 13:08:45 +0000 2008", '
        '"entities": {}}} ]'
    )
    (data / "tweets-part1.js").write_text(
        'window.YTD.tweets.part1 = [ {"tweet": {"id_str": "2", '
        '"full_text": "two", "created_at": "Thu Aug 28 09:00:00 +0000 2008", '
        '"entities": {}}} ]'
    )
    media = data / "tweets_media"
    media.mkdir()
    (media / "1-pic.jpg").write_bytes(b"jpegbytes")
    return tmp_path / "archive"


def test_archive_reads_account_tweets_and_media_from_a_folder(tmp_path):
    from thought_composer.twitter_archive import Archive

    archive = Archive(make_archive_dir(tmp_path))
    assert archive.account() == ("martin_eve", "12345")
    tweets = archive.tweets()
    assert sorted(t["id_str"] for t in tweets) == ["1", "2"]
    assert archive.read_bytes("data/tweets_media/1-pic.jpg") == b"jpegbytes"


def test_archive_reads_from_a_zip(tmp_path):
    import shutil

    from thought_composer.twitter_archive import Archive

    folder = make_archive_dir(tmp_path)
    zip_path = shutil.make_archive(str(tmp_path / "twitter"), "zip", folder)
    archive = Archive(zip_path)
    assert archive.account()[0] == "martin_eve"
    assert len(archive.tweets()) == 2
    assert archive.read_bytes("data/tweets_media/1-pic.jpg") == b"jpegbytes"
