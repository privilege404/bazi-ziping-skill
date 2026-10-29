from __future__ import annotations

import json
from itertools import combinations


PILLARS = ["year", "month", "day", "hour"]

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
STEM_POLARITY = {
    "甲": "阳",
    "乙": "阴",
    "丙": "阳",
    "丁": "阴",
    "戊": "阳",
    "己": "阴",
    "庚": "阳",
    "辛": "阴",
    "壬": "阳",
    "癸": "阴",
}
BRANCH_POLARITY = {
    "子": "阳",
    "丑": "阴",
    "寅": "阳",
    "卯": "阴",
    "辰": "阳",
    "巳": "阴",
    "午": "阳",
    "未": "阴",
    "申": "阳",
    "酉": "阴",
    "戌": "阳",
    "亥": "阴",
}

HIDDEN_STEMS = {
    "子": [("癸", "main_qi", 100)],
    "丑": [("己", "main_qi", 60), ("癸", "middle_qi", 30), ("辛", "residual_qi", 10)],
    "寅": [("甲", "main_qi", 60), ("丙", "middle_qi", 30), ("戊", "residual_qi", 10)],
    "卯": [("乙", "main_qi", 100)],
    "辰": [("戊", "main_qi", 60), ("乙", "middle_qi", 30), ("癸", "residual_qi", 10)],
    "巳": [("丙", "main_qi", 60), ("庚", "middle_qi", 30), ("戊", "residual_qi", 10)],
    "午": [("丁", "main_qi", 70), ("己", "middle_qi", 30)],
    "未": [("己", "main_qi", 60), ("丁", "middle_qi", 30), ("乙", "residual_qi", 10)],
    "申": [("庚", "main_qi", 60), ("壬", "middle_qi", 30), ("戊", "residual_qi", 10)],
    "酉": [("辛", "main_qi", 100)],
    "戌": [("戊", "main_qi", 60), ("辛", "middle_qi", 30), ("丁", "residual_qi", 10)],
    "亥": [("壬", "main_qi", 70), ("甲", "middle_qi", 30)],
}

BRANCH_STORAGE = {
    "辰": "水",
    "戌": "火",
    "丑": "金",
    "未": "木",
}
STORAGE_CLASH = {
    "辰": "戌",
    "戌": "辰",
    "丑": "未",
    "未": "丑",
}

