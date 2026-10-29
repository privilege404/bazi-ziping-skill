from __future__ import annotations


PILLARS = ["year", "month", "day", "hour"]
VISIBLE_POSITION_WEIGHTS = {"year": 8, "month": 18, "hour": 10}
HIDDEN_PILLAR_FACTORS = {"year": 0.35, "month": 0.6, "day": 0.5, "hour": 0.35}
HIDDEN_ROLE_FACTORS = {"main_qi": 1.0, "middle_qi": 0.55, "residual_qi": 0.25}
MONTH_COMMAND_BONUS = 30
ALL_TEN_GODS = ["比肩", "劫财", "食神", "伤官", "正财", "偏财", "正官", "七杀", "正印", "偏印"]


def analyze_ten_god_influence(chart: dict, structure: dict) -> dict:
    month_command = _month_command(chart, structure)
    by_ten_god = {ten_god: _empty_item(ten_god) for ten_god in ALL_TEN_GODS}
    _add_visible_positions(chart, by_ten_god)
    _add_hidden_positions(chart, structure, by_ten_god)
    _finalize_items(by_ten_god, month_command)
    present_items = [item for item in by_ten_god.values() if item["present"]]
    top_ten_gods = sorted(
        ({"ten_god": item["ten_god"], "score": item["score"], "level": item["influence_level"]} for item in present_items),
        key=lambda item: (-item["score"], item["ten_god"]),
    )
    return {
        "version": "ten-god-influence-mvp-1",
        "month_command": month_command,
        "by_ten_god": by_ten_god,
        "top_ten_gods": top_ten_gods,
        "priority_ten_gods": _priority_ten_gods(by_ten_god),
        "combination_signals": _combination_signals(by_ten_god),
        "structural_warnings": _structural_warnings(by_ten_god, structure),
        "method": "ten-god-influence-mvp-1: 透干位置 + 藏干权重 + 月令主气 bonus 的审计排序",
        "caveat": "十神影响力只用于排序和提示复核重点，不直接断吉凶、六亲事件或格局成败。",
    }


def _month_command(chart: dict, structure: dict) -> dict:
    month_hidden = structure["hidden_stems_weighted"]["month"][0]
    return {
        "branch": chart["pillars"]["month"]["branch"],
        "stem": month_hidden["stem"],
        "ten_god": chart["ten_gods"]["earth_branches"]["month"][0],
    }


def _empty_item(ten_god: str) -> dict:
    return {
        "ten_god": ten_god,
        "present": False,
        "is_month_command": False,
        "visible_positions": [],
        "hidden_positions": [],
        "visible_score": 0,
        "hidden_score": 0,
        "month_command_bonus": 0,
        "score": 0,
        "influence_level": "无",
        "flags": [],
    }


def _add_visible_positions(chart: dict, by_ten_god: dict) -> None:
    for pillar in ["year", "month", "hour"]:
        ten_god = chart["ten_gods"]["heaven_stems"][pillar]
        if ten_god == "日主":
            continue
        item = by_ten_god[ten_god]
        weight = VISIBLE_POSITION_WEIGHTS[pillar]
        item["visible_positions"].append(
            {"pillar": pillar, "stem": chart["pillars"][pillar]["stem"], "position_weight": weight}
        )
        item["visible_score"] += weight
        if pillar == "month":
            item["flags"].append("透于月干")


def _add_hidden_positions(chart: dict, structure: dict, by_ten_god: dict) -> None:
    for pillar in PILLARS:
        branch = chart["pillars"][pillar]["branch"]
        for index, hidden in enumerate(structure["hidden_stems_weighted"][pillar]):
            ten_god = chart["ten_gods"]["earth_branches"][pillar][index]
            item = by_ten_god[ten_god]
            item["hidden_positions"].append(
                {
                    "pillar": pillar,
                    "branch": branch,
                    "stem": hidden["stem"],
                    "role": hidden["role"],
                    "weight": hidden["weight"],
                }
            )
            item["hidden_score"] += hidden["weight"] * HIDDEN_PILLAR_FACTORS[pillar] * HIDDEN_ROLE_FACTORS[hidden["role"]]


def _finalize_items(by_ten_god: dict, month_command: dict) -> None:
    for item in by_ten_god.values():
        if item["ten_god"] == month_command["ten_god"]:
            item["is_month_command"] = True
            item["month_command_bonus"] = MONTH_COMMAND_BONUS
            item["flags"].append("月令主气")
        if item["visible_positions"] and item["hidden_positions"]:
            item["flags"].append("透藏并见")
        item["present"] = bool(item["visible_positions"] or item["hidden_positions"])
        total = item["visible_score"] + item["hidden_score"] + item["month_command_bonus"]
        item["hidden_score"] = round(item["hidden_score"], 2)
        item["score"] = round(total, 2)
        item["influence_level"] = _level(item["score"], item["present"])


def _level(score: float, present: bool) -> str:
    if not present:
        return "无"
    if score >= 70:
        return "强"
    if score >= 35:
        return "中"
    return "弱"


def _priority_ten_gods(by_ten_god: dict) -> list[dict]:
    priorities = []
    for ten_god, item in by_ten_god.items():
        if item["is_month_command"]:
            priorities.append({"ten_god": ten_god, "reason": "月令主气"})
        if any(position["pillar"] == "month" for position in item["visible_positions"]):
            priorities.append({"ten_god": ten_god, "reason": "月干透出"})
    return priorities


def _combination_signals(by_ten_god: dict) -> list[str]:
    signals = []
    has_seal = _present(by_ten_god, "正印") or _present(by_ten_god, "偏印")
    if _present(by_ten_god, "正官") and has_seal:
        signals.append("官印相生候选")
    if _present(by_ten_god, "七杀") and has_seal:
        signals.append("杀印相生候选")
    if (_present(by_ten_god, "食神") or _present(by_ten_god, "伤官")) and (
        _present(by_ten_god, "正财") or _present(by_ten_god, "偏财")
    ):
        signals.append("食伤生财候选")
    return signals


def _structural_warnings(by_ten_god: dict, structure: dict) -> list[str]:
    warnings = []
    if _present(by_ten_god, "正官") and _present(by_ten_god, "七杀"):
        warnings.append("官杀并见")
    if any(relation["type"] == "heavenly_combination" for relation in structure["stem_relations"]):
        warnings.append("天干有合，需查十神是否被合绊")
    if any(relation["type"] in {"six_clash", "punishment", "self_punishment", "six_harm", "six_break"} for relation in structure["branch_relations"]):
        warnings.append("地支有刑冲害破，需查对应十神受扰")
    return warnings


def _present(by_ten_god: dict, ten_god: str) -> bool:
    return by_ten_god[ten_god]["present"]
