from __future__ import annotations

import json
from pathlib import Path
from threading import Event
import shutil

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox, QFileDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QDialog, QDialogButtonBox, QInputDialog, QMainWindow, QMessageBox, QPushButton, QSpinBox, QSplitter, QTextEdit,
    QVBoxLayout, QWidget,
)

from powerpoint_app.domain.models import Slide, SlidePlan, TextElement
from powerpoint_app.importers import import_document
from powerpoint_app.planning import compact_prompt
from powerpoint_app.planning.teaching import teaching_brief
from powerpoint_app.ui.teaching_dialog import TeachingDialog
from powerpoint_app.projects import add_source, load_plan, safe_export_path, save_plan
from powerpoint_app.quality import inspect_plan
from powerpoint_app.rendering import PptxRenderer, load_theme, render_preview


class WorkerSignals(QObject):
    done = Signal(str)
    failed = Signal(str)


class ExportWorker(QRunnable):
    def __init__(self, root: Path, plan: SlidePlan, target: Path, mode="auto"):
        super().__init__(); self.root = root; self.plan = plan; self.target = target; self.mode = mode; self.signals = WorkerSignals(); self.cancelled = Event()

    def run(self):
        try:
            theme_file = self.root / "theme.json"
            PptxRenderer(self.root, load_theme(theme_file if theme_file.is_file() else None)).render(self.plan, self.target, self.cancelled.is_set, mode=self.mode); self.signals.done.emit(str(self.target))
        except Exception as exc:
            self.signals.failed.emit(str(exc))

    def cancel(self):
        self.cancelled.set()


