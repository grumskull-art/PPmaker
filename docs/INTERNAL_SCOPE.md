# Internal scope: teaching workflow

Base: grumskull-art/PPmaker commit a9d6ba0c63f69b2c3d041abe3bc667afc7ce890f.
Reviewed 2026-09-23. This is an implementation scope, not a claim of measured learning gains.

## Existing foundation

The repository has a Python/Pydantic slide contract, Markdown/DOCX/PDF text import,
project persistence, JSON prompts, optional providers, caching, PySide6 editing,
python-pptx rendering, image formulas/charts, PowerPoint COM and 21 existing tests
(including one desktop test). The initial 20 non-UI tests passed on the source snapshot.
No AGENTS.md is present in the retrieved tree.

Concrete gaps found: no pedagogical profile or activity contract; answers are ordinary
text; only static or Windows COM export; images stretch to fill boxes; text editing
recreates IDs and loses provenance; animation targets can point to another slide.

## First delivery and acceptance

1. Backward-compatible schema 1.1 with an explicit teaching profile, objective mappings,
   lesson stages, questions/feedback and independently evaluated calculation checks.
2. Persist profile in the project; expose a form in the UI and a CLI command. Include
   profile and versioned research rules in prompts and cache keys. No paid calls in tests.
3. Export questions before answers, and explicit click-step slides with stable geometry.
   Keep legacy static/COM behavior for ordinary 1.0 plans. Study export shows full answers.
4. Add one bounded native editable diagram: ideal DC supply with 2-4 parallel resistors.
   Link a formula to a validated branch and highlight it as the calculation is revealed.
   This is not a general circuit solver. Preserve picture aspect ratios.
5. Check bounded numerical expressions and supported SI dimensions without eval/exec.
   Unsupported operations require review. The checker does not prove algebra, correctness
   of the selected physical model, source truth, or agreement with prose/LaTeX.
6. Fix editor metadata loss and same-slide animation references. Test the full pilot:
   source/profile -> local prompt -> saved example plan -> checks -> question/step PPTX.
7. Add Danish instructions, research provenance, example project and tests. Review output
   with an actual slide renderer if available. Windows/Office remains a separate gate.

Acceptance: old sample still exports; old tests pass; new questions hide answers on the
first frame; reveal positions do not jump; bad dimensions fail; unsupported expressions
are never labelled verified; source IDs survive UI editing; exports make no provider calls.

## Subsequent scope (not represented as completed)

- General component-linked circuits, vector diagrams, boiler and thermodynamic templates.
- Symbolic algebra checking, thermodynamic properties, richer compound/temperature units.
- Better OCR, mathematical equation and image extraction from teaching documents.
- Per-slide provider revision and reliable source-ID unification across all import paths.
- Layout-aware overflow pagination and full rendered overlap/readability review tooling.
- Dedicated assessment export, delayed practice bank and classroom outcome measurement.
- Native teaching animations in Windows COM, installation/build tests on Windows.

Use the pilot architecture for these additions. Do not claim general support from the
single resistive DC example, or turn a research rule into a universal prescription.

## Research register

These sources were opened in the preceding research turn. Rules are curated offline;
the application does not automatically search the web or imply it has the latest paper.
- Cromley & Chen (2025): https://doi.org/10.1016/j.edurev.2025.100730
  Multimedia meta-analysis; useful support for text/diagrams and qualified animation use.
  Corpus scope is Mayer-authored studies, not all engineering teaching.
- Barbieri et al. (2023): https://doi.org/10.1007/s10648-023-09745-1
  Mathematics worked-example meta-analysis. Self-explanation prompts are not uniformly beneficial.
- Cao & Carvalho (2026): https://doi.org/10.1007/s10648-026-10169-w
  Experimental evidence that instruction and example variability affect generalization.
  Not a direct evaluation of marine-engineering slide lessons.
- Gjerde et al. (2022): https://doi.org/10.1103/PhysRevPhysEducRes.18.010136
  Physics model/principle/conditions prompts. Small studies; not a blanket mandate.

No effect size is a promised improvement for this application. A classroom pilot must
assess independent transfer and delayed retention, not just preference for slides.
