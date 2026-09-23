from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Theme:
    id: str
    background: str
    navy: str
    accent: str
    pale: str
    warning: str
    text: str
    font: str


DEFAULT_THEME = Theme(
    id="martec_inspired", background="F7F9FC", navy="17324D", accent="159EAF",
    pale="DCEEF2", warning="F2A93B", text="17212B", font="Aptos",
)


def load_theme(path: Path | None = None) -> Theme:
    if path is None:
        return DEFAULT_THEME
    return Theme(**json.loads(path.read_text(encoding="utf-8")))
