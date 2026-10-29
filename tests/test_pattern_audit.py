import json
import subprocess
import sys
from pathlib import Path

from bazi_shaoweihua.engine import BirthInput, build_chart
from bazi_shaoweihua.pattern_audit import analyze_pattern_audit
from bazi_shaoweihua.reading import build_natal_reading
from bazi_shaoweihua.report import build_report
from bazi_shaoweihua.structure import analyze_structure


ROOT = Path(__file__).resolve().parents[1]


def _audit_for(birth: BirthInput):
    chart = build_chart(birth, target_year=2026)
    structure = analyze_structure(chart)
    return chart, structure, analyze_pattern_audit(chart, structure)


def test_sample_one_pattern_audit_keeps_officer_seal_direction_without_claiming_success():
    _chart, _structure, audit = _audit_for(BirthInput(2002, 9, 2, 18, 0, 0, "male"))

    assert audit["version"] == "pattern-audit-mvp-1"
    assert audit["ge_shen"] == {
        "ten_god": "正印",
        "stem": "庚",
        "branch": "申",
        "pattern_name": "正印格候选",
        "basis": "月令主气",
    }
    assert {"ten_god": "正官", "role": "相神候选", "reason": "官生印"} in audit["supporting_agents"]
    assert "官印相生候选" in audit["structure_signals"]
    assert "格神未透，只藏于月令" in audit["condition_gaps"]
    assert "戊癸合火，需查月干正官是否合绊日主" in audit["risk_notes"]
    assert audit["decision"] == "格局复核候选，不判成格或破格"


def test_sample_two_pattern_audit_marks_qisha_needing_control_or_transformation():
    _chart, _structure, audit = _audit_for(BirthInput(2002, 6, 22, 18, 0, 0, "female"))

    assert audit["ge_shen"]["ten_god"] == "七杀"
    assert audit["ge_shen"]["pattern_name"] == "七杀格候选"
    assert {"ten_god": "伤官", "role": "制杀候选", "reason": "食伤制杀"} in audit["supporting_agents"]
    assert {"ten_god": "偏印", "role": "化杀候选", "reason": "印化杀生身"} in audit["supporting_agents"]
    assert "七杀有透出" in audit["success_supports"]
    assert "官杀并见" in audit["clarity_warnings"]
    assert "午午自刑" in audit["risk_notes"]
    assert "酉酉自刑" in audit["risk_notes"]


def test_sample_three_pattern_audit_marks_resource_pattern_with_killing_resource_candidate_and_conflict():
    _chart, _structure, audit = _audit_for(BirthInput(2004, 12, 12, 9, 45, 0, "male"))

    assert audit["ge_shen"]["ten_god"] == "偏印"
    assert audit["ge_shen"]["pattern_name"] == "偏印格候选"
    assert {"ten_god": "七杀", "role": "相神候选", "reason": "杀印相生"} in audit["supporting_agents"]
    assert {"ten_god": "伤官", "role": "配合候选", "reason": "伤官配印"} in audit["supporting_agents"]
    assert "杀印相生候选" in audit["structure_signals"]
    assert "格神未透，只藏于月令" in audit["condition_gaps"]
    assert "巳申合水与刑破并见，不能直接按合化成立处理" in audit["risk_notes"]
    assert "天干有合，需查格神或相神是否被合绊" in audit["clarity_warnings"]


def test_natal_reading_and_cli_include_pattern_audit():
    chart, structure, _audit = _audit_for(BirthInput(2002, 9, 2, 18, 0, 0, "male"))
    report = build_report(chart, structure)

    reading = build_natal_reading(chart, structure, report)

    assert reading["pattern_audit"]["ge_shen"]["ten_god"] == "正印"
    finding = next(item for item in reading["natal_findings"] if item["title"] == "格局复核MVP")
    assert "格神=正印" in finding["evidence"]
    assert "官印相生候选" in finding["conclusion"]
    assert "pattern-audit-mvp-001" in finding["rule_ids"]

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

    assert payload["pattern_audit"]["ge_shen"]["ten_god"] == "七杀"
    assert "官杀并见" in payload["reading"]["pattern_audit"]["clarity_warnings"]
