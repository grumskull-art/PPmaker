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
