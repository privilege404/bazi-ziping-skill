from __future__ import annotations

from datetime import datetime

from .engine import BirthInput, build_chart
from .transit import analyze_transit


TOPIC_ORDER = [
    "overall_luck",
    "birth_family",
    "education",
    "wealth",
    "career_official",
    "marriage_relationship",
    "health",
    "children",
    "six_relatives",
    "major_events",
]
TOPIC_LABELS = {
    "overall_luck": "整体运势",
    "birth_family": "出身家境",
    "education": "学历/学习",
    "wealth": "财运",
    "career_official": "事业/官运",
    "marriage_relationship": "婚姻状况",
    "health": "健康",
    "children": "子息",
    "six_relatives": "六亲",
    "major_events": "重大事件触发候选",
}
POLICY = "只列可计算证据和触发，不脱离本命事实直接断吉凶。"


def analyze_life_topics(chart: dict, structure: dict, reading: dict) -> dict:
    return {
        "version": "life-topics-mvp-1",
        "scope": "第一部分：自己的事。覆盖整体运势、出身家境、学历、财、事业、婚姻、健康、子女、六亲、重大事件的结构化证据层。",
        "topics": [
            _overall_luck(chart, structure, reading),
            _birth_family(chart, reading),
            _education(structure, reading),
            _wealth(chart, reading),
            _career_official(reading),
            _marriage_relationship(chart, reading),
            _health(structure, reading),
            _children(reading),
            _six_relatives(chart, reading),
            _major_events(chart, structure, reading),
        ],
        "limits": [
            "专题层不新增排盘事实，只汇总 chart、structure、strength、pattern、transit 中已经计算出的证据。",
            "重大事件只输出高触发年份和主题候选，不直接断已发生/必发生事件。",
            "专题层不直接输出具体事件日期、祸福断语或化解方案；这些需要后续规则卡、用户反馈和案例校准。",
        ],
    }


def _overall_luck(chart: dict, structure: dict, reading: dict) -> dict:
    strength = reading["strength"]
    audit = reading["strength_audit"]
    pattern = reading["pattern_audit"]
    transit = reading["transit"]
    return _topic(
        "overall_luck",
        natal_signals=[
            {"kind": "day_master_strength", "classification": strength["classification"], "score": strength["heuristic_score"]},
            {"kind": "season", "assessment": audit["season"]["assessment"]},
            {"kind": "pattern", "ge_shen": pattern["ge_shen"]["ten_god"], "pattern_name": pattern["ge_shen"]["pattern_name"]},
        ],
        transit_signals=_major_transit_signals(transit),
        risk_flags=_common_risks(structure, reading),
        rule_ids=["topic-overall-luck-mvp-001", "transit-mvp-001", "strength-audit-mvp-001", "pattern-audit-mvp-001"],
        limits=["整体运势只作总览，必须回到具体专题再看十神、宫位和岁运触发。"],
    )


def _wealth(chart: dict, reading: dict) -> dict:
    return _topic(
        "wealth",
        natal_signals=_ten_god_signals(reading, {"正财", "偏财"}),
        transit_signals=_transit_ten_god_signals(reading["transit"], {"正财", "偏财"}),
        risk_flags=_topic_risks(reading, ["财"]),
        rule_ids=["topic-wealth-mvp-001", "yhzp-ten-gods-001", "ten-god-influence-mvp-001", "transit-mvp-001"],
        limits=["财星只说明财富、资源、经营和男命配偶星等信号；是否得财须看身强弱、财星有力无力和岁运引动。"],
    )


def _birth_family(chart: dict, reading: dict) -> dict:
    natal = [
        {"kind": "family_palace", "pillar": "year", "ganzhi": chart["pillars"]["year"]["ganzhi"], "ten_god": chart["ten_gods"]["heaven_stems"]["year"]},
        {"kind": "family_palace", "pillar": "month", "ganzhi": chart["pillars"]["month"]["ganzhi"], "ten_god": chart["ten_gods"]["heaven_stems"]["month"]},
    ]
    natal.extend(_ten_god_signals(reading, {"正印", "偏印", "正财", "偏财"}))
    return _topic(
        "birth_family",
        natal_signals=natal,
        transit_signals=_targeted_transit_relations(reading["transit"], {"year", "month"}),
        risk_flags=_topic_risks(reading, ["印", "财", "年", "月", "刑冲害破"]),
        rule_ids=["topic-birth-family-mvp-001", "yhzp-ten-gods-001", "yhzp-ten-gods-position-001"],
        limits=["出身家境以年柱、月柱、印星、财星作入口，只能提示家庭资源和早年环境信号，不直接断贫富等级。"],
    )


