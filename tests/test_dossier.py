import json
import subprocess
import sys
from pathlib import Path

from bazi_shaoweihua.dossier import build_dossier
from bazi_shaoweihua.engine import BirthInput


ROOT = Path(__file__).resolve().parents[1]


def test_build_dossier_contains_reusable_case_payload_for_synthetic_input():
    dossier = build_dossier(
        case_id="synthetic-001",
        privacy_label="synthetic-local-case",
        birth=BirthInput(1990, 1, 1, 12, 0, 0, "male"),
        target_year=2026,
        notes=["synthetic test case"],
    )

    assert dossier["schema_version"] == "bazi-dossier-v1"
    assert dossier["case_id"] == "synthetic-001"
    assert dossier["privacy_label"] == "synthetic-local-case"
    assert dossier["birth_input"]["datetime"] == "1990-01-01T12:00:00"
    assert dossier["birth_input"]["gender"] == "male"
    assert dossier["chart"]["pillars"]["day"]["ganzhi"]
    assert dossier["reading"]["pattern_audit"]["ge_shen"]["ten_god"]
    assert "synthetic test case" in dossier["notes"]


def test_cli_dossier_command_writes_json_file(tmp_path):
    output = tmp_path / "synthetic-002.json"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "bazi_cli.py"),
            "dossier",
            "--case-id",
            "synthetic-002",
            "--privacy-label",
            "synthetic-local-case",
            "--datetime",
            "1991-03-15T18:00:00",
            "--gender",
            "female",
            "--target-year",
            "2026",
            "--note",
            "synthetic cli test",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    payload = json.loads(result.stdout)
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert payload["path"] == str(output)
    assert saved["case_id"] == "synthetic-002"
    assert saved["chart"]["pillars"]["day"]["ganzhi"]
    assert saved["reading"]["pattern_audit"]["ge_shen"]["ten_god"]


def test_cli_dossier_command_can_cache_to_local_ignored_directory(tmp_path):
    cache_dir = tmp_path / "bazi-cache"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "bazi_cli.py"),
            "dossier",
            "--case-id",
            "local-case-001",
            "--privacy-label",
            "private-local-case",
            "--datetime",
            "1992-05-20T09:45:00",
            "--gender",
            "male",
            "--target-year",
            "2026",
            "--cache-dir",
            str(cache_dir),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    payload = json.loads(result.stdout)
    dossier_path = Path(payload["path"])
    index_path = cache_dir / "index.json"
    dossier = json.loads(dossier_path.read_text(encoding="utf-8"))
    index = json.loads(index_path.read_text(encoding="utf-8"))

    assert dossier_path.parent == cache_dir
    assert dossier["case_id"] == "local-case-001"
    assert dossier["reading"]["pattern_audit"]["ge_shen"]["ten_god"]
    assert index["schema_version"] == "bazi-cache-index-v1"
    assert index["cases"][0]["case_id"] == "local-case-001"
    assert index["cases"][0]["file"] == dossier_path.name
