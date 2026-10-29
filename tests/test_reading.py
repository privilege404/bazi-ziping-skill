import json
import subprocess
import sys
from pathlib import Path

from bazi_shaoweihua.engine import BirthInput, build_chart
from bazi_shaoweihua.reading import build_natal_reading
from bazi_shaoweihua.report import build_report
from bazi_shaoweihua.structure import analyze_structure


ROOT = Path(__file__).resolve().parents[1]


def _reading_for(birth: BirthInput):
    chart = build_chart(birth, target_year=2026)
    structure = analyze_structure(chart)
    report = build_report(chart, structure)
    return build_natal_reading(chart, structure, report)


def test_natal_reading_contains_ten_god_profile_for_first_sample():
    reading = _reading_for(BirthInput(2002, 9, 2, 18, 0, 0, "male"))

    assert reading["version"] == "natal-mvp-1"
    assert reading["ten_god_profile"]["visible_counts"]["偏印"] == 1
    assert reading["ten_god_profile"]["visible_counts"]["正官"] == 1
    assert reading["ten_god_profile"]["visible_counts"]["劫财"] == 1
    assert reading["ten_god_profile"]["relationships"]["supporting_day_master"] == ["偏印", "正印"]
    assert reading["ten_god_profile"]["relationships"]["controlling_day_master"] == ["七杀", "正官"]
    assert reading["natal_findings"][0]["title"] == "月令与日主"
    assert "癸日主生申月" in reading["natal_findings"][0]["conclusion"]
    assert "zpxz-month-command-001" in reading["natal_findings"][0]["rule_ids"]
    assert any(finding["title"] == "十神结构" for finding in reading["natal_findings"])
    assert reading["strength"]["season"]["state"] == "相"
    assert reading["strength"]["classification"] in {"中和", "中和偏强"}
    assert reading["pattern"]["primary_candidate"]["name"] == "正印格候选"
    assert any(finding["title"] == "格局候选MVP" for finding in reading["natal_findings"])
    assert any(finding["title"] == "旺衰评分MVP" for finding in reading["natal_findings"])


def test_natal_reading_preserves_uncertainty_for_combination_transformation():
    reading = _reading_for(BirthInput(2002, 6, 22, 18, 0, 0, "female"))

    combination = next(f for f in reading["natal_findings"] if f["title"] == "合会刑冲")
    assert "不直接断定化气成立" in combination["conclusion"]
    assert "dts-flow-combination-001" in combination["rule_ids"]
    assert reading["ten_god_profile"]["visible_counts"]["正官"] == 1
    assert reading["ten_god_profile"]["visible_counts"]["七杀"] == 1
    assert set(reading["ten_god_profile"]["relationships"]["controlling_day_master"]) == {"正官", "七杀"}


def test_natal_reading_notes_conflicting_relations_for_third_sample():
    reading = _reading_for(BirthInput(2004, 12, 12, 9, 45, 0, "male"))

    relation = next(f for f in reading["natal_findings"] if f["title"] == "合会刑冲")
    assert "巳申合水" in relation["evidence"]
    assert "巳申破" in relation["evidence"]
    assert "同一组关系同时有合、刑、破" in relation["conclusion"]
    assert "zpxz-pattern-combo-001" in relation["rule_ids"]


def test_cli_reading_command_outputs_first_version_payload():
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

    assert payload["chart"]["pillars"]["day"]["ganzhi"] == "辛酉"
    assert payload["strength"]["classification"] in {"偏弱", "中和偏弱"}
    assert payload["reading"]["version"] == "natal-mvp-1"
    assert payload["reading"]["scope"] == "本命MVP，不含完整岁运断事"
