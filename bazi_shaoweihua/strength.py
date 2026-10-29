from __future__ import annotations

from collections import Counter


STEM_ELEMENTS = {
    "甲": "木",
    "乙": "木",
    "丙": "火",
    "丁": "火",
    "戊": "土",
    "己": "土",
    "庚": "金",
    "辛": "金",
    "壬": "水",
    "癸": "水",
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
STATE_SCORES = {"旺": 45, "相": 30, "休": 0, "囚": -25, "死": -45}
GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
CONTROLS = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
PILLARS = ["year", "month", "day", "hour"]
VISIBLE_WEIGHTS = {"year": 12, "month": 24, "hour": 16}
HIDDEN_ROLE_FACTOR = {"main_qi": 1.0, "middle_qi": 0.55, "residual_qi": 0.25}


def analyze_strength(chart: dict, structure: dict) -> dict:
    day_master = chart["day_master"]
    day_element = STEM_ELEMENTS[day_master]
    season = _season_strength(day_element, chart["pillars"]["month"]["branch"])
    roots = _root_strength(day_master, structure)
    support = _support_strength(day_element, chart, structure)
    pressure = _pressure_strength(day_element, chart, structure)
    total = season["score"] + roots["root_score"] + support["total_support_score"] - pressure["total_pressure_score"]
    classification = _classification(total, roots, season)
    return {
        "day_master": day_master,
        "day_master_element": day_element,
        "season": season,
        "roots": roots,
        "support": support,
        "pressure": pressure,
        "heuristic_score": round(total, 2),
        "classification": classification,
        "summary": _summary(day_master, day_element, season, roots, support, pressure, classification),
        "method": "strength-mvp-1: 旺相休囚死 + 同干通根 + 印比扶身 + 食伤财官杀泄耗克身的启发式评分",
        "caveat": "该分数用于排序和解释，不等同古籍原文；格局、调候、从格需后续模块复核。",
    }


def _season_strength(day_element: str, month_branch: str) -> dict:
    season = BRANCH_SEASON[month_branch]
    state = SEASON_STATES[season][day_element]
    return {
        "month_branch": month_branch,
        "season": season,
        "state": state,
        "score": STATE_SCORES[state],
        "all_element_states": SEASON_STATES[season],
    }


def _root_strength(day_master: str, structure: dict) -> dict:
    same_stem_weight = structure["day_master_context"]["root_weight"]
    root_score = min(35, same_stem_weight * 0.175)
    return {
        "same_stem_roots": structure["day_master_context"]["roots"],
        "same_stem_root_weight": same_stem_weight,
        "root_score": round(root_score, 2),
        "self_seated": structure["day_master_context"]["self_seated"],
    }


def _support_strength(day_element: str, chart: dict, structure: dict) -> dict:
    visible_counts = _visible_element_counts(chart)
    hidden_counts = _hidden_element_weights(structure)
    same_element = day_element
    generating_element = _generating_element(day_element)
    visible_support = (
        visible_counts[same_element] * 10
        + visible_counts[generating_element] * 12
    )
    hidden_support = (
        hidden_counts[same_element] * 0.08
        + hidden_counts[generating_element] * 0.1
    )
    return {
        "same_element": same_element,
        "generating_element": generating_element,
        "visible_support_score": round(visible_support, 2),
        "hidden_support_score": round(hidden_support, 2),
        "total_support_score": round(visible_support + hidden_support, 2),
    }


def _pressure_strength(day_element: str, chart: dict, structure: dict) -> dict:
    visible_counts = _visible_element_counts(chart)
    hidden_counts = _hidden_element_weights(structure)
    output_element = GENERATES[day_element]
    wealth_element = CONTROLS[day_element]
    officer_element = _controlling_element(day_element)
    visible_pressure = (
        visible_counts[output_element] * 9
        + visible_counts[wealth_element] * 10
        + visible_counts[officer_element] * 14
    )
    hidden_pressure = (
        hidden_counts[output_element] * 0.07
        + hidden_counts[wealth_element] * 0.08
        + hidden_counts[officer_element] * 0.1
    )
    return {
        "output_element": output_element,
        "wealth_element": wealth_element,
        "officer_killing_element": officer_element,
        "visible_pressure_score": round(visible_pressure, 2),
        "hidden_pressure_score": round(hidden_pressure, 2),
        "total_pressure_score": round(visible_pressure + hidden_pressure, 2),
    }


def _visible_element_counts(chart: dict) -> Counter:
    counts = Counter()
    for pillar in ["year", "month", "hour"]:
        stem = chart["pillars"][pillar]["stem"]
        counts[STEM_ELEMENTS[stem]] += VISIBLE_WEIGHTS[pillar] / 10
    return counts


def _hidden_element_weights(structure: dict) -> Counter:
    counts = Counter()
    for hidden_stems in structure["hidden_stems_weighted"].values():
        for item in hidden_stems:
            counts[STEM_ELEMENTS[item["stem"]]] += item["weight"] * HIDDEN_ROLE_FACTOR[item["role"]]
    return counts


def _generating_element(element: str) -> str:
    for source, target in GENERATES.items():
        if target == element:
            return source
    raise ValueError(element)


def _controlling_element(element: str) -> str:
    for source, target in CONTROLS.items():
        if target == element:
            return source
    raise ValueError(element)


def _classification(score: float, roots: dict, season: dict) -> str:
    if score >= 65:
        return "偏强"
    if score >= 25:
        return "中和偏强"
    if score >= -15:
        return "中和"
    if score >= -55:
        return "中和偏弱"
    if roots["same_stem_root_weight"] == 0 and season["state"] in {"囚", "死"}:
        return "极弱候选"
    return "偏弱"


def _summary(day_master: str, day_element: str, season: dict, roots: dict, support: dict, pressure: dict, classification: str) -> str:
    parts = [f"{day_master}{day_element}日主，月令{season['month_branch']}，季令状态为{season['state']}。"]
    if season["state"] in {"旺", "相"}:
        parts.append("有季令相气。")
    else:
        parts.append("不得季令。")
    if roots["same_stem_root_weight"]:
        parts.append(f"虽有{roots['self_seated']['branch']}根等根气，根气分={roots['root_score']}。")
    else:
        parts.append("同干根气未见。")
    parts.append(f"扶身分={support['total_support_score']}，泄耗克身分={pressure['total_pressure_score']}。")
    parts.append(f"暂判为{classification}。")
    return "".join(parts)
