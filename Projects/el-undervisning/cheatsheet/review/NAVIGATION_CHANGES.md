# Navigation i EL-opslagsværket

Originalen `EL-cheatsheet-BM4.pptx` og dens PDF er bevaret. Ny leverance er
`EL-cheatsheet-BM4-navigation.pptx`, dens PDF og det lokale `EL-cheatsheet-BM4-opslag.html`.
De 82 opslag og 33 eksempler har uændret fagligt indhold; de ekstra metadata beskriver
søgt størrelse, givne oplysninger og fysisk situation. Afgrænsningen for AC er bevaret.

## Ændringsankre

- `src/powerpoint_app/domain/models.py`: `NavigationLink`, `Slide.navigation`, `SlidePlan`-validering.
- `src/powerpoint_app/rendering/pptx_renderer.py`: `resolve_links` efter alle slides er renderet.
- `src/powerpoint_app/rendering/reference.py`: `lookup_start`, native navigation og ensartet indeksrækkehøjde.
- `src/powerpoint_app/rendering/navigation.py`: `navigation_shapes`, `resolve_links`; native interne slidejump-links. Startgenveje er native rektangler, så hele det lyse felt reagerer på klik.
- `src/powerpoint_app/planning/lookup.py`: `index_sections`, `bind_lookup_navigation`; mål og sidetal fra samme plan.
- `src/powerpoint_app/rendering/lookup_html.py`: `export_lookup_html`; én indlejret database, formler og offline filtre.
- `src/powerpoint_app/quality/navigation.py`: `audit_navigation`; hver linkrelation, indekskode og PDF-destination.
- `tests/test_navigation.py`: ekstra forside, omordning, ny formelkode og afvisning af ugyldige mål.
- Projektets `formula-database.json`: `navigation_groups`, `quantities`, `situations`, `entries[].lookup`.
- Projektets `regenerate.py`: start, emneindeks, kortgrupper, HTML og automatisk navigationstest.
- Projektets `export_windows.ps1`: nyt leverancefilnavn; native PDF og rendering.
- Projektets `verify.py`: alle indeksrækker via formelkode, kildehashes, uændret indhold og fælles HTML-data.
- Projektets `test_lookup.cjs`: lokal browserkontrol af alle 82 opslag og seks konkrete filtersituationer.
- Projektets `run_windows_navigation.py` og `test_navigation_windows.ps1`: udvalgte faktiske linkklik i PowerPoint.
- `README.md` og projektets `README.md`: genereringskommando, metadata og afprøvning.

## Generér og verificér

Fra `/home/grumsky/PPmaker`:

```bash
.venv/bin/python Projects/el-undervisning/cheatsheet/regenerate.py --pdf
.venv/bin/python Projects/el-undervisning/cheatsheet/verify.py
node Projects/el-undervisning/cheatsheet/test_lookup.cjs
.venv/bin/python Projects/el-undervisning/cheatsheet/run_windows_navigation.py
```

`--pdf` kræver Windows PowerPoint via WSL. Uden flaget genereres PPTX og HTML.
Der er ingen hårdkodede destinationssidetal; planens rækkefølge giver både tal og links.
En ny formel skal have gyldige metadata. Et manglende eller dubleret indeksmål afvises.

## Dokumenteret kontrol

- `navigation-links.json`: 82 entydige opslag og alle 173 native PPTX- og PDF-links.
- `navigation-verification.json`: alle kilder, 43 beskyttede filer, 33 eksempler og 1.680 native tekstfelter/celler.
- `navigation-tests.xml`: 49 tests uden fejl; ændret rækkefølge og ny kode er dækket.
- `html-tests.json`: internet slået fra, alle 82 koder og strukturerede søgeruter fundet, ingen eksterne forespørgsler.
- `navigation-cases.json` og `native-navigation-tests.json`: de udvalgte Windows-linkklik og deres faktiske mål.
- `native-*.png`: destinationsbilleder fra de interaktive Windows-kontroller.
- `navigation-pages-*.jpg`: alle 50 renderede sider visuelt kontrolleret; ny startside også kontrolleret efter sidste layoutændring.
- `exports/navigation-preview/page-*.png`: hver enkelt slide renderet i PowerPoint.

Kliktesten bruger faktiske fysiske museklik i diasshowet med koordinater tilpasset vinduets DPI og aflæser den faktisk åbnede slide;
den kalder ikke `GotoSlide` for at opfylde forventede mål. Automatisk sidefremskift ved klik på tomt areal er slået fra under testen; den gemte leverance ændres ikke. `GotoSlide` bruges kun til testens udgangspunkt.
PDF-kontrollen kontrollerer hver annotation mod både klikområdets placering og destinationssiden.
Hele indeksrækker skal have samme klikområde i PDF; tekstlinks kan få udvidede hitområder ved PowerPoints eksport.

Native tekst i PPTX og PDF bevarer søgning. Formelgrafik indeholder LaTeX som alternativ tekst;
LaTeX og søgeord findes også i indekset. Formeldata vedligeholdes kun i JSON, ikke særskilt i HTML.
