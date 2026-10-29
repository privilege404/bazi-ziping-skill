from __future__ import annotations

from .pattern import analyze_pattern
from .ten_god_influence import analyze_ten_god_influence


def analyze_pattern_audit(chart: dict, structure: dict) -> dict:
    pattern = analyze_pattern(chart, structure)
    influence = analyze_ten_god_influence(chart, structure)
    ge_shen = _ge_shen(pattern)
    supporting_agents = _supporting_agents(ge_shen["ten_god"], influence)
    success_supports, condition_gaps = _condition_checks(ge_shen["ten_god"], influence)
    risk_notes = _risk_notes(structure)
    clarity_warnings = _clarity_warnings(influence, structure)
    return {
        "version": "pattern-audit-mvp-1",
        "ge_shen": ge_shen,
        "supporting_agents": supporting_agents,
        "success_supports": success_supports,
        "condition_gaps": condition_gaps,
        "risk_notes": risk_notes,
        "clarity_warnings": clarity_warnings,
        "structure_signals": influence["combination_signals"],
        "decision": "格局复核候选，不判成格或破格",
        "method": "pattern-audit-mvp-1: 月令格神 + 十神影响力 + 制化救应 + 清浊扰动",
        "caveat": "本层只拆格局成败条件，不直接判断成格、破格、高低或最终用神。",
    }


def _ge_shen(pattern: dict) -> dict:
    month = pattern["month_command"]
    return {
        "ten_god": month["main_ten_god"],
        "stem": month["main_stem"],
        "branch": month["branch"],
        "pattern_name": pattern["primary_candidate"]["name"],
        "basis": "月令主气",
    }


def _supporting_agents(ge_ten_god: str, influence: dict) -> list[dict]:
    result = []
    if ge_ten_god in {"正印", "偏印"}:
        if _present(influence, "正官"):
            result.append({"ten_god": "正官", "role": "相神候选", "reason": "官生印"})
        if _present(influence, "七杀"):
            result.append({"ten_god": "七杀", "role": "相神候选", "reason": "杀印相生"})
        if _present(influence, "伤官"):
            result.append({"ten_god": "伤官", "role": "配合候选", "reason": "伤官配印"})
    if ge_ten_god == "七杀":
        if _present(influence, "食神"):
            result.append({"ten_god": "食神", "role": "制杀候选", "reason": "食伤制杀"})
        if _present(influence, "伤官"):
            result.append({"ten_god": "伤官", "role": "制杀候选", "reason": "食伤制杀"})
        for seal in ["正印", "偏印"]:
            if _present(influence, seal):
                result.append({"ten_god": seal, "role": "化杀候选", "reason": "印化杀生身"})
    if ge_ten_god == "正官":
        for seal in ["正印", "偏印"]:
            if _present(influence, seal):
                result.append({"ten_god": seal, "role": "相神候选", "reason": "官印相生"})
    return result


def _condition_checks(ge_ten_god: str, influence: dict) -> tuple[list[str], list[str]]:
    item = influence["by_ten_god"][ge_ten_god]
    supports = ["格神为月令主气"]
    gaps = []
    if item["visible_positions"]:
        supports.append(f"{ge_ten_god}有透出")
    else:
        gaps.append("格神未透，只藏于月令")
    if item["hidden_positions"]:
        supports.append("格神有藏干根气")
    return supports, gaps


def _risk_notes(structure: dict) -> list[str]:
    notes = []
    relation_names = [relation["name"] for relation in structure["stem_relations"] + structure["branch_relations"]]
    for name in relation_names:
        if name == "戊癸合火":
            notes.append("戊癸合火，需查月干正官是否合绊日主")
        elif name.endswith("自刑"):
            notes.append(name)
    if "巳申合水" in relation_names and ("巳申刑" in relation_names or "巳申破" in relation_names):
        notes.append("巳申合水与刑破并见，不能直接按合化成立处理")
    return _unique(notes)


def _clarity_warnings(influence: dict, structure: dict) -> list[str]:
    warnings = []
    if "官杀并见" in influence["structural_warnings"]:
        warnings.append("官杀并见")
    if any(relation["type"] == "heavenly_combination" for relation in structure["stem_relations"]):
        warnings.append("天干有合，需查格神或相神是否被合绊")
    if any(relation["type"] in {"six_clash", "punishment", "self_punishment", "six_harm", "six_break"} for relation in structure["branch_relations"]):
        warnings.append("地支有刑冲害破，格局清浊待辨")
    return warnings


def _present(influence: dict, ten_god: str) -> bool:
    return influence["by_ten_god"][ten_god]["present"]


def _unique(items: list[str]) -> list[str]:
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result
