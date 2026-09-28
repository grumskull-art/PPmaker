from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import math

from powerpoint_app.domain.models import FormulaElement, SlidePlan, TableElement, TextElement, ThreeSourceCircuitElement, WarningElement
from powerpoint_app.quality.calculations import UNITS, verify_calculation
from powerpoint_app.quality.three_source_dc import circuit_quantities


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
        if len(slide.elements) > (12 if slide.layout == "lookup_cards" else 7):
            findings.append(Finding("warning", slide.id, "Mere end syv elementer giver risiko for tekst-overflow."))
        chars = sum(len(e.text) for e in slide.elements if isinstance(e, (TextElement, WarningElement)))
        if chars > (2600 if slide.layout.startswith("lookup_") else 650 if slide.layout in {"two_columns", "comparison"} else 450):
            findings.append(Finding("warning", slide.id, "Tekstmængden giver sandsynlig risiko for overflow; fordel indholdet."))
        for element in slide.elements:
            if isinstance(element, TableElement) and (len(element.rows) > 10 or len(element.headers) > 6):
                findings.append(Finding("warning", slide.id, f"Tabellen {element.id} bør deles."))
            if isinstance(element, FormulaElement) and element.ambiguous:
                findings.append(Finding("review", slide.id, f"Formlen {element.id} er markeret som tvetydig."))
        for check in slide.calculation_checks:
            result = verify_calculation(check)
            if result.status != "passed":
                findings.append(Finding("error" if result.status == "failed" else "review", slide.id, f"{check.element_id}: {result.message}"))
            if check.diagram_id:
                diagram = next(e for e in slide.elements if isinstance(e, ThreeSourceCircuitElement) and e.id == check.diagram_id)
                for name, (value, unit) in circuit_quantities(diagram).items():
                    quantity = check.quantities.get(name)
                    if quantity is None:
                        continue
                    supplied = UNITS.get(quantity.unit)
                    canonical = UNITS[unit]
                    if supplied is None or supplied[1] != canonical[1] or not math.isclose(quantity.value*supplied[0], value*canonical[0], rel_tol=check.relative_tolerance, abs_tol=1e-8):
                        findings.append(Finding("error", slide.id, f"{check.element_id}: {name} stemmer ikke med det redigerbare kredsløb."))
        if slide.teaching and slide.teaching.stage == "worked_example":
            checked = {c.element_id for c in slide.calculation_checks}
            if any(isinstance(e, FormulaElement) and e.id not in checked for e in slide.elements):
                findings.append(Finding("review", slide.id, "Ikke alle formeltrin har numerisk kontrol. Kontrollér selv symbolsk algebra og modelvalg."))
        if plan.teaching_profile and not slide.teaching:
            findings.append(Finding("warning", slide.id, "Undervisningsrollen og koblingen til læringsmål mangler."))
        findings.extend(Finding("review", slide.id, w) for w in slide.warnings)
    if plan.teaching_profile:
        covered = {i for s in plan.slides if s.teaching for i in s.teaching.objective_indices}
        for i, objective in enumerate(plan.teaching_profile.learning_objectives):
            if i not in covered:
                findings.append(Finding("warning", "-", "Læringsmål uden slide: " + objective))
        if not any(s.teaching and s.teaching.question for s in plan.slides):
            findings.append(Finding("warning", "-", "Ingen spørgsmål med svar og feedback i undervisningsplanen."))
        if plan.teaching_profile.practical_context and not any(s.teaching and s.teaching.stage == "operational_decision" and s.teaching.question for s in plan.slides):
            findings.append(Finding("review", "-", "Praktisk kontekst uden spørgsmål om et driftsvalg. Knyt beregningen til de nødvendige data og en beslutning."))
        if plan.teaching_profile.practical_context and not any(s.teaching and s.teaching.stage == "model" and s.teaching.assumptions for s in plan.slides):
            findings.append(Finding("review", "-", "Praktisk kontekst uden tydelige modelantagelser. Vurder modellens gyldighed før anvendelse."))
        seconds = sum(s.estimated_seconds for s in plan.slides)
        if abs(seconds - plan.deck.duration_minutes*60) > plan.deck.duration_minutes*60*.2:
            findings.append(Finding("warning", "-", "Slidernes samlede tid afviger mere end 20 % fra deckets varighed. Medregn øvelsestid."))
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