def _education(structure: dict, reading: dict) -> dict:
    natal = _ten_god_signals(reading, {"正印", "偏印", "食神", "伤官"})
    natal.extend(
        {"kind": "education_shensha", **item}
        for item in structure["shensha"]
        if item["name"] in {"文昌", "天乙贵人", "天德贵人", "月德贵人"}
    )
    return _topic(
        "education",
        natal_signals=natal,
        transit_signals=_transit_ten_god_signals(reading["transit"], {"正印", "偏印", "食神", "伤官"}),
        risk_flags=_topic_risks(reading, ["印", "食神", "伤官", "刑冲害破"]),
        rule_ids=["topic-education-mvp-001", "yhzp-ten-gods-001", "smth-common-shensha-001"],
        limits=["学历推测以印星、食伤、文昌/贵人等学习资质信号为入口，不直接断最高学历或考试结果。"],
    )


def _career_official(reading: dict) -> dict:
    risks = _topic_risks(reading, ["官杀", "七杀", "正官"])
    risks.extend(reading["pattern_audit"]["clarity_warnings"])
    return _topic(
        "career_official",
        natal_signals=_ten_god_signals(reading, {"正官", "七杀", "正印", "偏印"}),
        transit_signals=_transit_ten_god_signals(reading["transit"], {"正官", "七杀", "正印", "偏印"}),
        risk_flags=_unique(risks),
        rule_ids=[
            "topic-career-official-mvp-001",
            "yhzp-ten-gods-001",
            "zpxz-officer-killing-mixed-001",
            "pattern-audit-mvp-001",
        ],
        limits=["事业官运先看官杀印食财的结构组合，不能只因流年见官杀就断升迁或灾祸。"],
    )


def _marriage_relationship(chart: dict, reading: dict) -> dict:
    spouse_gods = {"正财", "偏财"} if chart["input"]["gender"] == "male" else {"正官", "七杀"}
    natal = [{**signal, "kind": "spouse_star"} for signal in _ten_god_signals(reading, spouse_gods)]
    natal.append({"kind": "spouse_palace", "pillar": "day", "branch": chart["pillars"]["day"]["branch"]})
    transit = _transit_ten_god_signals(reading["transit"], spouse_gods)
    transit.extend(_targeted_transit_relations(reading["transit"], {"day"}))
    transit.extend(_transit_shensha(reading["transit"], {"桃花", "红鸾", "天喜"}))
    return _topic(
        "marriage_relationship",
        natal_signals=natal,
        transit_signals=transit,
        risk_flags=_topic_risks(reading, ["桃花", "日支", "刑冲害破"]),
        rule_ids=["topic-marriage-mvp-001", "yhzp-ten-gods-001", "yhzp-clash-harm-break-001", "xjbf-shensha-aux-001"],
        limits=["婚恋专题MVP只看配偶星、日支配偶宫、桃花和岁运触发；不直接判断婚期、离合或对象细节。"],
    )


def _health(structure: dict, reading: dict) -> dict:
    transit = reading["transit"]
    risks = _common_risks(structure, reading)
    regulation = reading["regulation"]
    if regulation["status"] == "not_covered":
        risks.append("调候规则未覆盖")
    else:
        risks.extend(regulation["warnings"])
    topic = _topic(
        "health",
        natal_signals=[
            {"kind": "strength", "classification": reading["strength"]["classification"]},
            {"kind": "regulation", "status": regulation["status"], "key": regulation["key"]},
            {"kind": "element_counts", "counts": reading["summary"].get("element_counts", {})},
        ],
        transit_signals=_disruptive_transit_signals(transit),
        risk_flags=_unique(risks),
        rule_ids=[
            "topic-health-mvp-001",
            "shenfeng-disease-medicine-001",
            "qianli-season-strength-001",
            "yhzp-clash-harm-break-001",
            "health-facts-wuxing-body-correspondence-001",
            "health-facts-imbalance-context-001",
            "health-facts-transit-disruption-001",
        ],
        limits=["健康专题只提示五行偏枯、调候、刑冲害破等命理信号，不作医学诊断。"],
    )
    topic["health_facts"] = reading["health_facts"]
    return topic


def _children(reading: dict) -> dict:
    return _topic(
        "children",
        natal_signals=_ten_god_signals(reading, {"食神", "伤官"}),
        transit_signals=_transit_ten_god_signals(reading["transit"], {"食神", "伤官"}),
        risk_flags=_topic_risks(reading, ["食神", "伤官", "子女"]),
        rule_ids=["topic-children-mvp-001", "yhzp-ten-gods-001", "ten-god-influence-mvp-001"],
        limits=["子女专题MVP以食伤为子女/表达输出信号的复核入口；性别细分、孕育年份和子女数量不在当前层直接判断。"],
    )


