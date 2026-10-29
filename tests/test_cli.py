import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_cli_outputs_structured_chart_json():
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "bazi_cli.py"),
            "chart",
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

    chart = json.loads(result.stdout)
    assert chart["pillars"]["year"]["ganzhi"] == "壬午"
    assert chart["pillars"]["month"]["ganzhi"] == "丙午"
    assert chart["pillars"]["day"]["ganzhi"] == "辛酉"
    assert chart["pillars"]["hour"]["ganzhi"] == "丁酉"
    assert chart["luck"]["current_cycle"]["ganzhi"] == "甲辰"
    assert chart["annual"]["ganzhi"] == "丙午"
