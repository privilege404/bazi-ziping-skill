import json
import subprocess
import sys
from pathlib import Path

from bazi_shaoweihua.engine import BirthInput, build_chart
from bazi_shaoweihua.health_facts import build_health_facts
from bazi_shaoweihua.reading import build_natal_reading
from bazi_shaoweihua.report import build_report
from bazi_shaoweihua.structure import analyze_structure


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SYSTEMS = {
    "urinary_reproductive",
    "respiratory",
    "digestive",
    "cardio",
    "head_neuro",
    "tumor_mass",
    "injury_surgery",
}


def _reading_for(birth: BirthInput, target_year: int = 2026):
    chart = build_chart(birth, target_year=target_year)
    structure = analyze_structure(chart)
    report = build_report(chart, structure)
    return chart, structure, build_natal_reading(chart, structure, report)


def test_health_facts_have_fixed_categories_evidence_and_limits():
    chart, structure, reading = _reading_for(BirthInput(1970, 5, 23, 18, 0, 0, "male"), target_year=2021)

    facts = build_health_facts(chart, structure, reading)

    assert facts["version"] == "health-facts-v1"
    assert {item["id"] for item in facts["body_system_signals"]} == EXPECTED_SYSTEMS
    for section_name in ["body_system_signals", "pathology_context", "severity", "injury_surgery_context"]:
        assert facts[section_name]
        for item in facts[section_name]:
            assert item["support"] or item["counter"]
            assert item["source_facts"]
            assert item["rule_ids"]
            assert item["limits"]
            text = json.dumps(item, ensure_ascii=False)
            assert "患" not in text
            assert "诊断" not in text
    assert facts["decision_policy"] == "health_facts are symbolic risk signals, not medical diagnosis"


def test_health_facts_include_supported_body_system_from_element_imbalance_or_transit():
    chart, structure, reading = _reading_for(BirthInput(2021, 1, 10, 8, 30, 0, "female"), target_year=2026)

    facts = build_health_facts(chart, structure, reading)
    by_id = {item["id"]: item for item in facts["body_system_signals"]}

    assert any(by_id[system]["support"] for system in EXPECTED_SYSTEMS)
    assert any(item["id"] == "injury_surgery" and item["support"] for item in facts["injury_surgery_context"])


def test_health_facts_include_conservative_strength_weakness_surgery_and_annual_layers():
    chart, structure, reading = _reading_for(BirthInput(2004, 12, 12, 9, 45, 0, "male"), target_year=2026)

    facts = build_health_facts(chart, structure, reading)

    strength = facts["body_system_strength"]
    expected_ranked = {"urinary_reproductive", "digestive", "respiratory", "cardio", "head_neuro"}
    assert {item["id"] for item in strength} == expected_ranked
    assert [item["rank"] for item in strength] == list(range(1, len(strength) + 1))
    assert all("signal_strength" in item for item in strength)
    assert all(item["support"] or item["counter"] for item in strength)
    assert all(item["rule_ids"] and item["limits"] and item["source_facts"] for item in strength)

    multi = facts["multi_system_weakness"]
    assert multi["id"] == "multi_system_weakness"
    assert multi["level"] in {"not_observed", "mild_symbolic_pressure", "multi_system_symbolic_pressure"}
    assert multi["support"] or multi["counter"]
    assert multi["rule_ids"] and multi["limits"] and multi["source_facts"]

    surgery = facts["surgery_body_part_context"]
    expected_parts = {"head_neuro", "cardio", "limb_joint", "abdomen_digestive", "urinary_reproductive"}
    assert {item["id"] for item in surgery} == expected_parts
    assert all("body_part_symbolic_signal" in item for item in surgery)
    assert all(item["support"] or item["counter"] for item in surgery)
    assert all(item["rule_ids"] and item["limits"] and item["source_facts"] for item in surgery)

    annual = facts["annual_health_activation"]
    assert annual["target_year"] == 2026
    assert annual["id"] == "annual_health_activation"
    assert annual["support"] or annual["counter"]
    assert annual["rule_ids"] and annual["limits"] and annual["source_facts"]
    assert facts["decision_policy"] == "health_facts are symbolic risk signals, not medical diagnosis"


def test_reading_embeds_health_facts_and_health_topic_references_them():
    _chart, _structure, reading = _reading_for(BirthInput(2004, 12, 12, 9, 45, 0, "male"), target_year=2026)

    assert "health_facts" in reading
    by_topic = {item["topic"]: item for item in reading["life_topics"]["topics"]}
    health = by_topic["health"]

    assert health["health_facts"]["version"] == "health-facts-v1"
    assert health["health_facts"]["body_system_signals"]
    assert "health-facts-wuxing-body-correspondence-001" in health["rule_ids"]


def test_cli_reading_outputs_health_facts():
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "bazi_cli.py"),
            "reading",
            "--datetime",
            "2004-12-12T09:45:00",
            "--gender",
            "male",
            "--target-year",
            "2026",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(result.stdout)

    facts = payload["reading"]["health_facts"]
    assert facts["version"] == "health-facts-v1"
    assert {item["id"] for item in facts["body_system_signals"]} == EXPECTED_SYSTEMS
