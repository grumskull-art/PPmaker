from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SourceRef(StrictModel):
    id: str = Field(min_length=1)
    file: str = Field(min_length=1)
    locator: str = ""


class TextElement(StrictModel):
    id: str
    type: Literal["text"]
    text: str
    source_ids: list[str] = Field(default_factory=list)
    assumption: bool = False


class FormulaElement(StrictModel):
    id: str
    type: Literal["formula"]
    latex: str
    source_ids: list[str] = Field(default_factory=list)
    ambiguous: bool = False


class ImageElement(StrictModel):
    id: str
    type: Literal["image"]
    asset: str
    alt_text: str
    caption: str = ""
    source_ids: list[str] = Field(default_factory=list)


class TableElement(StrictModel):
    id: str
    type: Literal["table"]
    headers: list[str]
    rows: list[list[str]]
    source_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def rectangular(self):
        if not self.headers or any(len(row) != len(self.headers) for row in self.rows):
            raise ValueError("tabellen skal have overskrifter og ens kolonneantal")
        return self


class ChartElement(StrictModel):
    id: str
    type: Literal["chart"]
    chart_type: Literal["line", "bar"] = "line"
    title: str = ""
    x_label: str = ""
    y_label: str = ""
    categories: list[str]
    series: dict[str, list[float]]
    source_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def equal_lengths(self):
        if any(len(v) != len(self.categories) for v in self.series.values()):
            raise ValueError("alle diagramserier skal matche antal kategorier")
        return self


class ProcessElement(StrictModel):
    id: str
    type: Literal["process"]
    steps: list[str] = Field(min_length=2, max_length=7)
    source_ids: list[str] = Field(default_factory=list)


class WarningElement(StrictModel):
    id: str
    type: Literal["warning"]
    text: str
    severity: Literal["info", "warning", "critical"] = "warning"
    source_ids: list[str] = Field(default_factory=list)


Element = Annotated[
    Union[TextElement, FormulaElement, ImageElement, TableElement, ChartElement, ProcessElement, WarningElement],
    Field(discriminator="type"),
]


class Animation(StrictModel):
    target_id: str
    effect: Literal["appear", "fade"] = "appear"
    trigger: Literal["on_click", "after_previous", "with_previous"] = "on_click"
    order: int = Field(ge=1)


LayoutName = Literal[
    "title", "agenda", "key_figure", "two_columns", "comparison",
    "process_steps", "formula_steps", "chart_table", "summary",
]


class Slide(StrictModel):
    id: str
    layout: LayoutName
    title: str
    objective: str = ""
    elements: list[Element] = Field(default_factory=list)
    speaker_notes: str = ""
    estimated_seconds: int = Field(default=60, ge=0, le=3600)
    animations: list[Animation] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class Deck(StrictModel):
    title: str
    language: Literal["da"] = "da"
    audience: str
    duration_minutes: int = Field(ge=1, le=600)
    theme_id: str = "martec_inspired"


class SlidePlan(StrictModel):
    schema_version: Literal["1.0"]
    deck: Deck
    sources: list[SourceRef] = Field(default_factory=list)
    slides: list[Slide] = Field(min_length=1)

    @model_validator(mode="after")
    def references_are_valid(self):
        source_ids = [x.id for x in self.sources]
        slide_ids = [x.id for x in self.slides]
        element_ids = [e.id for slide in self.slides for e in slide.elements]
        for label, values in (("kilde", source_ids), ("slide", slide_ids), ("element", element_ids)):
            dupes = sorted({x for x in values if values.count(x) > 1})
            if dupes:
                raise ValueError(f"dubleret {label}-id: {', '.join(dupes)}")
        sources = set(source_ids)
        elements = set(element_ids)
        for slide in self.slides:
            for element in slide.elements:
                unknown = set(element.source_ids) - sources
                if unknown:
                    raise ValueError(f"ukendte kilde-id'er i {element.id}: {sorted(unknown)}")
                if isinstance(element, ImageElement):
                    p = PurePosixPath(element.asset)
                    if p.is_absolute() or ".." in p.parts:
                        raise ValueError(f"asset skal være en sikker relativ sti: {element.asset}")
            for animation in slide.animations:
                if animation.target_id not in elements:
                    raise ValueError(f"animation peger på ukendt element: {animation.target_id}")
        return self

    def check_assets(self, project_root: Path) -> list[str]:
        problems: list[str] = []
        root = project_root.resolve()
        for slide in self.slides:
            for element in slide.elements:
                if isinstance(element, ImageElement):
                    candidate = (root / element.asset).resolve()
                    if root not in candidate.parents or not candidate.is_file():
                        problems.append(f"Manglende eller usikker asset: {element.asset}")
        return problems
