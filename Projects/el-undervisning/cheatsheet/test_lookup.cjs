/* Optional real-browser check. Production generation needs no Node/browser. */
const fs=require('fs'),path=require('path'),os=require('os'),{pathToFileURL}=require('url'),assert=require('assert');
const cache=path.join(os.homedir(),'.npm','_npx');
const modules=fs.existsSync(cache)?fs.readdirSync(cache).map(n=>path.join(cache,n,'node_modules','playwright')).filter(p=>fs.existsSync(path.join(p,'package.json'))):[];
const playwright=require(process.env.PLAYWRIGHT_MODULE||modules[0]||'playwright');
const browsers=path.join(os.homedir(),'.cache','ms-playwright');
const executable=process.env.BROWSER_BIN||fs.readdirSync(browsers).filter(n=>/^chromium-/.test(n)).map(n=>path.join(browsers,n,'chrome-linux64','chrome')).find(p=>fs.existsSync(p));
(async()=>{
 const browser=await playwright.chromium.launch({executablePath:executable,headless:true,args:['--no-sandbox']});
 try{
  const context=await browser.newContext({viewport:{width:1200,height:950},offline:true});
  const page=await context.newPage(),errors=[],network=[],cases=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))network.push(r.url())});
  await page.goto(pathToFileURL(path.join(__dirname,'exports','EL-cheatsheet-BM4-opslag.html')).href);
  async function current(){await page.selectOption('#seek','I');await page.locator('#givens input[value="U"]').check();await page.locator('#givens input[value="R"]').check();await page.selectOption('#situation','dc_ohmic');await page.locator('#incomplete').uncheck();}
  await current();assert.deepEqual(await page.locator('article').evaluateAll(els=>els.map(x=>x.dataset.entry)),['I01']);cases.push('I + U,R + ohmsk DC → I01 alene');
  await page.screenshot({path:path.join(__dirname,'review','html-current.png'),fullPage:true});
  await page.selectOption('#situation','ac_other');assert.equal(await page.locator('article').count(),0);assert.match(await page.locator('#model-note').innerText(),/AC-materialet mangler/);cases.push('AC / RLC / trefase → ingen generiske formelvalg');
  await page.selectOption('#seek','I');await page.locator('#givens input[value="P"]').check();await page.locator('#givens input[value="U"]').check();await page.selectOption('#situation','dc_power');assert.deepEqual(await page.locator('article').evaluateAll(els=>els.map(x=>x.dataset.entry)),['I02']);cases.push('Elektrisk P,U + stationær DC → I02');
  await page.selectOption('#seek','I');await page.locator('#givens input[value="P_mech"]').check();await page.locator('#givens input[value="U"]').check();await page.selectOption('#situation','dc_power');await page.locator('#incomplete').check();await page.fill('#search','I02');assert.match(await page.locator('article .missing').innerText(),/η/);cases.push('Mekanisk P,U uden η → manglende virkningsgrad');
  await page.selectOption('#seek','R');await page.fill('#search','R04');await page.locator('#givens input[value="l"]').check();await page.locator('#givens input[value="S"]').check();await page.selectOption('#situation','conductor');assert.match(await page.locator('article .missing').innerText(),/Resistivitet/);cases.push('Lederlængde + areal → ρ mangler');
  await page.screenshot({path:path.join(__dirname,'review','html-missing.png'),fullPage:true});
  await page.locator('#givens input[value="rho"]').check();assert.equal(await page.locator('article .ready').count(),1);cases.push('ρ tilføjet → R04 fuldstændig beregningsvej');
  await page.selectOption('#seek','');await page.fill('#search','');await page.selectOption('#situation','');await page.locator('#incomplete').check();
  await page.selectOption('#seek','C');await page.selectOption('#situation','plate_capacitor');
  await page.locator('#givens input[value="Q"]').check();await page.locator('#givens input[value="U"]').check();
  await page.locator('#incomplete').uncheck();
  assert(await page.locator('article[data-entry="C05"]').count()===1);cases.push('Q,U + pladekondensator → kapacitans C05');
  await page.selectOption('#seek','t');await page.selectOption('#situation','rc_discharge');
  for(const key of ['u0','targetU','R','C'])await page.locator(`#givens input[value="${key}"]`).check();
  assert(await page.locator('article[data-entry="C27"]').count()===1);cases.push('u0,um,R,C + lukket afladevej → tid C27');
  await page.selectOption('#situation','ac_other');assert.equal(await page.locator('article').count(),0);cases.push('AC-reaktans forbliver udækket');
  await page.selectOption('#seek','');await page.fill('#search','');await page.selectOption('#situation','');await page.locator('#incomplete').check();
  const ids=await page.evaluate(()=>db.entries.map(e=>e.id));for(const id of ids){await page.fill('#search',id);assert.equal(await page.locator(`article[data-entry="${id}"]`).count(),1,id);}
  const formulaRoutes=await page.evaluate(()=>db.entries.filter(e=>!matchEntries(e.lookup.seek_key,e.lookup.given_sets[0],e.lookup.situations[0],e.id,false).some(r=>r.entry.id===e.id)).map(e=>e.id));assert.deepEqual(formulaRoutes,[]);
  await current();await page.fill('#search','');assert.equal(await page.locator('article[data-entry="I01"]').count(),1);
  assert.deepEqual(errors,[]);assert.deepEqual(network,[]);assert(await page.locator('article img').evaluateAll(imgs=>imgs.every(i=>i.complete&&i.naturalWidth>0)));
  const result={html_sha256:require('crypto').createHash('sha256').update(fs.readFileSync(path.join(__dirname,'exports','EL-cheatsheet-BM4-opslag.html'))).digest('hex'),browser:await browser.version(),method:'Real Chromium on file:// with offline browser context',cases,all_codes_found:ids.length,all_structured_routes_found:ids.length,errors,external_requests:network};
  fs.writeFileSync(path.join(__dirname,'review','html-tests.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
