from thought_composer.text import (
    BLUESKY_LIMIT,
    MASTODON_LIMIT,
    find_links,
    grapheme_length,
    mastodon_length,
    split_thread,
    split_thread_mastodon,
    status_line,
)

# --- counting --------------------------------------------------------------


def test_plain_ascii_counts_characters():
    assert grapheme_length("hello world") == 11


def test_combining_characters_count_once():
    assert grapheme_length("café") == 4  # e + combining acute


def test_zwj_emoji_family_counts_once():
    assert grapheme_length("\U0001F468‍\U0001F469‍\U0001F467") == 1


def test_mastodon_counts_urls_as_23():
    url = "https://example.org/a/very/long/path/indeed/it/is"
    text = f"see {url} now"
    assert mastodon_length(text) == len("see ") + 23 + len(" now")
    assert mastodon_length("no links here") == 13


# --- link detection --------------------------------------------------------


def test_finds_url_with_byte_offsets():
    text = "read https://example.org/x today"
    (link,) = find_links(text)
    assert link["url"] == "https://example.org/x"
    assert link["byte_start"] == 5
    assert link["byte_end"] == 5 + len("https://example.org/x")


def test_byte_offsets_after_multibyte_characters():
    text = "café → https://example.org/x"
    (link,) = find_links(text)
    prefix_bytes = len("café → ".encode())
    assert link["byte_start"] == prefix_bytes
    assert text.encode("utf-8")[link["byte_start"]:link["byte_end"]] == (
        b"https://example.org/x"
    )


def test_trailing_punctuation_is_not_part_of_the_url():
    (link,) = find_links("go to https://example.org/x.")
    assert link["url"] == "https://example.org/x"
    (link,) = find_links("(see https://example.org/x)")
    assert link["url"] == "https://example.org/x"


def test_multiple_links_in_order():
    urls = [x["url"] for x in find_links(
        "a https://one.example b http://two.example c"
    )]
    assert urls == ["https://one.example", "http://two.example"]


# --- thread splitting ------------------------------------------------------


def test_short_text_is_a_single_untouched_segment():
    text = "Just a small thought, with a line\nbreak kept intact."
    assert split_thread(text) == [text]


def test_long_text_splits_within_limits_without_altering_words():
    words = " ".join(f"word{i}" for i in range(80))
    segments = split_thread(words)
    assert len(segments) > 1
    for segment in segments:
        assert grapheme_length(segment) <= BLUESKY_LIMIT
    assert "".join(words.split()) == "".join(
        "".join(segment.split()) for segment in segments
    )


def test_split_prefers_a_paragraph_break():
    first = "A" * 200
    second = "B" * 200
    segments = split_thread(f"{first}\n\nAnd then {second}")
    assert segments[0] == first
    assert segments[1] == f"And then {second}"


def test_single_oversized_token_is_hard_split():
    token = "x" * 700
    segments = split_thread(token)
    assert [len(s) for s in segments] == [300, 300, 100]
    assert "".join(segments) == token


def test_no_counters_or_ellipses_are_added():
    words = " ".join(f"word{i}" for i in range(80))
    for segment in split_thread(words):
        assert "…" not in segment
        assert "/" not in segment  # no "1/3" style markers


# --- Mastodon thread splitting ---------------------------------------------


def test_text_over_bluesky_but_under_mastodon_stays_whole_for_mastodon():
    words = " ".join(f"word{i}" for i in range(80))  # ~550 chars
    assert len(split_thread(words)) > 1
    assert split_thread_mastodon(words) == [words]


def test_mastodon_split_respects_its_own_limit():
    words = " ".join(f"word{i}" for i in range(300))  # well over 1000 chars
    segments = split_thread_mastodon(words)
    assert len(segments) > 1
    for segment in segments:
        assert mastodon_length(segment) <= MASTODON_LIMIT
    assert "".join(words.split()) == "".join(
        "".join(segment.split()) for segment in segments
    )


def test_mastodon_split_counts_urls_as_23():
    url = "https://example.org/" + "a" * 600
    text = f"see {url} for details"
    assert split_thread_mastodon(text) == [text]


def test_mastodon_single_oversized_token_is_hard_split():
    token = "x" * 1500
    segments = split_thread_mastodon(token)
    assert [len(s) for s in segments] == [1000, 500]
    assert "".join(segments) == token


# --- status line -----------------------------------------------------------


def test_status_line_fits_one_post():
    line = status_line("hello")
    assert "5/300" in line
    assert "1 post" in line


def test_status_line_announces_threading():
    line = status_line(" ".join(f"word{i}" for i in range(80)))
    assert "thread" in line.lower()


def test_status_line_shows_each_service_count_when_threading():
    line = status_line(" ".join(f"word{i}" for i in range(80)))
    assert "2 posts on Bluesky" in line
    assert "1 post on Mastodon" in line


def test_status_line_counts_mastodon_thread_too():
    line = status_line(" ".join(f"word{i}" for i in range(300)))
    assert "on Bluesky" in line
    assert "3 posts on Mastodon" in line


def test_status_line_counts_images():
    assert "2 image" in status_line("hi", images=2)
