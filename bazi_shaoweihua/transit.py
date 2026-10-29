from __future__ import annotations

from .structure import (
    BRANCH_STORAGE,
    HALF_HARMONIES,
    HALF_MEETINGS,
    HIDDEN_STEMS,
    HEAVENLY_COMBINATIONS,
    HEAVENLY_CLASHES,
    GROUP_SHENSHA,
    LU,
    PAIR_PUNISHMENTS,
    SELF_PUNISH,
    SIX_BREAKS,
    SIX_CLASHES,
    SIX_COMBINATIONS,
    SIX_HARMS,
    SOLITARY_SHENSHA,
    STORAGE_CLASH,
    THREE_HARMONIES,
    THREE_MEETINGS,
    TIANYI,
    TIANDE_BY_MONTH,
    WENCHANG,
    YANG_REN,
    YUEDE_BY_GROUP,
)


PILLARS = ["year", "month", "day", "hour"]
STEMS = "甲乙丙丁戊己庚辛壬癸"
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
GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
CONTROLS = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}


def analyze_transit(chart: dict, structure: dict) -> dict:
    day_master = chart["day_master"]
    current_luck = chart["luck"]["current_cycle"]
    annual = chart["annual"]
    luck_payload = _external_pillar(current_luck, day_master) if _has_pillar_ganzhi(current_luck) else None
    annual_payload = _external_pillar(annual, day_master)
    return {
        "version": "transit-mvp-1",
        "target_year": annual["target_year"],
        "current_luck": luck_payload,
        "annual": annual_payload,
        "relation_triggers": _relation_triggers(chart, luck_payload, annual_payload),
        "storage_triggers": _storage_triggers(chart, luck_payload, annual_payload),
        "shensha_triggers": _shensha_triggers(chart, luck_payload, annual_payload),
        "focus_ten_gods": _focus_ten_gods(luck_payload, annual_payload),
        "decision_policy": "岁运只作为触发层，必须回扣本命结构。",
        "caveat": "岁运MVP只列干支十神和关系触发，不直接断具体事件吉凶。",
    }


def _external_pillar(pillar: dict, day_master: str) -> dict:
    ganzhi = pillar["ganzhi"]
    stem = pillar.get("stem") or ganzhi[0]
    branch = pillar.get("branch") or ganzhi[1]
    return {
        **pillar,
        "stem": stem,
        "branch": branch,
        "stem_ten_god": _ten_god(day_master, stem),
        "branch_ten_gods": [_ten_god(day_master, hidden[0]) for hidden in HIDDEN_STEMS[branch]],
        "hidden_stems": [
            {"stem": stem_item, "role": role, "weight": weight, "ten_god": _ten_god(day_master, stem_item)}
            for stem_item, role, weight in HIDDEN_STEMS[branch]
        ],
    }


def _has_pillar_ganzhi(pillar: dict | None) -> bool:
    return bool(pillar and isinstance(pillar.get("ganzhi"), str) and len(pillar["ganzhi"]) >= 2)


def _relation_triggers(chart: dict, luck: dict | None, annual: dict) -> list[dict]:
    triggers = []
    externals = []
    if luck:
        externals.append(("luck", luck))
    externals.append(("annual", annual))
    for external_name, external in externals:
        for pillar in PILLARS:
            natal = chart["pillars"][pillar]
            triggers.extend(_stem_relation(external_name, external, pillar, natal))
            triggers.extend(_branch_relation(external_name, external, pillar, natal))
    if luck:
        triggers.extend(_stem_relation("annual", annual, "luck", luck))
        triggers.extend(_branch_relation("annual", annual, "luck", luck))
    triggers.extend(_group_completion_triggers(chart, luck, annual))
    return _dedupe_dicts(triggers)