HEAVENLY_COMBINATIONS = {
    frozenset(("甲", "己")): ("甲己合土", "土"),
    frozenset(("乙", "庚")): ("乙庚合金", "金"),
    frozenset(("丙", "辛")): ("丙辛合水", "水"),
    frozenset(("丁", "壬")): ("丁壬合木", "木"),
    frozenset(("戊", "癸")): ("戊癸合火", "火"),
}
HEAVENLY_CLASHES = {
    frozenset(("甲", "庚")): "甲庚冲",
    frozenset(("乙", "辛")): "乙辛冲",
    frozenset(("丙", "壬")): "丙壬冲",
    frozenset(("丁", "癸")): "丁癸冲",
}
SIX_COMBINATIONS = {
    frozenset(("子", "丑")): ("子丑合土", "土"),
    frozenset(("寅", "亥")): ("寅亥合木", "木"),
    frozenset(("卯", "戌")): ("卯戌合火", "火"),
    frozenset(("辰", "酉")): ("辰酉合金", "金"),
    frozenset(("巳", "申")): ("巳申合水", "水"),
    frozenset(("午", "未")): ("午未合土", "土"),
}
THREE_HARMONIES = {
    ("申", "子", "辰"): ("申子辰三合水", "水"),
    ("亥", "卯", "未"): ("亥卯未三合木", "木"),
    ("寅", "午", "戌"): ("寅午戌三合火", "火"),
    ("巳", "酉", "丑"): ("巳酉丑三合金", "金"),
}
HALF_HARMONIES = {
    frozenset(("申", "子")): ("申子半合水", "水"),
    frozenset(("子", "辰")): ("子辰半合水", "水"),
    frozenset(("亥", "卯")): ("亥卯半合木", "木"),
    frozenset(("卯", "未")): ("卯未半合木", "木"),
    frozenset(("寅", "午")): ("寅午半合火", "火"),
    frozenset(("午", "戌")): ("午戌半合火", "火"),
    frozenset(("巳", "酉")): ("巳酉半合金", "金"),
    frozenset(("酉", "丑")): ("酉丑半合金", "金"),
}
HALF_MEETINGS = {
    frozenset(("寅", "卯")): ("寅卯半会木", "木"),
    frozenset(("卯", "辰")): ("卯辰半会木", "木"),
    frozenset(("巳", "午")): ("巳午半会火", "火"),
    frozenset(("午", "未")): ("午未半会火", "火"),
    frozenset(("申", "酉")): ("申酉半会金", "金"),
    frozenset(("酉", "戌")): ("酉戌半会金", "金"),
    frozenset(("亥", "子")): ("亥子半会水", "水"),
    frozenset(("子", "丑")): ("子丑半会水", "水"),
}
THREE_MEETINGS = {
    ("寅", "卯", "辰"): ("寅卯辰三会木", "木"),
    ("巳", "午", "未"): ("巳午未三会火", "火"),
    ("申", "酉", "戌"): ("申酉戌三会金", "金"),
    ("亥", "子", "丑"): ("亥子丑三会水", "水"),
}
GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
CONTROLS = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
SIX_CLASHES = {
    frozenset(("子", "午")): "子午冲",
    frozenset(("丑", "未")): "丑未冲",
    frozenset(("寅", "申")): "寅申冲",
    frozenset(("卯", "酉")): "卯酉冲",
    frozenset(("辰", "戌")): "辰戌冲",
    frozenset(("巳", "亥")): "巳亥冲",
}
SIX_HARMS = {
    frozenset(("子", "未")): "子未害",
    frozenset(("丑", "午")): "丑午害",
    frozenset(("寅", "巳")): "寅巳害",
    frozenset(("卯", "辰")): "卯辰害",
    frozenset(("申", "亥")): "申亥害",
    frozenset(("酉", "戌")): "酉戌害",
}
SIX_BREAKS = {
    frozenset(("子", "酉")): "子酉破",
    frozenset(("卯", "午")): "卯午破",
    frozenset(("辰", "丑")): "辰丑破",
    frozenset(("戌", "未")): "戌未破",
    frozenset(("寅", "亥")): "寅亥破",
    frozenset(("巳", "申")): "巳申破",
}
THREE_PUNISHMENTS = {
    frozenset(("寅", "巳", "申")): "寅巳申三刑",
    frozenset(("丑", "戌", "未")): "丑戌未三刑",
}
PAIR_PUNISHMENTS = {
    frozenset(("子", "卯")): "子卯刑",
    frozenset(("寅", "巳")): "寅巳刑",
    frozenset(("巳", "申")): "巳申刑",
    frozenset(("申", "寅")): "申寅刑",
    frozenset(("丑", "戌")): "丑戌刑",
    frozenset(("戌", "未")): "戌未刑",
    frozenset(("未", "丑")): "未丑刑",
}
SELF_PUNISH = {"辰": "辰辰自刑", "午": "午午自刑", "酉": "酉酉自刑", "亥": "亥亥自刑"}

ELEMENT_SEASON_BRANCHES = {
    "木": {"寅", "卯", "辰"},
    "火": {"巳", "午", "未"},
    "金": {"申", "酉", "戌"},
    "水": {"亥", "子", "丑"},
    "土": {"辰", "戌", "丑", "未"},
}
IN_SEASON_STAGES = {"长生", "冠带", "临官", "帝旺"}
WEAK_STAGES = {"衰", "病", "死", "墓", "绝", "胎", "养"}

