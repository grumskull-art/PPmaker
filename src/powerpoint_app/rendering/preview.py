from __future__ import annotations

import platform
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PreviewResult:
    renderer: str
    images: list[Path]


def render_preview(pptx: Path, output_dir: Path, timeout_seconds: int = 120) -> PreviewResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    for old in list(output_dir.glob("*.png")) + list(output_dir.glob("*.PNG")) + list(output_dir.glob("*.pdf")):
        old.unlink()
    if platform.system() == "Windows":
        if getattr(sys, "frozen", False):
            helper = Path(sys.executable).with_name("PowerPointPreview.exe")
            if not helper.is_file(): raise RuntimeError("PowerPointPreview.exe mangler ved siden af appen.")
            command = [str(helper), str(pptx.resolve()), str(output_dir.resolve())]
        else:
            command = [sys.executable, "-m", "powerpoint_app.office.preview_worker", str(pptx.resolve()), str(output_dir.resolve())]
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds)
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or "PowerPoint kunne ikke generere preview.")
        images = _images(output_dir)
        if not images: raise RuntimeError("PowerPoint genererede ingen previewbilleder.")
        return PreviewResult("PowerPoint", images)
    libreoffice, pdftoppm = shutil.which("libreoffice"), shutil.which("pdftoppm")
    if not libreoffice or not pdftoppm:
        raise RuntimeError("Faktisk preview kræver PowerPoint på Windows eller LibreOffice og pdftoppm.")
    with tempfile.TemporaryDirectory(prefix="ppmaker-lo-") as profile:
        result = subprocess.run(
            [libreoffice, f"-env:UserInstallation=file://{profile}", "--headless", "--convert-to", "pdf:impress_pdf_Export", "--outdir", str(output_dir), str(pptx.resolve())],
            capture_output=True, text=True, timeout=timeout_seconds,
        )
    pdf = output_dir / f"{pptx.stem}.pdf"
    if result.returncode or not pdf.is_file():
        details = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"LibreOffice kunne ikke rendere preview: {details or 'ingen PDF blev oprettet'}")
    subprocess.run([pdftoppm, "-png", "-r", "110", str(pdf), str(output_dir / "slide")], check=True, capture_output=True, timeout=timeout_seconds)
    images = _images(output_dir)
    if not images: raise RuntimeError("Preview-rendereren genererede ingen billeder.")
    return PreviewResult("LibreOffice", images)


def _images(folder: Path) -> list[Path]:
    images = list(folder.glob("*.png")) + list(folder.glob("*.PNG"))
    return sorted(set(images), key=lambda p: (len(p.name), p.name.lower()))
