from pathlib import Path

import pytest

from powerpoint_app.rendering.preview import render_preview


def test_preview_reports_missing_renderer(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("powerpoint_app.rendering.preview.platform.system", lambda: "Linux")
    monkeypatch.setattr("powerpoint_app.rendering.preview.shutil.which", lambda name: None)
    with pytest.raises(RuntimeError, match="PowerPoint.*LibreOffice"):
        render_preview(tmp_path / "deck.pptx", tmp_path / "preview")