TIANYI = {
    "甲": {"丑", "未"},
    "戊": {"丑", "未"},
    "庚": {"丑", "未"},
    "乙": {"子", "申"},
    "己": {"子", "申"},
    "丙": {"亥", "酉"},
    "丁": {"亥", "酉"},
    "壬": {"卯", "巳"},
    "癸": {"卯", "巳"},
    "辛": {"寅", "午"},
}
LU = {"甲": "寅", "乙": "卯", "丙": "巳", "丁": "午", "戊": "巳", "己": "午", "庚": "申", "辛": "酉", "壬": "亥", "癸": "子"}
YANG_REN = {"甲": "卯", "丙": "午", "戊": "午", "庚": "酉", "壬": "子"}
WENCHANG = {"甲": "巳", "乙": "午", "丙": "申", "戊": "申", "丁": "酉", "己": "酉", "庚": "亥", "辛": "子", "壬": "寅", "癸": "卯"}
GROUP_SHENSHA = {
    ("申", "子", "辰"): {"桃花": "酉", "驿马": "寅", "华盖": "辰", "将星": "子", "劫煞": "巳", "灾煞": "午", "亡神": "亥"},
    ("寅", "午", "戌"): {"桃花": "卯", "驿马": "申", "华盖": "戌", "将星": "午", "劫煞": "亥", "灾煞": "子", "亡神": "巳"},
    ("巳", "酉", "丑"): {"桃花": "午", "驿马": "亥", "华盖": "丑", "将星": "酉", "劫煞": "寅", "灾煞": "卯", "亡神": "申"},
    ("亥", "卯", "未"): {"桃花": "子", "驿马": "巳", "华盖": "未", "将星": "卯", "劫煞": "申", "灾煞": "酉", "亡神": "寅"},
}
SOLITARY_SHENSHA = {
    ("亥", "子", "丑"): {"孤辰": "寅", "寡宿": "戌"},
    ("寅", "卯", "辰"): {"孤辰": "巳", "寡宿": "丑"},
    ("巳", "午", "未"): {"孤辰": "申", "寡宿": "辰"},
    ("申", "酉", "戌"): {"孤辰": "亥", "寡宿": "未"},
}
TIANDE_BY_MONTH = {
    "寅": "丁",
    "卯": "申",
    "辰": "壬",
    "巳": "辛",
    "午": "亥",
    "未": "甲",
    "申": "癸",
    "酉": "寅",
    "戌": "丙",
    "亥": "乙",
    "子": "巳",
    "丑": "庚",
}
YUEDE_BY_GROUP = {
    ("寅", "午", "戌"): "丙",
    ("申", "子", "辰"): "壬",
    ("亥", "卯", "未"): "甲",
    ("巳", "酉", "丑"): "庚",
}
DEXIU = {
    ("寅", "午", "戌"): {"de": {"丙", "丁", "戊", "癸"}, "xiu": {"戊", "癸"}},
    ("申", "子", "辰"): {"de": {"壬", "癸", "戊", "己"}, "xiu": {"丙", "辛", "甲", "己"}},
    ("巳", "酉", "丑"): {"de": {"庚", "辛", "乙"}, "xiu": {"乙", "庚"}},
    ("亥", "卯", "未"): {"de": {"甲", "乙", "丁", "壬"}, "xiu": {"丁", "壬"}},
}


def analyze_structure(chart: dict) -> dict:
    pillars = chart["pillars"]
    stems = [pillars[p]["stem"] for p in PILLARS]
    branches = [pillars[p]["branch"] for p in PILLARS]
    day_master = chart["day_master"]
    month_branch = pillars["month"]["branch"]
    growth_stage = chart.get("growth_stage", {})

    return {
        "hidden_stems_weighted": _hidden_stems_weighted(pillars),
        "day_master_context": _day_master_context(pillars, day_master, month_branch, growth_stage),
        "polarity": _polarity(stems, branches),
        "stem_relations": _stem_relations(stems, month_branch, pillars),
        "branch_relations": _branch_relations(branches, month_branch, pillars),
        "storages": _storages(branches),
        "shensha": _shensha(pillars, day_master),
        "element_interactions": _element_interactions(pillars),
        "method_notes": [
            "Structure facts separate detected relations from transformation candidates.",
            "Combination transformation is not asserted unless the transformed element has season or visible support.",
            "Hidden stem weights are conventional engineering weights for scoring, not a classical quotation.",
        ],
    }


def _hidden_stems_weighted(pillars: dict) -> dict:
    result = {}
    for pillar in PILLARS:
        branch = pillars[pillar]["branch"]
        result[pillar] = [
            {"stem": stem, "role": role, "weight": weight}
            for stem, role, weight in HIDDEN_STEMS[branch]
        ]
    return result


