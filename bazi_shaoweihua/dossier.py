from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
import json
from pathlib import Path
import re

from .engine import BirthInput, build_chart
from .reading import build_natal_reading
from .report import build_report
from .structure import analyze_structure


def build_dossier(
    case_id: str,
    privacy_label: str,
    birth: BirthInput,
    target_year: int = 2026,
    notes: list[str] | None = None,
) -> dict:
    chart = build_chart(birth, target_year=target_year)
    structure = analyze_structure(chart)
    report = build_report(chart, structure)
    reading = build_natal_reading(chart, structure, report)
    return {
        "schema_version": "bazi-dossier-v1",
        "case_id": case_id,
        "privacy_label": privacy_label,
        "created_by": "bazi-shaoweihua skill",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "target_year": target_year,
        "birth_input": _birth_input_payload(birth),
        "chart": chart,
        "structure": structure,
        "report": report,
        "reading": reading,
        "notes": notes or [],
        "limits": [
            "This dossier caches deterministic calculations and MVP audits for repeated local evaluation.",
            "Keep private dossiers in an ignored local cache directory; do not store personal birth data in skill assets.",
            "It is not a final expert judgment; case calibration should append notes instead of overwriting facts.",
        ],
    }


def save_dossier_to_cache(dossier: dict, cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{_safe_filename(dossier['case_id'])}.json"
    dossier_path = cache_dir / filename
    dossier_path.write_text(json.dumps(dossier, ensure_ascii=False, indent=2), encoding="utf-8")
    _update_index(cache_dir, dossier, filename)
    return dossier_path


def _birth_input_payload(birth: BirthInput) -> dict:
    payload = asdict(birth)
    payload["datetime"] = datetime(
        birth.year,
        birth.month,
        birth.day,
        birth.hour,
        birth.minute,
        birth.second,
    ).isoformat(timespec="seconds")
    return payload


def _update_index(cache_dir: Path, dossier: dict, filename: str) -> None:
    index_path = cache_dir / "index.json"
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
    else:
        index = {
            "schema_version": "bazi-cache-index-v1",
            "description": "Local ignored cache of BaZi dossiers generated during testing.",
            "cases": [],
        }
    entry = {
        "case_id": dossier["case_id"],
        "privacy_label": dossier["privacy_label"],
        "file": filename,
        "target_year": dossier["target_year"],
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    index["cases"] = [item for item in index["cases"] if item["case_id"] != dossier["case_id"]]
    index["cases"].append(entry)
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


def _safe_filename(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip(".-")
    return safe or "case"
