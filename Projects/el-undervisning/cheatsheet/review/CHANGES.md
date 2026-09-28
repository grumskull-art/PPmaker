# Filer og afgrænsede ændringer

Én fil pr. linje i `FILES.txt`; originaler og tidligere revisioner er bevaret.
Listen omfatter nye projektfiler, eksporter og kontrolartefakter samt ændret appkode.
Eksisterende kildefiler indgår ikke som ændrede filer.

## Ændringsankre

- `src/powerpoint_app/domain/models.py`: ved `CircuitElement.branch_sources`,
  `LayoutName`, `Slide.valid_lookup_layout`, `Deck.page_format` og
  `SlidePlan.references_are_valid`: begrænset A4-opslagsformat og typede grenkilder.
- `src/powerpoint_app/rendering/pptx_renderer.py`: ved `render` og `_slide`:
  A4-sidestørrelse og delegation til opslagsrendereren.
- `src/powerpoint_app/rendering/reference.py`: nye funktioner `reference_page`,
  `reference_table` og `nodal_page`: kompakte opslag, ens indeksrækker og native DC-figur.
- `src/powerpoint_app/quality/checks.py`: ved layoutets element-/tekstgrænser:
  tillad op til fire kompakte opslag pr. A4-side.
- `src/powerpoint_app/visuals/assets.py`: ved `formula_png`'s cache-nøgle:
  anvend den faktisk renderede formelfarve, så farveskift giver nye aktiver.
- `tests/test_reference.py`: fem tests for A4, redigerbarhed, kilde-LaTeX,
  gyldige opslag, grengrænsen og farveafhængig cache.
- `README.md`: indsæt dokumentation under `### A4-opslagsværk`.
- Projektets `formula-database.json`: opslag, betingelser, mellemtrin, værdier,
  eksempler og konkrete kildeslides. `regenerate.py`: `build` og `append_registers`
  opbygger den validerede plan og kalder appens eksport.
- `export_windows.ps1`: native PowerPoint-rendering af hver side, tekstmåling og PDF.
- `verify.py`: genberegning, kildehashes, indeks, PDF-format og placeringer.

## Kort verifikation

Kør fra PPmaker-mappen:

```bash
.venv/bin/python Projects/el-undervisning/cheatsheet/verify.py
.venv/bin/powerpoint-app validate Projects/el-undervisning/cheatsheet/slide-plan.json --project Projects/el-undervisning/cheatsheet
.venv/bin/python -m pytest -q --disable-warnings
```

Resultat: 45 A4-sider, 82 opslag, 33 genberegnede eksempler og 46 beståede tests.
160 kildeslides og alle 45 eksportsider er visuelt gennemgået.
PDF og PNG'er er eksporteret med Windows PowerPoint 16.0.
Formler er billeder med redigerbar LaTeX-kilde; der er ikke native Office Math.
AC/RLC/fasorer/trefase har ikke tilstrækkeligt lokalt kildemateriale og er afgrænset.
