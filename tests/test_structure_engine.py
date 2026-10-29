from bazi_shaoweihua.engine import BirthInput, build_chart
from bazi_shaoweihua.structure import analyze_structure


def test_hidden_stem_weights_roots_and_month_command_are_reported():
    chart = build_chart(BirthInput(2002, 6, 22, 18, 0, 0, "female"))
    structure = analyze_structure(chart)

    assert structure["hidden_stems_weighted"]["month"] == [
        {"stem": "丁", "role": "main_qi", "weight": 70},
        {"stem": "己", "role": "middle_qi", "weight": 30},
    ]
    assert structure["day_master_context"]["day_master"] == "辛"
    assert structure["day_master_context"]["month_branch"] == "午"
    assert structure["day_master_context"]["month_growth_stage"] == "病"
    assert structure["day_master_context"]["season_state"] == "not_in_season"
    assert structure["day_master_context"]["roots"] == [
        {"pillar": "day", "branch": "酉", "stem": "辛", "role": "main_qi", "weight": 100},
        {"pillar": "hour", "branch": "酉", "stem": "辛", "role": "main_qi", "weight": 100},
    ]
    assert structure["day_master_context"]["self_seated"] == {
        "branch": "酉",
        "growth_stage": "临官",
    }


def test_branch_relations_detect_trines_meetings_clashes_harms_breaks_and_storage():
    chart = {
        "pillars": {
            "year": {"stem": "壬", "branch": "申", "ganzhi": "壬申"},
            "month": {"stem": "壬", "branch": "子", "ganzhi": "壬子"},
            "day": {"stem": "壬", "branch": "辰", "ganzhi": "壬辰"},
            "hour": {"stem": "丙", "branch": "午", "ganzhi": "丙午"},
        },
        "day_master": "壬",
        "growth_stage": {"day": "墓", "month": "帝旺", "year": "长生", "hour": "胎"},
    }
    structure = analyze_structure(chart)

    assert any(
        r["type"] == "three_harmony"
        and r["name"] == "申子辰三合水"
        and r["branches"] == ["申", "子", "辰"]
        and r["element"] == "水"
        and r["status"] == "complete"
        and r["transform_candidate"] is True
        for r in structure["branch_relations"]
    )
    assert any(r["type"] == "six_clash" and r["name"] == "子午冲" for r in structure["branch_relations"])
    assert structure["storages"]["辰"]["stores"] == "水"
    assert structure["storages"]["辰"]["opened_by_clash"] is False


def test_branch_storage_is_marked_open_when_storage_branch_is_clashed():
    chart = {
        "pillars": {
            "year": {"stem": "戊", "branch": "辰", "ganzhi": "戊辰"},
            "month": {"stem": "壬", "branch": "戌", "ganzhi": "壬戌"},
            "day": {"stem": "癸", "branch": "酉", "ganzhi": "癸酉"},
            "hour": {"stem": "辛", "branch": "酉", "ganzhi": "辛酉"},
        },
        "day_master": "癸",
        "growth_stage": {"day": "病", "month": "衰", "year": "养", "hour": "病"},
    }
    structure = analyze_structure(chart)

    assert structure["storages"]["辰"]["stores"] == "水"
    assert structure["storages"]["辰"]["opened_by_clash"] is True
    assert structure["storages"]["戌"]["stores"] == "火"
    assert structure["storages"]["戌"]["opened_by_clash"] is True
    assert any(r["type"] == "six_clash" and r["name"] == "辰戌冲" for r in structure["branch_relations"])


def test_stem_relations_report_heavenly_clashes_without_erasing_combinations():
    chart = {
        "pillars": {
            "year": {"stem": "甲", "branch": "寅", "ganzhi": "甲寅"},
            "month": {"stem": "庚", "branch": "申", "ganzhi": "庚申"},
            "day": {"stem": "己", "branch": "丑", "ganzhi": "己丑"},
            "hour": {"stem": "乙", "branch": "酉", "ganzhi": "乙酉"},
        },
        "day_master": "己",
        "growth_stage": {"day": "墓", "month": "沐浴", "year": "死", "hour": "长生"},
    }
    structure = analyze_structure(chart)

    assert any(
        relation["type"] == "heavenly_combination"
        and relation["name"] == "甲己合土"
        for relation in structure["stem_relations"]
    )
    assert any(
        relation["type"] == "heavenly_clash"
        and relation["name"] == "甲庚冲"
        for relation in structure["stem_relations"]
    )


