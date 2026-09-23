from __future__ import annotations

import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EFFECTS = {"appear": 1, "fade": 10}
TRIGGERS = {"on_click": 1, "with_previous": 2, "after_previous": 3}


def powerpoint_available() -> tuple[bool, str]:
    if platform.system() != "Windows":
        return False, "PowerPoint COM kræver Windows og desktop-PowerPoint."
    try:
        import win32com.client  # noqa: F401
        return True, "Tilgængelig"
    except ImportError:
        return False, "pywin32 er ikke installeret."


def add_animations(static_pptx: Path, output_pptx: Path, plan, timeout_seconds: int = 180) -> Path:
    ok, reason = powerpoint_available()
    if not ok:
        raise RuntimeError(reason)
    shutil.copy2(static_pptx, output_pptx)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as handle:
        handle.write(plan.model_dump_json()); plan_path = Path(handle.name)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "powerpoint_app.office.worker", str(output_pptx.resolve()), str(plan_path)],
            capture_output=True, text=True, timeout=timeout_seconds,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or "Ukendt COM-fejl")
        return output_pptx
    except subprocess.TimeoutExpired as exc:
        if output_pptx.exists(): output_pptx.unlink()
        raise RuntimeError(f"PowerPoint COM overskred timeout på {timeout_seconds} sekunder.") from exc
    except Exception:
        if output_pptx.exists(): output_pptx.unlink()
        raise
    finally:
        plan_path.unlink(missing_ok=True)


def _add_animations_direct(output_pptx: Path, plan) -> None:
    import pythoncom
    import win32com.client

    app = presentation = None
    pythoncom.CoInitialize()
    try:
        app = win32com.client.DispatchEx("PowerPoint.Application")
        app.Visible = False
        presentation = app.Presentations.Open(str(output_pptx.resolve()), WithWindow=False)
        for slide_no, slide_spec in enumerate(plan.slides, 1):
            sequence = presentation.Slides(slide_no).TimeLine.MainSequence
            for animation in sorted(slide_spec.animations, key=lambda x: x.order):
                shape = presentation.Slides(slide_no).Shapes.Item(animation.target_id)
                sequence.AddEffect(shape, EFFECTS[animation.effect], 0, TRIGGERS[animation.trigger])
        presentation.Save()
    finally:
        if presentation is not None:
            presentation.Close()
        if app is not None:
            app.Quit()
        pythoncom.CoUninitialize()
