from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal

from lunar_python import Solar


STEMS = "甲乙丙丁戊己庚辛壬癸"
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
YANG_STEMS = {"甲", "丙", "戊", "庚", "壬"}
ELEMENTS = {
    "甲": "木",
    "乙": "木",
    "丙": "火",
    "丁": "火",
    "戊": "土",
    "己": "土",
    "庚": "金",
    "辛": "金",
    "壬": "水",
    "癸": "水",
    "子": "水",
    "丑": "土",
    "寅": "木",
    "卯": "木",
    "辰": "土",
    "巳": "火",
    "午": "火",
    "未": "土",
    "申": "金",
    "酉": "金",
    "戌": "土",
    "亥": "水",
}


Gender = Literal["male", "female"]
DayBoundary = Literal["23:00", "midnight"]
SolarTimeMode = Literal["standard", "mean_solar"]


@dataclass(frozen=True)
class BirthInput:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int
    gender: Gender
    day_boundary: DayBoundary = "23:00"
    timezone_offset: float = 8.0
    longitude: float | None = None
    solar_time_mode: SolarTimeMode = "standard"


def build_chart(birth: BirthInput, target_year: int | None = None) -> dict:
    _validate_birth(birth)
    adjusted = _adjust_datetime(birth)
    solar = Solar.fromYmdHms(
        adjusted.year,
        adjusted.month,
        adjusted.day,
        adjusted.hour,
        adjusted.minute,
        adjusted.second,
    )
    lunar = solar.getLunar()
    eight_char = lunar.getEightChar()
    eight_char.setSect(_sect_for_boundary(birth.day_boundary))

    pillars = {
        "year": _pillar(eight_char.getYear()),
        "month": _pillar(eight_char.getMonth()),
        "day": _pillar(eight_char.getDay()),
        "hour": _pillar(eight_char.getTime()),
    }
    target_year = target_year or adjusted.year
    luck = _luck(eight_char, birth.gender, pillars["year"]["stem"], target_year)
    annual_ganzhi = _annual_ganzhi(target_year, birth.day_boundary)

    return {
        "input": {
            "datetime": _format_input_datetime(birth),
            "gender": birth.gender,
            "timezone_offset": birth.timezone_offset,
            "longitude": birth.longitude,
            "solar_time_mode": birth.solar_time_mode,
        },
        "calculation_datetime": adjusted.isoformat(timespec="seconds"),
        "lunar_date": lunar.toString(),
        "day_boundary": birth.day_boundary,
        "pillars": pillars,
        "day_master": pillars["day"]["stem"],
        "five_elements": {
            "pillars": {
                "year": eight_char.getYearWuXing(),
                "month": eight_char.getMonthWuXing(),
                "day": eight_char.getDayWuXing(),
                "hour": eight_char.getTimeWuXing(),
            }
        },
        "element_counts": _element_counts(pillars),
        "ten_gods": {
            "heaven_stems": {
                "year": eight_char.getYearShiShenGan(),
                "month": eight_char.getMonthShiShenGan(),
                "day": eight_char.getDayShiShenGan(),
                "hour": eight_char.getTimeShiShenGan(),
            },
            "earth_branches": {
                "year": eight_char.getYearShiShenZhi(),
                "month": eight_char.getMonthShiShenZhi(),
                "day": eight_char.getDayShiShenZhi(),
                "hour": eight_char.getTimeShiShenZhi(),
            },
        },
        "hidden_stems": {
            "year": eight_char.getYearHideGan(),
            "month": eight_char.getMonthHideGan(),
            "day": eight_char.getDayHideGan(),
            "hour": eight_char.getTimeHideGan(),
        },
        "nayin": {
            "year": eight_char.getYearNaYin(),
            "month": eight_char.getMonthNaYin(),
            "day": eight_char.getDayNaYin(),
            "hour": eight_char.getTimeNaYin(),
        },
        "growth_stage": {
            "year": eight_char.getYearDiShi(),
            "month": eight_char.getMonthDiShi(),
            "day": eight_char.getDayDiShi(),
            "hour": eight_char.getTimeDiShi(),
        },
        "xun_kong": {
            "year": eight_char.getYearXunKong(),
            "month": eight_char.getMonthXunKong(),
            "day": eight_char.getDayXunKong(),
            "hour": eight_char.getTimeXunKong(),
        },
        "luck": luck,
        "annual": {
            "target_year": target_year,
            "ganzhi": annual_ganzhi,
            "stem": annual_ganzhi[0],
            "branch": annual_ganzhi[1],
        },
        "calculation_trace": _trace(birth, adjusted),
    }


