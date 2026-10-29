from __future__ import annotations

from collections import Counter

from .pattern import analyze_pattern
from .pattern_audit import analyze_pattern_audit
from .regulation import analyze_regulation
from .health_facts import build_health_facts
from .strength import analyze_strength
from .strength_audit import analyze_strength_audit
from .synthesis import build_natal_synthesis
from .ten_god_influence import analyze_ten_god_influence
from .topics import analyze_life_topics
from .transit import analyze_transit


TEN_GOD_GROUPS = {
    "supporting_day_master": {"正印", "偏印"},
    "same_party": {"比肩", "劫财"},
    "output": {"食神", "伤官"},
    "wealth": {"正财", "偏财"},
    "controlling_day_master": {"正官", "七杀"},
}


def build_natal_reading(chart: dict, structure: dict, report: dict) -> dict:
    ten_god_profile = _ten_god_profile(chart)
    strength = analyze_strength(chart, structure)
    strength_audit = analyze_strength_audit(chart, structure)
    ten_god_influence = analyze_ten_god_influence(chart, structure)
    pattern = analyze_pattern(chart, structure)
    pattern_audit = analyze_pattern_audit(chart, structure)
    regulation = analyze_regulation(chart, structure)
    transit = analyze_transit(chart, structure)
    reading = {
        "version": "natal-mvp-1",
        "scope": "本命MVP，不含完整岁运断事",
        "summary": report["summary"],
        "ten_god_profile": ten_god_profile,
        "ten_god_influence": ten_god_influence,
        "strength": strength,
        "strength_audit": strength_audit,
        "pattern": pattern,
        "pattern_audit": pattern_audit,
        "regulation": regulation,
        "transit": transit,
        "natal_findings": [
            _month_command_finding(chart, structure),
            _strength_finding(strength),
            _strength_audit_finding(strength_audit),
            _pattern_finding(pattern),
            _pattern_audit_finding(pattern_audit),
            _regulation_finding(regulation),
            _ten_god_finding(ten_god_profile),
            _ten_god_influence_finding(ten_god_influence),
            _roots_finding(structure),
            _relations_finding(structure),
            _shensha_finding(structure),
        ],
        "limits": [
            "旺衰评分为MVP启发式，不能把本命MVP结论当作最终喜忌。",
            "旺衰复核层只列证据，不直接覆盖最终强弱。",
            "十神影响力表只排序透藏和位置，不直接断六亲事件。",
            "格局复核层只列成格/破格条件，不直接断格局高低。",
            "调候用神仅覆盖少量已测试组合，尚未完成全量《穷通宝典》规则。",
            "合化只标候选，不直接断定成化。",
        ],
    }
    reading["health_facts"] = build_health_facts(chart, structure, reading)
    reading["life_topics"] = analyze_life_topics(chart, structure, reading)
    reading["synthesis"] = build_natal_synthesis(chart, structure, reading)
    return reading


def _pattern_audit_finding(audit: dict) -> dict:
    ge = audit["ge_shen"]
    signals = "、".join(audit["structure_signals"]) or "暂无组合信号"
    supports = "、".join(audit["success_supports"]) or "暂无成格支持"
    gaps = "、".join(audit["condition_gaps"]) or "暂无明显缺口"
    warnings = "、".join(audit["clarity_warnings"]) or "暂无清浊警告"
    return {
        "title": "格局复核MVP",
        "evidence": f"格神={ge['ten_god']}，格名={ge['pattern_name']}；支持={supports}；缺口={gaps}。",
        "conclusion": f"结构信号={signals}；清浊警告={warnings}。{audit['decision']}。",
        "rule_ids": ["pattern-audit-mvp-001", "zpxz-pattern-candidate-001", "zpxz-pattern-combo-001"],
    }


def _ten_god_influence_finding(influence: dict) -> dict:
    top_names = "、".join(item["ten_god"] for item in influence["top_ten_gods"][:3]) or "无"
    signals = "、".join(influence["combination_signals"]) or "暂无组合信号"
    warnings = "、".join(influence["structural_warnings"]) or "暂无结构警告"
    month = influence["month_command"]
    return {
        "title": "十神影响力MVP",
        "evidence": f"月令主气={month['ten_god']}({month['stem']}藏{month['branch']})；影响力前三={top_names}。",
        "conclusion": f"组合信号={signals}；结构警告={warnings}。该表只作十神复核顺序。",
        "rule_ids": ["ten-god-influence-mvp-001", "yhzp-ten-gods-001", "yhzp-ten-gods-position-001"],
    }


