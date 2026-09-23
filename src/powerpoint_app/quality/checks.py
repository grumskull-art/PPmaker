from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from powerpoint_app.domain.models import FormulaElement, SlidePlan, TableElement, TextElement, WarningElement


@dataclass
class Finding:
    level: str
    slide_id: str
    message: str


def inspect_plan(plan: SlidePlan, project_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for message in plan.check_assets(project_root):
        findings.append(Finding("error", "-", message))
    for slide in plan.slides:
        if len(slide.title) > 75:
            findings.append(Finding("warning", slide.id, "Lang titel kan blive svær at læse."))
        if not slide.speaker_notes.strip():
            findings.append(Finding("warning", slide.id, "Talernoter mangler."))
        if len(slide.elements) > 7:
            findings.append(Finding("warning", slide.id, "Mere end syv elementer giver risiko for tekst-overflow."))
        chars = sum(len(e.text) for e in slide.elements if isinstance(e, (TextElement, WarningElement)))
        if chars > (650 if slide.layout in {"two_columns", "comparison"} else 450):
            findings.append(Finding("warning", slide.id, "Tekstmængden giver sandsynlig risiko for overflow; fordel indholdet."))
        for element in slide.elements:
            if isinstance(element, TableElement) and (len(element.rows) > 10 or len(element.headers) > 6):
                findings.append(Finding("warning", slide.id, f"Tabellen {element.id} bør deles."))
            if isinstance(element, FormulaElement) and element.ambiguous:
                findings.append(Finding("review", slide.id, f"Formlen {element.id} er markeret som tvetydig."))
        findings.extend(Finding("review", slide.id, w) for w in slide.warnings)
    return findings


def findings_json(findings: list[Finding]) -> list[dict]:
    return [asdict(x) for x in findings]


def inspect_pptx_geometry(path: Path) -> list[Finding]:
    from pptx import Presentation

    prs = Presentation(path); findings: list[Finding] = []
    for number, slide in enumerate(prs.slides, 1):
        for shape in slide.shapes:
            if shape.left < 0 or shape.top < 0 or shape.left + shape.width > prs.slide_width or shape.top + shape.height > prs.slide_height:
                findings.append(Finding("error", str(number), f"Shape uden for sliden: {shape.name}"))
    return findings
