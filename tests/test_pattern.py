from bazi_shaoweihua.engine import BirthInput, build_chart
from bazi_shaoweihua.pattern import analyze_pattern
from bazi_shaoweihua.structure import analyze_structure


def _pattern_for(birth: BirthInput):
    chart = build_chart(birth, target_year=2026)
    structure = analyze_structure(chart)
    return analyze_pattern(chart, structure)


def test_sample_one_identifies_month_command_primary_qi_and_transmitted_official_signal():
    pattern = _pattern_for(BirthInput(2002, 9, 2, 18, 0, 0, "male"))

    assert pattern["month_command"] == {
        "branch": "申",
        "main_stem": "庚",
        "main_ten_god": "正印",
    }
    assert pattern["primary_candidate"]["name"] == "正印格候选"
    assert pattern["primary_candidate"]["status"] == "candidate"
    assert {"pillar": "month", "stem": "戊", "ten_god": "正官"} in pattern["transmitted_ten_gods"]
    assert any(item["name"] == "官印相生候选" for item in pattern["combination_candidates"])


def test_sample_two_marks_officer_and_killing_mixed_with_killing_rooted_in_month_command():
    pattern = _pattern_for(BirthInput(2002, 6, 22, 18, 0, 0, "female"))

    assert pattern["month_command"]["main_ten_god"] == "七杀"
    assert pattern["primary_candidate"]["name"] == "七杀格候选"
    assert {"pillar": "month", "stem": "丙", "ten_god": "正官"} in pattern["transmitted_ten_gods"]
    assert {"pillar": "hour", "stem": "丁", "ten_god": "七杀"} in pattern["transmitted_ten_gods"]
    assert "官杀并见" in pattern["warnings"]


def test_sample_three_marks_partial_seal_and_killing_seal_candidate_without_finalizing_pattern():
    pattern = _pattern_for(BirthInput(2004, 12, 12, 9, 45, 0, "male"))

    assert pattern["month_command"]["main_ten_god"] == "偏印"
    assert pattern["primary_candidate"]["name"] == "偏印格候选"
    assert {"pillar": "hour", "stem": "辛", "ten_god": "七杀"} in pattern["transmitted_ten_gods"]
    assert any(item["name"] == "杀印相生候选" for item in pattern["combination_candidates"])
    assert pattern["decision"] == "候选格局，待旺衰、调候、清浊复核"