def _strength_audit_finding(audit: dict) -> dict:
    pressure = audit["pressure"]
    modifiers = audit["relation_modifiers"]
    visible_pressure = "、".join(pressure["visible_pressure_ten_gods"]) or "无明显明透压力"
    support_relations = "、".join(modifiers["supportive_relations"]) or "无明显扶身合会"
    disruptive = "、".join(modifiers["disruptive_relations"]) or "无明显刑冲破害扰动"
    return {
        "title": "旺衰复核MVP",
        "evidence": (
            f"{audit['season']['assessment']}；{audit['rooting']['assessment']}；"
            f"明透扶身={audit['assistance']['visible_supporting_ten_gods']}；"
            f"明透泄耗克身={visible_pressure}；扶身合会={support_relations}；扰动={disruptive}。"
        ),
        "conclusion": "旺衰需由得令、得地、得助、受制与合冲扰动共同复核，当前不直接推出最终喜忌。",
        "rule_ids": [
            "strength-audit-mvp-001",
            "qianli-season-strength-001",
            "yhzp-hidden-root-001",
            "yhzp-ten-gods-position-001",
            "dts-flow-combination-001",
        ],
    }


def _regulation_finding(regulation: dict) -> dict:
    if regulation["status"] == "not_covered":
        return {
            "title": "调候用神MVP",
            "evidence": f"{regulation['key']}组合尚未在调候规则表中覆盖。",
            "conclusion": "不据此判断调候喜忌；需要补规则卡和测试后再分析。",
            "rule_ids": [],
        }
    primary = regulation["primary"]
    assistant_text = "，辅以" + "、".join(item["stem"] for item in regulation["assistants"]) if regulation["assistants"] else ""
    presence = _presence_text(primary)
    warnings = "；".join(regulation["warnings"]) if regulation["warnings"] else "暂未见调候警告"
    return {
        "title": "调候用神MVP",
        "evidence": f"{regulation['key'][0]}日主生{regulation['key'][1]}月，按{regulation['source']}取{primary['stem']}{assistant_text}；{presence}。",
        "conclusion": f"{regulation['principle']} 当前状态={regulation['status']}；{warnings}。",
        "rule_ids": [regulation["rule_id"]],
    }


def _presence_text(item: dict) -> str:
    if item["visible"]:
        positions = "、".join(position["label"] for position in item["visible_positions"])
        return f"{item['stem']}透于{positions}干"
    if item["hidden"]:
        positions = "、".join(f"{hidden['pillar']}支{hidden['branch']}" for hidden in item["hidden"])
        return f"{item['stem']}藏于{positions}"
    return f"{item['stem']}未见"


def _pattern_finding(pattern: dict) -> dict:
    transmitted = "；".join(
        f"{item['pillar']}干{item['stem']}为{item['ten_god']}"
        for item in pattern["transmitted_ten_gods"]
    )
    combo = "；".join(item["name"] for item in pattern["combination_candidates"]) or "暂无组合候选"
    warnings = "；".join(pattern["warnings"]) or "暂无明显破损警告"
    return {
        "title": "格局候选MVP",
        "evidence": (
            f"月令{pattern['month_command']['branch']}主气"
            f"{pattern['month_command']['main_stem']}为{pattern['month_command']['main_ten_god']}；"
            f"透干={transmitted}；组合={combo}；警告={warnings}。"
        ),
        "conclusion": f"{pattern['primary_candidate']['name']}；{pattern['decision']}。",
        "rule_ids": pattern["primary_candidate"]["rule_ids"] + ["zpxz-pattern-combo-001"],
    }


def _strength_finding(strength: dict) -> dict:
    return {
        "title": "旺衰评分MVP",
        "evidence": (
            f"季令={strength['season']['state']}({strength['season']['score']})；"
            f"根气={strength['roots']['root_score']}；"
            f"扶身={strength['support']['total_support_score']}；"
            f"泄耗克身={strength['pressure']['total_pressure_score']}；"
            f"总分={strength['heuristic_score']}。"
        ),
        "conclusion": strength["summary"],
        "rule_ids": ["qianli-season-strength-001", "yhzp-hidden-root-001", "wuxing-generating-controlling-001"],
    }


def _ten_god_profile(chart: dict) -> dict:
    visible = chart["ten_gods"]["heaven_stems"]
    hidden = chart["ten_gods"]["earth_branches"]
    visible_values = [god for pillar, god in visible.items() if pillar != "day" and god != "日主"]
    hidden_values = [god for gods in hidden.values() for god in gods]
    visible_counts = Counter(visible_values)
    hidden_counts = Counter(hidden_values)
    relationships = {}
    all_gods = set(visible_values) | set(hidden_values)
    for key, gods in TEN_GOD_GROUPS.items():
        relationships[key] = sorted(god for god in all_gods if god in gods)
    return {
        "visible_by_pillar": visible,
        "hidden_by_pillar": hidden,
        "visible_counts": dict(visible_counts),
        "hidden_counts": dict(hidden_counts),
        "relationships": relationships,
    }


