from __future__ import annotations

from pathlib import Path
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from powerpoint_app.domain.models import (
    ChartElement, FormulaElement, ImageElement, ProcessElement, SlidePlan,
    TableElement, TextElement, WarningElement,
)
from powerpoint_app.rendering.theme import Theme, load_theme
from powerpoint_app.visuals.assets import chart_png, formula_png


def _rgb(value: str) -> RGBColor:
    return RGBColor.from_string(value)


def default_template_path() -> Path | None:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[3]))
    candidate = base / "templates" / "martec_inspired.pptx"
    return candidate if candidate.is_file() else None


class PptxRenderer:
    def __init__(self, project_root: Path, theme: Theme | None = None, template_path: Path | None = None):
        self.root = project_root
        self.theme = theme or load_theme()
        project_template = project_root / "template.pptx"
        self.template_path = template_path or (project_template if project_template.is_file() else default_template_path())
        self.prs = Presentation(str(self.template_path)) if self.template_path else Presentation()
        self.prs.slide_width = Inches(13.333333)
        self.prs.slide_height = Inches(7.5)

    def render(self, plan: SlidePlan, output: Path, cancel_check=None) -> Path:
        problems = plan.check_assets(self.root)
        if problems:
            raise ValueError("; ".join(problems))
        for index, spec in enumerate(plan.slides, 1):
            if cancel_check and cancel_check():
                raise RuntimeError("Eksporten blev annulleret.")
            self._slide(spec, index, len(plan.slides), plan)
        output.parent.mkdir(parents=True, exist_ok=True)
        self.prs.save(output)
        return output

    def _slide(self, spec, number: int, total: int, plan: SlidePlan):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        bg = slide.background.fill
        bg.solid(); bg.fore_color.rgb = _rgb(self.theme.background)
        self._rect(slide, 0, 0, .18, 7.5, self.theme.accent)
        self._text(slide, spec.title, .65, .35, 11.8, .55, 32, self.theme.navy, bold=True)
        self._text(slide, f"{number}/{total}", 11.95, 7.05, .7, .2, 10, "687887", align=PP_ALIGN.RIGHT)
        self._text(slide, plan.deck.audience, .65, 7.05, 6, .2, 10, "687887")
        used_sources = sorted({source for element in spec.elements for source in element.source_ids})
        if used_sources:
            self._text(slide, "Kilder: " + ", ".join(used_sources), 6.9, 7.05, 4.7, .2, 9, "687887", align=PP_ALIGN.RIGHT)
        self._render_layout(slide, spec)
        notes = slide.notes_slide.notes_text_frame
        if notes is not None:
            notes.text = spec.speaker_notes

    def _render_layout(self, slide, spec):
        elements = spec.elements
        if spec.layout == "title":
            self._text(slide, spec.objective or "Undervisningspræsentation", 1.2, 2.5, 10.9, 1.5, 30, self.theme.text, align=PP_ALIGN.CENTER)
            self._rect(slide, 4.3, 4.3, 4.7, .08, self.theme.accent)
        elif spec.layout == "key_figure":
            visual = next((e for e in elements if isinstance(e, (ProcessElement, ImageElement, ChartElement))), None)
            if isinstance(visual, ProcessElement): self._process(slide, visual)
            elif visual is not None: self._element(slide, visual, 1.2, 1.35, 10.9, 3.65)
            self._panel(slide, [e for e in elements if e is not visual], 1.2, 5.05, 10.9, 1.35)
        elif spec.layout == "two_columns" or spec.layout == "comparison":
            self._panel(slide, elements[: max(1, (len(elements)+1)//2)], .65, 1.25, 5.85, 5.45)
            self._panel(slide, elements[max(1, (len(elements)+1)//2):], 6.82, 1.25, 5.85, 5.45)
        elif spec.layout == "process_steps":
            process = next((e for e in elements if isinstance(e, ProcessElement)), None)
            if process:
                self._process(slide, process)
            self._panel(slide, [e for e in elements if e is not process], .8, 5.35, 11.7, 1.25)
        elif spec.layout == "formula_steps":
            formulas = [e for e in elements if isinstance(e, FormulaElement)]
            self._panel(slide, [e for e in elements if not isinstance(e, FormulaElement)], .7, 1.25, 4.3, 5.35)
            self._panel(slide, formulas, 5.25, 1.25, 7.4, 5.35)
        elif spec.layout == "chart_table":
            self._panel(slide, elements, .65, 1.15, 12.0, 5.75)
        elif spec.layout in {"agenda", "summary"}:
            self._panel(slide, elements, 1.25, 1.25, 10.8, 5.45, numbered=True)
        else:
            self._panel(slide, elements, .65, 1.15, 12.0, 5.75)

    def _panel(self, slide, elements, x, y, w, h, numbered=False):
        if not elements:
            return
        gap = .14
        each = max(.7, (h - gap * (len(elements)-1)) / len(elements))
        cursor = y
        for i, element in enumerate(elements):
            self._element(slide, element, x, cursor, w, each, f"{i+1}. " if numbered else "")
            cursor += each + gap

    def _element(self, slide, element, x, y, w, h, prefix=""):
        if isinstance(element, TextElement):
            self._text(slide, prefix + element.text, x, y, w, h, 24, self.theme.text, name=element.id)
        elif isinstance(element, WarningElement):
            self._rect(slide, x, y, w, h, self.theme.warning, radius=True, name=element.id)
            self._text(slide, prefix + element.text, x+.2, y+.12, w-.4, h-.24, 21, self.theme.text, bold=True)
        elif isinstance(element, FormulaElement):
            image = formula_png(element, self.root / "cache", self.theme)
            shape = slide.shapes.add_picture(str(image), Inches(x), Inches(y), width=Inches(w), height=Inches(h))
            shape.name = element.id
            self._set_alt_text(shape, element.latex)
        elif isinstance(element, ImageElement):
            shape = slide.shapes.add_picture(str(self.root / element.asset), Inches(x), Inches(y), width=Inches(w), height=Inches(h))
            shape.name = element.id
            self._set_alt_text(shape, element.alt_text)
        elif isinstance(element, TableElement):
            self._table(slide, element, x, y, w, h)
        elif isinstance(element, ChartElement):
            image = chart_png(element, self.root / "cache", self.theme)
            shape = slide.shapes.add_picture(str(image), Inches(x), Inches(y), width=Inches(w), height=Inches(h))
            shape.name = element.id
        elif isinstance(element, ProcessElement):
            self._process(slide, element)

    def _process(self, slide, element):
        count = len(element.steps); available = 11.8; gap = .18
        width = (available - gap * (count - 1)) / count
        for index, step in enumerate(element.steps):
            x = .75 + index * (width + gap)
            self._rect(slide, x, 2.25, width, 2.0, self.theme.pale, radius=True, name=element.id if index == 0 else None)
            self._text(slide, f"{index+1}\n{step}", x+.12, 2.52, width-.24, 1.45, 20, self.theme.navy, bold=True, align=PP_ALIGN.CENTER)

    def _table(self, slide, element, x, y, w, h):
        rows, cols = len(element.rows)+1, len(element.headers)
        shape = slide.shapes.add_table(rows, cols, Inches(x), Inches(y), Inches(w), Inches(h))
        shape.name = element.id
        table = shape.table
        for c, header in enumerate(element.headers):
            table.cell(0, c).text = header
        for r, row in enumerate(element.rows, 1):
            for c, value in enumerate(row):
                table.cell(r, c).text = value
        for r in range(rows):
            for c in range(cols):
                cell = table.cell(r, c)
                cell.fill.solid(); cell.fill.fore_color.rgb = _rgb(self.theme.navy if r == 0 else "FFFFFF")
                for p in cell.text_frame.paragraphs:
                    p.font.size = Pt(15 if rows > 7 else 18)
                    p.font.color.rgb = _rgb("FFFFFF" if r == 0 else self.theme.text)
                    p.font.bold = r == 0

    def _text(self, slide, value, x, y, w, h, size, color, bold=False, align=PP_ALIGN.LEFT, name=None):
        shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        if name: shape.name = name
        frame = shape.text_frame; frame.clear(); frame.word_wrap = True; frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = frame.paragraphs[0]; p.text = value; p.alignment = align
        p.font.name = self.theme.font; p.font.size = Pt(size); p.font.bold = bold; p.font.color.rgb = _rgb(color)
        return shape

    def _rect(self, slide, x, y, w, h, color, radius=False, name=None):
        kind = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
        shape = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
        shape.fill.solid(); shape.fill.fore_color.rgb = _rgb(color); shape.line.fill.background()
        if name: shape.name = name
        return shape

    @staticmethod
    def _set_alt_text(shape, text):
        props = shape._element.xpath(".//*[local-name()='cNvPr']")
        if props: props[0].set("descr", text)
