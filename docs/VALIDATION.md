# Validation of the teaching workflow

2026-09-23, Linux, Python 3.12.

The first pilot had **40 tests passed**, including desktop tests, using the declared
pinned direct dependencies: python-pptx 1.0.2, Pydantic 2.11.9, Matplotlib 3.10.6,
Pillow 12.0.0, python-docx 1.2.0, pypdf 6.1.1, pytest 8.4.2 and PySide6 6.11.2.
The existing Matplotlib/pyparsing combination emits deprecation warnings; no test failed.
The local prompt command and study-export command also completed successfully.

- Source snapshot: 20/20 existing non-UI tests passed before changes.
- Existing UI test also passes after installing its declared PySide6 dependency.
- New coverage: numerical and dimensional failures; unsupported expressions; schema and
  branch references; profile persistence; provider profile enforcement; cache invalidation;
  offline prompt/export; hidden answers; stable reveal geometry; formula image proportions;
  circuit highlighting; UI metadata preservation.
- The Danish pilot exports 7 logical slides as 13 staged slides, or 7 study slides.
- PPTX geometry checks find no shapes outside the pilot slide boundaries.
- Imported the generated PPTX into the artifact-tool renderer and inspected all 13 slides.
  This was the earlier pilot before the additional decision question; the current
  14-slide example has geometry and answer-separation tests but has not had the
  same artifact-tool visual pass.
  Corrected circuit labels that initially overlapped wires. Re-rendered the pilot and
  checked the revised labels and branch highlighting.
- PowerPoint itself, native COM animations, PyInstaller and Windows installation were
  not tested. LibreOffice was unavailable in this environment. Artifact-tool rendering
  is an independent visual check, not proof of PowerPoint playback.
- No actual LLM provider was called. Provider behavior is tested with deterministic fakes.
  Real model adherence and generated content quality need a separate user-configured trial.

## Second pilot: original MARTEC F2023 exercise 3

The user-provided exam image fixes R5 at **8 Ω** and the source polarities E1
positive at L, E2 positive at B and E3 positive at D. With C = 0 V, solving
the two node equations gives VA = 12.23228995 V, VD = 21.36738056 V,
U_AB = -17.76771005 V. In the directions specified in `sources/exercise.md`,
I1..I5 = 1.51070840, 0.45304778, 1.05766063, 2.13673806,
1.07907743 A. The five resistor powers sum to 134.34925865 W;
E1·I1 + E2·I5 + E3·I3 gives the same value.

All **44 tests passed** on Linux after the second pilot. The deterministic
example exports 9 logical slides as 29 staged slides. Its
numeric checks pass; `validate` returns two review notices for symbolic KCL
steps on slides s3 and s4, which require a person to verify the algebra and
selected physical model. Test coverage now includes the exact currents,
voltage and power balance, a changed R5, binding of edited circuit values to
checks, fixed topology references, hidden answers and export geometry. The
generated file opened in LibreOffice and was rendered for visual inspection.
PowerPoint on Windows and teaching impact in a classroom remain untested.

The automated checker validates only the supplied numerical expression and its units.
It does not verify the displayed LaTeX or the choice of physical principle, and it does
not establish that students learn better. See INTERNAL_SCOPE.md for remaining work.
