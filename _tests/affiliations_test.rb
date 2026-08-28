# Behaviour tests for the date-aware print-cover affiliations: given a
# document date, Affiliations.for_date must return the affiliation entries in
# force at that time, in display order, with Liquid-readable string keys.
require "minitest/autorun"
require_relative "../_plugins/affiliations"

class AffiliationsTest < Minitest::Test
  BIRKBECK_PROF = {
    "role" => "Professor of Literature, Technology and Publishing",
    "institution" => "Birkbeck, University of London",
  }.freeze

  def test_no_affiliation_before_2009
    assert_equal [], Affiliations.for_date(Date.new(2007, 5, 15))
    assert_equal [], Affiliations.for_date(Date.new(2008, 12, 31))
  end

  def test_sussex_alone_from_2009_to_end_2012
    expected = [{ "institution" => "University of Sussex" }]
    assert_equal expected, Affiliations.for_date(Date.new(2009, 1, 1))
    assert_equal expected, Affiliations.for_date(Date.new(2012, 12, 31))
  end

  def test_sussex_entry_has_no_role
    entry = Affiliations.for_date(Date.new(2010, 6, 1)).first
    refute entry.key?("role")
  end

  def test_lincoln_lecturer_from_2013_to_end_2014
    expected = [
      {
        "role" => "Lecturer in English",
        "institution" => "University of Lincoln",
      },
    ]
    assert_equal expected, Affiliations.for_date(Date.new(2013, 1, 1))
    assert_equal expected, Affiliations.for_date(Date.new(2014, 12, 31))
  end

  def test_birkbeck_senior_lecturer_during_2015
    expected = [
      {
        "role" => "Senior Lecturer in Literature, Technology and Publishing",
        "institution" => "Birkbeck, University of London",
      },
    ]
    assert_equal expected, Affiliations.for_date(Date.new(2015, 1, 1))
    assert_equal expected, Affiliations.for_date(Date.new(2015, 12, 31))
  end

  def test_birkbeck_professor_alone_from_2016_to_end_2022
    assert_equal [BIRKBECK_PROF], Affiliations.for_date(Date.new(2016, 1, 1))
    assert_equal [BIRKBECK_PROF], Affiliations.for_date(Date.new(2022, 12, 31))
  end

  def test_birkbeck_plus_crossref_during_2023_and_2024
    expected = [
      BIRKBECK_PROF,
      { "role" => "Principal R&D Developer", "institution" => "Crossref" },
    ]
    assert_equal expected, Affiliations.for_date(Date.new(2023, 1, 1))
    assert_equal expected, Affiliations.for_date(Date.new(2024, 12, 31))
  end

  def test_birkbeck_plus_msu_technical_lead_from_2025_to_may_2026
    expected = [
      BIRKBECK_PROF,
      {
        "role" => "Technical Lead of Knowledge Commons",
        "institution" => "Michigan State University",
      },
    ]
    assert_equal expected, Affiliations.for_date(Date.new(2025, 1, 1))
    assert_equal expected, Affiliations.for_date(Date.new(2026, 5, 31))
  end

  def test_birkbeck_plus_msu_associate_director_from_june_2026
    expected = [
      BIRKBECK_PROF,
      {
        "role" => "Associate Director of Knowledge Commons",
        "institution" => "Michigan State University",
      },
    ]
    assert_equal expected, Affiliations.for_date(Date.new(2026, 6, 1))
    assert_equal expected, Affiliations.for_date(Date.new(2030, 1, 1))
  end

  def test_birkbeck_always_listed_first_in_dual_affiliations
    [2023, 2025, 2027].each do |year|
      entries = Affiliations.for_date(Date.new(year, 7, 1))
      assert_equal 2, entries.length
      assert_equal "Birkbeck, University of London",
                   entries.first["institution"]
    end
  end

  def test_accepts_time_objects
    assert_equal [BIRKBECK_PROF],
                 Affiliations.for_date(Time.utc(2020, 3, 14, 9, 26))
  end

  def test_nil_date_means_now
    assert_equal Affiliations.for_date(Date.today), Affiliations.for_date(nil)
  end
end