def _stem_relation(external_name: str, external: dict, natal_name: str, natal: dict) -> list[dict]:
    triggers = []
    relation = HEAVENLY_COMBINATIONS.get(frozenset((external["stem"], natal["stem"])))
    if relation:
        name, element = relation
        triggers.append(
            {
                "type": "heavenly_combination",
                "name": name,
                "external": external_name,
                "target": natal_name,
                "element": element,
                "status": "trigger",
            }
        )
    clash = HEAVENLY_CLASHES.get(frozenset((external["stem"], natal["stem"])))
    if clash:
        triggers.append(
            {
                "type": "heavenly_clash",
                "name": clash,
                "external": external_name,
                "target": natal_name,
                "status": "trigger",
            }
        )
    triggers.extend(_stem_element_triggers(external_name, external, natal_name, natal))
    return triggers


def _stem_element_triggers(external_name: str, external: dict, target_name: str, target: dict) -> list[dict]:
    external_element = STEM_ELEMENTS[external["stem"]]
    target_element = STEM_ELEMENTS[target["stem"]]
    if external_element == target_element:
        return []
    if GENERATES[external_element] == target_element:
        return [
            {
                "type": "stem_generate",
                "name": f"{external['stem']}生{target['stem']}",
                "external": external_name,
                "target": target_name,
                "generator": external["stem"],
                "generated": target["stem"],
                "status": "trigger",
            }
        ]
    if GENERATES[target_element] == external_element:
        return [
            {
                "type": "stem_generate",
                "name": f"{target['stem']}生{external['stem']}",
                "external": external_name,
                "target": target_name,
                "generator": target["stem"],
                "generated": external["stem"],
                "status": "trigger",
            }
        ]
    if CONTROLS[external_element] == target_element:
        return [
            {
                "type": "stem_control",
                "name": f"{external['stem']}克{target['stem']}",
                "external": external_name,
                "target": target_name,
                "controller": external["stem"],
                "controlled": target["stem"],
                "status": "trigger",
            }
        ]
    if CONTROLS[target_element] == external_element:
        return [
            {
                "type": "stem_control",
                "name": f"{target['stem']}克{external['stem']}",
                "external": external_name,
                "target": target_name,
                "controller": target["stem"],
                "controlled": external["stem"],
                "status": "trigger",
            }
        ]
    return []


def _group_completion_triggers(chart: dict, luck: dict | None, annual: dict) -> list[dict]:
    external_items = []
    if luck:
        external_items.append(("luck", luck))
    external_items.append(("annual", annual))
    triggers = []
    for external_name, external in external_items:
        other_items = [(pillar, chart["pillars"][pillar]) for pillar in PILLARS]
        for other_external_name, other_external in external_items:
            if other_external_name != external_name:
                other_items.append((other_external_name, other_external))
        triggers.extend(_group_completion_for_external(external_name, external, other_items))
    return triggers


def _group_completion_for_external(external_name: str, external: dict, other_items: list[tuple[str, dict]]) -> list[dict]:
    triggers = []
    for combo, (name, element) in THREE_HARMONIES.items():
        triggers.extend(_complete_group("three_harmony", combo, name, element, external_name, external, other_items))
    for combo, (name, element) in THREE_MEETINGS.items():
        triggers.extend(_complete_group("three_meeting", combo, name, element, external_name, external, other_items))
    return triggers


def _complete_group(
    relation_type: str,
    combo: tuple[str, str, str],
    name: str,
    element: str,
    external_name: str,
    external: dict,
    other_items: list[tuple[str, dict]],
) -> list[dict]:
    if external["branch"] not in combo:
        return []
    needed = [branch for branch in combo if branch != external["branch"]]
    matches = [(name_, item) for name_, item in other_items if item["branch"] in needed]
    if {item["branch"] for _name, item in matches} != set(needed):
        return []
    return [
        {
            "type": relation_type,
            "name": name,
            "branches": list(combo),
            "external": external_name,
            "target": [name_ for name_, item in matches if item["branch"] in needed],
            "element": element,
            "status": "completed_by_external",
        }
    ]


