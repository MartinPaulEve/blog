# Behaviour tests for the TIL selection and rewrite (/til/): only
# thoughts beginning "TIL:" are selected; the displayed text loses the
# prefix, and a leading "about"/"that" goes too with the next word
# capitalised; the stored entries are never mutated. Run with:
#   ruby _tests/til_filter_test.rb
require "minitest/autorun"
require_relative "../_plugins/thoughts"

class TilFilterTest < Minitest::Test
  def test_til_recognises_the_prefix
    assert ThoughtsFilter.til?("TIL: bats are mammals")
  end

  def test_til_rejects_other_text
    refute ThoughtsFilter.til?("Today I learned nothing")
    refute ThoughtsFilter.til?("A post mentioning TIL: midway through")
  end

  def test_strip_removes_prefix_and_that_and_capitalises
    assert_equal "The mating cycle of bats is regular",
                 ThoughtsFilter.til_strip("TIL: that the mating cycle of bats is regular")
  end

  def test_strip_removes_prefix_and_about_and_capitalises
    assert_equal "The history of the semicolon",
                 ThoughtsFilter.til_strip("TIL: about the history of the semicolon")
  end

  def test_strip_leaves_plain_text_untouched_after_prefix
    text = "TIL: Landlock is a security mod for the Linux kernel that " \
           "allows programs to restrict their own network/filesystem axx " \
           "(and other capabilities), at startup, so that if a malicious " \
           "actor runs code in their context, the blast radius is contained."
    assert_equal text.sub("TIL: ", ""), ThoughtsFilter.til_strip(text)
  end

  def test_strip_matches_leader_words_case_insensitively
    assert_equal "Birds can sleep mid-flight",
                 ThoughtsFilter.til_strip("TIL: That birds can sleep mid-flight")
  end

  def test_strip_does_not_treat_word_prefixes_as_leaders
    assert_equal "thatched roofs last decades",
                 ThoughtsFilter.til_strip("TIL: thatched roofs last decades")
    assert_equal "aboutness is a term in philosophy",
                 ThoughtsFilter.til_strip("TIL: aboutness is a term in philosophy")
  end

  def test_strip_copes_with_a_missing_space_after_the_colon
    assert_equal "no space here", ThoughtsFilter.til_strip("TIL:no space here")
  end

  def test_strip_only_touches_the_opening_of_multiline_text
    out = ThoughtsFilter.til_strip("TIL: that fact one\n\nabout something else")
    assert_equal "Fact one\n\nabout something else", out
  end

  def test_entries_selects_and_rewrites_tils_only
    thoughts = [
      { "id" => "1", "text" => "TIL: that bats are mammals", "date" => "2026-09-12" },
      { "id" => "2", "text" => "Just a normal thought", "date" => "2026-09-11" },
      { "id" => "3", "text" => "TIL: Landlock exists", "date" => "2026-09-10" }
    ]
    out = ThoughtsFilter.til_entries(thoughts)
    assert_equal %w[1 3], out.map { |t| t["id"] }
    assert_equal "Bats are mammals", out[0]["text"]
    assert_equal "Landlock exists", out[1]["text"]
    assert_equal "2026-09-12", out[0]["date"]
  end

  def test_entries_does_not_mutate_the_stored_data
    thoughts = [{ "id" => "1", "text" => "TIL: that bats are mammals" }]
    ThoughtsFilter.til_entries(thoughts)
    assert_equal "TIL: that bats are mammals", thoughts[0]["text"]
  end

  def test_entries_handles_nil
    assert_equal [], ThoughtsFilter.til_entries(nil)
  end
end
