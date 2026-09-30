/* Optional real-browser checks. Production needs no Node/browser. */
const fs=require('fs'),path=require('path'),os=require('os'),assert=require('assert');
const cache=path.join(os.homedir(),'.npm','_npx');
const modules=fs.existsSync(cache)?fs.readdirSync(cache).map(n=>path.join(cache,n,'node_modules','playwright')).filter(p=>fs.existsSync(path.join(p,'package.json'))):[];
const playwright=require(process.env.PLAYWRIGHT_MODULE||modules[0]||'playwright');
const browsers=path.join(os.homedir(),'.cache','ms-playwright');
const executable=process.env.BROWSER_BIN||fs.readdirSync(browsers).filter(n=>/^chromium-/.test(n)).map(n=>path.join(browsers,n,'chrome-linux64','chrome')).find(p=>fs.existsSync(p));
const htmlPath=path.join(__dirname,'exports','EL-cheatsheet-BM4-opslag.html');
const screenshots=fs.mkdtempSync(path.join(os.tmpdir(),'ppmaker-tm-browser-'));
(async()=>{
 const browser=await playwright.chromium.launch({executablePath:executable,headless:true,args:['--no-sandbox']});
 try{
  const context=await browser.newContext({viewport:{width:1280,height:950},offline:true});
  const page=await context.newPage(),errors=[],network=[],cases=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))network.push(r.url())});
  // Inline the standalone page so file-URL browser policies do not block the checks.
  await page.setContent(fs.readFileSync(htmlPath,'utf8'));
  assert.equal(await page.locator('article').count(),0);assert(await page.locator('#seek').isDisabled());assert(await page.locator('#known').isHidden());
  async function topic(discipline,id){await page.selectOption('#discipline',discipline);await page.selectOption('#topic',id);}
  async function route(id,index=0){
   const entry=await page.evaluate(id=>activeCatalog().entries.find(e=>e.id===id),id);
   await page.locator('#groups button[data-group=""]').click();
   await page.selectOption('#seek',entry.lookup.seek_key);await page.selectOption('#method',`${id}:${index}`);
   await page.selectOption('#situation',entry.lookup.situations[0]);await page.fill('#search','');await page.locator('#incomplete').check();await page.locator('#groups button[data-group=""]').click();
   assert.deepEqual(await page.locator('#givens input').evaluateAll(els=>els.map(x=>x.value)),entry.lookup.given_sets[index]);
  }
  async function given(...keys){for(const key of keys)await page.locator(`#givens input[value="${key}"]`).check();}
  async function only(id){assert.deepEqual(await page.locator('article').evaluateAll(els=>els.map(x=>x.dataset.entry)),[id]);}
  await topic('EL','el');assert.equal(await page.locator('article').count(),0);assert.equal(await page.locator('#seek option[value="Pfuel"]').count(),0);
  await page.selectOption('#seek','I');assert(await page.locator('#known').isHidden());
  await route('I01');await given('U','R');await page.locator('#incomplete').uncheck();await only('I01');
  await page.locator('.feedback summary').click();await page.selectOption('#feedback-type','missing');
  const feedback=new URL(await page.locator('#feedback-link').getAttribute('href')),body=feedback.searchParams.get('body');
  assert.equal(feedback.pathname,'Grumskull@gmail.com');assert.equal(feedback.searchParams.get('subject'),'EL Cheatsheet feedback');
  assert.match(body,/Type: Mangel \/ Mangel/);assert.match(body,/Version: \S+/);assert.match(body,/Opslag\/sektion: I01/);assert.match(body,/URL: $/m);
  await page.evaluate(()=>{document.documentElement.lang='en';updateFeedbackUi();});assert.equal(await page.locator('#feedback-link').innerText(),'Open mail');
  await page.evaluate(()=>{document.documentElement.lang='da';updateFeedbackUi();});await page.locator('.feedback summary').click();
  assert.equal(await page.locator('#situation option[value="ac_other"]').count(),0);
  await route('I02');await given('P','U');await only('I02');await route('I02',1);await given('P_mech','U');assert.match(await page.locator('article .missing').innerText(),/η/);
  await route('R04');await given('l','S');assert.match(await page.locator('article .missing').innerText(),/Resistivitet/);await given('rho');assert.equal(await page.locator('article .ready').count(),1);
  await route('C05');await given('Q','U');await only('C05');await route('C27');await given('u0','targetU','R','C');await only('C27');
  cases.push('EL: Ohm, DC-effekt, manglende eta, modstand, kapacitans, RC, AC-kildehul og feedback DA/EN');
  await topic('TM','tm-heat');assert.equal(await page.locator('article').count(),0);
  const heatOptions=await page.locator('#seek option').evaluateAll(els=>els.map(x=>x.value));assert(!heatOptions.includes('Pi'));assert(!heatOptions.includes('I'));
  await route('VH02');await given('n','T');assert.match(await page.locator('article .missing').innerText(),/Volumen/);await given('V');
  await page.fill('#search','noget der ikke findes');assert.equal(await page.locator('article').count(),0);assert(await page.locator('#givens input[value="T"]').isChecked());
  await page.fill('#search','');await only('VH02');assert(await page.locator('#givens input[value="T"]').isChecked());
  await page.locator('#groups button[data-group="gas"]').click();await only('VH02');assert.equal(await page.locator('#method').inputValue(),'VH02:0');
  assert.deepEqual(await page.locator('#seek option').evaluateAll(els=>els.map(x=>x.value).filter(Boolean)),['p','n','rho','p2']);
  await page.selectOption('#seek','p2');assert.deepEqual(await page.locator('#method option').evaluateAll(els=>els.map(x=>x.value).filter(Boolean)),['VH06:0']);
  await page.selectOption('#method','VH06:0');
  await page.locator('#groups button[data-group="process"]').click();assert.equal(await page.locator('#seek').inputValue(),'p2');assert.equal(await page.locator('#method').inputValue(),'');assert.equal(await page.locator('#method option[value="VH06:0"]').count(),0);assert(await page.locator('#known').isHidden());
  await page.locator('#groups button[data-group="gas"]').click();await page.selectOption('#method','VH06:0');
  await page.locator('#groups button[data-group="cycle"]').click();assert.equal(await page.locator('article').count(),0);assert.equal(await page.locator('#seek').inputValue(),'');assert.equal(await page.locator('#method').inputValue(),'');assert.equal(await page.locator('#situation').inputValue(),'');assert(await page.locator('#known').isHidden());
  assert.deepEqual(await page.locator('#seek option').evaluateAll(els=>els.map(x=>x.value).filter(Boolean)),['Wout','eta']);
  await page.locator('#groups button[data-group=""]').click();await route('VH02');await only('VH02');
  assert.equal(await page.locator('#seek option[value="cn"]').count(),0);
  assert.equal(await page.locator('#seek option[value="steam_h"]').count(),0);
  await page.selectOption('#seek','');await page.selectOption('#situation','');await page.fill('#search','damp');assert.match(await page.locator('#notes').innerText(),/damptabeller/);
  await route('VH16');await given('p1','V1','V2');await page.screenshot({path:path.join(screenshots,'heat-desktop.png'),fullPage:true});
  assert.match(await page.locator('article .source').innerText(),/Lektion 5 og 6 9.22-9.27.pptx · slide 7/);
  cases.push('Varmelaere: isolerede variable, metodespecifikke input, bevaret tilstand, kildehuller og kildehenvisning');
  await page.selectOption('#topic','tm-engine');assert.equal(await page.locator('article').count(),0);assert.equal(await page.locator('#seek option[value="steam_h"]').count(),0);assert.equal(await page.locator('#seek option[value="I"]').count(),0);
  await route('MO03');await given('pi','Vs','c','rpm');await only('MO03');
  await page.selectOption('#method','MO04:0');assert.equal(await page.locator('article').count(),0);await page.selectOption('#situation','four_stroke');await only('MO04');
  await page.selectOption('#topic','tm-heat');assert.equal(await page.locator('#method').inputValue(),'VH16:0');assert(await page.locator('#givens input[value="V1"]').isChecked());
  await page.selectOption('#topic','tm-engine');assert.equal(await page.locator('#method').inputValue(),'MO04:0');assert(await page.locator('#givens input[value="rpm"]').isChecked());
  await page.screenshot({path:path.join(screenshots,'engine-desktop.png'),fullPage:true});
  const catalogs=await page.evaluate(()=>db.catalogs);
  for(const catalog of catalogs){
   await topic(catalog.discipline,catalog.id);
   for(const group of ['',...catalog.navigation_groups.map(g=>g.id)]){
    await page.locator(`#groups button[data-group="${group}"]`).click();
    const scoped=catalog.entries.filter(e=>!group||e.lookup.group===group),keys=[...new Set(scoped.map(e=>e.lookup.seek_key))];
    assert.deepEqual(await page.locator('#seek option').evaluateAll(els=>els.map(x=>x.value).filter(Boolean)),keys,`${catalog.id}/${group}: søgte størrelser`);
    for(const key of keys){
     await page.selectOption('#seek',key);
     const entries=scoped.filter(e=>e.lookup.seek_key===key),methods=entries.flatMap(e=>e.lookup.given_sets.map((_,i)=>e.id+':'+i)),situations=[...new Set(entries.flatMap(e=>e.lookup.situations))];
     assert.deepEqual(await page.locator('#method option').evaluateAll(els=>els.map(x=>x.value).filter(Boolean)),methods,`${catalog.id}/${group}/${key}: metoder`);
     assert.deepEqual(await page.locator('#situation option').evaluateAll(els=>els.map(x=>x.value).filter(Boolean)),situations,`${catalog.id}/${group}/${key}: situationer`);
    }
   }
  }
  cases.push('Alle fag og underkategorier: kun størrelser, metoder og situationer med reelle opslag; idealgasser og nulstilling af ugyldige valg');
  await topic('TM','tm-heat');await route('VH02');await page.locator('#groups button[data-group="gas"]').click();
  await page.selectOption('#topic','tm-engine');await page.selectOption('#topic','tm-heat');
  assert.equal(await page.locator('#groups button[data-group="gas"]').getAttribute('aria-pressed'),'true');assert.equal(await page.locator('#method').inputValue(),'VH02:0');
  assert.deepEqual(await page.locator('#seek option').evaluateAll(els=>els.map(x=>x.value).filter(Boolean)),['p','n','rho','p2']);
  const allRoutes=await page.evaluate(()=>db.catalogs.flatMap(c=>c.entries.flatMap(e=>e.lookup.given_sets.map((set,i)=>({c,e,set,i})))).filter(({c,e,set,i})=>!matchEntries(e.lookup.seek_key,set,e.lookup.situations[0],e.id,false,'',c).some(r=>r.method===e.id+':'+i&&r.complete)).map(({e,i})=>e.id+':'+i));assert.deepEqual(allRoutes,[]);
  let count=0;
  for(const [discipline,id] of [['EL','el'],['TM','tm-heat'],['TM','tm-engine']]){
   await topic(discipline,id);await page.selectOption('#seek','');await page.selectOption('#situation','');await page.locator('#incomplete').check();await page.locator('#groups button[data-group=""]').click();
   const ids=await page.evaluate(()=>activeCatalog().entries.map(e=>e.id));
   for(const entry of ids){await page.fill('#search',entry);assert(await page.locator(`article[data-entry="${entry}"]`).count()>0,entry);assert(await page.locator('article img').evaluateAll(imgs=>imgs.every(i=>i.complete&&i.naturalWidth>0)),entry);}
   count+=ids.length;
  }
  cases.push('Motorlaere: 2-/4-takt, fagadskillelse og bevaret emnetilstand; alle '+count+' opslag og metoder findes');
  const dark=await browser.newContext({viewport:{width:390,height:844},offline:true,colorScheme:'dark'}),mobile=await dark.newPage();
  mobile.on('pageerror',e=>errors.push(e.message));await mobile.setContent(fs.readFileSync(htmlPath,'utf8'));await mobile.selectOption('#discipline','TM');await mobile.selectOption('#topic','tm-engine');await mobile.selectOption('#seek','Pi');await mobile.selectOption('#method','MO04:0');
  assert.notEqual(await mobile.locator('body').evaluate(el=>getComputedStyle(el).backgroundColor),'rgb(255, 255, 255)');assert(await mobile.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert(await mobile.locator('.feedback summary').isVisible());
  await mobile.screenshot({path:path.join(screenshots,'engine-mobile-dark.png'),fullPage:true});await mobile.locator('.feedback summary').click();assert(await mobile.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await mobile.setViewportSize({width:320,height:720});assert(await mobile.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await dark.close();
  cases.push('Mobil 320/390 px: dark mode, feedback og ingen vandret sideoverloeb');
  const hosted=await browser.newContext(),hostedPage=await hosted.newPage();
  await hostedPage.route('https://ppmaker.test/**',route=>route.fulfill({contentType:'text/html',body:fs.readFileSync(htmlPath,'utf8')}));await hostedPage.goto('https://ppmaker.test/PPmaker/');
  await hostedPage.selectOption('#discipline','TM');await hostedPage.selectOption('#topic','tm-engine');await hostedPage.selectOption('#seek','Pi');await hostedPage.selectOption('#method','MO03:0');
  const mail=new URL(await hostedPage.locator('#feedback-link').getAttribute('href'));assert.match(mail.searchParams.get('body'),/URL: https:\/\/ppmaker.test\/PPmaker\//);assert.match(mail.searchParams.get('body'),/Fag\/emne: TM \/ Motorlære/);assert.match(mail.searchParams.get('body'),/MO03/);await hosted.close();
  assert.deepEqual(errors,[]);assert.deepEqual(network,[]);
  const result={html_sha256:require('crypto').createHash('sha256').update(fs.readFileSync(htmlPath)).digest('hex'),browser:await browser.version(),method:'Real Chromium, offline inline HTML; intercepted HTML for hosted URL context',cases,all_codes_found:count,all_structured_routes_found:true,errors,external_requests:network,screenshots};
  fs.writeFileSync(path.join(__dirname,'review','html-tests.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
