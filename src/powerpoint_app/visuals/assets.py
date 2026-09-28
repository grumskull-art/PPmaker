from __future__ import annotations

import hashlib
import re
from typing import TYPE_CHECKING
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from powerpoint_app.domain.models import ChartElement, FormulaElement
if TYPE_CHECKING:
    from powerpoint_app.rendering.theme import Theme


MATH_STYLE = "stix-upright-current-display-v2"


def math_latex(source: str) -> str:
    """Keep source/search Latin I; enforce upright serif I only when drawing."""
    source = source.replace(r'\mathrm{I}', 'I')
    source = source.replace(r'\frac', r'\dfrac')
    tokens = re.findall(r"\\[A-Za-z]+|\\.|.", source, re.S)
    return ''.join(r'\mathrm{I}' if token == 'I' else token for token in tokens)


def formula_png(element: FormulaElement, cache: Path, theme: Theme) -> Path:
    latex = math_latex(element.latex)
    key = hashlib.sha256((MATH_STYLE + latex + theme.navy).encode()).hexdigest()[:16]
    target = cache / f"formula-{key}.png"
    if not target.exists():
        cache.mkdir(parents=True, exist_ok=True)
        with matplotlib.rc_context({'mathtext.fontset': 'stix', 'font.family': 'STIXGeneral'}):
            fig = plt.figure(figsize=(9, 1.5), facecolor="none")
            try:
                fig.text(.5, .5, f"${latex}$", ha="center", va="center", fontsize=25, color=f"#{theme.navy}")
                fig.savefig(target, dpi=220, transparent=True, bbox_inches="tight", pad_inches=.035)
            except ValueError as exc:
                target.unlink(missing_ok=True)
                raise ValueError(f'Ugyldig matematik i {element.id}: {element.latex}') from exc
            finally:
                plt.close(fig)
    return target


def chart_png(element: ChartElement, cache: Path, theme: Theme) -> Path:
    payload = element.model_dump_json() + theme.accent
    target = cache / f"chart-{hashlib.sha256(payload.encode()).hexdigest()[:16]}.png"
    if target.exists():
        return target
    cache.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4.2), layout="constrained")
    xs = list(range(len(element.categories)))
    for index, (name, values) in enumerate(element.series.items()):
        if element.chart_type == "bar":
            width = .8 / max(1, len(element.series))
            ax.bar([x + index * width for x in xs], values, width=width, label=name)
        else:
            ax.plot(xs, values, marker="o", linewidth=2.5, label=name)
    ax.set_xticks(xs, element.categories)
    ax.set_title(element.title)
    ax.set_xlabel(element.x_label)
    ax.set_ylabel(element.y_label)
    ax.grid(axis="y", alpha=.25)
    if len(element.series) > 1:
        ax.legend()
    fig.savefig(target, dpi=180, transparent=False)
    plt.close(fig)
    return target
