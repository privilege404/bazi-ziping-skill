import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RULE_FILE = ROOT / "references" / "rules" / "core-structure.jsonl"


def test_core_structure_rule_cards_cover_health_fact_predicates():
    cards = [json.loads(line) for line in RULE_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_id = {card["id"]: card for card in cards}
    expected = {
        "health-facts-wuxing-body-correspondence-001",
        "health-facts-imbalance-context-001",
        "health-facts-cold-heat-dry-wet-001",
        "health-facts-transit-disruption-001",
        "health-facts-storage-mass-context-001",
        "health-facts-severity-calibration-001",
        "health-facts-body-system-strength-001",
        "health-facts-multi-system-weakness-001",
        "health-facts-surgery-body-part-context-001",
        "health-facts-annual-activation-001",
    }

    assert expected.issubset(by_id)
    for rule_id in expected:
        card = by_id[rule_id]
        assert "health_facts" in card["applies_to"]
        assert "medical diagnosis" in card["caveat"]
