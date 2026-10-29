from __future__ import annotations

import json

from bazi_shaoweihua.engine import BirthInput
from bazi_ziping.cli import main
from bazi_ziping.context import build_context


def test_build_context_keeps_calculation_and_topic_evidence_separate():
    context = build_context(
        BirthInput(2002, 9, 2, 18, 0, 0, "male"),
        target_year=2026,
        topic="education",
        question="现在是什么学历？",
    )

    assert context["chart"]["pillars"] == {
        "year": "壬午", "month": "戊申", "day": "癸酉", "hour": "辛酉"
    }
    assert context["chart"]["day_master"] == "癸"
    assert context["topic"]["id"] == "education"
    assert context["question"] == "现在是什么学历？"
    assert context["topic"]["natal_signals"]
    assert all(signal["source"].startswith("reading.life_topics.") for signal in context["topic"]["natal_signals"])
    assert all(
        signal["source"].split(".topics[", 1)[1].split("]", 1)[0].isdigit()
        for signal in context["topic"]["natal_signals"]
    )
    assert any("不直接断最高学历" in limit for limit in context["topic"]["limits"])
    assert "学历" not in context.get("prediction", "")


def test_cli_json_outputs_parseable_context(capsys):
    result = main([
        "--datetime", "2002-06-19T23:51:00",
        "--gender", "female",
        "--target-year", "2026",
        "--topic", "overview",
        "--format", "json",
    ])

    assert result == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["chart"]["day_boundary"] == "23:00"
    assert payload["chart"]["pillars"]["day"] == "己未"
    assert payload["topic"]["id"] == "overview"


def test_cli_text_is_compact_and_does_not_claim_outcomes(capsys):
    result = main([
        "--datetime", "2002-09-02T18:00:00",
        "--gender", "male",
        "--target-year", "2026",
        "--topic", "education",
    ])

    assert result == 0
    output = capsys.readouterr().out
    assert "壬午" in output
    assert "学历" in output
    assert "不能" in output or "不直接" in output
    assert len(output) < 2500