def _day_master_context(pillars: dict, day_master: str, month_branch: str, growth_stage: dict) -> dict:
    roots = []
    for pillar in PILLARS:
        branch = pillars[pillar]["branch"]
        for stem, role, weight in HIDDEN_STEMS[branch]:
            if stem == day_master:
                roots.append({"pillar": pillar, "branch": branch, "stem": stem, "role": role, "weight": weight})
    month_stage = growth_stage.get("month")
    return {
        "day_master": day_master,
        "month_branch": month_branch,
        "month_growth_stage": month_stage,
        "season_state": _season_state(month_stage),
        "roots": roots,
        "root_count": len(roots),
        "root_weight": sum(root["weight"] for root in roots),
        "self_seated": {
            "branch": pillars["day"]["branch"],
            "growth_stage": growth_stage.get("day"),
        },
    }


def _season_state(month_stage: str | None) -> str:
    if month_stage in IN_SEASON_STAGES:
        return "in_season"
    if month_stage in WEAK_STAGES:
        return "not_in_season"
    return "neutral"


def _polarity(stems: list[str], branches: list[str]) -> dict:
    stem_polarity = [STEM_POLARITY[stem] for stem in stems]
    branch_polarity = [BRANCH_POLARITY[branch] for branch in branches]
    all_values = stem_polarity + branch_polarity
    return {
        "stems": stem_polarity,
        "branches": branch_polarity,
        "is_all_yin": all(value == "阴" for value in all_values),
        "is_all_yang": all(value == "阳" for value in all_values),
    }


def _stem_relations(stems: list[str], month_branch: str, pillars: dict) -> list[dict]:
    relations = []
    for left, right in combinations(range(len(stems)), 2):
        key = frozenset((stems[left], stems[right]))
        if key in HEAVENLY_COMBINATIONS:
            name, element = HEAVENLY_COMBINATIONS[key]
            supported = _element_supported(element, month_branch, pillars)
            relations.append(
                {
                    "type": "heavenly_combination",
                    "name": name,
                    "stems": [stems[left], stems[right]],
                    "element": element,
                    "status": "detected",
                    "transform_candidate": supported,
                    "note": _transform_note(supported),
                }
            )
        if key in HEAVENLY_CLASHES:
            relations.append(
                {
                    "type": "heavenly_clash",
                    "name": HEAVENLY_CLASHES[key],
                    "stems": [stems[left], stems[right]],
                    "status": "detected",
                    "note": "天干冲作明透干气相战信号，仍须结合合化、旺衰和位置复核。",
                }
            )
    return relations


def _branch_relations(branches: list[str], month_branch: str, pillars: dict) -> list[dict]:
    relations = []
    branch_set = set(branches)
    for combo, (name, element) in THREE_HARMONIES.items():
        if set(combo).issubset(branch_set):
            relations.append(_element_relation("three_harmony", name, list(combo), element, month_branch, pillars, "complete"))
    for combo, (name, element) in THREE_MEETINGS.items():
        if set(combo).issubset(branch_set):
            relations.append(_element_relation("three_meeting", name, list(combo), element, month_branch, pillars, "complete"))
    for left, right in combinations(range(len(branches)), 2):
        pair = frozenset((branches[left], branches[right]))
        branch_pair = [branches[left], branches[right]]
        if pair in SIX_COMBINATIONS:
            name, element = SIX_COMBINATIONS[pair]
            relations.append(_element_relation("six_combination", name, branch_pair, element, month_branch, pillars, "detected"))
        if pair in HALF_HARMONIES:
            name, element = HALF_HARMONIES[pair]
            relations.append(_element_relation("half_harmony", name, branch_pair, element, month_branch, pillars, "partial"))
        if pair in HALF_MEETINGS:
            name, element = HALF_MEETINGS[pair]
            relations.append(_element_relation("half_meeting", name, branch_pair, element, month_branch, pillars, "partial"))
        if pair in SIX_CLASHES:
            relations.append({"type": "six_clash", "name": SIX_CLASHES[pair], "branches": branch_pair, "status": "detected"})
        if pair in SIX_HARMS:
            relations.append({"type": "six_harm", "name": SIX_HARMS[pair], "branches": branch_pair, "status": "detected"})
        if pair in SIX_BREAKS:
            relations.append({"type": "six_break", "name": SIX_BREAKS[pair], "branches": branch_pair, "status": "detected"})
        if pair in PAIR_PUNISHMENTS:
            relations.append({"type": "punishment", "name": PAIR_PUNISHMENTS[pair], "branches": branch_pair, "status": "detected"})
    for combo, name in THREE_PUNISHMENTS.items():
        if combo.issubset(branch_set):
            relations.append({"type": "punishment", "name": name, "branches": sorted(combo), "status": "complete"})
    for branch, name in SELF_PUNISH.items():
        if branches.count(branch) >= 2:
            relations.append({"type": "self_punishment", "name": name, "branches": [branch, branch], "status": "detected"})
    return _dedupe_dicts(relations)


