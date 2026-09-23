import os
import json
import shutil
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from powerpoint_app.projects import load_plan
from powerpoint_app.ui.window import MainWindow


def test_ui_edits_reorders_adds_deletes_and_saves(tmp_path: Path):
    app = QApplication.instance() or QApplication([])
    root = tmp_path / "project"; shutil.copytree(Path("examples/demo_project"), root)
    window = MainWindow(root); window.slides.setCurrentRow(0); app.processEvents()
    window.title.setText("Rettet titel"); window.content.setPlainText("Første tekst\nAnden tekst"); window.notes.setPlainText("Rettede noter"); window.commit(); window.save()
    saved = load_plan(root / "slide-plan.json")
    assert saved.slides[0].title == "Rettet titel" and saved.slides[0].speaker_notes == "Rettede noter"
    assert [e.text for e in saved.slides[0].elements if e.type == "text"] == ["Første tekst", "Anden tekst"]
    advanced = saved.slides[0].model_dump(); advanced["layout"] = "formula_steps"; advanced["elements"] = [{"id": "formula", "type": "formula", "latex": "U=R\\cdot I"}]
    window.apply_slide_json(json.dumps(advanced)); assert window.plan.slides[0].layout == "formula_steps" and window.plan.slides[0].elements[0].type == "formula"
    original_count = len(window.plan.slides); window.add_slide(); assert len(window.plan.slides) == original_count + 1
    window.move(-1); window.delete_slide(); assert len(window.plan.slides) == original_count
    window.close()