def _six_relatives(chart: dict, reading: dict) -> dict:
    spouse_gods = {"正财", "偏财"} if chart["input"]["gender"] == "male" else {"正官", "七杀"}
    natal = []
    natal.extend(_relative_signals(reading, "parents_family", {"正印", "偏印", "正财", "偏财"}))
    natal.extend(_relative_signals(reading, "siblings_peers", {"比肩", "劫财"}))
    natal.extend(_relative_signals(reading, "spouse", spouse_gods))
    natal.extend(_relative_signals(reading, "children", {"食神", "伤官"}))
    return _topic(
        "six_relatives",
        natal_signals=natal,
        transit_signals=_major_transit_signals(reading["transit"]),
        risk_flags=_topic_risks(reading, ["官杀", "财", "印", "比肩", "劫财", "食神", "伤官", "刑冲害破"]),
        rule_ids=["topic-six-relatives-mvp-001", "yhzp-ten-gods-001", "yhzp-ten-gods-position-001"],
        limits=["六亲专题只列十神入口和宫位触发；具体父母、兄弟、配偶、子女事件需要结合实际关系和岁运校准。"],
    )


def _major_events(chart: dict, structure: dict, reading: dict) -> dict:
    windows = _event_windows(chart, structure, reading)
    return _topic(
        "major_events",
        natal_signals=[
            {"kind": "current_luck", "cycle": reading["transit"]["current_luck"]},
            {"kind": "natal_risks", "risk_flags": _common_risks(structure, reading)},
        ],
        transit_signals=windows,
        risk_flags=_unique([flag for window in windows for flag in window["themes"]]),
        rule_ids=["topic-major-events-mvp-001", "transit-mvp-001", "transit-group-completion-001", "yhzp-clash-harm-break-001"],
        limits=["重大事件专题只扫描目标年前后三年的高触发年份；需要用户反馈后才能校准为历史事件或未来重点年份。"],
    )


def _topic(topic: str, natal_signals: list[dict], transit_signals: list[dict], risk_flags: list[str], rule_ids: list[str], limits: list[str]) -> dict:
    return {
        "topic": topic,
        "label": TOPIC_LABELS[topic],
        "natal_signals": natal_signals or [{"kind": "not_observed", "note": "当前MVP未见明确本命信号"}],
        "transit_signals": transit_signals,
        "risk_flags": _unique(risk_flags),
        "rule_ids": rule_ids,
        "limits": limits,
        "decision_policy": POLICY,
    }


def _ten_god_signals(reading: dict, ten_gods: set[str]) -> list[dict]:
    result = []
    by_ten_god = reading["ten_god_influence"]["by_ten_god"]
    for ten_god in sorted(ten_gods):
        item = by_ten_god[ten_god]
        if not item["present"]:
            continue
        result.append(
            {
                "kind": "ten_god",
                "ten_god": ten_god,
                "score": item["score"],
                "level": item["influence_level"],
                "visible_positions": item["visible_positions"],
                "hidden_positions": item["hidden_positions"],
                "flags": item["flags"],
            }
        )
    return result


def _transit_ten_god_signals(transit: dict, ten_gods: set[str]) -> list[dict]:
    result = []
    for external_name in ["current_luck", "annual"]:
        external = transit[external_name]
        if not external:
            continue
        if external["stem_ten_god"] in ten_gods:
            result.append({"kind": "transit_stem_ten_god", "external": external_name, "ganzhi": external["ganzhi"], "ten_god": external["stem_ten_god"]})
        for hidden in external["hidden_stems"]:
            if hidden["ten_god"] in ten_gods:
                result.append(
                    {
                        "kind": "transit_hidden_ten_god",
                        "external": external_name,
                        "ganzhi": external["ganzhi"],
                        "stem": hidden["stem"],
                        "ten_god": hidden["ten_god"],
                        "role": hidden["role"],
                    }
                )
    return result


def _major_transit_signals(transit: dict) -> list[dict]:
    signals = []
    if transit["current_luck"]:
        signals.append({"kind": "current_luck", "ganzhi": transit["current_luck"]["ganzhi"], "stem_ten_god": transit["current_luck"]["stem_ten_god"]})
    signals.append({"kind": "annual", "ganzhi": transit["annual"]["ganzhi"], "stem_ten_god": transit["annual"]["stem_ten_god"]})
    signals.extend(transit["relation_triggers"][:8])
    signals.extend(transit["storage_triggers"])
    signals.extend(transit["shensha_triggers"][:6])
    return signals


def _relative_signals(reading: dict, relative: str, ten_gods: set[str]) -> list[dict]:
    signals = []
    for signal in _ten_god_signals(reading, ten_gods):
        signals.append({**signal, "relative": relative})
    if not signals:
        signals.append({"kind": "relative_not_observed", "relative": relative, "ten_gods": sorted(ten_gods)})
    return signals