def _element_relation(
    relation_type: str,
    name: str,
    branches: list[str],
    element: str,
    month_branch: str,
    pillars: dict,
    status: str,
) -> dict:
    supported = _element_supported(element, month_branch, pillars)
    return {
        "type": relation_type,
        "name": name,
        "branches": branches,
        "element": element,
        "status": status,
        "transform_candidate": supported,
        "note": _transform_note(supported),
    }


def _element_supported(element: str, month_branch: str, pillars: dict) -> bool:
    if month_branch in ELEMENT_SEASON_BRANCHES[element]:
        return True
    for pillar in PILLARS:
        if STEM_ELEMENTS[pillars[pillar]["stem"]] == element:
            return True
        branch = pillars[pillar]["branch"]
        if any(STEM_ELEMENTS[stem] == element for stem, _role, _weight in HIDDEN_STEMS[branch]):
            return True
    return False


def _transform_note(supported: bool) -> str:
    if supported:
        return "transformation candidate only; final 化气 judgment still needs strength, obstruction, and season review"
    return "detected relation only; transformed element lacks basic season/visible support"


def _storages(branches: list[str]) -> dict:
    result = {}
    branch_set = set(branches)
    for branch in branches:
        if branch not in BRANCH_STORAGE:
            continue
        result[branch] = {
            "stores": BRANCH_STORAGE[branch],
            "opened_by_clash": STORAGE_CLASH[branch] in branch_set,
            "clash_branch": STORAGE_CLASH[branch],
        }
    return result


def _element_interactions(pillars: dict) -> list[dict]:
    stem_items = [
        {"pillar": pillar, "stem": pillars[pillar]["stem"], "element": STEM_ELEMENTS[pillars[pillar]["stem"]]}
        for pillar in PILLARS
    ]
    branch_items = [
        {"pillar": pillar, "branch": pillars[pillar]["branch"], "element": BRANCH_ELEMENTS[pillars[pillar]["branch"]]}
        for pillar in PILLARS
    ]
    return _paired_element_interactions("stem", stem_items) + _paired_element_interactions("branch", branch_items)


def _paired_element_interactions(kind: str, items: list[dict]) -> list[dict]:
    interactions = []
    for left, right in combinations(items, 2):
        left_element = left["element"]
        right_element = right["element"]
        if left_element == right_element:
            continue
        if GENERATES[left_element] == right_element:
            interactions.append(_interaction(kind, "generate", left, right))
        if GENERATES[right_element] == left_element:
            interactions.append(_interaction(kind, "generate", right, left))
        if CONTROLS[left_element] == right_element:
            interactions.append(_interaction(kind, "control", left, right))
        if CONTROLS[right_element] == left_element:
            interactions.append(_interaction(kind, "control", right, left))
    return interactions


def _interaction(kind: str, relation: str, source: dict, target: dict) -> dict:
    source_key = "controller" if relation == "control" else "generator"
    target_key = "controlled" if relation == "control" else "generated"
    return {
        "type": f"{kind}_{relation}",
        source_key: source,
        target_key: target,
    }


