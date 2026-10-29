from __future__ import annotations

import argparse
import json
from datetime import datetime

from bazi_shaoweihua.engine import BirthInput

from .context import TOPICS, build_context


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bazi-ziping",
        description="Calculate a BaZi chart and return concise, cited interpretation context.",
    )
    parser.add_argument("--datetime", required=True, help="Birth local time, e.g. 1991-03-15T18:00:00")
    parser.add_argument("--gender", required=True, choices=("male", "female"))
    parser.add_argument("--target-year", type=int, default=datetime.now().year)
    parser.add_argument("--topic", choices=tuple(TOPICS), default="overview")
    parser.add_argument("--question", default="")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--day-boundary", choices=("23:00", "midnight"), default="23:00")
    parser.add_argument("--timezone-offset", type=float, default=8.0)
    parser.add_argument("--longitude", type=float)
    parser.add_argument("--solar-time-mode", choices=("standard", "mean_solar"), default="standard")
    args = parser.parse_args(argv)

    try:
        dt = datetime.fromisoformat(args.datetime)
    except ValueError as exc:
        parser.error(f"invalid --datetime: {exc}")
    if dt.tzinfo is not None:
        parser.error("pass local birth time without an ISO timezone suffix; set --timezone-offset separately")
    if args.solar_time_mode == "mean_solar" and args.longitude is None:
        parser.error("--longitude is required for --solar-time-mode mean_solar")

    birth = BirthInput(
        year=dt.year, month=dt.month, day=dt.day,
        hour=dt.hour, minute=dt.minute, second=dt.second,
        gender=args.gender, day_boundary=args.day_boundary,
        timezone_offset=args.timezone_offset, longitude=args.longitude,
        solar_time_mode=args.solar_time_mode,
    )
    context = build_context(
        birth, target_year=args.target_year, topic=args.topic, question=args.question
    )
    if args.format == "json":
        print(json.dumps(context, ensure_ascii=False, indent=2))
    else:
        print(render_text(context))
    return 0


def render_text(context: dict) -> str:
    chart = context["chart"]
    topic = context["topic"]
    pillars = chart["pillars"]
    lines = [
        "子平八字 | 可核对的命盘线索",
        "四柱：" + " ".join(pillars[key] or "?" for key in ("year", "month", "day", "hour")),
        f"日主：{chart['day_master']}；关注：{topic['label']}",
        "当前线索：",
    ]
    for signal in topic["natal_signals"][:3]:
        detail = signal.get("ten_god") or signal.get("name") or signal.get("kind") or "结构信号"
        level = signal.get("level") or ""
        lines.append(f"- {detail} {level} ({signal['source']})")
    if not topic["natal_signals"]:
        lines.append("- 暂无足以单独解释此主题的本命信号")
    lines.append("边界：" + (topic["limits"][0] if topic["limits"] else context["interpretation_limits"][1]))
    return "\n".join(lines)
