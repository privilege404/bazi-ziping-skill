import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_cli_batch_reads_private_case_file_and_outputs_compact_summaries(tmp_path):
    case_file = tmp_path / "cases.json"
    case_file.write_text(
        json.dumps(
            {
                "cases": [
                    {
                        "case_id": "synthetic-a",
                        "datetime": "1991-03-15T18:00:00",
                        "gender": "female",
                        "target_year": 2026,
                    },
                    {
                        "case_id": "synthetic-b",
                        "datetime": "1992-05-20T09:45:00",
                        "gender": "male",
                        "target_year": 2026,
                    },
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "bazi_cli.py"),
            "batch",
            "--input",
            str(case_file),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(result.stdout)

    assert payload["schema_version"] == "bazi-batch-summary-v1"
    assert [item["case_id"] for item in payload["cases"]] == ["synthetic-a", "synthetic-b"]
    first = payload["cases"][0]
    assert first["pillars"]
    assert first["day_master"]
    assert first["strength"]["classification"]
    assert first["pattern"]["ge_shen"]
    assert first["transit"]["annual"]
    assert first["synthesis_topics"][-1] == "transit_overall"
