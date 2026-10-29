import pytest

from bazi_shaoweihua.engine import BirthInput, build_chart


tyme4py = pytest.importorskip("tyme4py")


@pytest.mark.parametrize(
    "birth",
    [
        BirthInput(1983, 2, 15, 20, 0, 0, "female"),
        BirthInput(2002, 6, 22, 18, 0, 0, "female"),
        BirthInput(1990, 12, 23, 8, 37, 0, "male"),
        BirthInput(1988, 2, 15, 23, 30, 0, "male", day_boundary="23:00"),
    ],
)
def test_core_pillars_match_tyme4py_for_2300_day_boundary(birth):
    from tyme4py.solar import SolarTime

    chart = build_chart(birth)
    tyme_hour = SolarTime.from_ymd_hms(
        birth.year,
        birth.month,
        birth.day,
        birth.hour,
        birth.minute,
        birth.second,
    ).get_lunar_hour()
    tyme_eight_char = tyme_hour.get_eight_char()

    assert chart["pillars"]["year"]["ganzhi"] == tyme_eight_char.get_year().get_name()
    assert chart["pillars"]["month"]["ganzhi"] == tyme_eight_char.get_month().get_name()
    assert chart["pillars"]["day"]["ganzhi"] == tyme_eight_char.get_day().get_name()
    assert chart["pillars"]["hour"]["ganzhi"] == tyme_eight_char.get_hour().get_name()
