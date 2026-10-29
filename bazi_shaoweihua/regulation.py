from __future__ import annotations


PILLARS = ["year", "month", "day", "hour"]
PILLAR_LABELS = {"year": "年", "month": "月", "day": "日", "hour": "时"}

REGULATION_RULES = {
    "癸申": {
        "rule_id": "qtbj-gui-shen-001",
        "source": "穷通宝典",
        "source_ref": "癸水生申月调候取用",
        "primary": "丁",
        "assistants": [],
        "principle": "申月金旺水相，癸水宜以丁火温暖制金，兼看火是否透出、有根及受制。",
        "warnings": ["丁火未透"],
    },
    "辛午": {
        "rule_id": "qtbj-xin-wu-001",
        "source": "穷通宝典",
        "source_ref": "辛金生午月调候取用",
        "primary": "壬",
        "assistants": ["己"],
        "principle": "午月火旺炼金，辛金先取壬水润洗，己土可为辅助，须辨火势与官杀压力。",
        "warnings": ["丁火司权"],
    },
    "乙子": {
        "rule_id": "qtbj-yi-zi-001",
        "source": "穷通宝典",
        "source_ref": "乙木生子月调候取用",
        "primary": "丙",
        "assistants": ["戊"],
        "principle": "子月寒水当令，乙木先要丙火解寒，戊土佐以培木制水，须防寒湿。",
        "warnings": ["冬木寒湿"],
    },
}


def analyze_regulation(chart: dict, structure: dict) -> dict:
    day_master = chart["day_master"]
    month_branch = chart["pillars"]["month"]["branch"]
    key = f"{day_master}{month_branch}"
    rule = REGULATION_RULES.get(key)
    if rule is None:
        return {
            "key": key,
            "rule_id": None,
            "status": "not_covered",
            "primary": None,
            "assistants": [],
            "warnings": ["调候MVP尚未覆盖该日主月令组合"],
            "principle": "当前只覆盖已测试样例涉及的少量《穷通宝典》调候组合。",
            "caveat": "未覆盖不代表无调候需要；应新增规则卡和测试后再判断。",
        }

    primary = _stem_presence(rule["primary"], chart, structure)
    assistants = [_stem_presence(stem, chart, structure) for stem in rule["assistants"]]
    warnings = _warnings(rule, primary, assistants)
    return {
        "key": key,
        "rule_id": rule["rule_id"],
        "source": rule["source"],
        "source_ref": rule["source_ref"],
        "principle": rule["principle"],
        "primary": primary,
        "assistants": assistants,
        "warnings": warnings,
        "status": _status(primary, assistants),
        "caveat": "调候MVP只标记取用线索和透藏状态，不直接等同最终喜用神或格局成败。",
    }


def _stem_presence(stem: str, chart: dict, structure: dict) -> dict:
    visible = []
    for pillar in ["year", "month", "hour"]:
        if chart["pillars"][pillar]["stem"] == stem:
            visible.append({"pillar": pillar, "label": PILLAR_LABELS[pillar]})

    hidden = []
    for pillar in PILLARS:
        branch = chart["pillars"][pillar]["branch"]
        for item in structure["hidden_stems_weighted"][pillar]:
            if item["stem"] == stem:
                hidden.append(
                    {
                        "pillar": pillar,
                        "branch": branch,
                        "role": item["role"],
                        "weight": item["weight"],
                    }
                )

    return {
        "stem": stem,
        "visible": bool(visible),
        "visible_positions": visible,
        "hidden": hidden,
        "present": bool(visible or hidden),
    }


def _warnings(rule: dict, primary: dict, assistants: list[dict]) -> list[str]:
    warnings = []
    if not primary["present"]:
        warnings.append(f"{primary['stem']}未见")
    elif not primary["visible"]:
        warnings.extend(warning for warning in rule["warnings"] if primary["stem"] in warning)
    for assistant in assistants:
        if not assistant["present"]:
            warnings.append(f"{assistant['stem']}未见")
    warnings.extend(warning for warning in rule["warnings"] if warning not in warnings and primary["stem"] not in warning)
    return warnings


def _status(primary: dict, assistants: list[dict]) -> str:
    if not primary["present"]:
        return "missing_primary"
    if primary["visible"]:
        if all(item["present"] for item in assistants):
            return "supported"
        return "primary_visible"
    return "partial"