class PreviewWorker(QRunnable):
    def __init__(self, root: Path, plan: SlidePlan):
        super().__init__(); self.root = root; self.plan = plan; self.signals = WorkerSignals()

    def run(self):
        try:
            folder = self.root / "cache" / "preview"; pptx = folder / "preview.pptx"
            theme_file = self.root / "theme.json"
            PptxRenderer(self.root, load_theme(theme_file if theme_file.is_file() else None)).render(self.plan, pptx, mode="study")
            result = render_preview(pptx, folder)
            self.signals.done.emit("|".join([result.renderer, *map(str, result.images)]))
        except Exception as exc:
            self.signals.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self, project: Path):
        super().__init__(); self.root = project; self.plan: SlidePlan | None = None; self.current = -1; self.preview_images: list[Path] = []
        self.setWindowTitle("Lokal PowerPoint-app"); self.resize(1380, 780)
        self.pool = QThreadPool.globalInstance(); self._build(); self._load()

    def _build(self):
        root = QWidget(); outer = QVBoxLayout(root)
        toolbar = QHBoxLayout()
        for text, callback in (("Tilføj fil", self.add_files), ("Lav slideplan (ingen LLM)", self.make_prompt), ("Importér slideplan", self.import_plan), ("Vælg tema", self.choose_theme), ("Tilføj slide", self.add_slide), ("Slet slide", self.delete_slide), ("Ret slide (JSON)", self.edit_slide_json), ("↑", lambda: self.move(-1)), ("↓", lambda: self.move(1)), ("Gem", self.save), ("Vis eksempel", self.make_preview), ("Eksportér PowerPoint", self.export), ("Annullér", self.cancel_export)):
            button = QPushButton(text); button.clicked.connect(callback); toolbar.addWidget(button)
        outer.addLayout(toolbar)
        teaching_toolbar = QHBoxLayout()
        for label, callback in (("Undervisningsprofil", self.edit_teaching_profile), ("Kontrollér undervisning", self.check_teaching)):
            button = QPushButton(label); button.clicked.connect(callback); teaching_toolbar.addWidget(button)
        self.export_mode = QComboBox()
        for label, mode in [("Automatisk", "auto"), ("Trinvis fremvisning", "steps"), ("Studieversion med svar", "study"), ("Statisk (spørgsmål før svar)", "static")]:
            self.export_mode.addItem(label, mode)
        teaching_toolbar.addWidget(QLabel("Eksportform")); teaching_toolbar.addWidget(self.export_mode)
        teaching_toolbar.addStretch(); outer.addLayout(teaching_toolbar)
        split = QSplitter()
        left = QWidget(); left_l = QVBoxLayout(left); left_l.addWidget(QLabel("Kilder")); self.sources = QListWidget(); left_l.addWidget(self.sources)
        middle = QWidget(); middle_l = QVBoxLayout(middle); middle_l.addWidget(QLabel("Slidernes rækkefølge")); self.slides = QListWidget(); self.slides.currentRowChanged.connect(self.select_slide); middle_l.addWidget(self.slides)
        right = QWidget(); right_l = QVBoxLayout(right); right_l.addWidget(QLabel("Ret slide")); form = QFormLayout()
        self.title = QLineEdit(); self.objective = QLineEdit(); self.seconds = QSpinBox(); self.seconds.setRange(0, 3600); self.notes = QTextEdit(); self.content = QTextEdit()
        form.addRow("Titel", self.title); form.addRow("Mål", self.objective); form.addRow("Sekunder", self.seconds); form.addRow("Indhold (én tekstblok pr. linje)", self.content); form.addRow("Talernoter", self.notes)
        right_l.addLayout(form); self.preview = QLabel("Vælg en slide. 'Vis eksempel' renderer den faktiske PPTX."); self.preview.setWordWrap(True); self.preview.setMinimumHeight(260); self.preview.setStyleSheet("background:#F7F9FC;border:1px solid #B9C8D6;padding:18px;font-size:18px;"); right_l.addWidget(self.preview)
        split.addWidget(left); split.addWidget(middle); split.addWidget(right); split.setSizes([230, 300, 850]); outer.addWidget(split)
        self.status = QLabel("Klar — lokale handlinger kontakter ikke en LLM."); outer.addWidget(self.status); self.setCentralWidget(root)

    def _load(self):
        self.sources.clear()
        for path in sorted((self.root / "sources").glob("*")): self.sources.addItem(path.name)
        plan_path = self.root / "slide-plan.json"
        if plan_path.exists():
            try: self.plan = load_plan(plan_path)
            except ValueError as exc: QMessageBox.critical(self, "Ugyldig plan", str(exc)); return
            self.refresh_slides()

    def refresh_slides(self):
        selected = max(0, min(self.current, len(self.plan.slides)-1)) if self.plan and self.plan.slides else -1
        self.slides.blockSignals(True); self.slides.clear()
        if self.plan:
            for slide in self.plan.slides: self.slides.addItem(slide.title)
            if self.plan.slides: self.slides.setCurrentRow(selected)
        self.slides.blockSignals(False); self.current = -1; self.select_slide(selected)

    def commit(self):
        if not self.plan or self.current < 0 or self.current >= len(self.plan.slides): return
        before = self.plan.slides[self.current].model_dump()
        slide = self.plan.slides[self.current]; slide.title = self.title.text(); slide.objective = self.objective.text(); slide.estimated_seconds = self.seconds.value(); slide.speaker_notes = self.notes.toPlainText()
        # Keep stable IDs, source references, assumptions and element ordering.
        old_text = [e for e in slide.elements if e.type == "text"]
        displayed = "\n".join(e.text for e in old_text)
        if self.content.toPlainText() != displayed:
            lines = [line for line in self.content.toPlainText().splitlines() if line.strip()]
            rebuilt = []; index = 0
            used = {e.id for s in self.plan.slides for e in s.elements}
            for element in slide.elements:
                if element.type != "text":
                    rebuilt.append(element)
                elif index < len(lines):
                    rebuilt.append(element.model_copy(update={"text": lines[index]})); index += 1
            while index < len(lines):
                suffix = 1
                while f"{slide.id}-text-{suffix}" in used: suffix += 1
                eid = f"{slide.id}-text-{suffix}"; used.add(eid)
                rebuilt.append(TextElement(id=eid, type="text", text=lines[index])); index += 1
            slide.elements = rebuilt
            remaining = {e.id for e in rebuilt}
            slide.animations = [a for a in slide.animations if a.target_id in remaining]
        if before != slide.model_dump(): self.preview_images = []

    def edit_teaching_profile(self):
        try: TeachingDialog(self.root, self).exec()
        except ValueError as exc: QMessageBox.warning(self, "Ugyldig undervisningsprofil", str(exc))

    def check_teaching(self):
        if not self.plan: return
        self.commit()
        try:
            plan = SlidePlan.model_validate(self.plan.model_dump())
            findings = inspect_plan(plan, self.root)
            text = "\n".join(f"{f.level}: {f.slide_id}: {f.message}" for f in findings) or "Ingen problemer fundet af de automatiske kontroller."
            QMessageBox.information(self, "Undervisningskontrol", text + "\nKontrollen beviser ikke faglig korrekthed eller læringseffekt.")
        except ValueError as exc: QMessageBox.warning(self, "Ugyldig plan", str(exc))

    def select_slide(self, row):
        if self.current != row: self.commit()
        self.current = row
        if not self.plan or row < 0: return
        s = self.plan.slides[row]; self.title.setText(s.title); self.objective.setText(s.objective); self.seconds.setValue(s.estimated_seconds); self.notes.setPlainText(s.speaker_notes)
        self.content.setPlainText("\n".join(e.text for e in s.elements if e.type == "text"))
        if self.preview_images and row < len(self.preview_images): self._show_preview(row)
        else: self.preview.setText(f"{s.title}\n\n{s.objective}\n\n" + "\n".join(f"• {e.text}" for e in s.elements if e.type == "text") + "\n\nOmtrentlig UI-visning — klik 'Vis eksempel' for faktisk rendering.")

    def add_files(self):
        names, _ = QFileDialog.getOpenFileNames(self, "Tilføj kilder", "", "Dokumenter (*.md *.txt *.docx *.pdf)")
        for name in names:
            try: add_source(self.root, Path(name))
            except Exception as exc: QMessageBox.warning(self, "Importfejl", str(exc))
        self._load()

    def add_slide(self):
        if not self.plan: QMessageBox.information(self, "Mangler plan", "Importér en slide-plan.json først."); return
        self.commit()
        index = len(self.plan.slides)+1
        while f"s{index}" in {s.id for s in self.plan.slides}: index += 1
        self.plan.slides.append(Slide(id=f"s{index}", layout="key_figure", title="Ny slide", elements=[], speaker_notes=""))
        self.current = len(self.plan.slides)-1; self.refresh_slides()

    def delete_slide(self):
        if self.plan and len(self.plan.slides) > 1 and self.current >= 0: self.plan.slides.pop(self.current); self.current = max(0, self.current-1); self.refresh_slides()

    def move(self, delta):
        if not self.plan or self.current < 0: return
        other = self.current + delta
        if 0 <= other < len(self.plan.slides): self.commit(); self.plan.slides[self.current], self.plan.slides[other] = self.plan.slides[other], self.plan.slides[self.current]; self.current = other; self.refresh_slides()

    def save(self):
        if not self.plan: return
        self.commit(); save_plan(self.root, SlidePlan.model_validate(self.plan.model_dump())); self.refresh_slides(); self.status.setText("Gemt lokalt med versionshistorik.")

    def make_prompt(self):
        paths = [p for p in sorted((self.root / "sources").iterdir()) if p.suffix.lower() in {".md", ".markdown", ".txt", ".docx", ".pdf"}]
        if not paths: QMessageBox.warning(self, "Mangler kilder", "Tilføj mindst én kilde først."); return
        topic, ok = QInputDialog.getText(self, "Emne", "Præsentationens emne:")
        if not ok or not topic.strip(): return
        audience, ok = QInputDialog.getText(self, "Målgruppe", "Målgruppe:")
        if not ok or not audience.strip(): return
        documents = [import_document(path, f"src-{i+1}") for i, path in enumerate(paths)]
        prompt = compact_prompt(documents, teaching_brief(self.root, {"topic": topic, "audience": audience, "language": "da", "output": "pptx"}), SlidePlan.model_json_schema())
        target = self.root / "planning-prompt.txt"; target.write_text(prompt, encoding="utf-8")
        QMessageBox.information(self, "Prompt klar", f"Gemt i {target}. Ingen LLM blev kontaktet. Indsæt prompten i en valgfri chat, og importér JSON-svaret bagefter.")

    def import_plan(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Importér slideplan", "", "JSON (*.json)")
        if not filename: return
        try:
            plan = load_plan(Path(filename)); save_plan(self.root, plan); self.plan = plan; self.current = 0; self.refresh_slides()
        except Exception as exc: QMessageBox.critical(self, "Ugyldig slideplan", str(exc))

    def choose_theme(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Vælg tema", "", "Tema (*.json)")
        if not filename: return
        try:
            load_theme(Path(filename)); shutil.copy2(filename, self.root / "theme.json")
            self.preview_images = []; self.status.setText("Tema gemt lokalt. Ingen LLM blev kontaktet.")
        except Exception as exc: QMessageBox.critical(self, "Ugyldigt tema", str(exc))

    def edit_slide_json(self):
        if not self.plan or self.current < 0: return
        self.commit(); dialog = QDialog(self); dialog.setWindowTitle("Ret hele sliden som valideret JSON"); dialog.resize(780, 620)
        layout = QVBoxLayout(dialog); editor = QTextEdit(); editor.setPlainText(json.dumps(self.plan.slides[self.current].model_dump(mode="json"), ensure_ascii=False, indent=2)); layout.addWidget(editor)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel); layout.addWidget(buttons); buttons.rejected.connect(dialog.reject)
        def accept():
            try: self.apply_slide_json(editor.toPlainText()); dialog.accept()
            except Exception as exc: QMessageBox.critical(dialog, "Ugyldig slide", str(exc))
        buttons.accepted.connect(accept); dialog.exec()

    def apply_slide_json(self, payload: str):
        if not self.plan or self.current < 0: raise ValueError("Ingen slide er valgt.")
        candidate = Slide.model_validate_json(payload); slides = list(self.plan.slides); slides[self.current] = candidate
        validated = SlidePlan.model_validate({**self.plan.model_dump(), "slides": [slide.model_dump() for slide in slides]})
        self.plan = validated; self.refresh_slides()

    def export(self):
        if not self.plan: return
        self.commit(); findings = inspect_plan(self.plan, self.root)
        errors = [f.message for f in findings if f.level == "error"]
        if errors: QMessageBox.critical(self, "Eksport stoppet", "\n".join(errors)); return
        target = safe_export_path(self.root, "presentation.pptx"); worker = ExportWorker(self.root, self.plan.model_copy(deep=True), target, self.export_mode.currentData())
        self.worker = worker; worker.signals.done.connect(lambda p: self.status.setText(f"Eksporteret: {p}")); worker.signals.failed.connect(lambda e: self.status.setText(e) if "annulleret" in e.lower() else QMessageBox.critical(self, "Eksportfejl", e)); self.status.setText("Eksporterer i baggrunden…"); self.pool.start(worker)

    def make_preview(self):
        if not self.plan: return
        self.commit(); worker = PreviewWorker(self.root, self.plan.model_copy(deep=True)); self.preview_worker = worker
        worker.signals.done.connect(self._preview_ready); worker.signals.failed.connect(lambda e: QMessageBox.warning(self, "Preview ikke tilgængeligt", e))
        self.status.setText("Renderer faktisk preview i baggrunden…"); self.pool.start(worker)

    def _preview_ready(self, payload: str):
        parts = payload.split("|"); self.preview_images = [Path(value) for value in parts[1:]]
        self.status.setText(f"Faktisk preview via {parts[0]}: fuld løsning. Eksport viser spørgsmål og trin separat."); self._show_preview(max(0, self.current))

    def _show_preview(self, index: int):
        pixmap = QPixmap(str(self.preview_images[index]))
        self.preview.setPixmap(pixmap.scaled(self.preview.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def cancel_export(self):
        worker = getattr(self, "worker", None)
        if worker: worker.cancel(); self.status.setText("Annullerer efter den aktuelle slide…")
