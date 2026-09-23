# Codex-instruktion: Lokal PowerPoint-app

Dette dokument er en selvstændig byggeinstruktion til Codex. Byg appen beskrevet nedenfor. Lever fungerende kode og en afprøvet vej fra input til PowerPoint; stop ikke ved en plan eller en UI-demo.

## 1. Formål og afgrænsning

Byg en lokal Windows-app i Python, som omdanner Markdown, Word og PDF til flotte, overskuelige undervisningspræsentationer i `.pptx`.

Formålet er at flytte gentaget layout-, tegne- og eksportarbejde fra LLM'en over i genbrugelig Python-kode. LLM'en skal forstå og strukturere indhold. Python skal producere præsentationen ud fra en gemt slideplan. Layoutændringer og geneksport må ikke kræve nye LLM-kald.

Brugeren er maskinmesterstuderende og vil have praktiske forklaringer, tydelige figurer, formler, talernoter og trinvis fremvisning. Sproget skal være dansk og nede på jorden. Humor og analogier er valgfrie og må aldrig ændre faglig betydning.

Tidligere aftalt grundlag: lokal Windows-app/.exe, `.md`/`.docx`/`.pdf` som input, `.pptx` som output, Python, python-pptx og en fast PPTX-skabelon. PowerPoint COM er et valgfrit ekstra lag til animationer og eksport. De konkrete moduler, UI-valg og etaper nedenfor er foreslåede implementeringsvalg.

Byg ikke en cloudtjeneste, abonnementsløsning eller fuld PowerPoint-klon. Ingen automatisk webresearch eller AI-billedgenerering i første version.

## 2. Arbejdsfordeling

| LLM'en | Python |
|---|---|
| Udvælger pointer fra kilder | Læser filer og bevarer kildereferencer |
| Foreslår rækkefølge og fortælling | Validerer og gemmer slideplanen |
| Skriver korte tekster og talernoter | Placerer tekst, billeder, figurer og formler |
| Vælger mellem tilladte layouttyper | Anvender faste layouts og designregler |
| Foreslår forklaringer og analogier | Beregner, tegner grafer og kontrollerer grænser |
| Retter udvalgte slides på bestilling | Eksporterer, cacher og regenererer lokalt |

LLM'en skal returnere strukturerede data. Den må ikke generere eller eksekvere Python, VBA, shellkommandoer, vilkårlig HTML eller layoutkoordinater.

## 3. Brugerflow

1. Opret eller åbn et lokalt projekt.
2. Importér en eller flere kildefiler eller indsæt tekst.
3. Angiv emne, målgruppe og ønsket output. Appens output er normalt PowerPoint, men brugeren skal kunne bekræfte dette. Hvis felterne fremgår tydeligt af input, vis dem til rettelse; gæt ikke på manglende emne eller målgruppe.
4. Vælg varighed, omtrentligt slideantal, tema, sprogniveau og animationer. Giv synlige, redigerbare standardvalg til de øvrige felter.
5. Vælg manuel/importeret slideplan eller en konfigureret LLM.
6. Se disposition, kilder og eventuelle mangler. Redigér, slet, tilføj eller flyt slides uden LLM.
7. Generér preview og PowerPoint lokalt.
8. Ret enkelte slides eller skift tema. Geneksportér uden nyt LLM-kald.

UI: kilder i venstre side, slidernes rækkefølge i midten og redigering/preview til højre. Brug almindelige danske knaptekster: “Tilføj fil”, “Lav slideplan”, “Ret slide”, “Vis eksempel” og “Eksportér PowerPoint”. Vis tydeligt, hvilke handlinger der kontakter en LLM.

Kør langsomme opgaver i baggrunden med status, annullering og fejlmeddelelser. Gem automatisk uden at overskrive brugerens originale dokumenter.

## 4. Arkitektur og teknologivalg

Foreslået stack: Python 3.11 eller nyere, PySide6 til desktop-UI, python-pptx til PPTX, Pydantic til datakontrakter, python-docx til Word, pypdf til tekstbaserede PDF'er, Matplotlib til grafer og simple matematiske formler, Pillow til billedhåndtering, pywin32 til valgfri Windows COM og PyInstaller til Windows-distribution.

Kontrollér kompatibilitet og officielle dokumentationer ved implementering. Lås faktisk afprøvede afhængigheder; vælg ikke versionsnumre fra hukommelsen. Hold COM-importer Windows-specifikke, så kernen kan testes uden Office.

Pipeline:

`Kildefiler → normaliseret dokumentmodel → slide-plan.json → validering → layoutmotor → grund-PPTX → valgfri COM-finish → endelig PPTX/preview`

