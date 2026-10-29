import json
import subprocess
import sys
from pathlib import Path

from bazi_shaoweihua.engine import BirthInput, build_chart
from bazi_shaoweihua.regulation import analyze_regulation
from bazi_shaoweihua.report import build_report
from bazi_shaoweihua.reading import build_natal_reading
from bazi_shaoweihua.structure import analyze_structure


ROOT = Path(__file__).resolve().parents[1]


def _chart_and_structure(birth: BirthInput):
    chart = build_chart(birth, target_year=2026)
    return chart, analyze_structure(chart)


def test_first_sample_regulation_detects_gui_water_in_shen_month():
    chart, structure = _chart_and_structure(BirthInput(2002, 9, 2, 18, 0, 0, "male"))

    regulation = analyze_regulation(chart, structure)

    assert regulation["key"] == "癸申"
    assert regulation["rule_id"] == "qtbj-gui-shen-001"
    assert regulation["primary"]["stem"] == "丁"
    assert regulation["primary"]["visible"] is False
    assert regulation["primary"]["hidden"] == [{"pillar": "year", "branch": "午", "role": "main_qi", "weight": 70}]
    assert "丁火未透" in regulation["warnings"]
    assert regulation["status"] == "partial"


def test_second_sample_regulation_detects_ren_and_ji_for_xin_metal_in_wu_month():
    chart, structure = _chart_and_structure(BirthInput(2002, 6, 22, 18, 0, 0, "female"))

    regulation = analyze_regulation(chart, structure)

    assert regulation["key"] == "辛午"
    assert regulation["rule_id"] == "qtbj-xin-wu-001"
    assert regulation["primary"]["stem"] == "壬"
    assert regulation["primary"]["visible"] is True
    assert regulation["assistants"][0]["stem"] == "己"
    assert regulation["assistants"][0]["hidden"] == [
        {"pillar": "year", "branch": "午", "role": "middle_qi", "weight": 30},
        {"pillar": "month", "branch": "午", "role": "middle_qi", "weight": 30},
    ]
    assert "丁火司权" in regulation["warnings"]
    assert regulation["status"] == "supported"


def test_third_sample_regulation_detects_bing_and_wu_for_yi_wood_in_zi_month():
    chart, structure = _chart_and_structure(BirthInput(2004, 12, 12, 9, 45, 0, "male"))

    regulation = analyze_regulation(chart, structure)

    assert regulation["key"] == "乙子"
    assert regulation["rule_id"] == "qtbj-yi-zi-001"
    assert regulation["primary"]["stem"] == "丙"
    assert regulation["primary"]["visible"] is True
    assert regulation["assistants"][0]["stem"] == "戊"
    assert regulation["assistants"][0]["hidden"] == [
        {"pillar": "year", "branch": "申", "role": "residual_qi", "weight": 10},
        {"pillar": "hour", "branch": "巳", "role": "residual_qi", "weight": 10},
    ]
    assert "冬木寒湿" in regulation["warnings"]
    assert regulation["status"] == "supported"


def test_natal_reading_includes_regulating_useful_god_finding_with_citation():
    chart, structure = _chart_and_structure(BirthInput(2002, 9, 2, 18, 0, 0, "male"))
    report = build_report(chart, structure)

    reading = build_natal_reading(chart, structure, report)

    assert reading["regulation"]["rule_id"] == "qtbj-gui-shen-001"
    finding = next(item for item in reading["natal_findings"] if item["title"] == "调候用神MVP")
    assert "癸日主生申月" in finding["evidence"]
    assert "丁火未透" in finding["conclusion"]
    assert finding["rule_ids"] == ["qtbj-gui-shen-001"]


def test_cli_reading_payload_includes_regulation_block():
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "bazi_cli.py"),
            "reading",
            "--datetime",
            "2004-12-12T09:45:00",
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

    assert payload["regulation"]["key"] == "乙子"
    assert payload["reading"]["regulation"]["rule_id"] == "qtbj-yi-zi-001"
