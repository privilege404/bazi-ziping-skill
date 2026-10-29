from __future__ import annotations


def build_natal_synthesis(chart: dict, structure: dict, reading: dict) -> dict:
    conclusions = [
        _strength_conclusion(reading),
        _pattern_conclusion(reading),
        _ten_gods_conclusion(reading),
        _regulation_conclusion(reading),
        _relations_conclusion(structure),
    ]
    if "transit" in reading:
        conclusions.append(_transit_conclusion(reading))
    return {
        "version": "natal-synthesis-mvp-1",
        "day_master": chart["day_master"],
        "decision_policy": "结论必须引用已计算事实；不从模型记忆补断。",
        "conclusions": conclusions,
        "limits": [
            "本命结论组装器只汇总既有审计事实，不新增未经计算的断语。",
            "confidence 表示证据完整度，不表示命理事件确定发生。",
            "事业、财运、婚恋、健康等具体断语仍需更多规则卡和案例校准。",
        ],
    }


def _strength_conclusion(reading: dict) -> dict:
    strength = reading["strength"]
    audit = reading["strength_audit"]
    return {
        "topic": "day_master_strength",
        "conclusion": f"日主强弱暂以 {strength['classification']} 作为启发式结果，需结合复核层继续校准。",
        "confidence": "medium",
        "evidence": [
            f"评分={strength['heuristic_score']}",
            f"季令={audit['season']['assessment']}",
            f"通根={audit['rooting']['assessment']}",
        ],
        "rule_ids": ["strength-mvp-heuristic-001", "strength-audit-mvp-001"],
        "limits": ["启发式评分不等同最终喜忌；从格和化气尚未最终裁定。"],
    }


def _pattern_conclusion(reading: dict) -> dict:
    audit = reading["pattern_audit"]
    ge = audit["ge_shen"]
    signals = "、".join(audit["structure_signals"]) or "暂无组合信号"
    confidence = "medium" if audit["success_supports"] and not audit["clarity_warnings"] else "low"
    return {
        "topic": "pattern",
        "conclusion": f"格局以 {ge['pattern_name']} 复核，结构信号为 {signals}。",
        "confidence": confidence,
        "evidence": [
            f"格神={ge['ten_god']}",
            f"成格支持={audit['success_supports']}",
            f"条件缺口={audit['condition_gaps']}",
            f"清浊警告={audit['clarity_warnings']}",
        ],
        "rule_ids": ["zpxz-pattern-candidate-001", "pattern-audit-mvp-001"],
        "limits": ["当前只列候选格局和成败条件，不判格局高低。"],
    }


def _ten_gods_conclusion(reading: dict) -> dict:
    influence = reading["ten_god_influence"]
    top = influence["top_ten_gods"][:3]
    top_text = "、".join(item["ten_god"] for item in top) or "暂无"
    return {
        "topic": "ten_gods",
        "conclusion": f"十神复核优先观察 {top_text}。",
        "confidence": "medium" if top else "low",
        "evidence": [
            f"月令主气={influence['month_command']['ten_god']}",
            f"前三影响力={top}",
            f"结构警告={influence['structural_warnings']}",
        ],
        "rule_ids": ["yhzp-ten-gods-001", "ten-god-influence-mvp-001"],
        "limits": ["十神排序不直接推出六亲吉凶或具体事件。"],
    }


def _regulation_conclusion(reading: dict) -> dict:
    regulation = reading["regulation"]
    if regulation["status"] == "not_covered":
        return {
            "topic": "regulation",
            "conclusion": "调候规则尚未覆盖该日主月令组合。",
            "confidence": "low",
            "evidence": [regulation["key"], *regulation["warnings"]],
            "rule_ids": ["shenfeng-disease-medicine-001"],
            "limits": ["未覆盖不代表无需调候；需补规则卡后再判断。"],
        }
    primary = regulation["primary"]["stem"]
    return {
        "topic": "regulation",
        "conclusion": f"调候线索取 {primary}，当前状态为 {regulation['status']}。",
        "confidence": "medium" if regulation["primary"]["present"] else "low",
        "evidence": [
            regulation["principle"],
            f"警告={regulation['warnings']}",
        ],
        "rule_ids": [regulation["rule_id"]],
        "limits": ["调候线索不等同最终喜用神。"],
    }


def _relations_conclusion(structure: dict) -> dict:
    relation_names = [relation["name"] for relation in structure["stem_relations"] + structure["branch_relations"]]
    return {
        "topic": "relations",
        "conclusion": "合会刑冲害破已作为结构扰动或牵连信号保留。",
        "confidence": "medium",
        "evidence": relation_names or ["未见主要合会刑冲害破"],
        "rule_ids": ["dts-flow-combination-001", "yhzp-clash-harm-break-001", "tiangan-shengke-hechong-001"],
        "limits": ["合会不直接断化气成立；刑冲害破不自动断凶。"],
    }


def _transit_conclusion(reading: dict) -> dict:
    transit = reading["transit"]
    annual = transit["annual"]
    luck = transit["current_luck"]
    luck_text = luck["ganzhi"] if luck else "未落入当前大运"
    trigger_names = [item["name"] for item in transit["relation_triggers"][:6]]
    shensha_names = [item["name"] for item in transit["shensha_triggers"][:6]]
    return {
        "topic": "transit_overall",
        "conclusion": f"{transit['target_year']} 年流年为 {annual['ganzhi']}，当前大运为 {luck_text}；岁运只作触发层。",
        "confidence": "medium" if luck else "low",
        "evidence": [
            f"大运={luck}",
            f"流年={annual}",
            f"触发关系={trigger_names}",
            f"岁运神煞={shensha_names}",
            f"冲库触发={transit['storage_triggers']}",
            f"岁运十神={transit['focus_ten_gods']}",
        ],
        "rule_ids": [
            "transit-mvp-001",
            "transit-group-completion-001",
            "transit-shensha-trigger-001",
            "yhzp-ten-gods-001",
            "dts-flow-combination-001",
            "tiangan-shengke-hechong-001",
        ],
        "limits": ["整体运势只列岁运触发点；具体财官婚恋健康需进入专题模块。"],
    }