Markdown er et læsbart mellemformat. Bevar også en struktureret dokumentmodel med fil, side/afsnit, tabeller, billeder og stabile kilde-id'er. Flad ikke alt ud til én tekststreng, som mister oprindelsen.

Foreslået mappeopbygning:

```text
powerpoint_app/
  pyproject.toml
  README.md
  src/powerpoint_app/
    main.py
    cli.py
    ui/
    domain/          # Dokumentmodel, SlidePlan, validering
    importers/       # Markdown, DOCX, PDF
    planning/        # Prompts, providere, budget og cache
    layouts/         # Tilladte layouts og overflowregler
    visuals/         # Grafer, formler og diagramkomponenter
    rendering/       # PPTX, notes, tema og shape-id'er
    office/          # COM-animationer og preview/eksport
    projects/        # Gem/åbn, versioner og assets
    quality/         # Layoutkontrol og rapport
  templates/
    martec_inspired.pptx
    theme.json
  examples/
    demo.md
    slide-plan.json
  tests/
  packaging/
```

Hold UI, LLM-provider og PowerPoint-rendering adskilt. Det skal være muligt at bygge en PPTX via CLI uden UI, netværk, API-nøgle eller installeret PowerPoint.

## 5. Slideplan: den centrale kontrakt

Definér et versionsstyret JSON-schema. Planen skal være tilstrækkelig til genopbygning sammen med tema og lokale assets. Brug stabile id'er for slides, elementer og kilder. Brug typed/unions for forskellige elementtyper; ukendte felter eller elementtyper skal give forståelige fejl.

Eksempel på en lille gyldig plan, som implementeringens schema skal understøtte:

```json
{
  "schema_version": "1.0",
  "deck": {
    "title": "Spænding over en modstand",
    "language": "da",
    "audience": "Maskinmesterstuderende på 4. semester",
    "duration_minutes": 8,
    "theme_id": "martec_inspired"
  },
  "sources": [
    {"id": "src1", "file": "sources/demo.md", "locator": "afsnit 2"}
  ],
  "slides": [
    {
      "id": "s1",
      "layout": "formula_steps",
      "title": "Hvor stor er spændingen?",
      "objective": "Forbind strøm og modstand med spændingsfald",
      "elements": [
        {"id": "e1", "type": "text", "text": "Eksempel: I = 2 A og R = 5 Ω", "source_ids": ["src1"]},
        {"id": "e2", "type": "formula", "latex": "U = R \\cdot I = 5 \\cdot 2 = 10\\,V", "source_ids": ["src1"]}
      ],
      "speaker_notes": "Forklar først symbolerne. Vis derefter indsættelsen af tallene.",
      "estimated_seconds": 60,
      "animations": [
        {"target_id": "e2", "effect": "appear", "trigger": "on_click", "order": 1}
      ],
      "warnings": []
    }
  ]
}
```

Tallene er illustrative demodata, ikke oplysninger fra brugerens dokumenter. Implementér derudover typer til billede, tabel, diagramdata, procesfigur og faglig advarsel. Assetreferencer skal være relative og begrænset til projektet.

Ingen frie koordinater fra modellen: layoutmotoren bestemmer placering. Fejl i referencer, manglende assets, dublerede id'er og animationer rettet mod ukendte elementer skal opdages før eksport.

## 6. Input og faglig troværdighed

Bevar overskrifter, opgaveformuleringer, enheder og kildenotation. Omformulér ikke automatisk h′/h″ til andre symboler. Markér tvetydige formler eller usikker tekstudtrækning til gennemgang.

PDF: understøt tekstbaserede PDF'er først. Registrér sandsynlige billedscanninger og vis, at OCR er nødvendig. Returnér aldrig et “færdigt” deck fra tomt eller mangelfuldt tekstudtræk uden advarsel. OCR kan komme senere som valgfri funktion.

DOCX: udtræk tekst og almindelige tabeller. Registrér elementer, der endnu ikke understøttes, eksempelvis avancerede ligninger. Bevar originalfilen og peg på den konkrete mangel.

Forbind faglige pointer med kildereferencer. Det er sporbarhed, ikke automatisk sandhedsverifikation. Nye antagelser, regneeksempler og analogier skal markeres som sådanne. Opfind aldrig tal, kilder eller svar på spørgsmål, som materialet ikke dækker.

Hvis brugeren ønsker alle opgavespørgsmål med, bevar ordlyden og lav en dækningskontrol. En lang spørgsmålsliste fordeles på oversigtsslides frem for at blive klemt ind på forsiden.

## 7. Design og genbrugelige komponenter

