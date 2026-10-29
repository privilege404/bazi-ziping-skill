import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RULE_FILE = ROOT / "references" / "rules" / "core-structure.jsonl"


def test_core_structure_rule_cards_are_valid_jsonl_with_unique_ids():
    cards = [json.loads(line) for line in RULE_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]

    assert len(cards) >= 8
    assert len({card["id"] for card in cards}) == len(cards)
    for card in cards:
        assert card["id"]
        assert card["source"]
        assert card["topic"]
        assert isinstance(card["conditions"], dict)
        assert card["claim"]
        assert card["applies_to"]
        assert isinstance(card["priority"], int)
        assert card["caveat"]


def test_core_structure_rule_cards_cover_minimum_fact_types():
    cards = [json.loads(line) for line in RULE_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    topics = {card["topic"] for card in cards}

    assert "月令" in topics
    assert "藏干通根" in topics
    assert "墓库" in topics
    assert "合化" in topics
    assert "冲刑害破" in topics
    assert "神煞" in topics
    assert "生克制化" in topics
    assert "十神影响" in topics
    assert "格局复核" in topics
    assert "本命结论" in topics
    assert "岁运" in topics
    assert "调候" in topics
    assert "旺衰复核" in topics
