import json

import pytest

from powerpoint_app.domain.models import SlidePlan
from powerpoint_app.projects import load_plan


def minimal_plan():
    return {
        "schema_version": "1.0",
        "deck": {"title": "Test", "audience": "Studerende", "duration_minutes": 5},
        "sources": [{"id": "src1", "file": "sources/a.md"}],
        "slides": [{"id": "s1", "layout": "title", "title": "Æ, ø, å og Ω", "elements": [], "speaker_notes": "Note"}],
    }


def test_unknown_fields_are_rejected():
    data = minimal_plan(); data["surprise"] = True
    with pytest.raises(ValueError, match="surprise"):
        SlidePlan.model_validate(data)


def test_unknown_animation_target_is_rejected():
    data = minimal_plan(); data["slides"][0]["animations"] = [{"target_id": "missing", "effect": "appear", "trigger": "on_click", "order": 1}]
    with pytest.raises(ValueError, match="ukendt element"):
        SlidePlan.model_validate(data)


def test_unsafe_asset_path_is_rejected():
    data = minimal_plan(); data["slides"][0]["elements"] = [{"id": "img", "type": "image", "asset": "../secret.png", "alt_text": "x"}]
    with pytest.raises(ValueError, match="sikker relativ sti"):
        SlidePlan.model_validate(data)


def test_json_roundtrip_preserves_unicode():
    plan = SlidePlan.model_validate(minimal_plan())
    assert SlidePlan.model_validate_json(plan.model_dump_json()).slides[0].title == "Æ, ø, å og Ω"


def test_invalid_json_has_clear_error(tmp_path):
    bad = tmp_path / "bad.json"; bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError, match="Ugyldig slideplan"):
        load_plan(bad)


def test_long_danish_text_is_flagged(tmp_path):
    from powerpoint_app.quality import inspect_plan
    data = minimal_plan(); data["slides"][0]["elements"] = [{"id": "e1", "type": "text", "text": "æøå " * 200}]
    findings = inspect_plan(SlidePlan.model_validate(data), tmp_path)
    assert any("overflow" in finding.message for finding in findings)
