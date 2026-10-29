from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bazi_shaoweihua.batch import build_batch_summary
from bazi_shaoweihua.dossier import build_dossier, save_dossier_to_cache
from bazi_shaoweihua.engine import BirthInput, build_chart
from bazi_shaoweihua.pattern import analyze_pattern
from bazi_shaoweihua.pattern_audit import analyze_pattern_audit
from bazi_shaoweihua.reading import build_natal_reading
from bazi_shaoweihua.regulation import analyze_regulation
from bazi_shaoweihua.report import build_report
from bazi_shaoweihua.strength import analyze_strength
from bazi_shaoweihua.strength_audit import analyze_strength_audit
from bazi_shaoweihua.structure import analyze_structure
from bazi_shaoweihua.synthesis import build_natal_synthesis
from bazi_shaoweihua.ten_god_influence import analyze_ten_god_influence
from bazi_shaoweihua.transit import analyze_transit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bazi_cli.py")
    subparsers = parser.add_subparsers(dest="command", required=True)

    chart_parser = subparsers.add_parser("chart", help="calculate a BaZi chart")
    chart_parser.add_argument("--datetime", required=True, help="ISO datetime, e.g. 1991-03-15T18:00:00")
    chart_parser.add_argument("--gender", required=True, choices=["male", "female"])
    chart_parser.add_argument("--target-year", type=int)
    chart_parser.add_argument("--day-boundary", choices=["23:00", "midnight"], default="23:00")
    chart_parser.add_argument("--timezone-offset", type=float, default=8.0)
    chart_parser.add_argument("--longitude", type=float)
    chart_parser.add_argument("--solar-time-mode", choices=["standard", "mean_solar"], default="standard")

    structure_parser = subparsers.add_parser("structure", help="calculate BaZi chart and structural facts")
    structure_parser.add_argument("--datetime", required=True, help="ISO datetime, e.g. 1991-03-15T18:00:00")
    structure_parser.add_argument("--gender", required=True, choices=["male", "female"])
    structure_parser.add_argument("--target-year", type=int)
    structure_parser.add_argument("--day-boundary", choices=["23:00", "midnight"], default="23:00")
    structure_parser.add_argument("--timezone-offset", type=float, default=8.0)
    structure_parser.add_argument("--longitude", type=float)
    structure_parser.add_argument("--solar-time-mode", choices=["standard", "mean_solar"], default="standard")

    report_parser = subparsers.add_parser("report", help="calculate chart, structure facts, and applied rule citations")
    report_parser.add_argument("--datetime", required=True, help="ISO datetime, e.g. 1991-03-15T18:00:00")
    report_parser.add_argument("--gender", required=True, choices=["male", "female"])
    report_parser.add_argument("--target-year", type=int)
    report_parser.add_argument("--day-boundary", choices=["23:00", "midnight"], default="23:00")
    report_parser.add_argument("--timezone-offset", type=float, default=8.0)
    report_parser.add_argument("--longitude", type=float)
    report_parser.add_argument("--solar-time-mode", choices=["standard", "mean_solar"], default="standard")

    reading_parser = subparsers.add_parser("reading", help="calculate first-version natal reading with citations")
    reading_parser.add_argument("--datetime", required=True, help="ISO datetime, e.g. 1991-03-15T18:00:00")
    reading_parser.add_argument("--gender", required=True, choices=["male", "female"])
    reading_parser.add_argument("--target-year", type=int)
    reading_parser.add_argument("--day-boundary", choices=["23:00", "midnight"], default="23:00")
    reading_parser.add_argument("--timezone-offset", type=float, default=8.0)
    reading_parser.add_argument("--longitude", type=float)
    reading_parser.add_argument("--solar-time-mode", choices=["standard", "mean_solar"], default="standard")

    dossier_parser = subparsers.add_parser("dossier", help="build a reusable BaZi dossier JSON")
    dossier_parser.add_argument("--case-id", required=True)
    dossier_parser.add_argument("--privacy-label", required=True)
    dossier_parser.add_argument("--datetime", required=True, help="ISO datetime, e.g. 1991-03-15T18:00:00")
    dossier_parser.add_argument("--gender", required=True, choices=["male", "female"])
    dossier_parser.add_argument("--target-year", type=int, default=2026)
    dossier_parser.add_argument("--day-boundary", choices=["23:00", "midnight"], default="23:00")
    dossier_parser.add_argument("--timezone-offset", type=float, default=8.0)
    dossier_parser.add_argument("--longitude", type=float)
    dossier_parser.add_argument("--solar-time-mode", choices=["standard", "mean_solar"], default="standard")
    dossier_parser.add_argument("--note", action="append", default=[])
    dossier_parser.add_argument("--output")
    dossier_parser.add_argument("--cache-dir", help="write dossier to a local ignored cache directory and update index.json")

    batch_parser = subparsers.add_parser("batch", help="read private case file and output compact summaries")
    batch_parser.add_argument("--input", required=True, help="JSON file with a top-level cases list")

    args = parser.parse_args(argv)
    if args.command == "batch":
        payload = build_batch_summary(Path(args.input))
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command in {"chart", "structure", "report", "reading", "dossier"}:
        dt = datetime.fromisoformat(args.datetime)
        birth = BirthInput(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second,
            gender=args.gender,
            day_boundary=args.day_boundary,
            timezone_offset=args.timezone_offset,
            longitude=args.longitude,
            solar_time_mode=args.solar_time_mode,
        )
        if args.command == "dossier":
            dossier = build_dossier(
                case_id=args.case_id,
                privacy_label=args.privacy_label,
                birth=birth,
                target_year=args.target_year,
                notes=args.note,
            )
            if args.cache_dir:
                path = save_dossier_to_cache(dossier, Path(args.cache_dir))
                print(json.dumps({"path": str(path), "case_id": args.case_id}, ensure_ascii=False, indent=2))
            elif args.output:
                output = Path(args.output)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(json.dumps(dossier, ensure_ascii=False, indent=2), encoding="utf-8")
                print(json.dumps({"path": str(output), "case_id": args.case_id}, ensure_ascii=False, indent=2))
            else:
                print(json.dumps(dossier, ensure_ascii=False, indent=2))
            return 0
        chart = build_chart(birth, target_year=args.target_year)
        payload = chart
        if args.command in {"structure", "report", "reading"}:
            structure = analyze_structure(chart)
            payload = {"chart": chart, "structure": structure}
            if args.command in {"report", "reading"}:
                report = build_report(chart, structure)
                payload = {"chart": chart, "structure": structure, "report": report}
                if args.command == "reading":
                    strength = analyze_strength(chart, structure)
                    strength_audit = analyze_strength_audit(chart, structure)
                    ten_god_influence = analyze_ten_god_influence(chart, structure)
                    pattern = analyze_pattern(chart, structure)
                    pattern_audit = analyze_pattern_audit(chart, structure)
                    regulation = analyze_regulation(chart, structure)
                    transit = analyze_transit(chart, structure)
                    reading = build_natal_reading(chart, structure, report)
                    synthesis = build_natal_synthesis(chart, structure, reading)
                    payload = {
                        "chart": chart,
                        "structure": structure,
                        "strength": strength,
                        "strength_audit": strength_audit,
                        "ten_god_influence": ten_god_influence,
                        "pattern": pattern,
                        "pattern_audit": pattern_audit,
                        "regulation": regulation,
                        "transit": transit,
                        "synthesis": synthesis,
                        "report": report,
                        "reading": reading,
                    }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
