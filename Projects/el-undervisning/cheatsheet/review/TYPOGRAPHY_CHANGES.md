# Typografi og matematik · BM4

- `formula-database.json`: alle 82 opslag beholdt; ligninger i TRIN, ENH., PAS PÅ og EKS. er markeret som matematik, og de 33 kontrollerede eksempler er bevaret.
- `src/powerpoint_app/visuals/assets.py`: fælles STIX-rendering med opretstående latinsk `I` og rigtige brøker. Rå data, HTML-filtre og skjult søgetekst bruger fortsat almindeligt `I`.
- `src/powerpoint_app/rendering/rich_math.py` og `math_markup.py`: samme matematik for hovedformler og hjælpeligninger; tal/prosa forbliver native tekst. To kort pr. side giver plads til læsbare ligninger.
- `src/powerpoint_app/rendering/lookup_html.py`: den lokale HTML bruger de samme data og formelbilleder som PowerPoint.
- `verify.py`: kontrollerer 82 opslag, 275 matematikblokke, 33 eksempler, 211 links i både PPTX og PDF, kilders hash og målte tekstfelter på 69 sider.
- `typography-comparison-W04.png`, `typography-comparison-I01.png` og `typography-comparison-E01.png`: udsnit af PowerPoint-renderede slides før og efter.

Verifikation: 50 pytest-tests, offline Chromium-opslag af alle 82 koder, 16 faktiske klik i Windows PowerPoint, PowerPoint-PDF-eksport og visuel kontrol af sider 13, 14, 50, 53 samt HTML-opslaget. Den første native klikrunde ramte midlertidigt ikke den anden genvej; genkørsel bestod alle 16.
