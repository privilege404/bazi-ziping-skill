from __future__ import annotations

from typing import Any

from bazi_shaoweihua.engine import BirthInput, build_chart
from bazi_shaoweihua.reading import build_natal_reading
from bazi_shaoweihua.report import build_report
from bazi_shaoweihua.structure import analyze_structure


TOPICS = {
    "overview": ("overall_luck", "整体节奏"),
    "career": ("career_official", "事业与工作"),
    "wealth": ("wealth", "财务与资源"),
    "relationship": ("marriage_relationship", "关系与亲密感"),
    "education": ("education", "学历与学习"),
    "health": ("health", "健康与生活节奏"),
    "family": ("six_relatives", "家庭与六亲"),
}

SIGNAL_FIELDS = (
    "kind", "ten_god", "score", "level", "name", "external",
    "ganzhi", "year", "annual", "role", "theme", "status",
)


def build_context(
    birth: BirthInput,
    *,
    target_year: int,
    topic: str = "overview",
    question: str = "",
) -> dict[str, Any]:
    if topic not in TOPICS:
        raise ValueError(f"unsupported topic: {topic}")

    chart = build_chart(birth, target_year=target_year)
    structure = analyze_structure(chart)
    report = build_report(chart, structure)
    reading = build_natal_reading(chart, structure, report)

    engine_topic, label = TOPICS[topic]
    topics = (reading.get("life_topics") or {}).get("topics") or []
    topic_index, selected = next(
        ((index, item) for index, item in enumerate(topics) if item.get("topic") == engine_topic),
        (None, {}),
    )
    natal_signals = selected.get("natal_signals") or []
    transit_signals = selected.get("transit_signals") or []
    pillars = chart.get("pillars") or {}
    current_luck = (chart.get("luck") or {}).get("current_cycle") or {}
    annual = chart.get("annual") or {}
    top_ten_gods = (reading.get("ten_god_influence") or {}).get("top_ten_gods") or []
    strength = reading.get("strength") or {}

    return {
        "version": "2.0",
        "question": question,
        "chart": {
            "pillars": {key: (pillars.get(key) or {}).get("ganzhi") for key in ("year", "month", "day", "hour")},
            "day_master": chart.get("day_master"),
            "day_boundary": chart.get("day_boundary"),
            "timezone_offset": (chart.get("input") or {}).get("timezone_offset"),
            "solar_time_mode": (chart.get("input") or {}).get("solar_time_mode"),
            "current_luck": {
                key: current_luck.get(key)
                for key in ("ganzhi", "start_year", "end_year")
            },
            "annual": {key: annual.get(key) for key in ("target_year", "ganzhi")},
        },
        "core": {
            "strength": {
                "classification": strength.get("classification"),
                "source": "reading.strength.classification",
                "limit": strength.get("caveat"),
            },
            "top_ten_gods": [
                {
                    "ten_god": item.get("ten_god"),
                    "level": item.get("level") or item.get("influence_level"),
                    "source": f"reading.ten_god_influence.top_ten_gods[{index}]",
                }
                for index, item in enumerate(top_ten_gods[:3])
            ],
        },
        "topic": {
            "id": topic,
            "label": label,
            "source_topic": engine_topic,
            "natal_signals": _compact_signals(natal_signals, 5, "natal_signals", topic_index),
            "transit_signals": _compact_signals(transit_signals, 3, "transit_signals", topic_index),
            "risk_flags": list(selected.get("risk_flags") or [])[:3],
            "limits": list(selected.get("limits") or []),
        },
        "interpretation_limits": [
            "四柱和干支是计算结果；旺衰、格局、专题信号是有边界的命理解释。",
            "专题信号不能证明学历、疾病、婚姻状态、财富或某件事已经发生。",
            "缺少出生时辰或准确时区时，不应补造时柱。",
        ],
    }


def _compact_signals(
    signals: list[dict[str, Any]],
    limit: int,
    field: str,
    topic_index: int | None,
) -> list[dict[str, Any]]:
    result = []
    for index, signal in enumerate(signals[:limit]):
        if not isinstance(signal, dict):
            continue
        compact = {key: signal[key] for key in SIGNAL_FIELDS if key in signal}
        compact["source"] = f"reading.life_topics.topics[{topic_index}].{field}[{index}]"
        result.append(compact)
    return result
