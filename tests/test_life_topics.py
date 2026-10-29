from bazi_shaoweihua.engine import BirthInput, build_chart
from bazi_shaoweihua.reading import build_natal_reading
from bazi_shaoweihua.report import build_report
from bazi_shaoweihua.structure import analyze_structure
from bazi_shaoweihua.topics import _targeted_transit_relations


def _reading_for(birth: BirthInput):
    chart = build_chart(birth, target_year=2026)
    structure = analyze_structure(chart)
    report = build_report(chart, structure)
    return build_natal_reading(chart, structure, report)


def test_reading_contains_life_topics_with_evidence_rules_and_limits():
    reading = _reading_for(BirthInput(2002, 6, 22, 18, 0, 0, "female"))

    topics = reading["life_topics"]
    assert topics["version"] == "life-topics-mvp-1"
    assert [item["topic"] for item in topics["topics"]] == [
        "overall_luck",
        "birth_family",
        "education",
        "wealth",
        "career_official",
        "marriage_relationship",
        "health",
        "children",
        "six_relatives",
        "major_events",
    ]
    for item in topics["topics"]:
        assert item["natal_signals"]
        assert "transit_signals" in item
        assert item["rule_ids"]
        assert item["limits"]
        assert item["decision_policy"] == "只列可计算证据和触发，不脱离本命事实直接断吉凶。"


def test_wealth_and_career_topics_use_ten_god_and_transit_facts():
    wealth_reading = _reading_for(BirthInput(2004, 12, 12, 9, 45, 0, "male"))
    by_topic = {item["topic"]: item for item in wealth_reading["life_topics"]["topics"]}

    wealth = by_topic["wealth"]
    assert any(signal["ten_god"] in {"正财", "偏财"} for signal in wealth["natal_signals"])
    assert any(signal["ten_god"] in {"正财", "偏财"} for signal in wealth["transit_signals"])
    assert "topic-wealth-mvp-001" in wealth["rule_ids"]

    career_reading = _reading_for(BirthInput(2002, 6, 22, 18, 0, 0, "female"))
    by_topic = {item["topic"]: item for item in career_reading["life_topics"]["topics"]}
    career = by_topic["career_official"]
    assert any(signal["ten_god"] in {"正官", "七杀"} for signal in career["natal_signals"])
    assert any("七杀" in flag or "官杀" in flag for flag in career["risk_flags"])
    assert "topic-career-official-mvp-001" in career["rule_ids"]


def test_marriage_health_and_children_topics_have_domain_specific_triggers():
    reading = _reading_for(BirthInput(2004, 12, 12, 9, 45, 0, "male"))
    by_topic = {item["topic"]: item for item in reading["life_topics"]["topics"]}

    marriage = by_topic["marriage_relationship"]
    assert any(signal["kind"] == "spouse_star" for signal in marriage["natal_signals"])
    assert any(signal.get("target") == "day" for signal in marriage["transit_signals"])

    health = by_topic["health"]
    assert any("调候" in flag or "刑冲害破" in flag for flag in health["risk_flags"])
    assert any(signal.get("type") in {"six_clash", "six_harm", "punishment", "stem_control"} for signal in health["transit_signals"])

    children = by_topic["children"]
    assert any(signal["ten_god"] in {"食神", "伤官"} for signal in children["natal_signals"])
    assert "topic-children-mvp-001" in children["rule_ids"]


def test_birth_family_education_and_six_relatives_are_present():
    reading = _reading_for(BirthInput(2002, 9, 2, 18, 0, 0, "male"))
    by_topic = {item["topic"]: item for item in reading["life_topics"]["topics"]}

    birth_family = by_topic["birth_family"]
    assert any(signal["kind"] == "family_palace" and signal["pillar"] in {"year", "month"} for signal in birth_family["natal_signals"])
    assert any(signal.get("ten_god") in {"正印", "偏印", "正财", "偏财"} for signal in birth_family["natal_signals"])
    assert "topic-birth-family-mvp-001" in birth_family["rule_ids"]

    education = by_topic["education"]
    assert any(signal.get("ten_god") in {"正印", "偏印", "食神", "伤官"} for signal in education["natal_signals"])
    assert any(signal.get("name") in {"文昌", "天乙贵人", "天德贵人", "月德贵人"} for signal in education["natal_signals"])
    assert "topic-education-mvp-001" in education["rule_ids"]

    six_relatives = by_topic["six_relatives"]
    relations = {signal["relative"] for signal in six_relatives["natal_signals"]}
    assert {"parents_family", "siblings_peers", "spouse", "children"}.issubset(relations)
    assert "topic-six-relatives-mvp-001" in six_relatives["rule_ids"]


def test_major_events_topic_scans_nearby_years_with_trigger_reasons():
    reading = _reading_for(BirthInput(2004, 12, 12, 9, 45, 0, "male"))
    by_topic = {item["topic"]: item for item in reading["life_topics"]["topics"]}
    major_events = by_topic["major_events"]

    assert major_events["transit_signals"]
    years = {signal["year"] for signal in major_events["transit_signals"]}
    assert 2026 in years
    assert all("score" in signal and "themes" in signal and "trigger_names" in signal for signal in major_events["transit_signals"])
    assert any("day_pillar" in signal["themes"] or "month_pillar" in signal["themes"] for signal in major_events["transit_signals"])
    assert "topic-major-events-mvp-001" in major_events["rule_ids"]


def test_targeted_transit_relations_accepts_list_targets():
    transit = {
        "relation_triggers": [
            {"type": "six_clash", "target": ["month", "day"], "name": "sample"},
            {"type": "six_harmony", "target": "hour", "name": "ignored"},
        ]
    }

    result = _targeted_transit_relations(transit, {"day"})

    assert result == [{"type": "six_clash", "target": ["month", "day"], "name": "sample"}]


def test_targeted_transit_relations_ignores_non_matching_list_targets():
    transit = {
        "relation_triggers": [
            {"type": "six_clash", "target": ["month", "year"], "name": "ignored"},
        ]
    }

    result = _targeted_transit_relations(transit, {"day"})

    assert result == []
