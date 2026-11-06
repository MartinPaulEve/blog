# Behaviour tests for the /posts/ full-text search index: a post's words
# are the unique, lowercased, Unicode-aware tokens of its rendered body
# and title with markup stripped; the index maps each word to the
# (gap-encoded) positions of the posts containing it. Run with:
#   ruby _tests/posts_search_test.rb
require "minitest/autorun"
require_relative "../_plugins/posts_search"

class PostsSearchTest < Minitest::Test
  def post(url:, title: "Untitled", content: "")
    { "url" => url, "title" => title, "content" => content }
  end

  # --- words ---------------------------------------------------------------

  def test_words_are_lowercased_unique_and_sorted
    assert_equal %w[fox quick the],
                 PostsSearch.words("The quick fox; the QUICK fox.")
  end

  def test_words_strip_markup_and_decode_entities
    html = "<p>Open &amp; <em>shut</em> caf&eacute;</p>"
    assert_equal %w[café open shut], PostsSearch.words(html)
  end

  def test_words_decode_the_latin1_letter_entities_across_the_range
    assert_equal %w[zürich ágil ÿ11],
                 PostsSearch.words("Z&uuml;rich &Aacute;gil &yuml;11 &mdash;")
  end

  def test_words_drop_script_and_style_bodies_entirely
    html = "<style>.a{color:red}</style><p>visible</p>" \
           "<script>var hidden = 1;</script>"
    assert_equal %w[visible], PostsSearch.words(html)
  end

  def test_words_split_on_punctuation_and_keep_unicode_letters_and_digits
    assert_equal %w[2029 ref žižek],
                 PostsSearch.words("Žižek's REF-2029!")
  end

  def test_words_drop_single_characters
    assert_equal %w[be not or to], PostsSearch.words("To be, or not to be: a B")
  end

  def test_words_of_nothing_are_empty
    assert_equal [], PostsSearch.words(nil)
    assert_equal [], PostsSearch.words("")
    assert_equal [], PostsSearch.words("<p></p>")
  end

  # --- delta_encode --------------------------------------------------------

  def test_delta_encode_stores_gaps_between_ascending_positions
    assert_equal [0, 0, 3, 0], PostsSearch.delta_encode([0, 1, 5, 6])
    assert_equal [4], PostsSearch.delta_encode([4])
    assert_equal [], PostsSearch.delta_encode([])
  end

  # --- build_index ---------------------------------------------------------

  def test_build_index_lists_urls_in_the_given_order
    index = PostsSearch.build_index([
      post(url: "/2026/01/01/newest/"),
      post(url: "/2025/01/01/older/"),
    ])
    assert_equal ["/2026/01/01/newest/", "/2025/01/01/older/"], index["u"]
  end

  def test_build_index_maps_each_word_to_gap_encoded_post_positions
    index = PostsSearch.build_index([
      post(url: "/a/", content: "<p>Pynchon and Derrida</p>"),
      post(url: "/b/", content: "<p>Open access</p>"),
      post(url: "/c/", content: "<p>Derrida again</p>"),
    ])
    assert_equal [0, 1], index["w"]["derrida"]
    assert_equal [0], index["w"]["pynchon"]
    assert_equal [1], index["w"]["open"]
    assert_equal [2], index["w"]["again"]
    refute index["w"].key?("a")
  end

  def test_build_index_includes_title_words
    index = PostsSearch.build_index([
      post(url: "/a/", title: "The problem for REF 2029", content: "<p>body</p>"),
    ])
    assert_equal [0], index["w"]["problem"]
    assert_equal [0], index["w"]["2029"]
    assert_equal [0], index["w"]["body"]
  end

  def test_build_index_words_are_sorted
    index = PostsSearch.build_index([
      post(url: "/a/", content: "zebra apple mango"),
    ])
    assert_equal %w[apple mango untitled zebra], index["w"].keys
  end

  def test_build_index_of_nothing_is_empty
    assert_equal({ "u" => [], "w" => {} }, PostsSearch.build_index([]))
    assert_equal({ "u" => [], "w" => {} }, PostsSearch.build_index(nil))
  end
end