def _event_windows(chart: dict, structure: dict, reading: dict) -> list[dict]:
    target_year = reading["transit"]["target_year"]
    birth = _birth_from_chart(chart)
    windows = []
    for year in range(target_year - 3, target_year + 4):
        year_chart = build_chart(birth, target_year=year)
        transit = analyze_transit(year_chart, structure)
        windows.append(_event_window(year, transit))
    return sorted(windows, key=lambda item: (-item["score"], item["year"]))


def _event_window(year: int, transit: dict) -> dict:
    relation_triggers = transit["relation_triggers"]
    storage_triggers = transit["storage_triggers"]
    shensha_triggers = transit["shensha_triggers"]
    disruptive = {"six_clash", "six_harm", "six_break", "punishment", "self_punishment", "heavenly_clash", "stem_control"}
    score = 0
    themes = []
    for trigger in relation_triggers:
        if trigger["type"] in disruptive:
            score += 3
            themes.append("刑冲克害")
        elif trigger["type"] in {"three_harmony", "three_meeting"}:
            score += 2
            themes.append("合会成局候选")
        else:
            score += 1
        target = trigger.get("target")
        if target == "day" or (isinstance(target, list) and "day" in target):
            score += 2
            themes.append("day_pillar")
        if target == "month" or (isinstance(target, list) and "month" in target):
            score += 2
            themes.append("month_pillar")
    if storage_triggers:
        score += 4 * len(storage_triggers)
        themes.append("墓库冲动")
    if shensha_triggers:
        score += len(shensha_triggers)
        themes.append("神煞应期")
    score += len(transit["focus_ten_gods"])
    themes.extend(_ten_god_themes(transit["focus_ten_gods"]))
    return {
        "year": year,
        "annual": transit["annual"]["ganzhi"],
        "current_luck": transit["current_luck"]["ganzhi"] if transit["current_luck"] else None,
        "score": score,
        "themes": _unique(themes),
        "trigger_names": _unique([item["name"] for item in relation_triggers + storage_triggers + shensha_triggers])[:12],
        "focus_ten_gods": transit["focus_ten_gods"],
    }


def _ten_god_themes(ten_gods: list[str]) -> list[str]:
    themes = []
    if any(god in ten_gods for god in ["正财", "偏财"]):
        themes.append("财务/资源")
    if any(god in ten_gods for god in ["正官", "七杀"]):
        themes.append("事业/压力")
    if any(god in ten_gods for god in ["正印", "偏印"]):
        themes.append("学习/资质/文书")
    if any(god in ten_gods for god in ["食神", "伤官"]):
        themes.append("表达/子息/输出")
    if any(god in ten_gods for god in ["比肩", "劫财"]):
        themes.append("同辈/竞争")
    return themes


def _birth_from_chart(chart: dict) -> BirthInput:
    dt = datetime.fromisoformat(chart["input"]["datetime"])
    return BirthInput(
        year=dt.year,
        month=dt.month,
        day=dt.day,
        hour=dt.hour,
        minute=dt.minute,
        second=dt.second,
        gender=chart["input"]["gender"],
        day_boundary=chart["day_boundary"],
        timezone_offset=chart["input"]["timezone_offset"],
        longitude=chart["input"]["longitude"],
        solar_time_mode=chart["input"]["solar_time_mode"],
    )


def _targeted_transit_relations(transit: dict, targets: set[str]) -> list[dict]:
    result = []
    for item in transit["relation_triggers"]:
        target = item.get("target")
        if isinstance(target, list):
            if targets.intersection(target):
                result.append(item)
        elif target in targets:
            result.append(item)
    return result


def _disruptive_transit_signals(transit: dict) -> list[dict]:
    disruptive = {"six_clash", "six_harm", "six_break", "punishment", "self_punishment", "heavenly_clash", "stem_control"}
    result = [item for item in transit["relation_triggers"] if item["type"] in disruptive]
    result.extend(transit["storage_triggers"])
    return result


def _transit_shensha(transit: dict, names: set[str]) -> list[dict]:
    return [item for item in transit["shensha_triggers"] if item["name"] in names]


def _common_risks(structure: dict, reading: dict) -> list[str]:
    risks = []
    risks.extend(reading["strength_audit"]["relation_modifiers"]["disruptive_relations"])
    risks.extend(reading["pattern_audit"]["clarity_warnings"])
    if structure["storages"]:
        risks.append("命局有墓库，遇冲合岁运需复核所藏十神")
    return _unique(risks)


def _topic_risks(reading: dict, keywords: list[str]) -> list[str]:
    risks = []
    for warning in reading["ten_god_influence"]["structural_warnings"] + reading["pattern_audit"]["clarity_warnings"]:
        if any(keyword in warning for keyword in keywords) or "刑冲害破" in warning:
            risks.append(warning)
    return _unique(risks)


def _unique(items: list[str]) -> list[str]:
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result
