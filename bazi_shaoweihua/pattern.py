from __future__ import annotations


PILLARS = ["year", "month", "day", "hour"]
PILLAR_NAMES = {"year": "年", "month": "月", "day": "日", "hour": "时"}
HIDDEN_STEM_TO_TEN_GOD_KEY = {
    "year": "year",
    "month": "month",
    "day": "day",
    "hour": "hour",
}
PATTERN_NAMES = {
    "正官": "正官格候选",
    "七杀": "七杀格候选",
    "正财": "正财格候选",
    "偏财": "偏财格候选",
    "正印": "正印格候选",
    "偏印": "偏印格候选",
    "食神": "食神格候选",
    "伤官": "伤官格候选",
    "比肩": "建禄月劫候选",
    "劫财": "月劫格候选",
}


def analyze_pattern(chart: dict, structure: dict) -> dict:
    month_branch = chart["pillars"]["month"]["branch"]
    month_hidden = structure["hidden_stems_weighted"]["month"]
    main_stem = month_hidden[0]["stem"]
    main_ten_god = chart["ten_gods"]["earth_branches"]["month"][0]
    transmitted = _transmitted_ten_gods(chart)
    candidates = _combination_candidates(main_ten_god, transmitted)
    warnings = _warnings(transmitted, structure)
    return {
        "month_command": {
            "branch": month_branch,
            "main_stem": main_stem,
            "main_ten_god": main_ten_god,
        },
        "primary_candidate": {
            "name": PATTERN_NAMES.get(main_ten_god, f"{main_ten_god}格候选"),
            "basis": "月令主气",
            "status": "candidate",
            "rule_ids": ["zpxz-month-command-001", "zpxz-pattern-candidate-001"],
        },
        "transmitted_ten_gods": transmitted,
        "combination_candidates": candidates,
        "warnings": warnings,
        "decision": "候选格局，待旺衰、调候、清浊复核",
        "caveat": "格局MVP只判候选，不判成格、破格、高低。",
    }


def _transmitted_ten_gods(chart: dict) -> list[dict]:
    result = []
    for pillar in ["year", "month", "hour"]:
        ten_god = chart["ten_gods"]["heaven_stems"][pillar]
        if ten_god == "日主":
            continue
        result.append(
            {
                "pillar": pillar,
                "stem": chart["pillars"][pillar]["stem"],
                "ten_god": ten_god,
            }
        )
    return result


def _combination_candidates(main_ten_god: str, transmitted: list[dict]) -> list[dict]:
    gods = {item["ten_god"] for item in transmitted}
    if main_ten_god:
        gods.add(main_ten_god)
    candidates = []
    if ("正官" in gods or "七杀" in gods) and ("正印" in gods or "偏印" in gods):
        name = "杀印相生候选" if "七杀" in gods else "官印相生候选"
        if "正官" in gods and ("正印" in gods or "偏印" in gods):
            candidates.append({"name": "官印相生候选", "basis": "官杀与印星同见"})
        if "七杀" in gods and ("正印" in gods or "偏印" in gods):
            candidates.append({"name": name, "basis": "官杀与印星同见"})
    if ("食神" in gods or "伤官" in gods) and ("正财" in gods or "偏财" in gods):
        candidates.append({"name": "食伤生财候选", "basis": "食伤与财星同见"})
    return _dedupe(candidates)


def _warnings(transmitted: list[dict], structure: dict) -> list[str]:
    gods = [item["ten_god"] for item in transmitted]
    warnings = []
    if "正官" in gods and "七杀" in gods:
        warnings.append("官杀并见")
    if any(relation["type"] in {"six_clash", "punishment", "self_punishment", "six_harm", "six_break"} for relation in structure["branch_relations"]):
        warnings.append("地支有刑冲害破，自带格局扰动信号")
    if any(relation["type"] == "heavenly_combination" for relation in structure["stem_relations"]):
        warnings.append("天干有合，需查格神是否被合绊")
    return warnings


def _dedupe(items: list[dict]) -> list[dict]:
    result = []
    seen = set()
    for item in items:
        key = tuple(sorted(item.items()))
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result