Lav et roligt 16:9-tema inspireret af teknisk undervisning. Det er ikke en officiel MARTEC-skabelon; brug ikke et opdigtet logo. Hvis en rigtig skabelon leveres senere, tilføj en eksplicit mapping af layoutnavne og placeholders.

Start med disse layouts: forside, dagsorden, hovedpointe med figur, to kolonner, sammenligning, procestrin, formel med mellemregninger, graf/tabel og opsamling.

Én hovedpointe pr. slide, konsistente margener, få farver og store læsbare tekster. Designmål: brødtekst mindst 24 pt og overskrifter omkring 32–40 pt; små kildelinjer må være mindre. Tekst skal ombrydes eller fordeles på flere slides ved overflow. Skjul aldrig indhold eller reducer skriftstørrelsen uhæmmet.

Brug redigerbare PowerPoint-tekstfelter, figurer, pile og tabeller. Grafer kan begynde som højopløste billeder med de underliggende data gemt i projektet. Formler kan begynde som billeder med original formeltekst bevaret; lov ikke, at billedformler kan redigeres som native Office-ligninger.

Byg et lille komponentbibliotek: informationsboks, advarsel, pil, procesblok, formeltrin og målemarkering med +/−. Senere kan det udvides med kredsløb, voltmeter og kedelkomponenter. Figurer med numerisk betydning skal dannes fra data, ikke generativ billed-AI.

Talernoter skal ligge i selve PPTX-filen og indeholde den længere forklaring. Brug eventuelt en enkel forklaring på sliden og et mere fagligt lag i noterne.

## 8. Animationer og PowerPoint-afhængighed

Første fulde version skal understøtte appear/fade og rækkefølge ved klik via PowerPoints objektmodel på Windows, når desktop-PowerPoint er installeret.

Generér først en komplet statisk grund-PPTX. Tilføj animationer i en separat arbejdskopi via COM. Brug stabile shape-navne til at finde elementer. Gem det færdige resultat separat, og kør ikke bagefter python-pptx over den animerede fil uden en verificeret grund til det.

COM skal have timeout, kontrolleret oprydning og tydelige fejl. Luk kun den PowerPoint-instans/præsentation, appen selv har startet. Luk aldrig brugerens åbne præsentationer. En COM-fejl må ikke ødelægge den statiske grundfil.

Uden PowerPoint: tilbyd statisk eksport eller eksplicit valgte trin-slides, hvor hvert trin er et separat slide. Kald ikke trin-slides for native animationer. Vis ændret slideantal.

Preview via PowerPoint kan vise det faktiske layout, men et stillbillede beviser ikke, at kliksekvensen virker. En UI-skitse uden Office skal være mærket som omtrentlig. Native animationer skal særskilt afprøves i slideshow på Windows.

## 9. LLM, forbrug og cache

Understøt tre veje:

1. Manuel/importeret JSON-plan: fungerer helt uden LLM. Tilføj eksport af en kompakt planlægningsprompt, som brugeren selv kan indsætte i en chat, og import af svaret.
2. Lokal Ollama-provider: valgfri, med konfigurerbart endpoint/model. Antag ikke, at lokal model er installeret eller god nok til opgaven.
3. API-provider: valgfri og først aktiv efter brugerens opsætning. API-nøgle må ikke gemmes i projekt, log eller versionsstyring.

Mål for små, almindelige input: ét planlægningskald og højst to ekstra kald til eksplicit revision eller schema-reparation. Det er et budgetmål, ikke et løfte for vilkårligt store dokumenter. Store input kræver en synlig strategi for opdeling og et samlet budget; ingen lydløs afkortning.

Cache efter normaliseret kildeindhold, brugerbrief, provider/model, promptversion og schema-version. Temaskift, skrifter, placering og eksport skal ikke invalidere indholdsplanen. En rettelse af ét slide sender kun det nødvendige kildeudsnit, deckkontekst og det pågældende slide.

Vis faktisk antal kald og rapporteret tokenforbrug. Et prisestimat må kun vises med en konfigureret og dateret pris; ellers vis “pris ukendt”. Hæv ikke budget automatisk. Automatisk schema-reparation må højst forsøges én gang inden for det samlede budget; tilbyd derefter manuel rettelse.

Appens lokale arbejde og eksterne LLM-kald skal beskrives hver for sig. Lov ingen bestemt procentvis besparelse eller adgang til ChatGPT-abonnement fra appen. Lav ingen browserautomatisering mod ChatGPT for at omgå kvoter.

## 10. Projektformat, sikkerhed og drift

