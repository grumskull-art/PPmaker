from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from powerpoint_app.domain.models import SlidePlan
from powerpoint_app.importers import import_document

PROJECT_DIRS = ("sources", "assets", "cache", "exports", "history")


def atomic_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def create_project(root: Path, title: str = "Nyt projekt") -> Path:
    root.mkdir(parents=True, exist_ok=True)
    for name in PROJECT_DIRS:
        (root / name).mkdir(exist_ok=True)
    metadata = {"format_version": "1.0", "title": title, "created_at": datetime.now(timezone.utc).isoformat()}
    atomic_json(root / "project.json", metadata)
    return root


def assert_project(root: Path) -> None:
    if not (root / "project.json").is_file():
        raise ValueError(f"Ikke en projektmappe: {root}")
    for name in PROJECT_DIRS:
        (root / name).mkdir(exist_ok=True)


def save_plan(root: Path, plan: SlidePlan) -> Path:
    assert_project(root)
    target = root / "slide-plan.json"
    if target.exists():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        shutil.copy2(target, root / "history" / f"slide-plan-{stamp}.json")
    atomic_json(target, plan.model_dump(mode="json"))
    return target


def load_plan(path: Path) -> SlidePlan:
    try:
        return SlidePlan.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"Ugyldig slideplan i {path}: {exc}") from exc


def add_source(root: Path, source: Path) -> dict:
    assert_project(root)
    if not source.is_file():
        raise FileNotFoundError(source)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()[:12]
    target = root / "sources" / f"{digest}-{source.name}"
    if not target.exists():
        shutil.copy2(source, target)
    doc = import_document(target, f"src-{digest}")
    normalized = root / "cache" / f"document-{digest}.json"
    atomic_json(normalized, doc.to_dict())
    return {"document": doc, "stored_path": target, "normalized_path": normalized}


def safe_export_path(root: Path, filename: str, overwrite: bool = False) -> Path:
    assert_project(root)
    clean = Path(filename).name
    if not clean.lower().endswith(".pptx"):
        clean += ".pptx"
    target = root / "exports" / clean
    if target.exists() and not overwrite:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        target = target.with_name(f"{target.stem}-{stamp}{target.suffix}")
    return target
