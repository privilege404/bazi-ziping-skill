from __future__ import annotations

from typing import Any


VERSION = "health-facts-v1"
DECISION_POLICY = "health_facts are symbolic risk signals, not medical diagnosis"
LIMITS = [
    "Only symbolic BaZi health-risk correspondences are listed.",
    "Do not read any signal as a medical diagnosis or a claim that a disease will occur.",
    "Body-system labels are engineering predicates for contest-option comparison and need case calibration.",
]
DISRUPTIVE_TYPES = {"six_clash", "six_harm", "six_break", "punishment", "self_punishment", "heavenly_clash", "stem_control"}
SYSTEM_TO_ELEMENTS = {
    "urinary_reproductive": ["水"],
    "respiratory": ["金"],
    "digestive": ["土"],
    "cardio": ["火"],
    "head_neuro": ["木", "火"],
    "tumor_mass": ["土"],
    "injury_surgery": [],
}
BODY_SYSTEM_IDS = [
    "urinary_reproductive",
    "respiratory",
    "digestive",
    "cardio",
    "head_neuro",
    "tumor_mass",
    "injury_surgery",
]
BODY_SYSTEM_STRENGTH_IDS = ["urinary_reproductive", "digestive", "respiratory", "cardio", "head_neuro"]
SURGERY_BODY_PART_TO_SYSTEMS = {
    "head_neuro": ["head_neuro"],
    "cardio": ["cardio"],
    "limb_joint": ["head_neuro", "respiratory"],
    "abdomen_digestive": ["digestive"],
    "urinary_reproductive": ["urinary_reproductive"],
}
ELEMENT_TO_SYSTEMS = {
    "水": ["urinary_reproductive"],
    "土": ["digestive"],
    "金": ["respiratory"],
    "火": ["cardio", "head_neuro"],
    "木": ["head_neuro", "limb_joint"],
}
BRANCH_ELEMENTS = {
    "子": "水",
    "丑": "土",
    "寅": "木",
    "卯": "木",
    "辰": "土",
    "巳": "火",
    "午": "火",
    "未": "土",
    "申": "金",
    "酉": "金",
    "戌": "土",
    "亥": "水",
}
ELEMENT_ALIASES = {
    "姘?": "水",
    "鍦?": "土",
    "閲?": "金",
    "鐏?": "火",
    "鏈?": "木",
}


def build_health_facts(chart: dict[str, Any], structure: dict[str, Any], reading: dict[str, Any]) -> dict[str, Any]:
    context = _context(chart, structure, reading)
    return {
        "version": VERSION,
        "body_system_signals": [_body_system_signal(system_id, context) for system_id in BODY_SYSTEM_IDS],
        "body_system_strength": _body_system_strength(context),
        "multi_system_weakness": _multi_system_weakness(context),
        "surgery_body_part_context": _surgery_body_part_context(context),
        "annual_health_activation": _annual_health_activation(context),
        "pathology_context": _pathology_context(context),
        "severity": _severity_context(context),
        "injury_surgery_context": [_injury_surgery_signal(context)],
        "support": _global_support(context),
        "counter": _global_counter(context),
        "limits": LIMITS,
        "rule_ids": [
            "health-facts-wuxing-body-correspondence-001",
            "health-facts-imbalance-context-001",
            "health-facts-transit-disruption-001",
        ],
        "decision_policy": DECISION_POLICY,
    }


def _context(chart: dict[str, Any], structure: dict[str, Any], reading: dict[str, Any]) -> dict[str, Any]:
    counts = chart.get("element_counts") or reading.get("summary", {}).get("element_counts", {})
    relations = list(structure.get("branch_relations", [])) + list(structure.get("stem_relations", []))
    transit = reading.get("transit", {})
    transit_relations = list(transit.get("relation_triggers", []))
    annual = transit.get("annual") or {}
    current_luck = transit.get("current_luck") or {}
    return {
        "chart": chart,
        "counts": counts,
        "pillars": chart.get("pillars", {}),
        "target_year": transit.get("target_year") or annual.get("target_year"),
        "annual": annual,
        "current_luck": current_luck,
        "month_branch": structure.get("day_master_context", {}).get("month_branch"),
        "weak_elements": [element for element, value in counts.items() if value <= 1],
        "excess_elements": [element for element, value in counts.items() if value >= 4],
        "disruptive_relations": [item for item in relations if item.get("type") in DISRUPTIVE_TYPES],
        "transit_disruptions": [item for item in transit_relations if item.get("type") in DISRUPTIVE_TYPES],
        "storage_triggers": list(transit.get("storage_triggers", [])),
        "storages": structure.get("storages", {}),
        "regulation": reading.get("regulation", {}),
        "has_regulation_gap": reading.get("regulation", {}).get("status") == "not_covered",
    }


