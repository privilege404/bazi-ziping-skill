from bazi_shaoweihua.engine import BirthInput, build_chart
from bazi_shaoweihua.strength import analyze_strength
from bazi_shaoweihua.structure import analyze_structure


def _strength_for(birth: BirthInput):
    chart = build_chart(birth, target_year=2026)
    structure = analyze_structure(chart)
    return analyze_strength(chart, structure)


def test_sample_one_water_in_shen_month_gets_season_support_but_lacks_same_stem_roots():
    strength = _strength_for(BirthInput(2002, 9, 2, 18, 0, 0, "male"))

    assert strength["day_master"] == "癸"
    assert strength["day_master_element"] == "水"
    assert strength["season"]["season"] == "autumn"
    assert strength["season"]["state"] == "相"
    assert strength["season"]["score"] == 30
    assert strength["roots"]["same_stem_root_weight"] == 0
    assert strength["support"]["visible_support_score"] > 0
    assert strength["pressure"]["visible_pressure_score"] > 0
    assert strength["classification"] in {"中和", "中和偏强"}
    assert "有季令相气" in strength["summary"]


def test_sample_two_xin_metal_has_roots_but_is_dead_in_summer_and_under_fire_pressure():
    strength = _strength_for(BirthInput(2002, 6, 22, 18, 0, 0, "female"))

    assert strength["day_master"] == "辛"
    assert strength["day_master_element"] == "金"
    assert strength["season"]["season"] == "summer"
    assert strength["season"]["state"] == "死"
    assert strength["season"]["score"] == -45
    assert strength["roots"]["same_stem_root_weight"] == 200
    assert strength["roots"]["root_score"] == 35
    assert strength["pressure"]["visible_pressure_score"] >= 40
    assert strength["classification"] in {"偏弱", "中和偏弱"}
    assert "虽有酉根" in strength["summary"]


def test_sample_three_yi_wood_in_winter_gets_season_generating_support_but_no_roots():
    strength = _strength_for(BirthInput(2004, 12, 12, 9, 45, 0, "male"))

    assert strength["day_master"] == "乙"
    assert strength["day_master_element"] == "木"
    assert strength["season"]["season"] == "winter"
    assert strength["season"]["state"] == "相"
    assert strength["roots"]["same_stem_root_weight"] == 0
    assert strength["support"]["hidden_support_score"] > 0
    assert strength["pressure"]["visible_pressure_score"] > 0
    assert strength["classification"] in {"偏弱", "中和偏弱", "中和"}
