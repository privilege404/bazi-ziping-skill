from bazi_shaoweihua.engine import BirthInput, build_chart
from bazi_shaoweihua.report import build_report
from bazi_shaoweihua.structure import analyze_structure


def _report_for(birth: BirthInput):
    chart = build_chart(birth, target_year=2026)
    structure = analyze_structure(chart)
    return build_report(chart, structure)


def test_report_cites_rules_and_observes_first_sample_structure():
    report = _report_for(BirthInput(2002, 9, 2, 18, 0, 0, "male"))

    assert report["summary"]["pillars"] == "壬午 戊申 癸酉 辛酉"
    assert report["summary"]["day_master"] == "癸"
    assert any(rule["id"] == "zpxz-month-command-001" for rule in report["applied_rules"])
    assert any(rule["id"] == "dts-flow-combination-001" for rule in report["applied_rules"])
    assert any(rule["id"] == "smth-dexiu-001" for rule in report["applied_rules"])
    assert any(rule["id"] == "wuxing-generating-controlling-001" for rule in report["applied_rules"])
    assert any(obs["key"] == "stem_relations" and "戊癸合火" in obs["value"] for obs in report["observations"])
    assert any(obs["key"] == "branch_relations" and "申酉半会金" in obs["value"] and "酉酉自刑" in obs["value"] for obs in report["observations"])
    assert any(obs["key"] == "element_interactions" and "戊土克壬水" in obs["value"] for obs in report["observations"])
    assert any(obs["key"] == "shensha" and "德秀贵人" in obs["value"] for obs in report["observations"])


def test_report_cites_shensha_and_roots_for_second_sample():
    report = _report_for(BirthInput(2002, 6, 22, 18, 0, 0, "female"))

    assert report["summary"]["pillars"] == "壬午 丙午 辛酉 丁酉"
    assert any(rule["id"] == "xjbf-shensha-aux-001" for rule in report["applied_rules"])
    assert any(obs["key"] == "roots" and "日支酉藏辛主气" in obs["value"] for obs in report["observations"])
    assert any(obs["key"] == "shensha" and "天乙贵人" in obs["value"] for obs in report["observations"])


def test_report_cites_storage_and_conflicting_relations_for_third_sample():
    report = _report_for(BirthInput(2004, 12, 12, 9, 45, 0, "male"))

    assert report["summary"]["pillars"] == "甲申 丙子 乙丑 辛巳"
    assert any(rule["id"] == "smth-storage-001" for rule in report["applied_rules"])
    assert any(obs["key"] == "storages" and "丑为金库" in obs["value"] for obs in report["observations"])
    assert any(obs["key"] == "branch_relations" and "巳申合水" in obs["value"] and "巳申破" in obs["value"] for obs in report["observations"])