def _body_system_signal(system_id: str, context: dict[str, Any]) -> dict[str, Any]:
    support: list[str] = []
    source_facts: list[dict[str, Any]] = []
    for element in SYSTEM_TO_ELEMENTS[system_id]:
        if element in context["weak_elements"]:
            support.append(f"{element} element is sparse, creating a {system_id} symbolic risk signal")
            source_facts.append(_fact("element_weakness", {"element": element, "counts": context["counts"]}))
        if element in context["excess_elements"]:
            support.append(f"{element} element is concentrated, creating a {system_id} symbolic risk signal")
            source_facts.append(_fact("element_excess", {"element": element, "counts": context["counts"]}))
    if system_id == "tumor_mass" and context["storages"]:
        support.append("storage branches are present, so mass/storage symbolism is worth reviewing")
        source_facts.extend(_fact("storage_branch", {"branch": branch, **payload}) for branch, payload in context["storages"].items())
    if system_id == "injury_surgery" and _has_disruption(context):
        support.append("disruptive relation or storage activation gives injury/surgery-context symbolism")
        source_facts.extend(_facts("disruptive_relation", context["disruptive_relations"][:4]))
        source_facts.extend(_facts("transit_disruption", context["transit_disruptions"][:4]))
        source_facts.extend(_facts("storage_trigger", context["storage_triggers"][:4]))
    counter = [] if support else [f"no first-pass {system_id} element, storage, or disruption signal is visible"]
    return _item(
        system_id,
        support,
        counter,
        source_facts,
        ["health-facts-wuxing-body-correspondence-001", "health-facts-imbalance-context-001"],
    )


def _body_system_strength(context: dict[str, Any]) -> list[dict[str, Any]]:
    ranked = []
    for system_id in BODY_SYSTEM_STRENGTH_IDS:
        score, support, counter, source_facts = _system_strength_parts(system_id, context)
        ranked.append(
            {
                **_item(
                    system_id,
                    support,
                    counter,
                    source_facts,
                    [
                        "health-facts-body-system-strength-001",
                        "health-facts-wuxing-body-correspondence-001",
                        "health-facts-imbalance-context-001",
                        "health-facts-transit-disruption-001",
                    ],
                ),
                "signal_strength": round(score, 6),
            }
        )
    ranked.sort(key=lambda item: (-item["signal_strength"], item["id"]))
    for index, item in enumerate(ranked, start=1):
        item["rank"] = index
    return ranked


def _system_strength_parts(system_id: str, context: dict[str, Any]) -> tuple[float, list[str], list[str], list[dict[str, Any]]]:
    score = 0.0
    support: list[str] = []
    counter: list[str] = []
    source_facts: list[dict[str, Any]] = []
    for raw_element in SYSTEM_TO_ELEMENTS.get(system_id, []):
        element = _canonical_element(raw_element)
        count = _element_count(context, element)
        if count <= 1:
            score += 2.0
            support.append(f"{system_id} has sparse-element symbolic pressure from {element}")
            source_facts.append(_fact("element_weakness", {"system": system_id, "element": element, "count": count, "counts": context["counts"]}))
        elif count >= 4:
            score += 2.0
            support.append(f"{system_id} has concentrated-element symbolic pressure from {element}")
            source_facts.append(_fact("element_excess", {"system": system_id, "element": element, "count": count, "counts": context["counts"]}))
        else:
            counter.append(f"{system_id} element {element} is not strongly sparse or concentrated")
            source_facts.append(_fact("element_balance_review", {"system": system_id, "element": element, "count": count, "counts": context["counts"]}))

        if _month_element(context) == element:
            score += 0.5
            support.append(f"month branch carries {element}, so {system_id} needs seasonal review")
            source_facts.append(_fact("month_branch_element", {"month_branch": context.get("month_branch"), "element": element}))

        relation_hits = _relation_hits_for_element(context["disruptive_relations"], element)
        if relation_hits:
            score += min(1.5, len(relation_hits) * 0.5)
            support.append(f"natal disruptive relation touches {element}-related branches for {system_id}")
            source_facts.extend(_facts("disruptive_relation_element_hit", relation_hits[:4]))

        transit_hits = _relation_hits_for_element(context["transit_disruptions"], element)
        if transit_hits:
            score += min(2.0, len(transit_hits) * 0.75)
            support.append(f"luck or annual disruptive relation touches {element}-related branches for {system_id}")
            source_facts.extend(_facts("transit_disruption_element_hit", transit_hits[:4]))

        storage_hits = _storage_hits_for_element(context, element)
        if storage_hits:
            score += min(1.0, len(storage_hits) * 0.5)
            support.append(f"storage symbolism involves {element}, adding conservative review for {system_id}")
            source_facts.extend(_facts("storage_element_hit", storage_hits[:4]))

    if _regulation_mentions_cold_wet(context) and system_id in {"urinary_reproductive", "digestive"}:
        score += 0.5
        support.append(f"regulation warns of cold/wet context; {system_id} is flagged for conservative review")
        source_facts.append(_fact("regulation_context", context.get("regulation", {})))
    return score, _unique(support), _unique(counter if not support else counter[:2]), source_facts