def _validate_birth(birth: BirthInput) -> None:
    if birth.gender not in {"male", "female"}:
        raise ValueError("gender must be 'male' or 'female'")
    if birth.day_boundary not in {"23:00", "midnight"}:
        raise ValueError("day_boundary must be '23:00' or 'midnight'")
    if birth.solar_time_mode not in {"standard", "mean_solar"}:
        raise ValueError("solar_time_mode must be 'standard' or 'mean_solar'")
    if birth.solar_time_mode == "mean_solar" and birth.longitude is None:
        raise ValueError("longitude is required when solar_time_mode='mean_solar'")
    datetime(birth.year, birth.month, birth.day, birth.hour, birth.minute, birth.second)


def _adjust_datetime(birth: BirthInput) -> datetime:
    dt = datetime(birth.year, birth.month, birth.day, birth.hour, birth.minute, birth.second)
    if birth.solar_time_mode == "standard":
        return dt
    standard_meridian = birth.timezone_offset * 15.0
    minutes = (birth.longitude - standard_meridian) * 4.0
    return dt + timedelta(minutes=minutes)


def _sect_for_boundary(day_boundary: DayBoundary) -> int:
    return 1 if day_boundary == "23:00" else 2


def _pillar(ganzhi: str) -> dict:
    return {"stem": ganzhi[0], "branch": ganzhi[1], "ganzhi": ganzhi}


def _element_counts(pillars: dict) -> dict:
    counts = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for pillar in pillars.values():
        counts[ELEMENTS[pillar["stem"]]] += 1
        counts[ELEMENTS[pillar["branch"]]] += 1
    return counts


def _luck(eight_char, gender: Gender, year_stem: str, target_year: int) -> dict:
    gender_code = 1 if gender == "male" else 0
    yun = eight_char.getYun(gender_code)
    cycles = []
    for da_yun in yun.getDaYun():
        cycle = {
            "index": da_yun.getIndex(),
            "ganzhi": da_yun.getGanZhi(),
            "start_year": da_yun.getStartYear(),
            "end_year": da_yun.getEndYear(),
            "start_age": da_yun.getStartAge(),
            "end_age": da_yun.getEndAge(),
        }
        cycles.append(cycle)
    current = next(
        (cycle for cycle in cycles if cycle["start_year"] <= target_year <= cycle["end_year"]),
        None,
    )
    return {
        "direction": _luck_direction(gender, year_stem),
        "start": {
            "years": yun.getStartYear(),
            "months": yun.getStartMonth(),
            "days": yun.getStartDay(),
            "solar_date": yun.getStartSolar().toYmd(),
        },
        "cycles": cycles,
        "current_cycle": current,
    }


def _luck_direction(gender: Gender, year_stem: str) -> str:
    is_yang_year = year_stem in YANG_STEMS
    is_male = gender == "male"
    return "forward" if is_yang_year == is_male else "backward"


def _annual_ganzhi(year: int, day_boundary: DayBoundary) -> str:
    solar = Solar.fromYmdHms(year, 7, 1, 12, 0, 0)
    eight_char = solar.getLunar().getEightChar()
    eight_char.setSect(_sect_for_boundary(day_boundary))
    return eight_char.getYear()


def _format_input_datetime(birth: BirthInput) -> str:
    dt = datetime(birth.year, birth.month, birth.day, birth.hour, birth.minute, birth.second)
    return dt.isoformat(timespec="seconds")


def _trace(birth: BirthInput, adjusted: datetime) -> list[dict]:
    trace = [
        {
            "step": "calendar_engine",
            "detail": "Pillars are calculated with lunar_python EightChar, using solar terms for year/month pillars.",
        },
        {
            "step": "day_boundary",
            "detail": "23:00 means zi hour changes the day pillar at 23:00; midnight keeps the civil date until 00:00.",
            "value": birth.day_boundary,
        },
    ]
    if birth.solar_time_mode == "mean_solar":
        trace.append(
            {
                "step": "mean_solar_time",
                "detail": "Clock time adjusted by 4 minutes per longitude degree from the timezone meridian.",
                "longitude": birth.longitude,
                "timezone_meridian": birth.timezone_offset * 15.0,
                "adjusted_datetime": adjusted.isoformat(timespec="seconds"),
            }
        )
    return trace
