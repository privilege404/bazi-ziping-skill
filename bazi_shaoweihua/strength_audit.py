from __future__ import annotations


PILLARS = ["year", "month", "day", "hour"]
SUPPORTING_TEN_GODS = {"正印", "偏印", "比肩", "劫财"}
PRESSURE_TEN_GODS = {"食神", "伤官", "正财", "偏财", "正官", "七杀"}
SEASON_ASSESSMENTS = {
    "旺": "得令旺气",
    "相": "得令相气",
    "休": "休囚待辨",
    "囚": "失令受囚",
    "死": "失令死地",
}
BRANCH_SEASON = {
    "寅": "spring",
    "卯": "spring",
    "辰": "spring",
    "巳": "summer",
    "午": "summer",
    "未": "summer",
    "申": "autumn",
    "酉": "autumn",
    "戌": "autumn",
    "亥": "winter",
    "子": "winter",
    "丑": "winter",
}
SEASON_STATES = {
    "spring": {"木": "旺", "火": "相", "水": "休", "金": "囚", "土": "死"},
    "summer": {"火": "旺", "土": "相", "木": "休", "水": "囚", "金": "死"},
    "autumn": {"金": "旺", "水": "相", "土": "休", "火": "囚", "木": "死"},
    "winter": {"水": "旺", "木": "相", "金": "休", "土": "囚", "火": "死"},
}
ROOT_ASSESSMENTS = [
    (160, "同干强根"),
    (60, "同干有根"),
    (1, "同干弱根"),
    (0, "同干无根"),
]


def analyze_strength_audit(chart: dict, structure: dict) -> dict:
    season = _season_audit(chart, structure)
    rooting = _rooting_audit(structure)
    assistance = _ten_god_side(chart, SUPPORTING_TEN_GODS, "support")
    pressure = _pressure_audit(chart)
    modifiers = _relation_modifiers(chart, structure)
    return {
        "version": "strength-audit-mvp-1",
        "season": season,
        "rooting": rooting,
        "assistance": assistance,
        "pressure": pressure,
        "relation_modifiers": modifiers,
        "decision_policy": "只输出旺衰复核证据，不直接覆盖 strength.classification。",
        "caveat": "旺衰复核层只列证据和候选影响；从格、化气、最终喜忌须由格局、调候和人工校准继续复核。",
    }


def _season_audit(chart: dict, structure: dict) -> dict:
    context = structure["day_master_context"]
    day_element = _day_element(chart)
    month_branch = context["month_branch"]
    stage = context["month_growth_stage"]
    season = BRANCH_SEASON[month_branch]
    seasonal_state = SEASON_STATES[season][day_element]
    assessment = SEASON_ASSESSMENTS[seasonal_state]
    return {
        "month_branch": month_branch,
        "season": season,
        "day_element_season_state": seasonal_state,
        "month_growth_stage": stage,
        "season_state": context["season_state"],
        "assessment": assessment,
        "rule_ids": ["zpxz-month-command-001", "qianli-season-strength-001"],
    }


def _rooting_audit(structure: dict) -> dict:
    context = structure["day_master_context"]
    root_weight = context["root_weight"]
    assessment = next(label for threshold, label in ROOT_ASSESSMENTS if root_weight >= threshold)
    roots = context["roots"]
    return {
        "assessment": assessment,
        "root_weight": root_weight,
        "root_count": context["root_count"],
        "root_branches": [root["branch"] for root in roots],
        "roots": roots,
        "self_seated": context["self_seated"],
        "rule_ids": ["yhzp-hidden-root-001", "qianli-season-strength-001"],
    }


def _pressure_audit(chart: dict) -> dict:
    pressure = _ten_god_side(chart, PRESSURE_TEN_GODS, "pressure")
    month_main_ten_god = chart["ten_gods"]["earth_branches"]["month"][0]
    pressure["month_command_ten_god"] = month_main_ten_god
    pressure["month_command_pressure"] = month_main_ten_god in PRESSURE_TEN_GODS
    return pressure


def _ten_god_side(chart: dict, target_gods: set[str], side: str) -> dict:
    visible = []
    for pillar in ["year", "month", "hour"]:
        ten_god = chart["ten_gods"]["heaven_stems"][pillar]
        if ten_god in target_gods:
            visible.append(ten_god)

    hidden = []
    hidden_positions = []
    for pillar in PILLARS:
        branch = chart["pillars"][pillar]["branch"]
        for index, ten_god in enumerate(chart["ten_gods"]["earth_branches"][pillar]):
            if ten_god in target_gods:
                hidden.append(ten_god)
                hidden_positions.append({"pillar": pillar, "branch": branch, "ten_god": ten_god, "index": index})

    prefix = "supporting" if side == "support" else "pressure"
    return {
        f"visible_{prefix}_ten_gods": _unique(visible),
        f"hidden_{prefix}_ten_gods": _unique(hidden),
        f"hidden_{prefix}_positions": hidden_positions,
        "rule_ids": ["yhzp-ten-gods-001", "yhzp-ten-gods-position-001"],
    }


def _relation_modifiers(chart: dict, structure: dict) -> dict:
    day_element = _day_element(chart)
    supportive_elements = {day_element, _generating_element(day_element)}
    supportive = []
    transform_or_binding = []
    disruptive = []
    for relation in structure["stem_relations"]:
        if relation["type"] == "heavenly_combination":
            transform_or_binding.append(relation["name"])
        if relation.get("transform_candidate") and relation.get("element") in supportive_elements:
            supportive.append(relation["name"])
    for relation in structure["branch_relations"]:
        if relation.get("transform_candidate") and relation.get("element") in supportive_elements:
            supportive.append(relation["name"])
        if relation["type"] in {"six_clash", "punishment", "self_punishment", "six_harm", "six_break"}:
            disruptive.append(relation["name"])
    return {
        "supportive_relations": _unique(supportive),
        "transform_or_binding_candidates": _unique(transform_or_binding),
        "disruptive_relations": _unique(disruptive),
        "rule_ids": ["dts-flow-combination-001", "zpxz-pattern-combo-001", "yhzp-clash-harm-break-001"],
    }


def _day_element(chart: dict) -> str:
    element_text = chart["five_elements"]["pillars"]["day"]
    return element_text[0]


def _generating_element(element: str) -> str:
    generates = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    for source, target in generates.items():
        if target == element:
            return source
    raise ValueError(element)


def _unique(items: list[str]) -> list[str]:
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result