def _month_command_finding(chart: dict, structure: dict) -> dict:
    context = structure["day_master_context"]
    return {
        "title": "月令与日主",
        "evidence": (
            f"{context['day_master']}日主生{context['month_branch']}月，"
            f"月令十二长生为{context['month_growth_stage']}，"
            f"得令状态={context['season_state']}。"
        ),
        "conclusion": (
            f"{context['day_master']}日主生{context['month_branch']}月，"
            "先以月令为纲，再看通根、透干、合冲刑害。"
        ),
        "rule_ids": ["zpxz-month-command-001", "qianli-season-strength-001"],
    }


def _ten_god_finding(profile: dict) -> dict:
    controlling = profile["relationships"]["controlling_day_master"]
    supporting = profile["relationships"]["supporting_day_master"]
    output = profile["relationships"]["output"]
    wealth = profile["relationships"]["wealth"]
    pieces = []
    if supporting:
        pieces.append(f"印星({','.join(supporting)})为生日主之类")
    if controlling:
        pieces.append(f"官杀({','.join(controlling)})为克制日主之类")
    if output:
        pieces.append(f"食伤({','.join(output)})为日主所生之类")
    if wealth:
        pieces.append(f"财星({','.join(wealth)})为日主所克之类")
    if not pieces:
        pieces.append("明透十神信号较少，需重看藏干")
    return {
        "title": "十神结构",
        "evidence": f"明透十神计数={profile['visible_counts']}；藏干十神计数={profile['hidden_counts']}。",
        "conclusion": "；".join(pieces) + "。十神只说明关系类别，仍需结合旺衰和位置。",
        "rule_ids": ["yhzp-ten-gods-001", "yhzp-hidden-root-001"],
    }


def _roots_finding(structure: dict) -> dict:
    context = structure["day_master_context"]
    if context["roots"]:
        evidence = "；".join(
            f"{root['pillar']}支{root['branch']}藏{root['stem']}({root['role']}, {root['weight']})"
            for root in context["roots"]
        )
        conclusion = f"日主有根，根气权重合计{context['root_weight']}，但仍须看月令和受制情况。"
    else:
        evidence = "四支藏干未见日主同干根气。"
        conclusion = "日主根气不足信号明显，但不能脱离月令、印比和合化候选单断弱。"
    return {
        "title": "通根与自坐",
        "evidence": evidence + f" 自坐{context['self_seated']['branch']}为{context['self_seated']['growth_stage']}。",
        "conclusion": conclusion,
        "rule_ids": ["yhzp-hidden-root-001", "qianli-season-strength-001"],
    }


def _relations_finding(structure: dict) -> dict:
    names = [relation["name"] for relation in structure["stem_relations"] + structure["branch_relations"]]
    evidence = "；".join(names) if names else "未见主要合会刑冲害破。"
    has_conflict = any("合" in name for name in names) and any(("破" in name or "刑" in name or "冲" in name) for name in names)
    if has_conflict:
        conclusion = "同一组关系同时有合、刑、破或冲的信号，需保留冲突，不直接按单一合局处理，也不直接断定化气成立。"
    else:
        conclusion = "合会只作结构牵连和化气候选；不直接断定化气成立。"
    return {
        "title": "合会刑冲",
        "evidence": evidence,
        "conclusion": conclusion,
        "rule_ids": ["dts-flow-combination-001", "zpxz-pattern-combo-001", "yhzp-clash-harm-break-001"],
    }


def _shensha_finding(structure: dict) -> dict:
    if not structure["shensha"]:
        return {
            "title": "神煞辅助",
            "evidence": "未见当前最小神煞表中的常见神煞。",
            "conclusion": "神煞暂不参与主判。",
            "rule_ids": ["xjbf-shensha-aux-001"],
        }
    names = [item["name"] for item in structure["shensha"]]
    rule_ids = ["xjbf-shensha-aux-001"]
    rule_ids.append("smth-common-shensha-001")
    if "德秀贵人" in names:
        rule_ids.append("smth-dexiu-001")
    return {
        "title": "神煞辅助",
        "evidence": "；".join(names),
        "conclusion": "神煞只作辅助象义与应期信号，不越过月令、旺衰、格局主线。",
        "rule_ids": rule_ids,
    }