def test_stem_and_branch_combinations_do_not_claim_transformation_without_support():
    chart = build_chart(BirthInput(2004, 12, 12, 9, 45, 0, "male"))
    structure = analyze_structure(chart)

    assert any(
        r["type"] == "six_combination"
        and r["name"] == "巳申合水"
        and r["status"] == "detected"
        and r["transform_candidate"] is True
        for r in structure["branch_relations"]
    )
    assert any(
        r["type"] == "six_break"
        and r["name"] == "巳申破"
        for r in structure["branch_relations"]
    )


def test_pure_yin_yang_and_common_shensha_are_reported():
    chart = build_chart(BirthInput(2002, 6, 22, 18, 0, 0, "female"))
    structure = analyze_structure(chart)

    assert structure["polarity"] == {
        "stems": ["阳", "阳", "阴", "阴"],
        "branches": ["阳", "阳", "阴", "阴"],
        "is_all_yin": False,
        "is_all_yang": False,
    }
    assert {"name": "天乙贵人", "basis": "day_stem", "branch": "午", "pillar": "year"} in structure["shensha"]
    assert {"name": "天乙贵人", "basis": "day_stem", "branch": "午", "pillar": "month"} in structure["shensha"]
    assert {"name": "禄神", "basis": "day_stem", "branch": "酉", "pillar": "day"} in structure["shensha"]
    assert {"name": "禄神", "basis": "day_stem", "branch": "酉", "pillar": "hour"} in structure["shensha"]
    assert {"name": "桃花", "basis": "day_branch", "branch": "午", "pillar": "year"} in structure["shensha"]


def test_cli_structure_command_outputs_chart_and_structure_json():
    import json
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "bazi_cli.py"),
            "structure",
            "--datetime",
            "2002-06-22T18:00:00",
            "--gender",
            "female",
            "--target-year",
            "2026",
        ],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(result.stdout)

    assert payload["chart"]["pillars"]["day"]["ganzhi"] == "辛酉"
    assert payload["structure"]["day_master_context"]["self_seated"]["growth_stage"] == "临官"


def test_first_sample_reports_dexiu_noble_control_relations_and_half_meeting():
    chart = build_chart(BirthInput(2002, 9, 2, 18, 0, 0, "male"))
    structure = analyze_structure(chart)

    assert any(
        item["name"] == "德秀贵人"
        and item["basis"] == "month_branch"
        and item["branch"] == "申"
        and item["de_stems"] == ["壬", "戊", "癸"]
        and item["xiu_stems"] == ["辛"]
        for item in structure["shensha"]
    )
    assert any(
        relation["type"] == "half_meeting"
        and relation["name"] == "申酉半会金"
        and relation["transform_candidate"] is True
        for relation in structure["branch_relations"]
    )
    assert any(
        item["type"] == "stem_control"
        and item["controller"] == {"pillar": "month", "stem": "戊", "element": "土"}
        and item["controlled"] == {"pillar": "year", "stem": "壬", "element": "水"}
        for item in structure["element_interactions"]
    )
    assert any(
        item["type"] == "branch_control"
        and item["controller"]["branch"] == "午"
        and item["controlled"]["branch"] == "申"
        for item in structure["element_interactions"]
    )


def test_common_additional_shensha_are_reported_with_basis():
    chart = build_chart(BirthInput(2002, 9, 2, 18, 0, 0, "male"))
    structure = analyze_structure(chart)

    assert any(
        item["name"] == "天德贵人"
        and item["basis"] == "month_branch"
        and item["target"] == "癸"
        and item["pillar"] == "day"
        for item in structure["shensha"]
    )
    assert any(
        item["name"] == "月德贵人"
        and item["basis"] == "month_branch"
        and item["target"] == "壬"
        and item["pillar"] == "year"
        for item in structure["shensha"]
    )
    assert any(
        item["name"] == "将星"
        and item["basis"] == "day_branch"
        and item["branch"] == "酉"
        and item["pillar"] == "day"
        for item in structure["shensha"]
    )
    assert any(
        item["name"] == "亡神"
        and item["basis"] == "day_branch"
        and item["branch"] == "申"
        and item["pillar"] == "month"
        for item in structure["shensha"]
    )
