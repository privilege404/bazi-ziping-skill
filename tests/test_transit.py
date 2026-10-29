import json
import subprocess
import sys
from pathlib import Path

from bazi_shaoweihua.engine import BirthInput, build_chart
from bazi_shaoweihua.structure import analyze_structure
from bazi_shaoweihua.transit import analyze_transit


ROOT = Path(__file__).resolve().parents[1]


def _transit_for(birth: BirthInput, target_year: int = 2026):
    chart = build_chart(birth, target_year=target_year)
    structure = analyze_structure(chart)
    return chart, structure, analyze_transit(chart, structure)


def test_transit_reports_current_luck_annual_ten_gods_and_relation_triggers():
    _chart, _structure, transit = _transit_for(BirthInput(1991, 3, 15, 18, 0, 0, "female"))

    assert transit["version"] == "transit-mvp-1"
    assert transit["target_year"] == 2026
    assert transit["current_luck"]["ganzhi"]
    assert transit["annual"]["ganzhi"] == "丙午"
    assert transit["current_luck"]["stem_ten_god"]
    assert transit["annual"]["stem_ten_god"]
    assert transit["annual"]["branch_ten_gods"]
    assert isinstance(transit["relation_triggers"], list)
    assert transit["decision_policy"] == "岁运只作为触发层，必须回扣本命结构。"


def test_transit_reports_half_harmony_half_meeting_and_completed_groups():
    chart = {
        "pillars": {
            "year": {"stem": "壬", "branch": "申", "ganzhi": "壬申"},
            "month": {"stem": "癸", "branch": "子", "ganzhi": "癸子"},
            "day": {"stem": "乙", "branch": "卯", "ganzhi": "乙卯"},
            "hour": {"stem": "甲", "branch": "寅", "ganzhi": "甲寅"},
        },
        "day_master": "乙",
        "luck": {
            "current_cycle": {
                "index": 2,
                "ganzhi": "戊辰",
                "start_year": 2020,
                "end_year": 2029,
                "start_age": 20,
                "end_age": 29,
            }
        },
        "annual": {"target_year": 2026, "ganzhi": "丙午", "stem": "丙", "branch": "午"},
    }
    structure = analyze_structure(
        {
            **chart,
            "growth_stage": {"year": "胎", "month": "病", "day": "临官", "hour": "帝旺"},
        }
    )
    transit = analyze_transit(chart, structure)
    names = [item["name"] for item in transit["relation_triggers"]]

    assert "子辰半合水" in names
    assert "卯辰半会木" in names
    assert "申子辰三合水" in names
    assert "寅卯辰三会木" in names
    assert "寅午半合火" in names


def test_transit_reports_stem_generation_control_and_heavenly_clash():
    chart = {
        "pillars": {
            "year": {"stem": "甲", "branch": "寅", "ganzhi": "甲寅"},
            "month": {"stem": "壬", "branch": "午", "ganzhi": "壬午"},
            "day": {"stem": "乙", "branch": "卯", "ganzhi": "乙卯"},
            "hour": {"stem": "辛", "branch": "酉", "ganzhi": "辛酉"},
        },
        "day_master": "乙",
        "luck": {"current_cycle": None},
        "annual": {"target_year": 2026, "ganzhi": "庚午", "stem": "庚", "branch": "午"},
    }
    structure = analyze_structure(
        {
            **chart,
            "growth_stage": {"year": "帝旺", "month": "长生", "day": "临官", "hour": "绝"},
        }
    )
    transit = analyze_transit(chart, structure)

    assert any(
        item["type"] == "stem_control"
        and item["name"] == "庚克甲"
        and item["external"] == "annual"
        and item["target"] == "year"
        for item in transit["relation_triggers"]
    )
    assert any(
        item["type"] == "stem_generate"
        and item["name"] == "庚生壬"
        and item["external"] == "annual"
        and item["target"] == "month"
        for item in transit["relation_triggers"]
    )
    assert any(
        item["type"] == "heavenly_clash"
        and item["name"] == "甲庚冲"
        and item["external"] == "annual"
        and item["target"] == "year"
        for item in transit["relation_triggers"]
    )


def test_transit_reports_annual_shensha_triggers_for_common_symbols():
    _chart, _structure, transit = _transit_for(BirthInput(2002, 6, 22, 18, 0, 0, "female"))

    assert any(
        item["name"] == "天乙贵人"
        and item["external"] == "annual"
        and item["basis"] == "day_stem"
        and item["branch"] == "午"
        for item in transit["shensha_triggers"]
    )
    assert any(
        item["name"] == "月德贵人"
        and item["external"] == "annual"
        and item["basis"] == "month_branch"
        and item["target"] == "丙"
        for item in transit["shensha_triggers"]
    )
    assert any(
        item["name"] == "桃花"
        and item["external"] == "annual"
        and item["basis"] == "day_branch"
        and item["branch"] == "午"
        for item in transit["shensha_triggers"]
    )
    assert any(
        item["name"] == "将星"
        and item["external"] == "annual"
        and item["basis"] == "year_branch"
        and item["branch"] == "午"
        for item in transit["shensha_triggers"]
    )


def test_transit_reports_storage_activation_by_external_clash():
    chart = {
        "pillars": {
            "year": {"stem": "戊", "branch": "辰", "ganzhi": "戊辰"},
            "month": {"stem": "壬", "branch": "子", "ganzhi": "壬子"},
            "day": {"stem": "癸", "branch": "酉", "ganzhi": "癸酉"},
            "hour": {"stem": "辛", "branch": "酉", "ganzhi": "辛酉"},
        },
        "day_master": "癸",
        "luck": {"current_cycle": None},
        "annual": {"target_year": 2030, "ganzhi": "庚戌", "stem": "庚", "branch": "戌"},
    }
    structure = analyze_structure(
        {
            **chart,
            "growth_stage": {"year": "养", "month": "临官", "day": "病", "hour": "病"},
        }
    )
    transit = analyze_transit(chart, structure)

    assert {
        "type": "storage_activation",
        "name": "辰戌冲开水库候选",
        "external": "annual",
        "target": "year",
        "storage_branch": "辰",
        "clash_branch": "戌",
        "stores": "水",
        "status": "trigger",
    } in transit["storage_triggers"]


def test_transit_is_included_in_cli_reading_payload():
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "bazi_cli.py"),
            "reading",
            "--datetime",
            "1992-05-20T09:45:00",
            "--gender",
            "male",
            "--target-year",
            "2026",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(result.stdout)

    assert payload["transit"]["version"] == "transit-mvp-1"
    assert payload["reading"]["transit"]["annual"]["ganzhi"] == "丙午"
    assert any(item["topic"] == "transit_overall" for item in payload["reading"]["synthesis"]["conclusions"])


def test_transit_handles_pre_luck_start_blank_current_cycle():
    chart, _structure, transit = _transit_for(BirthInput(1996, 2, 23, 0, 30, 0, "female"), target_year=2000)

    assert chart["luck"]["current_cycle"]["ganzhi"] == ""
    assert transit["current_luck"] is None
    assert transit["annual"]["ganzhi"] == chart["annual"]["ganzhi"]
    assert len(transit["annual"]["ganzhi"]) >= 2
    assert isinstance(transit["relation_triggers"], list)
