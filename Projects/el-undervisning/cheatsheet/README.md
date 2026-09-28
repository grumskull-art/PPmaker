# EL-opslagsværk · BM4

69 A4-sider med 82 opslag og 33 genberegnede eksempler. Genereret med PPmakers
eksisterende typed plan, LaTeX-rendering og PPTX-eksport; ingen modelkald under regenerering.

Færdige filer: `exports/EL-cheatsheet-BM4-navigation.pptx`,
`exports/EL-cheatsheet-BM4-navigation.pdf` og `exports/EL-cheatsheet-BM4-opslag.html`.
Den tidligere PPTX og PDF er bevaret.
Redigerbart indhold: `formula-database.json` og den genererede `slide-plan.json`.
Tekst, tabeller, kredsløb, pile og polariteter kan redigeres direkte i PowerPoint.
Hovedformler og hjælpeligninger er højopløste matematikbilleder med opretstående
serif-I, egentlige brøker og indekser. Deres LaTeX findes i databasen og billedets
alternative tekst; en skjult teksttransskription bevarer søgning i PPTX/PDF. Der er ikke native Office Math-formelfelter.

## Brug og regenerering

Start på side 1 med otte klikbare genveje. Indekset på side 2–12 viser søgt størrelse,
givne oplysninger og fysisk situation; hele hver af de 82 rækker åbner sit formelkort.
Side 13–54 har opslag; knudepunktseksemplet er på side 55. Side 56–69 samler registre,
kilder og afgrænsning. Opslag har “Til indeks” og “Til start”; øvrige sider har “Til start”.

HTML-filen åbnes direkte i en browser uden internet. Vælg fx “Jeg søger: Strøm I [A]”,
“ohmsk DC” og kendt spænding U samt modstand R. Match bruger størrelsers identitet og
fysisk situation; samme enhed er ikke tilstrækkelig. Kort viser gyldighed og manglende
oplysninger. Slå visning af manglende oplysninger til, hvis ingen fulde match findes.

Kør fra `/home/grumsky/PPmaker`:

```bash
.venv/bin/python Projects/el-undervisning/cheatsheet/regenerate.py --pdf
.venv/bin/python Projects/el-undervisning/cheatsheet/verify.py
.venv/bin/powerpoint-app validate Projects/el-undervisning/cheatsheet/slide-plan.json --project Projects/el-undervisning/cheatsheet
.venv/bin/python -m pytest -q --disable-warnings
```

PDF-flaget kræver WSL, `powershell.exe` og installeret Microsoft PowerPoint.
Udelad `--pdf` for PPTX og HTML. Appen bevarer tidligere eksporter med tidsstempel;
regenereringsscriptet opdaterer også de faste leverancefilnavne med nyeste eksport.
Redigér databasen og regenerér, så sidetal og indeks følger opslagene. Hvert opslag har
`lookup` med `group`, `seek_key`, `given_sets` og `situations`; registre findes i samme JSON.
Sidetal og linkmål bindes fra den færdige slideplan via slide-ID’er. Nye formler skal have
metadata og findes præcis én gang i indekset. Generering kontrollerer alle native links;
med `--pdf` kontrolleres også hver PDF-destination. Planen må ikke bruges med gamle sidehenvisninger.

## Kildegrundlag og grænser

De 16 originale PPTX-filer i `../orginaler/OneDrive_1_26.9.2026 (1)/` udgør 160 slides.
Deres tekst, noter og alle renderede figurer er gennemgået. Kilde-ID og konkrete
slidenumre står ved hvert databaseopslag og i PPTX-noterne. Originale filer er bevaret.
En laboratorierapport fra Downloads er importeret som praksiskontekst, ikke som nyt pensum.

Dækket: DC-net, kilder, resistivitet, temperatur, effekt/energi, mekaniske sammenhænge
fra energiopgaverne, elektriske/magnetiske felter, magnetkredse, induktion og lederkræfter.
Der blev ikke fundet et beregningsgrundlag for RLC, kapacitans, reaktans, impedans,
fasorer, AC-effekt, resonans, transformeromsætning eller trefase. Nævnte bogsider,
Word-øvelser og Teams-opgaver er ikke vedlagt. Samlingen er derfor ikke hele BM4-pensum.

SI-definition og konstantskel er kontrolleret mod [BIPM](https://www.bipm.org/en/si-base-units/ampere)
og [NIST CODATA 2022](https://physics.nist.gov/cuu/pdf/wall_2022.pdf).
Undervisningens afrundinger og materialetemperaturer står i værdiregisteret.

## Kontrol

Alle 69 sider er renderet i Windows PowerPoint 16.0; ændrede sider og tre
før/efter-eksempler er visuelt gennemgået.
`review/windows-layout.json` måler 2.536 native tekstfelter/celler. `verify.py` kontrollerer
kildehashes, opslagshenvisninger, eksempler, indekssider, PDF-format og placeringer.
Alle 82 indeksrækker har præcis ét korrekt mål; alle 211 interne links er kontrolleret i
PPTX og PDF. Tekstbaseret søgning i begge formater er bevaret.

Browserkontrol åbner den lokale HTML med internet slået fra: alle 82 opslag findes;
strøm, effekt, manglende virkningsgrad, resistivitet og udækkede AC-emner er afprøvet.
50 app-tests består, herunder ekstra forside, omordnede sider, ny formelkode og fejlmål.
Alle 33 regneeksempler er genberegnet. Breddetolerancen på 3 pt dækker lille måleoverhæng;
ingen synlig beskæring. `review/navigation-verification.json`, `navigation-links.json`,
`html-tests.json`, `native-navigation-tests.json` og `navigation-tests.xml` dokumenterer kontrollen.

Ekstra interaktive kontroller fra projektroden:

```bash
node Projects/el-undervisning/cheatsheet/test_lookup.cjs
.venv/bin/python Projects/el-undervisning/cheatsheet/run_windows_navigation.py
```

Browserkontrollen bruger installeret Playwright/Chromium (eller `PLAYWRIGHT_MODULE` og
`BROWSER_BIN`). Windows-kontrollen kræver et tilgængeligt skrivebord og PowerPoint;
den klikker faktisk med musen i diasshowets linkområder og gemmer destinationsbilleder. Den udfører
16 klik: alle startgenveje, første og sidste indeks, I01, retur, næste indeks og reference.
Før/efter-udsnit: `review/typography-comparison-{W04,I01,E01}.png`.
Filoversigt og ændringsankre for navigation: `review/NAVIGATION_CHANGES.md` og
`review/NAVIGATION_FILES.txt`. Tidligere faglig revision: `review/CHANGES.md`.
