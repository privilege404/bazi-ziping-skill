import json
import subprocess
import sys
from pathlib import Path

from bazi_shaoweihua.engine import BirthInput, build_chart
from bazi_shaoweihua.reading import build_natal_reading
from bazi_shaoweihua.report import build_report
from bazi_shaoweihua.structure import analyze_structure
from bazi_shaoweihua.ten_god_influence import analyze_ten_god_influence


ROOT = Path(__file__).resolve().parents[1]


def _influence_for(birth: BirthInput):
    chart = build_chart(birth, target_year=2026)
    structure = analyze_structure(chart)
    return chart, structure, analyze_ten_god_influence(chart, structure)


def test_sample_one_marks_month_command印_and_month_stem_officer_for_officer_seal_pattern():
    _chart, _structure, influence = _influence_for(BirthInput(2002, 9, 2, 18, 0, 0, "male"))

    assert influence["version"] == "ten-god-influence-mvp-1"
    assert influence["month_command"] == {"branch": "申", "stem": "庚", "ten_god": "正印"}
    assert influence["by_ten_god"]["正印"]["is_month_command"] is True
    assert influence["by_ten_god"]["正印"]["hidden_positions"] == [
        {"pillar": "month", "branch": "申", "stem": "庚", "role": "main_qi", "weight": 60}
    ]
    assert {"pillar": "month", "stem": "戊", "position_weight": 18} in influence["by_ten_god"]["正官"]["visible_positions"]
    assert "透于月干" in influence["by_ten_god"]["正官"]["flags"]
    assert "官印相生候选" in influence["combination_signals"]
    assert {"ten_god": "正印", "reason": "月令主气"} in influence["priority_ten_gods"]


def test_sample_two_marks_qisha_month_command_and_officer_killing_mixed_warning():
    _chart, _structure, influence = _influence_for(BirthInput(2002, 6, 22, 18, 0, 0, "female"))

    qisha = influence["by_ten_god"]["七杀"]
    assert influence["month_command"] == {"branch": "午", "stem": "丁", "ten_god": "七杀"}
    assert qisha["is_month_command"] is True
    assert {"pillar": "hour", "stem": "丁", "position_weight": 10} in qisha["visible_positions"]
    assert qisha["hidden_positions"] == [
        {"pillar": "year", "branch": "午", "stem": "丁", "role": "main_qi", "weight": 70},
        {"pillar": "month", "branch": "午", "stem": "丁", "role": "main_qi", "weight": 70},
    ]
    assert qisha["influence_level"] == "强"
    assert "官杀并见" in influence["structural_warnings"]
    assert influence["top_ten_gods"][0]["ten_god"] == "七杀"


def test_sample_three_marks_indirect_resource_month_command_and_killing_resource_signal():
    _chart, _structure, influence = _influence_for(BirthInput(2004, 12, 12, 9, 45, 0, "male"))

    assert influence["month_command"] == {"branch": "子", "stem": "癸", "ten_god": "偏印"}
    assert influence["by_ten_god"]["偏印"]["is_month_command"] is True
    assert influence["by_ten_god"]["偏印"]["visible_positions"] == []
    assert influence["by_ten_god"]["七杀"]["visible_positions"] == [
        {"pillar": "hour", "stem": "辛", "position_weight": 10}
    ]
    assert "杀印相生候选" in influence["combination_signals"]
    assert "天干有合，需查十神是否被合绊" in influence["structural_warnings"]


def test_natal_reading_and_cli_include_ten_god_influence():
    chart, structure, _influence = _influence_for(BirthInput(2002, 9, 2, 18, 0, 0, "male"))
    report = build_report(chart, structure)

    reading = build_natal_reading(chart, structure, report)

    assert reading["ten_god_influence"]["by_ten_god"]["正印"]["is_month_command"] is True
    finding = next(item for item in reading["natal_findings"] if item["title"] == "十神影响力MVP")
    assert "月令主气=正印" in finding["evidence"]
    assert "官印相生候选" in finding["conclusion"]
    assert "ten-god-influence-mvp-001" in finding["rule_ids"]

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "bazi_cli.py"),
            "reading",
            "--datetime",
            "2002-06-22T18:00:00",
            "--gender",
            "female",
            "--target-year",
            "2026",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(result.stdout)

    assert payload["ten_god_influence"]["by_ten_god"]["七杀"]["is_month_command"] is True
    assert payload["reading"]["ten_god_influence"]["top_ten_gods"][0]["ten_god"] == "七杀"
