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


def test_ui_preserves_teaching_metadata_and_reveal_targets(tmp_path):
    from powerpoint_app.ui.teaching_dialog import TeachingDialog
    from powerpoint_app.planning.teaching import load_profile
    app = QApplication.instance() or QApplication([])
    root = tmp_path/'teaching'; shutil.copytree(Path('examples/teaching_dc'), root)
    window = MainWindow(root)
    # Text edit retains the source and identity, while the circuit remains first.
    window.content.setPlainText('Ny forklaring')
    window.commit(); window.save()
    saved = load_plan(root/'slide-plan.json')
    assert saved.slides[0].elements[0].id == 'c1'
    assert saved.slides[0].elements[1].id == 't1'
    assert saved.slides[0].elements[1].source_ids == ['dc']
    assert saved.teaching_profile.required_method
    window.slides.setCurrentRow(2); app.processEvents(); window.commit(); window.save()
    saved = load_plan(root/'slide-plan.json')
    assert [a.target_id for a in saved.slides[2].animations] == ['f31','f32','f33']
    dialog = TeachingDialog(root, window)
    dialog.fields['required_method'].setText('Bevar knudepunktsmetoden')
    dialog.save()
    assert load_profile(root).required_method == 'Bevar knudepunktsmetoden'
    window.close()