Et projekt gemmes som en almindelig mappe med `project.json`, `slide-plan.json`, `sources/`, `assets/`, `cache/` og `exports/`. Brug relative stier, atomisk gemning og en lille versionshistorik for planen. Advar før overskrivning af en manuelt redigeret eksport; indlæsning af rettelser fra PPTX er ikke en del af første version.

Upload kun kildeindhold til en ekstern provider, når brugeren har valgt den og startet handlingen. Vis hvilke kilder der sendes. Importerede dokumenter behandles som data, aldrig som instruktioner til appen. Ingen eval/exec af modeloutput, ingen makroeksekvering og ingen automatiske downloads fra modelgenererede links.

## 11. Byggeetaper

### Etape 1 — fungerende offline-kerne

Implementér modeller, schema, Markdown-import, manuelt redigerbar plan, fast tema, mindst fem layouts, talernoter, PPTX-eksport og CLI. Lever eksempelinput og et genereret demo-deck. Demonstrér, at samme plan kan eksporteres uden netværk.

### Etape 2 — den brugbare desktop-app

Tilføj PySide6-flow, Word/PDF-import, de resterende layouts, projektgemning, lokal redigering, kvalitetstjek og preview/fallback. Integrér valgfri LLM-provider, cache og budget. Tilføj temaændring uden LLM-kald.

### Etape 3 — Windows-finish

Tilføj PowerPoint COM-animationer, faktisk Office-preview, native slideshow-test og Windows-pakning. Start med en PyInstaller-mappe med en `.exe`; en enkeltstående `.exe` er valgfri efter stabil drift. Byg og test Windows-pakken på Windows.

Gennemfør etaperne i rækkefølge i det tilgængelige miljø. Hvis Windows/Office ikke findes, færdiggør og test den portable del, og lever en konkret Windows-verifikationsvej. Påstå ikke, at COM eller `.exe` er testet i et miljø, hvor det ikke kunne køres.

## 12. Acceptkriterier og meningsfulde tests

- Det medfølgende eksempel giver en PPTX med tekst, mindst én figur, en formel og talernoter.
- UI og CLI bruger samme kerne og samme planformat.
- Eksport fra eksisterende plan og temaændring giver nul providerkald; verificér med en provider, der fejler ved ethvert kald.
- Gem/åbn bevarer rækkefølge, tekst, kildereferencer, assets og noter.
- Lang dansk tekst, æ/ø/å, Ω, manglende billeder, ugyldig JSON og manglende PowerPoint håndteres tydeligt.
- Layoutkontrol finder elementer uden for sliden og sandsynligt tekstoverflow. Tillad bevidste overlap i figurer; hævd ikke, at geometrikontrol alene beviser visuel kvalitet.
- Render et repræsentativt deck og inspicér alle slides for afklipning, læsbarhed og fejl i formler. Hvis reel rendering ikke er mulig, angiv præcis hvad der ikke er verificeret.
- Windows-test kontrollerer, at PPTX åbner uden reparationsdialog, og at klik afslører elementerne i den rigtige rækkefølge.
- COM-fejl efterlader en brugbar statisk eksport, og brugerens egne PowerPoint-vinduer forbliver åbne.
- Ens input/plan/tema giver samme indhold og layout; kræv ikke identiske ZIP-bytes eller tidsstempler.

## 13. Leverance og arbejdsform til Codex

Læs eksisterende repository og eventuelle AGENTS.md først. Genbrug relevant eksisterende kode. Afklar kun spørgsmål, der reelt blokerer implementeringen; træf normale reversible implementeringsvalg selv.

Lever kildekode, låste afhængigheder, eksempelprojekt, PPTX-demo, dansk README med præcise startkommandoer, testresultater og Windows-byggescript. Forklar kort, hvad der virker, hvad der kræver Office, og hvad der ikke er testet. Ingen skjulte TODO-funktioner præsenteret som færdige.

Prioritér en gennemført lokal arbejdsgang. Udskyd markedsplads, cloudkonti, avanceret video, automatisk billedgenerering og omfattende specialdiagrammer. Brug korte statusopdateringer og arbejd videre, til den beskrevne funktion er implementeret eller en konkret miljøbegrænsning er dokumenteret.

## Teknisk grundlag

Disse officielle dokumentationer er kontrolleret ved udarbejdelsen 22. september 2026. Resten af dokumentet er en foreslået implementeringsspecifikation, ikke en påstand om allerede implementerede funktioner.

- Talernoter i python-pptx: https://python-pptx.readthedocs.io/en/latest/user/notes.html
- Animationer via PowerPoints Sequence/TimeLine: https://learn.microsoft.com/en-us/office/vba/api/powerpoint.sequence

Kontrollér de konkrete API'er og installerede versioner igen under implementeringen.