def _multi_system_weakness(context: dict[str, Any]) -> dict[str, Any]:
    strengths = _body_system_strength(context)
    active = [item for item in strengths if item["signal_strength"] >= 2.0]
    pressure_count = len(context["disruptive_relations"]) + len(context["transit_disruptions"]) + len(context["storage_triggers"])
    support = []
    source_facts = []
    if len(active) >= 3:
        support.append(f"{len(active)} body-system symbolic signals are active")
        source_facts.extend(_fact("active_body_system", {"id": item["id"], "signal_strength": item["signal_strength"]}) for item in active)
    if pressure_count >= 2:
        support.append(f"{pressure_count} disruptive/storage trigger(s) add long-pressure context")
        source_facts.extend(_facts("disruptive_relation", context["disruptive_relations"][:4]))
        source_facts.extend(_facts("transit_disruption", context["transit_disruptions"][:4]))
        source_facts.extend(_facts("storage_trigger", context["storage_triggers"][:4]))
    if _regulation_mentions_cold_wet(context) or context["has_regulation_gap"]:
        support.append("regulation context keeps chronic imbalance review open")
        source_facts.append(_fact("regulation_context", context.get("regulation", {})))
    if len(active) >= 3 and pressure_count >= 2:
        level = "multi_system_symbolic_pressure"
    elif support:
        level = "mild_symbolic_pressure"
    else:
        level = "not_observed"
    return {
        **_item(
            "multi_system_weakness",
            _unique(support),
            [] if support else ["no multi-system symbolic weakness pattern is visible in first-pass facts"],
            source_facts,
            ["health-facts-multi-system-weakness-001", "health-facts-severity-calibration-001"],
        ),
        "level": level,
        "active_systems": [{"id": item["id"], "signal_strength": item["signal_strength"]} for item in active],
    }


def _surgery_body_part_context(context: dict[str, Any]) -> list[dict[str, Any]]:
    strengths = {item["id"]: item for item in _body_system_strength(context)}
    surgery_context = _has_disruption(context)
    result = []
    for body_part_id, system_ids in SURGERY_BODY_PART_TO_SYSTEMS.items():
        support = []
        counter = []
        source_facts = []
        matched_systems = [strengths[system_id] for system_id in system_ids if strengths.get(system_id, {}).get("signal_strength", 0) >= 2.0]
        if matched_systems:
            support.append(f"{body_part_id} has body-part symbolic signal through {', '.join(item['id'] for item in matched_systems)}")
            source_facts.extend(_fact("body_system_strength", {"id": item["id"], "signal_strength": item["signal_strength"]}) for item in matched_systems)
        else:
            counter.append(f"no strong body-system support for {body_part_id} body-part symbolism")
        if surgery_context:
            support.append("injury/surgery context is present as a candidate trigger layer")
            source_facts.extend(_facts("disruptive_relation", context["disruptive_relations"][:3]))
            source_facts.extend(_facts("transit_disruption", context["transit_disruptions"][:3]))
            source_facts.extend(_facts("storage_trigger", context["storage_triggers"][:3]))
        else:
            counter.append("no injury/surgery trigger context is visible")
        result.append(
            {
                **_item(
                    body_part_id,
                    _unique(support),
                    _unique(counter),
                    source_facts,
                    ["health-facts-surgery-body-part-context-001", "health-facts-transit-disruption-001"],
                ),
                "body_part_symbolic_signal": bool(matched_systems),
                "related_systems": system_ids,
            }
        )
    return result


