# Kondensatorlektioner: visuel kildekontrol

- EL17: `2 Kondensator.pptx`, 15 slides. `2 Kondensator.pdf` er en sideidentisk PDF-kopi eksporteret med Microsoft PowerPoint; begge hashes findes i databasen. Alle 15 sider og figurer er gennemgået.
- EL18: `3 Kondensatorer op- og afladning.pdf`, 14 sider. Alle sider og de tre indlejrede billed-eksempler på side 12–14 er gennemgået.

## Faglige præciseringer

- EL18:7: Ved opladning er forsyningsspændingen `U_s`, mens kondensatorens startspænding er `u_0`. Kildens `U_0(1−exp(−t/RC))` gælder kun for `u_0=0`. Generelt: `u_C(t)=U_s+(u_0−U_s)exp(−t/RC)`.
- EL18:7,9: Ved `5τ` er restafvigelsen `exp(−5)=0,006737946999`, dvs. ca. 0,67 %. Tilstanden er ikke præcis fuld eller nul.
- EL18:8–9: Efter afbrydelse af forsyningen kræver RC-afladning en lukket vej gennem `R`; en isoleret kondensator opfylder ikke modellen.
- EL17:14: `D` tredobles med `ε_r` kun ved fast spænding og geometri (`D=εU/a`). Ved fast ladning og areal er `D=Q/A` uændret.
- EL18:3–4: `q` er ladning [C], og `i=dq/dt` er strøm [A]. Den ene analogitekst kalder fejlagtigt `q` strøm.
- EL17:13–14: `D` [C/m²] er elektrisk fluxtæthed, adskilt fra det ældre opslag `Ψ` [V·m] om elektrisk flux.
- `e` i eksponentialfunktioner er det dimensionsløse grundtal 2,71828…, ikke elementarladningen `e` [C].

## Billed-eksempler

EL18:12 bruger 623 V, 1 MΩ, 12 µF, 10 s. Selvstændigt: `623 exp(−10/12)=270,7546839 V`. Kilden skriver 270,76 V; standardafrunding af de viste input giver 270,75 V.

EL18:13 bruger samme startdata og 50 V. Selvstændigt: `−12 ln(50/623)=30,2702822 s`.

EL18:14 bruger 623 V, 12 µF, 50 V, 35 s. Selvstændigt: `−35/[12·10⁻⁶ ln(50/623)]=1,15624955 MΩ`, dvs. 1,16 MΩ. Kilden skriver 1,15 MΩ som grov afrunding.

De alternative energiformler følger algebraisk af EL18:10 og EL17:7,14; de er ikke trykt som selvstændige formler i kilderne. De omvendte felt-, areal- og afstandsformler er algebraiske isoleringer af EL17:13–15. Plademodellen antager homogent lineært dielektrikum og ser bort fra randfelter. Variabelmodellen antager ens, skiftevis forbundne plader med ens mellemrum og fælles overlapareal pr. par.
