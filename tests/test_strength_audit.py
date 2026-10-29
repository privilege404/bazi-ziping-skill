import json
import subprocess
import sys
from pathlib import Path

from bazi_shaoweihua.engine import BirthInput, build_chart
from bazi_shaoweihua.reading import build_natal_reading
from bazi_shaoweihua.report import build_report
from bazi_shaoweihua.strength_audit import analyze_strength_audit
from bazi_shaoweihua.structure import analyze_structure


ROOT = Path(__file__).resolve().parents[1]


def _audit_for(birth: BirthInput):
    chart = build_chart(birth, target_year=2026)
    structure = analyze_structure(chart)
    return chart, structure, analyze_strength_audit(chart, structure)


def test_sample_one_audit_marks_season_support_no_same_stem_root_and印_support():
    _chart, _structure, audit = _audit_for(BirthInput(2002, 9, 2, 18, 0, 0, "male"))

    assert audit["version"] == "strength-audit-mvp-1"
    assert audit["season"]["assessment"] == "得令相气"
    assert audit["rooting"]["assessment"] == "同干无根"
    assert audit["assistance"]["visible_supporting_ten_gods"] == ["劫财", "偏印"]
    assert audit["assistance"]["hidden_supporting_ten_gods"] == ["正印", "劫财", "偏印"]
    assert audit["pressure"]["visible_pressure_ten_gods"] == ["正官"]
    assert "申酉半会金" in audit["relation_modifiers"]["supportive_relations"]
    assert "戊癸合火" in audit["relation_modifiers"]["transform_or_binding_candidates"]
    assert audit["caveat"].startswith("旺衰复核层只列证据")


def test_sample_two_audit_marks_dead_season_strong_roots_and_visible_officer_killing_pressure():
    _chart, _structure, audit = _audit_for(BirthInput(2002, 6, 22, 18, 0, 0, "female"))

    assert audit["season"]["assessment"] == "失令死地"
    assert audit["rooting"]["assessment"] == "同干强根"
    assert audit["rooting"]["root_branches"] == ["酉", "酉"]
    assert audit["assistance"]["visible_supporting_ten_gods"] == []
    assert audit["pressure"]["visible_pressure_ten_gods"] == ["伤官", "正官", "七杀"]
    assert audit["pressure"]["month_command_pressure"] is True
    assert "午午自刑" in audit["relation_modifiers"]["disruptive_relations"]
    assert "酉酉自刑" in audit["relation_modifiers"]["disruptive_relations"]


def test_sample_three_audit_marks_winter_support_no_roots_and_killing_pressure_with_relation_conflict():
    _chart, _structure, audit = _audit_for(BirthInput(2004, 12, 12, 9, 45, 0, "male"))

    assert audit["season"]["assessment"] == "得令相气"
    assert audit["rooting"]["assessment"] == "同干无根"
    assert audit["assistance"]["hidden_supporting_ten_gods"] == ["正印", "偏印"]
    assert audit["pressure"]["visible_pressure_ten_gods"] == ["伤官", "七杀"]
    assert audit["pressure"]["hidden_pressure_ten_gods"] == ["正官", "正财", "偏财", "七杀", "伤官"]
    assert "巳申合水" in audit["relation_modifiers"]["supportive_relations"]
    assert "巳申刑" in audit["relation_modifiers"]["disruptive_relations"]
    assert "巳申破" in audit["relation_modifiers"]["disruptive_relations"]


def test_natal_reading_and_cli_include_strength_audit():
    chart, structure, _audit = _audit_for(BirthInput(2002, 9, 2, 18, 0, 0, "male"))
    report = build_report(chart, structure)
    reading = build_natal_reading(chart, structure, report)

    assert reading["strength_audit"]["season"]["assessment"] == "得令相气"
    finding = next(item for item in reading["natal_findings"] if item["title"] == "旺衰复核MVP")
    assert "得令相气" in finding["evidence"]
    assert "同干无根" in finding["evidence"]
    assert "strength-audit-mvp-001" in finding["rule_ids"]

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

    assert payload["strength_audit"]["rooting"]["assessment"] == "同干强根"
    assert payload["reading"]["strength_audit"]["pressure"]["month_command_pressure"] is True