def _annual_health_activation(context: dict[str, Any]) -> dict[str, Any]:
    support = []
    counter = []
    source_facts = []
    annual = context.get("annual") or {}
    if annual:
        source_facts.append(_fact("annual", annual))
    if context["transit_disruptions"]:
        support.append("target year or current luck has health-relevant disruptive triggers")
        source_facts.extend(_facts("transit_disruption", context["transit_disruptions"][:8]))
    else:
        counter.append("target year has no disruptive transit relation in first-pass facts")
    if context["storage_triggers"]:
        support.append("target year or luck activates storage symbolism")
        source_facts.extend(_facts("storage_trigger", context["storage_triggers"][:6]))
    annual_branch_element = _canonical_element(BRANCH_ELEMENTS.get(annual.get("branch"), ""))
    if annual_branch_element:
        matched_systems = _systems_for_element(annual_branch_element)
        if matched_systems:
            support.append(f"annual branch element {annual_branch_element} gives candidate body-system activation")
            source_facts.append(_fact("annual_branch_element", {"element": annual_branch_element, "systems": matched_systems}))
    active_strengths = [item for item in _body_system_strength(context) if item["signal_strength"] >= 2.0]
    if active_strengths and (context["transit_disruptions"] or context["storage_triggers"]):
        support.append("annual/luck triggers overlap with active body-system symbolic signals")
        source_facts.extend(_fact("active_body_system", {"id": item["id"], "signal_strength": item["signal_strength"]}) for item in active_strengths[:5])
    return {
        **_item(
            "annual_health_activation",
            _unique(support),
            _unique(counter),
            source_facts,
            ["health-facts-annual-activation-001", "health-facts-transit-disruption-001"],
        ),
        "target_year": context.get("target_year"),
        "annual_ganzhi": annual.get("ganzhi"),
        "candidate_only": True,
    }


def _pathology_context(context: dict[str, Any]) -> list[dict[str, Any]]:
    imbalance_support: list[str] = []
    source: list[dict[str, Any]] = []
    for element in context["weak_elements"]:
        imbalance_support.append(f"{element} element sparse: deficiency/imbalance symbolism")
        source.append(_fact("element_weakness", {"element": element, "counts": context["counts"]}))
    for element in context["excess_elements"]:
        imbalance_support.append(f"{element} element concentrated: excess/imbalance symbolism")
        source.append(_fact("element_excess", {"element": element, "counts": context["counts"]}))
    storage_support = []
    storage_facts = []
    if context["storages"] or context["storage_triggers"]:
        storage_support.append("storage symbolism is present or activated, so accumulation/mass context needs review")
        storage_facts.extend(_fact("storage_branch", {"branch": branch, **payload}) for branch, payload in context["storages"].items())
        storage_facts.extend(_facts("storage_trigger", context["storage_triggers"]))
    dry_wet_support = ["regulation rule not covered, so cold/heat/dry/wet review remains unresolved"] if context["has_regulation_gap"] else []
    return [
        _item("five_element_imbalance", imbalance_support, [] if imbalance_support else ["no obvious element bias"], source, ["health-facts-imbalance-context-001"]),
        _item("cold_heat_dry_wet_context", dry_wet_support, [] if dry_wet_support else ["regulation layer did not raise a cold/heat/dry/wet caveat"], [_fact("regulation", context["regulation"])], ["health-facts-cold-heat-dry-wet-001"]),
        _item("storage_accumulation_context", storage_support, [] if storage_support else ["no storage branch or activation observed"], storage_facts, ["health-facts-storage-mass-context-001"]),
    ]


def _severity_context(context: dict[str, Any]) -> list[dict[str, Any]]:
    pressure_count = len(context["disruptive_relations"]) + len(context["transit_disruptions"]) + len(context["storage_triggers"])
    if pressure_count >= 4:
        level = "high_symbolic_pressure"
    elif pressure_count >= 2:
        level = "medium_symbolic_pressure"
    elif pressure_count >= 1:
        level = "low_symbolic_pressure"
    else:
        level = "not_observed"
    return [
        {
            **_item(
                "symbolic_pressure_level",
                [f"{pressure_count} disruptive/storage trigger(s) visible"] if pressure_count else [],
                [] if pressure_count else ["no disruptive or storage trigger pressure visible"],
                _facts("disruptive_relation", context["disruptive_relations"]) + _facts("transit_disruption", context["transit_disruptions"]) + _facts("storage_trigger", context["storage_triggers"]),
                ["health-facts-transit-disruption-001", "health-facts-severity-calibration-001"],
            ),
            "level": level,
        }
    ]