def _shensha(pillars: dict, day_master: str) -> list[dict]:
    result = []
    branches_by_pillar = {pillar: pillars[pillar]["branch"] for pillar in PILLARS}
    stems_by_pillar = {pillar: pillars[pillar]["stem"] for pillar in PILLARS}
    for pillar, branch in branches_by_pillar.items():
        if branch in TIANYI[day_master]:
            result.append({"name": "天乙贵人", "basis": "day_stem", "branch": branch, "pillar": pillar})
        if branch == LU[day_master]:
            result.append({"name": "禄神", "basis": "day_stem", "branch": branch, "pillar": pillar})
        if day_master in YANG_REN and branch == YANG_REN[day_master]:
            result.append({"name": "羊刃", "basis": "day_stem", "branch": branch, "pillar": pillar})
        if branch == WENCHANG[day_master]:
            result.append({"name": "文昌", "basis": "day_stem", "branch": branch, "pillar": pillar})
    result.extend(_group_shensha("day_branch", pillars["day"]["branch"], branches_by_pillar))
    result.extend(_group_shensha("year_branch", pillars["year"]["branch"], branches_by_pillar))
    result.extend(_solitary_shensha("year_branch", pillars["year"]["branch"], branches_by_pillar))
    result.extend(_solitary_shensha("day_branch", pillars["day"]["branch"], branches_by_pillar))
    result.extend(_month_virtues(pillars["month"]["branch"], stems_by_pillar, branches_by_pillar))
    result.extend(_dexiu(pillars))
    return _dedupe_dicts(result)


def _group_shensha(basis: str, base_branch: str, branches_by_pillar: dict) -> list[dict]:
    targets = {}
    for group, shensha in GROUP_SHENSHA.items():
        if base_branch in group:
            targets = shensha
            break
    result = []
    for name, target_branch in targets.items():
        for pillar, branch in branches_by_pillar.items():
            if branch == target_branch:
                result.append({"name": name, "basis": basis, "branch": branch, "pillar": pillar})
    return result


def _solitary_shensha(basis: str, base_branch: str, branches_by_pillar: dict) -> list[dict]:
    targets = {}
    for group, shensha in SOLITARY_SHENSHA.items():
        if base_branch in group:
            targets = shensha
            break
    result = []
    for name, target_branch in targets.items():
        for pillar, branch in branches_by_pillar.items():
            if branch == target_branch:
                result.append({"name": name, "basis": basis, "branch": branch, "pillar": pillar})
    return result


def _month_virtues(month_branch: str, stems_by_pillar: dict, branches_by_pillar: dict) -> list[dict]:
    result = []
    tiande_target = TIANDE_BY_MONTH[month_branch]
    for pillar, stem in stems_by_pillar.items():
        if stem == tiande_target:
            result.append({"name": "天德贵人", "basis": "month_branch", "target": tiande_target, "pillar": pillar})
    for pillar, branch in branches_by_pillar.items():
        if branch == tiande_target:
            result.append({"name": "天德贵人", "basis": "month_branch", "target": tiande_target, "pillar": pillar})
    yuede_target = _yuede_target(month_branch)
    for pillar, stem in stems_by_pillar.items():
        if stem == yuede_target:
            result.append({"name": "月德贵人", "basis": "month_branch", "target": yuede_target, "pillar": pillar})
    return result


def _yuede_target(month_branch: str) -> str:
    for group, target in YUEDE_BY_GROUP.items():
        if month_branch in group:
            return target
    raise ValueError(month_branch)


def _dexiu(pillars: dict) -> list[dict]:
    month_branch = pillars["month"]["branch"]
    stems = [pillars[pillar]["stem"] for pillar in PILLARS]
    for group, rule in DEXIU.items():
        if month_branch not in group:
            continue
        de_stems = [stem for stem in stems if stem in rule["de"]]
        xiu_stems = [stem for stem in stems if stem in rule["xiu"]]
        if de_stems and xiu_stems:
            return [
                {
                    "name": "德秀贵人",
                    "basis": "month_branch",
                    "branch": month_branch,
                    "pillar": "month",
                    "de_stems": de_stems,
                    "xiu_stems": xiu_stems,
                    "note": "德秀以月令分组查天干；冲克减力，仍需看整体结构。",
                }
            ]
    return []


def _dedupe_dicts(items: list[dict]) -> list[dict]:
    seen = set()
    result = []
    for item in items:
        key = json.dumps(item, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result
