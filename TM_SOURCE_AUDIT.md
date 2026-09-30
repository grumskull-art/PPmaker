# TM-kilderevision

Dato: 2026-09-30. Kilder: `Projects/TM1/OneDrive_1_26.9.2026`.
Appens TM-katalog: `Projects/TM1/formula-database.json`.

## Inventar

12 dokumenter: 7 PPTX med 117 slides, 2 PDF med 185 sider og 3 DOCX.
Alle 12 filer er byte-identiske med de tilsvarende filer i det uploadede ZIP-arkiv.
Zone.Identifier-filer er metadata og indgår ikke som faglige kilder.

| ID | Filnavn | Omfang |
| --- | --- | --- |
| VH1 | Lektion 1 og 2 9.14, 9.16-9.19.pptx | 25 slides |
| VH2 | Lektion 3 og 4 9.20-9.21.pptx | 15 slides |
| VH3 | Lektion 5 og 6 9.22-9.27.pptx | 12 slides |
| VH4 | Lektion 7 og 8 9.27 og 9.31-9.33.pptx | 14 slides |
| MO1 | Lektion 1 og 2 Opstart af fag - motorens funktion og konstruktion overordnet.pptx | 28 slides |
| MO2 | Lektion 3 Dieselmotorens hjælpesystemer.pptx | 13 slides |
| MO3 | Lektion 4 Dieselmotorens effekter og virkningsgrader.pptx | 10 slides |
| MOB | Noget om Dieselmotorer version 4.pdf | 183 sider |
| MAN | man-l35-44df.pdf | 2 sider |
| MOD1 | Opgave hovedele for 2-takt diesel.docx | 29 afsnit |
| MOD2 | Spørgsmål til filmen How diesel engines work part 1.docx | 10 afsnit |
| MOD3 | Opgave i motoreffekter og virkningsgrader (1).docx | 38 afsnit |

PPTX-tekst og OpenXML-ligninger er udlæst, og de indlejrede rasterbilleder er visuelt gennemgået. PDF-siderne er tekstudlæst; motorbogen er desuden gennemgået som sideoversigter med relevante formelsider i større gengivelse. DOCX-afsnit og tabeller er læst. PDF-sidetal følger de trykte sidetal. Ingen eksterne kilder eller nye pakker er anvendt.

## Formelopslag

Kataloget indeholder 28 varmelæreopslag og 23 motoropslag. Hver metode har egne variable, enheder, procesbetingelser og præcise henvisninger. Appen viser filnavn og slide/side; følgende er en samlet dækningsoversigt, mens de individuelle henvisninger står i katalogets `source_locations`.

| Opslag | Indhold | Kildesteder |
| --- | --- | --- |
| VH01-VH07 | Absolut tryk, idealgas, stofmængde, massefylde, tilstandsligning, Dalton | VH1:3,6-16 |
| VH08-VH10 | Første hovedsætning og volumenarbejde | VH1:20-23; VH3:3 |
| VH11-VH12 | Varme ved konstant volumen/tryk | VH2:11-12; VH3:3,5 |
| VH13-VH16 | Isokor, isobar og isoterm tilstandsændring; isotermt arbejde | VH1:11-13; VH3:2,4-7 |
| VH17-VH21 | Isentropiske og polytropiske processer | VH3:8-11; VH1:7 |
| VH22-VH25 | Entropi, specifik entropi, entalpi og entalpiændring | VH2:3-6,13-14 |
| VH26-VH28 | Cyklusarbejde, termisk virkningsgrad og Carnot | VH4:2-9; VH2:7 |
| MO01-MO04 | Brændselseffekt, slagvolumen, indiceret effekt for 2-/4-takt | MO3:2-4; MOB:157,163 |
| MO05-MO08 | Bremseeffekt, moment og mekanisk virkningsgrad | MO3:5-6; MOB:173 |
| MO09-MO10 | Specifikt brændselsforbrug | MO3:7; MOB:163-164 |
| MO11-MO15 | Termisk/økonomisk virkningsgrad og varmebalance | MO3:8-9; MOB:158,161,164 |
| MO16-MO17 | Indiceret arbejde og gasarbejde | MOB:157; MO1:28 |
| MO18-MO19 | Ideelle Otto-/Diesel-virkningsgrader | MOB:154 |
| MO20-MO21 | Empirisk brændværdi og teoretisk luftbehov | MOB:167 |
| MO22-MO23 | Røggasmassebalance og turbineeffekt | MOB:170 |

Algebraiske omstillinger er markeret, hvor de bruges. Molargasformen bruger lektionens R cirka 8,314 J/(mol·K). Bogens gasspecifikke R er ikke indsat som en universel værdi. Motormiddeltryk er konsekvent angivet i kPa for at give kW sammen med m³ og rpm; kildens bar-konvention er forklaret i opslaget. Specifikt forbrug bruger kg/kWh, og brændværdi bruger kJ/kg i formlen med faktoren 3600.

## Afgrænsning

- Arbejde på systemet er positivt i VH08-VH20. VH26-VH27 bruger positivt leveret nettoarbejde. Begge konventioner fremgår af kilderne; fortegn blandes ikke mellem opslagene.
- VH2, slide 2, viser begge former for første hovedsætning. Den tvetydighed er beskrevet i en søgbar note.
- VH3, slide 11, giver ikke en komplet relation for c_n. Målet c_n viser en kildehulstatus. VH21 kræver en udtrykkeligt oplyst c_n og beregner den ikke fra n.
- Komplette damptabeller mangler. Dampentalpi viser en kildehulstatus med de tilstandsdata, der er nødvendige for opslag. Ingen h- eller s-tabelværdier er opfundet.
- Bogens øvrige procesudledninger, gentagne omstillinger og opgavefacitter er ikke gengivet som separate metoder. Kataloget er et formelopslag, ikke en kopi af hele bogen eller en facitsamling.
- Opgaveværdier, MAN-motordata og omtrentlige brændværdier er ikke globale standardværdier. Centrale begreber om motoropbygning, hjælpesystemer, damp og energitab er bevaret i søgbare noter.
- Motorlektionens slide 10 har en indlejret WMF-figur, som den lokale LibreOffice ikke kunne rasterisere. De redigerbare tekstforklaringer og bogens energibalance er læst; ingen numeriske værdier eller formler er udledt alene af WMF-figuren.

## Generering og kontrol

Samme Python-generator fremstiller HTML-eksporten og kopierer den til `docs/index.html`. EL-PowerPointen bruger fortsat EL-kataloget. Pages-workflowet kalder allerede denne generator; workflow og GitHub-indstillinger er ikke ændret. TM-katalogfilen skal følge med ved en senere commit.

Kontroller: `.venv/bin/pytest`, `.venv/bin/python Projects/el-undervisning/cheatsheet/regenerate.py`, `.venv/bin/python Projects/el-undervisning/cheatsheet/verify.py`, `node Projects/el-undervisning/cheatsheet/test_lookup.cjs`, `git diff --check`.
Browsertesten kontrollerer alle opslag og metoder, emneadskillelse, tilstand ved filtrering, kildehuller, feedback DA/EN, offline-indlæsning, formelbilleder og mobil/dark mode. Hosted feedbackkontekst testes med lokalt HTML ved en opsnappet test-URL, ikke med en offentlig publicering.