def _branch_relation(external_name: str, external: dict, natal_name: str, natal: dict) -> list[dict]:
    pair = frozenset((external["branch"], natal["branch"]))
    branch_pair = [external["branch"], natal["branch"]]
    triggers = []
    if pair in SIX_COMBINATIONS:
        name, element = SIX_COMBINATIONS[pair]
        triggers.append(_branch_trigger("six_combination", name, branch_pair, external_name, natal_name, element))
    if pair in HALF_HARMONIES:
        name, element = HALF_HARMONIES[pair]
        triggers.append(_branch_trigger("half_harmony", name, branch_pair, external_name, natal_name, element))
    if pair in HALF_MEETINGS:
        name, element = HALF_MEETINGS[pair]
        triggers.append(_branch_trigger("half_meeting", name, branch_pair, external_name, natal_name, element))
    if pair in SIX_CLASHES:
        triggers.append(_branch_trigger("six_clash", SIX_CLASHES[pair], branch_pair, external_name, natal_name))
    if pair in SIX_HARMS:
        triggers.append(_branch_trigger("six_harm", SIX_HARMS[pair], branch_pair, external_name, natal_name))
    if pair in SIX_BREAKS:
        triggers.append(_branch_trigger("six_break", SIX_BREAKS[pair], branch_pair, external_name, natal_name))
    if pair in PAIR_PUNISHMENTS:
        triggers.append(_branch_trigger("punishment", PAIR_PUNISHMENTS[pair], branch_pair, external_name, natal_name))
    if external["branch"] == natal["branch"] and external["branch"] in SELF_PUNISH:
        triggers.append(_branch_trigger("self_punishment", SELF_PUNISH[external["branch"]], branch_pair, external_name, natal_name))
    return triggers


def _branch_trigger(
    relation_type: str,
    name: str,
    branches: list[str],
    external_name: str,
    natal_name: str,
    element: str | None = None,
) -> dict:
    trigger = {
        "type": relation_type,
        "name": name,
        "branches": branches,
        "external": external_name,
        "target": natal_name,
        "status": "trigger",
    }
    if element:
        trigger["element"] = element
    return trigger


def _storage_triggers(chart: dict, luck: dict | None, annual: dict) -> list[dict]:
    triggers = []
    externals = []
    if luck:
        externals.append(("luck", luck))
    externals.append(("annual", annual))
    for external_name, external in externals:
        for pillar in PILLARS:
            natal = chart["pillars"][pillar]
            if natal["branch"] in BRANCH_STORAGE and STORAGE_CLASH[natal["branch"]] == external["branch"]:
                triggers.append(
                    {
                        "type": "storage_activation",
                        "name": f"{natal['branch']}{external['branch']}冲开{BRANCH_STORAGE[natal['branch']]}库候选",
                        "external": external_name,
                        "target": pillar,
                        "storage_branch": natal["branch"],
                        "clash_branch": external["branch"],
                        "stores": BRANCH_STORAGE[natal["branch"]],
                        "status": "trigger",
                    }
                )
    return _dedupe_dicts(triggers)


def _shensha_triggers(chart: dict, luck: dict | None, annual: dict) -> list[dict]:
    triggers = []
    externals = []
    if luck:
        externals.append(("luck", luck))
    externals.append(("annual", annual))
    for external_name, external in externals:
        triggers.extend(_external_shensha_for(external_name, external, chart))
    return _dedupe_dicts(triggers)


