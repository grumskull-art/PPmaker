from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

from powerpoint_app.projects import create_project
from powerpoint_app.ui.window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    selected = QFileDialog.getExistingDirectory(None, "Åbn PowerPoint-projekt")
    if not selected: raise SystemExit(0)
    root = Path(selected)
    if not (root / "project.json").exists():
        answer = QMessageBox.question(None, "Opret projekt", "Mappen er ikke et projekt endnu. Opret et nyt projekt her?")
        if answer != QMessageBox.StandardButton.Yes: raise SystemExit(0)
        create_project(root, root.name)
    window = MainWindow(root); window.show(); raise SystemExit(app.exec())


if __name__ == "__main__": main()
