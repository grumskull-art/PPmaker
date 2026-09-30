---
name: pptx-didactic
description: Create or review a didactic PowerPoint deck when slide flow, technical clarity, or click-by-click reveals matter.
---

# Didactic PowerPoint decks

Use this workflow for lessons, technical briefings, and slide plans. Aim for one teachable point per slide, brief text, a clear visual hierarchy, and figures that explain relationships rather than decorate.

## Workflow

1. Identify the audience, learning outcome, time available, and source material. Separate sourced facts from assumptions.
2. Build a clear sequence: prior knowledge, explanation, worked example, learner action, and recap where appropriate. Keep answers in notes when they should not appear before a reveal.
3. Prefer editable PowerPoint shapes, tables, and text for diagrams and formulas. Check contrast, alignment, line breaks, units, and slide density.
4. For PPmaker, validate the slide plan and export with its documented CLI. Render every slide and inspect the rendered deck; a text outline or static image cannot verify slideshow behavior.
5. Native click animations need a PowerPoint slideshow test on Windows. PPmaker currently documents that native COM animations are not integrated; do not claim they work based on static rendering. If the requested reveal cannot be authored or tested with available tools, describe that limitation and deliver the supported static deck.

## Validate

Run the repository's documented validation and export commands. Inspect all rendered slides and speaker notes. For requested animations, open the exported file in PowerPoint and advance each reveal in slideshow mode; otherwise mark animation behavior unverified.