def _external_shensha_for(external_name: str, external: dict, chart: dict) -> list[dict]:
    day_master = chart["day_master"]
    branch = external["branch"]
    stem = external["stem"]
    pillars = chart["pillars"]
    result = []
    if branch in TIANYI[day_master]:
        result.append(_external_shensha("天乙贵人", external_name, "day_stem", branch=branch))
    if branch == LU[day_master]:
        result.append(_external_shensha("禄神", external_name, "day_stem", branch=branch))
    if day_master in YANG_REN and branch == YANG_REN[day_master]:
        result.append(_external_shensha("羊刃", external_name, "day_stem", branch=branch))
    if branch == WENCHANG[day_master]:
        result.append(_external_shensha("文昌", external_name, "day_stem", branch=branch))
    result.extend(_external_group_shensha(external_name, "day_branch", pillars["day"]["branch"], branch))
    result.extend(_external_group_shensha(external_name, "year_branch", pillars["year"]["branch"], branch))
    result.extend(_external_solitary_shensha(external_name, "year_branch", pillars["year"]["branch"], branch))
    result.extend(_external_solitary_shensha(external_name, "day_branch", pillars["day"]["branch"], branch))
    result.extend(_external_month_virtues(external_name, pillars["month"]["branch"], stem, branch))
    return result


def _external_shensha(name: str, external_name: str, basis: str, branch: str | None = None, target: str | None = None) -> dict:
    item = {"name": name, "external": external_name, "basis": basis}
    if branch:
        item["branch"] = branch
    if target:
        item["target"] = target
    return item


def _external_group_shensha(external_name: str, basis: str, base_branch: str, external_branch: str) -> list[dict]:
    for group, shensha in GROUP_SHENSHA.items():
        if base_branch not in group:
            continue
        return [
            _external_shensha(name, external_name, basis, branch=external_branch)
            for name, target_branch in shensha.items()
            if target_branch == external_branch
        ]
    return []


def _external_solitary_shensha(external_name: str, basis: str, base_branch: str, external_branch: str) -> list[dict]:
    for group, shensha in SOLITARY_SHENSHA.items():
        if base_branch not in group:
            continue
        return [
            _external_shensha(name, external_name, basis, branch=external_branch)
            for name, target_branch in shensha.items()
            if target_branch == external_branch
        ]
    return []


def _external_month_virtues(external_name: str, month_branch: str, external_stem: str, external_branch: str) -> list[dict]:
    result = []
    tiande_target = TIANDE_BY_MONTH[month_branch]
    if external_stem == tiande_target or external_branch == tiande_target:
        result.append(_external_shensha("天德贵人", external_name, "month_branch", target=tiande_target))
    yuede_target = _yuede_target(month_branch)
    if external_stem == yuede_target:
        result.append(_external_shensha("月德贵人", external_name, "month_branch", target=yuede_target))
    return result


def _yuede_target(month_branch: str) -> str:
    for group, target in YUEDE_BY_GROUP.items():
        if month_branch in group:
            return target
    raise ValueError(month_branch)


def _focus_ten_gods(luck: dict | None, annual: dict) -> list[str]:
    gods = []
    for item in [luck, annual]:
        if not item:
            continue
        gods.append(item["stem_ten_god"])
        gods.extend(item["branch_ten_gods"])
    return _unique(gods)


def _ten_god(day_master: str, other_stem: str) -> str:
    if day_master == other_stem:
        return "比肩"
    day_element = STEM_ELEMENTS[day_master]
    other_element = STEM_ELEMENTS[other_stem]
    same_polarity = STEM_POLARITY[day_master] == STEM_POLARITY[other_stem]
    if day_element == other_element:
        return "比肩" if same_polarity else "劫财"
    if GENERATES[other_element] == day_element:
        return "偏印" if same_polarity else "正印"
    if GENERATES[day_element] == other_element:
        return "食神" if same_polarity else "伤官"
    if CONTROLS[day_element] == other_element:
        return "偏财" if same_polarity else "正财"
    if CONTROLS[other_element] == day_element:
        return "七杀" if same_polarity else "正官"
    raise ValueError((day_master, other_stem))


def _unique(items: list[str]) -> list[str]:
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result


def _dedupe_dicts(items: list[dict]) -> list[dict]:
    result = []
    seen = set()
    for item in items:
        key = str(sorted(item.items()))
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result
