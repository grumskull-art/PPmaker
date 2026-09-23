# Lokal PowerPoint-app

En lokal Python-app, der importerer Markdown, DOCX og tekstbaserede PDF'er, validerer en versionsstyret slideplan og eksporterer en 16:9-undervisningspræsentation med figurer, formler og talernoter. Statisk PPTX-eksport kræver hverken netværk, API-nøgle eller PowerPoint.

## Hurtig start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -e ".[test]"
powerpoint-app validate examples/demo_project/slide-plan.json --project examples/demo_project
powerpoint-app export examples/demo_project --output demo.pptx
```

Resultatet gemmes i `examples/demo_project/exports/`. Samme plan kan eksporteres igen eller med et andet `theme.json` uden LLM-kald.

`requirements-lock.txt` er det præcise, afprøvede Linux/WSL-testmiljø. UI- og Windows-pakkerne er platformsafhængige og ligger derfor i de separate extras `ui` og `windows`.

## Projekter og kilder

```bash
powerpoint-app init mit-projekt --title "Pumper og anlæg"
powerpoint-app import mit-projekt noter.md kompendium.docx manual.pdf
```

Originalerne kopieres til `sources/`; den normaliserede dokumentmodel gemmes i `cache/`. PDF-sider uden tekst markeres som OCR-krævende. DOCX-tabeller bevares, og avancerede Word-ligninger markeres til kontrol.

Slideplanen er `slide-plan.json`. Ukendte felter, ugyldige elementer, dublerede id'er, manglende kilder/assets og forkerte animation-targets afvises. `save-plan` validerer og laver en historikkopi:

```bash
powerpoint-app save-plan mit-projekt svar-fra-chat.json
powerpoint-app validate mit-projekt/slide-plan.json --project mit-projekt
powerpoint-app export mit-projekt --theme templates/theme.json
```

## Planlægning med eller uden LLM

Manuel JSON fungerer altid. Appen kan desuden lave en kompakt prompt med schema og kilde-id'er, som brugeren selv indsætter i en valgfri chat:

```bash
powerpoint-app prompt mit-projekt --topic "Centrifugalpumper" --audience "Maskinmesterstuderende" --minutes 20 --slides 12
```

Kommandoen skriver kun en lokal tekstfil og foretager ingen eksterne kald. API-nøgler gemmes ikke. Det aktuelle program foretager derfor nul providerkald ved import, redigering, temaændring og eksport.

Et eksplicit providerkald viser kald- og tokenforbrug, caches efter kilder/brief/model/schema og forsøger højst én schema-reparation:

```bash
# KONTAKTER den lokale Ollama-instans
powerpoint-app plan mit-projekt --provider ollama --model qwen3 --topic "Pumper" --audience "Maskinmesterstuderende"
# KONTAKTER det angivne API; nøglen læses kun fra miljøet
powerpoint-app plan mit-projekt --provider api --model min-model --endpoint https://udbyder.example/v1/chat/completions --key-env POWERPOINT_APP_API_KEY --topic "Pumper" --audience "Maskinmesterstuderende"
```

## Desktop-UI

```bash
python -m pip install -e ".[ui]"
powerpoint-app-ui
```

UI'en viser kilder til venstre, rækkefølgen i midten og redigering til højre. Titel, mål, tid, tekst og noter kan rettes direkte; “Ret slide (JSON)” giver valideret adgang til layout, formler, tabeller, figurer og animationer. Før klik på “Vis eksempel” vises kun en mærket tekstskitse. Knappen renderer derefter den faktiske PPTX via PowerPoint på Windows eller LibreOffice/pdftoppm på andre systemer. Eksport og preview kører i baggrunden.

## Animationer og Windows

På Windows med desktop-PowerPoint og `pywin32` kan `--animate` lave en separat animeret arbejdskopi med appear/fade og klikrækkefølge:

```powershell
powerpoint-app export mit-projekt --animate
```

Den statiske grundfil oprettes først og beholdes ved COM-fejl. Integrationen bruger en separat PowerPoint-instans og lukker kun den præsentation/instans, den selv opretter. COM har ikke kunnet afprøves i dette Linux/WSL-miljø; kontrollér på Windows, at filen åbner uden reparationsdialog, at klikrækkefølgen virker i slideshow, og at allerede åbne PowerPoint-vinduer forbliver åbne.

## Windows-pakke

Kør `packaging\build_windows.ps1` i PowerShell. Scriptet tester først og bygger derefter en mappebaseret PyInstaller-app i `dist\PowerPointApp`. Bygningen skal udføres og funktionstestes på Windows; repositoryets Linux-test kan ikke bevise Windows/Office-adfærd.

## Fra WSL til Windows

Kør appen fra et Windows-drev for PowerPoint COM, preview og PyInstaller. Kopiér kildekoden, men ikke Linux-miljøet `.venv`. Find først distributionsnavnet med `wsl -l -q`, erstat `<Distro>` nedenfor og kør i Windows PowerShell:

```powershell
robocopy "\\wsl.localhost\<Distro>\home\grumsky\PPmaker" "$env:USERPROFILE\Documents\PPmaker" /E /XD .venv .pytest_cache __pycache__ build dist /XF *.pyc
Set-Location "$env:USERPROFILE\Documents\PPmaker"
py -3.12 -m venv .venv-win
Set-ExecutionPolicy -Scope Process Bypass
.\.venv-win\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[ui,windows,test]"
pytest -q
powerpoint-app validate examples\demo_project\slide-plan.json --project examples\demo_project
powerpoint-app export examples\demo_project --output windows-demo.pptx
powerpoint-app-ui
```

I UI'en: åbn `examples\demo_project`, ret titel/noter, flyt en slide, gem, vælg `templates\theme.json`, klik “Vis eksempel”, og eksportér. Åbn derefter PPTX-filen i PowerPoint og kontrollér alle slides og noter. Test animationer separat med `powerpoint-app export examples\demo_project --output animation-test.pptx --animate` og gennemfør slideshowet med klik.

## Kontrol og begrænsninger

```bash
pytest
```

Kvalitetskontrollen finder manglende assets, risikabel tekstmængde, store tabeller og tvetydige formler. Det er heuristik, ikke et bevis på visuel kvalitet. Formler og grafer indsættes som billeder; de oprindelige data/formeltekster bevares i planen/cache. Første version understøtter ikke OCR, læsning af manuelle PPTX-rettelser, makroer eller automatisk web-/billedresearch.

## Didaktisk undervisning (schema 1.1)

Appen har en undervisningsprofil med læringsmål, forkundskaber, praktisk sammenhæng,
regnemetode og notation. Profilen styrer nye prompts. Den omskriver ikke en eksisterende
plan automatisk. I UI: vælg **Undervisningsprofil**, udfyld felterne og gem. Opret derefter
prompten med **Lav slideplan (ingen LLM)**. Importér den færdige JSON-plan som før.
Brug **Kontrollér undervisning** til at se mangler og beregningsproblemer.

Et komplet dansk eksempel findes i `examples/teaching_dc`. Det bruger illustrative
værdier og en ideel spændingskilde. Det er undervisning, ikke anlægsdimensionering.

```bash
powerpoint-app teaching examples/teaching_dc
powerpoint-app prompt examples/teaching_dc --topic "Parallel DC" --audience "BM4"
powerpoint-app validate examples/teaching_dc/slide-plan.json --project examples/teaching_dc
powerpoint-app export examples/teaching_dc --output undervisning.pptx
powerpoint-app export examples/teaching_dc --mode study --output studieversion.pptx
```

`prompt` skriver en lokal fil til brug i en valgfri chat. Eksemplets færdige slideplan
kan eksporteres direkte, uden chat, API-nøgle eller providerkald. Et nyt projekt kan
bruge en tilpasset kopi af profilen:

```bash
powerpoint-app teaching mit-projekt --file examples/teaching_dc/teaching-profile.json
```

Piloten har en kort kilde i `sources/martec_bm4_scope.md` med MARTECs
BM4-ramme og EL-TEK1-forløbsplanen for efterår 2026. Ohms lov og Kirchhoffs
love står i EL-TEK1-planen; pilotens tal og udvalgte knudepunktsmetode er
fortsat illustrative. `examples/bm4_source_guides/` rummer korte, separate
kildeoverblik til TM1.1, TM1.2 og BM4-projektet. Brug `powerpoint-app import`
til kun at tilføje den relevante guide til et nyt projekt. Se
`docs/MARTEC_BM4_ALIGNMENT.md` for kildeafgrænsning og eksamensformater.
De trykte bøgers ISBN og kapitelhenvisninger er ikke indlæst bogtekst.
Overfør et konkret, læsbart uddrag eller en opgave som tekst før gengivelse;
appens dokumentimport udfører ikke OCR på fotos af bogsider.

### Fremvisning og svar

- `--mode auto`: undervisningsprofiler giver trinvis fremvisning; gamle planer forbliver statiske.
- `--mode steps`: hvert klik giver en ny slide. Diagram og tidligere trin bliver på deres plads.
- `--mode static`: alle formeltrin vises sammen. Spørgsmål kommer stadig før deres svar.
- `--mode study`: én slide pr. logisk slide, inklusive svar og forklaringer.

UI'en har de samme eksportvalg. Preview viser studieversionen med hele løsningen.
Piloten har 7 logiske slides og bliver til 14 slides i den trinvise eksport. Dette er
almindelige slides, ikke native animationer. Talernoter kan indeholde svar, også på
spørgeslides, så brug fremvisningstilstand til publikum. Svar kan ikke holdes hemmelige
for en person med adgang til selve PPTX-filen.

Schema 1.0-planer kan stadig læses. Nye undervisningsfelter og `parallel_circuit`
kræver schema 1.1. `objective_indices` er nulbaserede indeks i profilens læringsmål.
Spørgsmålets prompt, answer, explanation og wait_seconds ligger i `slide.teaching.question`.
Begrebsspørgsmål kan desuden bruge options, correct_option (nulbaseret) og discussion_prompt.
Skriv ikke svaret i spørgeslidens titel, figur eller almindelige tekstfelter.
Den komplette plan i eksemplet dokumenterer formatet.

### Beregningskontrol og begrænsninger

`slide.calculation_checks` kontrollerer et særskilt numerisk udtryk og dets dimension.
Kontrollen er knyttet til et formel-id på samme slide. Forkerte tal/dimensioner stopper
eksport; ikke-understøttede udtryk markeres til manuel gennemgang. Der bruges ikke eval/exec.

Understøttet: variable, tal, +, -, *, / og heltalspotenser fra -6 til 6. Enheder:
`1, kg, g, m, s, min, h, A, mA, V, kV, ohm, Ω, kohm, W, kW, J, kJ, N, Pa, bar, Hz, m2, m3`.
Enhedsnavne skelner mellem store og små bogstaver. Ingen temperaturkonvertering,
damptabeller, generel symbolsk algebra eller automatisk fortolkning af LaTeX.
Et bestået tjek beviser ikke, at formlen, diagrammet, teksten eller den fysiske model er korrekt.

Den redigerbare kredsløbsfigur understøtter kun én ideel DC-kilde og 2-4 parallelle,
konstante modstande. Den kræver tilstrækkelig plads i layoutet. Formler er fortsat
billeder med original LaTeX i planen. Billeder og formler bevarer nu deres proportioner.

Et andet afgrænset kredsløb, `three_source_dc`, gengiver topologien i den
brugerleverede MARTEC F2023-opgave 3 med tre ideelle spændingskilder og fem
modstande. Topologi og kildepoler er faste, mens komponentværdierne kan redigeres
i slideplanens JSON. Bundne beregningskontroller sammenholder tal og enheder med
den genberegnede figur. Denne kredsløbstype er ikke en generel netværkssolver.
Figuren viser plus/minus ved hver kilde og pile ved I1–I5. Pilene angiver de
valgte positive strømretninger; tallene afsløres i de efterfølgende formeltrin.
L er knuden før R1, B er knuden efter R5, og C er valgt som 0 V.

```bash
python examples/bm4_exam_2023/build_example.py
powerpoint-app validate examples/bm4_exam_2023/slide-plan.json --project examples/bm4_exam_2023
powerpoint-app export examples/bm4_exam_2023 --output bm4-opgave-3.pptx
```

Eksemplet giver 9 logiske slides og 29 kliktrin med et spørgsmål før svaret.
`sources/exercise.md` indeholder topologi og opgavens tal; selve fotografiet af
eksamensarket er ikke lagt i repositoryet. Se `docs/VALIDATION.md` for de
efterprøvede resultater og afgrænsninger.

De kuraterede undervisningsregler og deres forskningskilder er dokumenteret i
`docs/INTERNAL_SCOPE.md`. Appen søger ikke automatisk efter nye studier. Regler,
profil og promptversion indgår i planlægningscachen. Forståelse, overførsel til nye
opgaver og senere genkaldelse skal afprøves med studerende, før der påstås læringseffekt.

Native COM-animationer for undervisningsplaner er endnu ikke integreret. Brug trinvis
fremvisning. Eksisterende schema 1.0-planer kan fortsat bruge `--animate`. Windows og
PowerPoint skal verificeres på Windows, også når portable tests passerer.

En grenformel kan have `diagram_id` og `branch_index` (1-baseret). Begge skal pege på en
reel gren i et `parallel_circuit` eller `three_source_dc` på samme slide. Trinvis fremvisning fremhæver den gren,
som den senest synlige formel henviser til. Figuren flytter sig ikke mellem trinnene.
