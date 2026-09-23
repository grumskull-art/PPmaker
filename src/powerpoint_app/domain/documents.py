from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class Block:
    kind: str
    text: str = ""
    locator: str = ""
    rows: list[list[str]] = field(default_factory=list)
    warning: str = ""


@dataclass
class Document:
    source_id: str
    file: str
    title: str
    blocks: list[Block]
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
