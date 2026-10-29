from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

from .engine import BirthInput, build_chart
from .reading import build_natal_reading
from .report import build_report
from .structure import analyze_structure


def build_batch_summary(input_path: Path) -> dict:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    cases = payload.get("cases")
    if not isinstance(cases, list):
        raise ValueError("batch input must contain a 'cases' list")
    return {
        "schema_version": "bazi-batch-summary-v1",
        "source": str(input_path),
        "cases": [_summarize_case(item) for item in cases],
    }


def _summarize_case(item: dict) -> dict:
    birth = _birth_from_case(item)
    chart = build_chart(birth, target_year=item.get("target_year"))
    structure = analyze_structure(chart)
    report = build_report(chart, structure)
    reading = build_natal_reading(chart, structure, report)
    synthesis = reading["synthesis"]
    transit = reading["transit"]
    return {
        "case_id": item["case_id"],
        "pillars": _pillar_text(chart),
        "day_master": chart["day_master"],
        "strength": _strength_summary(reading),
        "pattern": _pattern_summary(reading),
        "transit": _transit_summary(transit),
        "life_topics": _life_topics_summary(reading["life_topics"]),
        "synthesis_topics": [entry["topic"] for entry in synthesis["conclusions"]],
        "limits": [
            "Batch summaries are compact review records; use the reading command for full evidence.",
            "Private birth data should be read from ignored local files, not committed skill assets.",
        ],
    }


def _life_topics_summary(life_topics: dict) -> list[dict]:
    return [
        {
            "topic": item["topic"],
            "natal_signal_count": len(item["natal_signals"]),
            "transit_signal_count": len(item["transit_signals"]),
            "risk_flags": item["risk_flags"][:5],
            "rule_ids": item["rule_ids"],
        }
        for item in life_topics["topics"]
    ]


def _birth_from_case(item: dict) -> BirthInput:
    dt = datetime.fromisoformat(item["datetime"])
    return BirthInput(
        year=dt.year,
        month=dt.month,
        day=dt.day,
        hour=dt.hour,
        minute=dt.minute,
        second=dt.second,
        gender=item["gender"],
        day_boundary=item.get("day_boundary", "23:00"),
        timezone_offset=item.get("timezone_offset", 8.0),
        longitude=item.get("longitude"),
        solar_time_mode=item.get("solar_time_mode", "standard"),
    )


def _pillar_text(chart: dict) -> str:
    return " ".join(chart["pillars"][name]["ganzhi"] for name in ["year", "month", "day", "hour"])


def _strength_summary(reading: dict) -> dict:
    strength = reading["strength"]
    audit = reading["strength_audit"]
    return {
        "classification": strength["classification"],
        "heuristic_score": strength["heuristic_score"],
        "season": audit["season"]["assessment"],
        "rooting": audit["rooting"]["assessment"],
    }


def _pattern_summary(reading: dict) -> dict:
    audit = reading["pattern_audit"]
    ge = audit["ge_shen"]
    return {
        "ge_shen": ge["ten_god"],
        "pattern_name": ge["pattern_name"],
        "supports": audit["success_supports"],
        "gaps": audit["condition_gaps"],
        "warnings": audit["clarity_warnings"],
    }


def _transit_summary(transit: dict) -> dict:
    luck = transit["current_luck"]
    annual = transit["annual"]
    return {
        "target_year": transit["target_year"],
        "current_luck": luck["ganzhi"] if luck else None,
        "annual": annual["ganzhi"],
        "focus_ten_gods": transit["focus_ten_gods"],
        "shensha_triggers": transit["shensha_triggers"],
        "storage_triggers": transit["storage_triggers"],
        "relation_triggers": [
            {
                "type": item["type"],
                "name": item["name"],
                "external": item["external"],
                "target": item["target"],
            }
            for item in transit["relation_triggers"]
        ],
    }
