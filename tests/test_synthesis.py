import json
import subprocess
import sys
from pathlib import Path

from bazi_shaoweihua.engine import BirthInput, build_chart
from bazi_shaoweihua.reading import build_natal_reading
from bazi_shaoweihua.report import build_report
from bazi_shaoweihua.structure import analyze_structure
from bazi_shaoweihua.synthesis import build_natal_synthesis


ROOT = Path(__file__).resolve().parents[1]


def _synthesis_for(birth: BirthInput):
    chart = build_chart(birth, target_year=2026)
    structure = analyze_structure(chart)
    report = build_report(chart, structure)
    reading = build_natal_reading(chart, structure, report)
    return build_natal_synthesis(chart, structure, reading)


def test_natal_synthesis_returns_auditable_conclusions_for_synthetic_input():
    synthesis = _synthesis_for(BirthInput(1991, 3, 15, 18, 0, 0, "female"))

    assert synthesis["version"] == "natal-synthesis-mvp-1"
    assert synthesis["decision_policy"] == "结论必须引用已计算事实；不从模型记忆补断。"
    topics = [item["topic"] for item in synthesis["conclusions"]]
    assert topics == ["day_master_strength", "pattern", "ten_gods", "regulation", "relations", "transit_overall"]
    for item in synthesis["conclusions"]:
        assert item["conclusion"]
        assert item["confidence"] in {"low", "medium", "high"}
        assert item["evidence"]
        assert item["rule_ids"]
        assert item["limits"]


def test_natal_synthesis_is_included_in_reading_and_cli_payload():
    chart = build_chart(BirthInput(1992, 5, 20, 9, 45, 0, "male"), target_year=2026)
    structure = analyze_structure(chart)
    report = build_report(chart, structure)
    reading = build_natal_reading(chart, structure, report)

    assert reading["synthesis"]["version"] == "natal-synthesis-mvp-1"
    assert any(item["topic"] == "pattern" for item in reading["synthesis"]["conclusions"])

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

    assert payload["synthesis"]["version"] == "natal-synthesis-mvp-1"
    assert payload["reading"]["synthesis"]["decision_policy"] == "结论必须引用已计算事实；不从模型记忆补断。"
