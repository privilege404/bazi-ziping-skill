from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RULE_FILE = ROOT / "references" / "rules" / "core-structure.jsonl"
PILLAR_LABELS = {"year": "年", "month": "月", "day": "日", "hour": "时"}


def build_report(chart: dict, structure: dict, rule_file: Path = RULE_FILE) -> dict:
    cards = _load_cards(rule_file)
    observations = _observations(chart, structure)
    applied_ids = _applied_rule_ids(structure)
    applied_rules = [
        {
            "id": card["id"],
            "source": card["source"],
            "source_ref": card.get("source_ref", ""),
            "topic": card["topic"],
            "claim": card["claim"],
            "caveat": card["caveat"],
        }
        for card in cards
        if card["id"] in applied_ids
    ]
    return {
        "summary": {
            "pillars": _pillars_text(chart),
            "day_master": chart["day_master"],
            "current_luck": chart["luck"]["current_cycle"],
            "annual": chart["annual"],
        },
        "observations": observations,
        "applied_rules": applied_rules,
    }


def _load_cards(rule_file: Path) -> list[dict]:
    return [json.loads(line) for line in rule_file.read_text(encoding="utf-8").splitlines() if line.strip()]


def _pillars_text(chart: dict) -> str:
    return " ".join(chart["pillars"][pillar]["ganzhi"] for pillar in ["year", "month", "day", "hour"])


def _applied_rule_ids(structure: dict) -> set[str]:
    ids = {
        "zpxz-month-command-001",
        "qianli-season-strength-001",
        "yhzp-hidden-root-001",
        "shenfeng-disease-medicine-001",
    }
    if structure["storages"]:
        ids.add("smth-storage-001")
    if any(storage["opened_by_clash"] for storage in structure["storages"].values()):
        ids.add("smth-storage-clash-001")
    if structure["stem_relations"] or any(
        relation["type"] in {"six_combination", "three_harmony", "three_meeting", "half_harmony", "half_meeting"}
        for relation in structure["branch_relations"]
    ):
        ids.add("dts-flow-combination-001")
        ids.add("zpxz-pattern-combo-001")
    if structure["stem_relations"]:
        ids.add("tiangan-shengke-hechong-001")
    if any(
        relation["type"] in {"six_clash", "punishment", "self_punishment", "six_harm", "six_break"}
        for relation in structure["branch_relations"]
    ):
        ids.add("yhzp-clash-harm-break-001")
    if structure["shensha"]:
        ids.add("xjbf-shensha-aux-001")
        ids.add("smth-common-shensha-001")
    if any(item["name"] == "德秀贵人" for item in structure["shensha"]):
        ids.add("smth-dexiu-001")
    if structure.get("element_interactions"):
        ids.add("wuxing-generating-controlling-001")
    return ids


def _observations(chart: dict, structure: dict) -> list[dict]:
    context = structure["day_master_context"]
    observations = [
        {
            "key": "month_command",
            "value": (
                f"日主{context['day_master']}，月令{context['month_branch']}，"
                f"十二长生为{context['month_growth_stage']}，得令状态={context['season_state']}。"
            ),
        },
        {
            "key": "self_seated",
            "value": (
                f"日主自坐{context['self_seated']['branch']}，"
                f"自坐十二长生为{context['self_seated']['growth_stage']}。"
            ),
        },
        {
            "key": "polarity",
            "value": (
                f"天干阴阳={','.join(structure['polarity']['stems'])}；"
                f"地支阴阳={','.join(structure['polarity']['branches'])}；"
                f"全阴={structure['polarity']['is_all_yin']}，全阳={structure['polarity']['is_all_yang']}。"
            ),
        },
    ]
    observations.append({"key": "roots", "value": _roots_text(structure)})
    if structure["stem_relations"]:
        observations.append({"key": "stem_relations", "value": _relations_text(structure["stem_relations"])})
    if structure["branch_relations"]:
        observations.append({"key": "branch_relations", "value": _relations_text(structure["branch_relations"])})
    if structure["storages"]:
        observations.append({"key": "storages", "value": _storages_text(structure["storages"])})
    if structure.get("element_interactions"):
        observations.append({"key": "element_interactions", "value": _element_interactions_text(structure["element_interactions"])})
    if structure["shensha"]:
        observations.append({"key": "shensha", "value": _shensha_text(structure["shensha"])})
    observations.append({"key": "caution", "value": "本报告只测试结构事实与规则命中，不直接给出最终喜忌和格局成败。"})
    return observations


def _roots_text(structure: dict) -> str:
    roots = structure["day_master_context"]["roots"]
    if not roots:
        return "日主在四支藏干中未见同干根气。"
    parts = []
    for root in roots:
        parts.append(
            f"{PILLAR_LABELS[root['pillar']]}支{root['branch']}藏{root['stem']}"
            f"{_role_name(root['role'])}，权重{root['weight']}"
        )
    return "；".join(parts) + "。"


def _relations_text(relations: list[dict]) -> str:
    parts = []
    for relation in relations:
        text = relation["name"]
        if "transform_candidate" in relation:
            text += f"({relation['status']}，化气候选={relation['transform_candidate']})"
        else:
            text += f"({relation['status']})"
        parts.append(text)
    return "；".join(parts) + "。"


def _storages_text(storages: dict) -> str:
    parts = []
    for branch, storage in storages.items():
        parts.append(
            f"{branch}为{storage['stores']}库，冲库支={storage['clash_branch']}，"
            f"已逢冲={storage['opened_by_clash']}"
        )
    return "；".join(parts) + "。"


def _element_interactions_text(interactions: list[dict]) -> str:
    parts = []
    for item in interactions:
        if item["type"].endswith("_control"):
            source = item["controller"]
            target = item["controlled"]
            parts.append(f"{_symbol(source)}{source['element']}克{_symbol(target)}{target['element']}")
        elif item["type"].endswith("_generate"):
            source = item["generator"]
            target = item["generated"]
            parts.append(f"{_symbol(source)}{source['element']}生{_symbol(target)}{target['element']}")
    return "；".join(parts) + "。"


def _shensha_text(shensha: list[dict]) -> str:
    parts = []
    for item in shensha:
        marker = item.get("branch", item.get("target", ""))
        text = f"{item['pillar']}柱{marker}见{item['name']}({item['basis']})"
        if item["name"] == "德秀贵人":
            text += f"，德干={','.join(item['de_stems'])}，秀干={','.join(item['xiu_stems'])}"
        parts.append(text)
    return "；".join(parts) + "。"


def _symbol(item: dict) -> str:
    return item.get("stem", item.get("branch"))


def _role_name(role: str) -> str:
    return {"main_qi": "主气", "middle_qi": "中气", "residual_qi": "余气"}[role]
