from bazi_shaoweihua.engine import BirthInput, build_chart


def test_build_chart_uses_lichun_year_and_month_pillars():
    chart = build_chart(
        BirthInput(
            year=1983,
            month=2,
            day=15,
            hour=20,
            minute=0,
            second=0,
            gender="female",
        )
    )

    assert chart["pillars"] == {
        "year": {"stem": "癸", "branch": "亥", "ganzhi": "癸亥"},
        "month": {"stem": "甲", "branch": "寅", "ganzhi": "甲寅"},
        "day": {"stem": "甲", "branch": "戌", "ganzhi": "甲戌"},
        "hour": {"stem": "甲", "branch": "戌", "ganzhi": "甲戌"},
    }
    assert chart["day_master"] == "甲"
    assert chart["lunar_date"] == "一九八三年正月初三"


def test_ten_gods_wuxing_and_hidden_stems_are_computed_from_day_master():
    chart = build_chart(
        BirthInput(
            year=2002,
            month=6,
            day=22,
            hour=18,
            minute=0,
            second=0,
            gender="female",
        )
    )

    assert chart["pillars"]["day"]["ganzhi"] == "辛酉"
    assert chart["five_elements"]["pillars"] == {
        "year": "水火",
        "month": "火火",
        "day": "金金",
        "hour": "火金",
    }
    assert chart["ten_gods"]["heaven_stems"] == {
        "year": "伤官",
        "month": "正官",
        "day": "日主",
        "hour": "七杀",
    }
    assert chart["ten_gods"]["earth_branches"]["year"] == ["七杀", "偏印"]
    assert chart["hidden_stems"]["month"] == ["丁", "己"]
    assert chart["element_counts"]["火"] == 4
    assert chart["element_counts"]["金"] == 3


def test_luck_cycles_for_female_yang_year_run_backward():
    chart = build_chart(
        BirthInput(
            year=2002,
            month=6,
            day=22,
            hour=18,
            minute=0,
            second=0,
            gender="female",
        )
    )

    assert chart["luck"]["direction"] == "backward"
    assert chart["luck"]["start"] == {
        "years": 5,
        "months": 6,
        "days": 10,
        "solar_date": "2008-01-01",
    }
    assert chart["luck"]["cycles"][:4] == [
        {
            "index": 0,
            "ganzhi": "",
            "start_year": 2002,
            "end_year": 2007,
            "start_age": 1,
            "end_age": 6,
        },
        {
            "index": 1,
            "ganzhi": "乙巳",
            "start_year": 2008,
            "end_year": 2017,
            "start_age": 7,
            "end_age": 16,
        },
        {
            "index": 2,
            "ganzhi": "甲辰",
            "start_year": 2018,
            "end_year": 2027,
            "start_age": 17,
            "end_age": 26,
        },
        {
            "index": 3,
            "ganzhi": "癸卯",
            "start_year": 2028,
            "end_year": 2037,
            "start_age": 27,
            "end_age": 36,
        },
    ]


def test_zi_hour_day_boundary_is_explicit_and_defaults_to_2300_changeover():
    default_chart = build_chart(
        BirthInput(
            year=1988,
            month=2,
            day=15,
            hour=23,
            minute=30,
            second=0,
            gender="male",
        )
    )
    midnight_chart = build_chart(
        BirthInput(
            year=1988,
            month=2,
            day=15,
            hour=23,
            minute=30,
            second=0,
            gender="male",
            day_boundary="midnight",
        )
    )

    assert default_chart["day_boundary"] == "23:00"
    assert default_chart["pillars"]["day"]["ganzhi"] == "辛丑"
    assert default_chart["pillars"]["hour"]["ganzhi"] == "戊子"
    assert midnight_chart["day_boundary"] == "midnight"
    assert midnight_chart["pillars"]["day"]["ganzhi"] == "庚子"
    assert midnight_chart["pillars"]["hour"]["ganzhi"] == "戊子"


def test_current_luck_cycle_and_flow_year_are_reported():
    chart = build_chart(
        BirthInput(
            year=1990,
            month=12,
            day=23,
            hour=8,
            minute=37,
            second=0,
            gender="male",
        ),
        target_year=2026,
    )

    assert chart["pillars"]["day"]["ganzhi"] == "壬戌"
    assert chart["luck"]["current_cycle"]["ganzhi"] == "壬辰"
    assert chart["luck"]["current_cycle"]["start_year"] == 2025
    assert chart["annual"]["target_year"] == 2026
    assert chart["annual"]["ganzhi"] == "丙午"
