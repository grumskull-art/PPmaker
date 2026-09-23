import json
from pathlib import Path

from PIL import Image

from powerpoint_app.domain.models import SlidePlan
from powerpoint_app.projects import create_project, load_plan, save_plan


def plan(title="Første"):
    return SlidePlan.model_validate({"schema_version": "1.0", "deck": {"title": title, "audience": "M", "duration_minutes": 2}, "slides": [{"id": "s1", "layout": "title", "title": title}]})


def test_save_load_and_history(tmp_path: Path):
    create_project(tmp_path, "Demo"); save_plan(tmp_path, plan()); save_plan(tmp_path, plan("Anden"))
    assert load_plan(tmp_path / "slide-plan.json").deck.title == "Anden"
    assert len(list((tmp_path / "history").glob("*.json"))) == 1


def test_roundtrip_preserves_order_sources_assets_and_notes(tmp_path: Path):
    create_project(tmp_path); Image.new("RGB", (4, 4), "red").save(tmp_path / "assets" / "x.png")
    data = plan().model_dump(); data["sources"] = [{"id": "src1", "file": "sources/a.md", "locator": "linje 1"}]
    data["slides"] = [
        {"id": "s2", "layout": "key_figure", "title": "B", "speaker_notes": "Note B", "elements": [{"id": "img", "type": "image", "asset": "assets/x.png", "alt_text": "Rød", "source_ids": ["src1"]}]},
        {"id": "s1", "layout": "title", "title": "A", "speaker_notes": "Note A", "elements": []},
    ]
    save_plan(tmp_path, SlidePlan.model_validate(data)); loaded = load_plan(tmp_path / "slide-plan.json")
    assert [slide.id for slide in loaded.slides] == ["s2", "s1"] and loaded.slides[0].speaker_notes == "Note B"
    assert loaded.slides[0].elements[0].source_ids == ["src1"] and (tmp_path / loaded.slides[0].elements[0].asset).is_file()
