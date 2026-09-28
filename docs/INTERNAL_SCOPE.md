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

The second pilot adds one more bounded native component diagram: the exact
three-source/five-resistor topology of the user-supplied MARTEC F2023 re-exam
exercise 3. Source values and resistances are editable in JSON; the solver
independently computes two node potentials, five oriented currents and the
resistor/source power balance. Calculation checks can bind their quantities to
that diagram and block export after inconsistent edits. This is not support
for arbitrary source positions or circuit topologies. The original task image
is an input, while `examples/bm4_exam_2023/sources/exercise.md` is a concise
source description. The nine-slide didactic example is reproducibly generated
by `examples/bm4_exam_2023/build_example.py`.

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

## User-supplied didactics report (2026-09-23)

The supplied `Didaktik på Maskinmesteruddannelsen.md` is an input for design decisions,
not a validated source of technical facts or a proof that the app improves outcomes.
Its practical-to-abstract-to-practical loop is now reflected by optional `model` and
`operational_decision` stages, assumptions, planner instructions, and a review finding
when a practical-context lesson omits these steps. The pilot ends with an explicit
question about the data needed before connecting another load; it does not invent a
supply current limit. Concept questions now accept 3-5 options, a correct index and
discussion guidance; audience-facing answers still require a separate reveal frame.

The report's assertion/evidence headings are a suggestion for explanatory slides,
not a universal format. Likewise, no fixed 30/70 polling rule is coded: vote results
need instructor judgment. Source 1 in the report is a DTU study regulation, not a
maskinmester curriculum; some other cited links are slide-sharing or secondary summaries.
Check any subject-specific physics claim against primary course material before use.
Peer Instruction background: Crouch & Mazur (2001),
https://mazur.harvard.edu/publications/peer-instruction-ten-years-experience-and-results
and Mazur's original ConcepTest sequence:
https://mazur.harvard.edu/presentations/peer-instruction-getting-students-think-class-0

## MARTEC BM4 curriculum provided by the user

Source: user-provided `Studieordningen.pdf`, MARTEC document Q-0231, version 9;
the page headers say valid from 11 August 2026. The cover and section 23 retain
the earlier 27 January 2025 start date; the header and revision log distinguish
this supplied version from the original effective date. The source PDF is not
copied into this repository. The concise project source
`examples/teaching_dc/sources/martec_bm4_scope.md` records page citations,
verified course structure, and limits for the offline planning prompt.

Section 22.2 (PDF p. 14) lists six 5-ECTS BM4 modules: EL-TEK1, EL-TEK2,
TM1.1, TM1.2, TFE, and the thermal/interdisciplinary project. EL1 and TM1
are internally assessed oral exams with a lottery; P_BM4 is an internal
project exam. Appendix 1 (PDF pp. 22-23) states broad cross-semester area
purposes, not detailed BM4 topic-by-topic learning objectives. The pilot's
nodal/parallel-DC objectives remain illustrative and cannot be represented as
official EL-TEK1 or EL-TEK2 outcomes from this document alone. The next
curriculum gate is the actual BM4 module descriptions (MOB) and assignments.

An autumn-2026 EL-TEK1 course plan has since been supplied. Its `Tema/Emne`
rows place Ohm's law, DC circuits and Kirchhoff's laws in EL-TEK1, so the DC
pilot has topic-level alignment there. It remains an illustrative exercise,
not a copy of a module assignment. TM1.1 and TM1.2 course plans, the BM4
project brief and the RKJ problem-formulation worksheet have also been read.
See `docs/MARTEC_BM4_ALIGNMENT.md` for scope, distinct presentation timings,
physical-book limits and reusable topic summaries in `examples/bm4_source_guides/`.
The EL-TEK2 plan, assigned exam prompts and referenced AI procedures are not
available; do not infer their content.