def _injury_surgery_signal(context: dict[str, Any]) -> dict[str, Any]:
    support = []
    if context["disruptive_relations"]:
        support.append("natal clash/harm/break/punishment symbolism is present")
    if context["transit_disruptions"]:
        support.append("luck or annual disruption activates natal structure")
    if context["storage_triggers"]:
        support.append("storage activation is present")
    return _item(
        "injury_surgery",
        support,
        [] if support else ["no injury/surgery-context trigger observed"],
        _facts("disruptive_relation", context["disruptive_relations"]) + _facts("transit_disruption", context["transit_disruptions"]) + _facts("storage_trigger", context["storage_triggers"]),
        ["health-facts-transit-disruption-001", "yhzp-clash-harm-break-001", "smth-storage-clash-001"],
    )


def _global_support(context: dict[str, Any]) -> list[str]:
    support = []
    if context["weak_elements"] or context["excess_elements"]:
        support.append("five-element distribution has sparse or concentrated elements")
    if context["disruptive_relations"] or context["transit_disruptions"]:
        support.append("natal or transit disruptive relations are present")
    if context["storages"] or context["storage_triggers"]:
        support.append("storage symbolism is present or activated")
    if context["has_regulation_gap"]:
        support.append("regulation coverage is incomplete, preserving cold/heat/dry/wet uncertainty")
    return support


def _global_counter(context: dict[str, Any]) -> list[str]:
    counter = []
    if not context["weak_elements"] and not context["excess_elements"]:
        counter.append("five-element distribution is not strongly sparse or concentrated")
    if not context["disruptive_relations"] and not context["transit_disruptions"]:
        counter.append("no natal or transit disruptive relation observed")
    return counter


def _has_disruption(context: dict[str, Any]) -> bool:
    return bool(context["disruptive_relations"] or context["transit_disruptions"] or context["storage_triggers"])


def _canonical_element(element: Any) -> str:
    text = str(element or "")
    return ELEMENT_ALIASES.get(text, text)


def _element_count(context: dict[str, Any], element: str) -> float:
    if element in context["counts"]:
        return float(context["counts"].get(element) or 0)
    for raw, value in context["counts"].items():
        if _canonical_element(raw) == element:
            return float(value or 0)
    return 0.0


def _month_element(context: dict[str, Any]) -> str:
    return _canonical_element(BRANCH_ELEMENTS.get(context.get("month_branch"), ""))


def _relation_hits_for_element(relations: list[dict[str, Any]], element: str) -> list[dict[str, Any]]:
    hits = []
    for relation in relations:
        if _canonical_element(relation.get("element")) == element:
            hits.append(relation)
            continue
        branches = relation.get("branches") or []
        if any(_canonical_element(BRANCH_ELEMENTS.get(branch, "")) == element for branch in branches):
            hits.append(relation)
    return hits


def _storage_hits_for_element(context: dict[str, Any], element: str) -> list[dict[str, Any]]:
    hits = []
    for branch, payload in context["storages"].items():
        stored = payload.get("stores") if isinstance(payload, dict) else None
        if _canonical_element(stored) == element or _canonical_element(BRANCH_ELEMENTS.get(branch, "")) == element:
            hits.append({"branch": branch, **(payload if isinstance(payload, dict) else {})})
    for trigger in context["storage_triggers"]:
        if _canonical_element(trigger.get("element")) == element:
            hits.append(trigger)
            continue
        branch = trigger.get("branch") or trigger.get("target_branch")
        if _canonical_element(BRANCH_ELEMENTS.get(branch, "")) == element:
            hits.append(trigger)
    return hits


def _regulation_mentions_cold_wet(context: dict[str, Any]) -> bool:
    regulation = context.get("regulation") or {}
    text = str(regulation)
    return any(marker in text for marker in ("寒", "湿", "燥", "热", "cold", "wet", "dry", "heat"))


def _systems_for_element(element: str) -> list[str]:
    return ELEMENT_TO_SYSTEMS.get(_canonical_element(element), [])


def _item(item_id: str, support: list[str], counter: list[str], source_facts: list[dict[str, Any]], rule_ids: list[str]) -> dict[str, Any]:
    return {
        "id": item_id,
        "support": support,
        "counter": counter,
        "source_facts": source_facts or [_fact("not_observed", {"id": item_id})],
        "rule_ids": rule_ids,
        "limits": LIMITS,
    }


def _fact(name: str, value: Any) -> dict[str, Any]:
    return {"name": name, "value": value}


def _facts(name: str, values: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [_fact(name, value) for value in values]


def _unique(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result
