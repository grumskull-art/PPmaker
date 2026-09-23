from __future__ import annotations

import hashlib
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from powerpoint_app.domain.models import ChartElement, FormulaElement
from powerpoint_app.rendering.theme import Theme


def formula_png(element: FormulaElement, cache: Path, theme: Theme) -> Path:
    key = hashlib.sha256((element.latex + theme.text).encode()).hexdigest()[:16]
    target = cache / f"formula-{key}.png"
    if not target.exists():
        cache.mkdir(parents=True, exist_ok=True)
        fig = plt.figure(figsize=(9, 1.5), facecolor="none")
        try:
            fig.text(.5, .5, f"${element.latex}$", ha="center", va="center", fontsize=25, color=f"#{theme.navy}")
            fig.savefig(target, dpi=220, transparent=True, bbox_inches="tight", pad_inches=.15)
        except ValueError:
            fig.clear()
            fig.text(.5, .5, element.latex, ha="center", va="center", fontsize=22, color=f"#{theme.navy}")
            fig.savefig(target, dpi=220, transparent=True, bbox_inches="tight", pad_inches=.15)
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
