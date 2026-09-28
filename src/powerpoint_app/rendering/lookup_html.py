"""Standalone, offline lookup; its only content source is the formula database."""
from pathlib import Path
import base64, hashlib, json
from powerpoint_app.domain.models import FormulaElement
from powerpoint_app.planning.lookup import validate_catalog
from powerpoint_app.visuals.assets import formula_png
from powerpoint_app.rendering.theme import load_theme
from powerpoint_app.rendering.math_markup import math_blocks,markup_search_text,math_search_text
from powerpoint_app.visuals.assets import MATH_STYLE
from PIL import Image


def export_lookup_html(db, output: Path, project_root: Path):
    validate_catalog(db)
    payload={k:db[k] for k in ('entries','quantities','situations','navigation_groups','scope','constants','materials','material_reference','external_sources')}
    payload['data_hash']=hashlib.sha256(json.dumps(db['entries'],ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    payload['formula_images']={};payload['math_assets']={};payload['math_style']=MATH_STYLE
    for e in db['entries']:
        asset=formula_png(FormulaElement(id=e['id'],type='formula',latex=e['latex']),project_root/'cache',load_theme(project_root/'theme.json'))
        payload['formula_images'][e['id']]='data:image/png;base64,'+base64.b64encode(asset.read_bytes()).decode()
        sources=[e['latex']]
        for field in ('steps','conversion','pitfall','example'):
            sources.extend(value for kind,value in math_blocks(e[field]) if kind=='math')
        payload.setdefault('search_text',{})[e['id']]='\n'.join(markup_search_text(e[f]) for f in ('steps','conversion','pitfall','example'))
        for latex in sources:
            if latex in payload['math_assets']:continue
            image=formula_png(FormulaElement(id=e['id']+'-detail',type='formula',latex=latex),project_root/'cache',load_theme(project_root/'theme.json'))
            with Image.open(image) as im:width,height=im.size
            payload['math_assets'][latex]={'src':'data:image/png;base64,'+base64.b64encode(image.read_bytes()).decode(),
                'width':width/220*96,'height':height/220*96,'search':math_search_text(latex)}
    serialized=json.dumps(payload,ensure_ascii=False).replace('<',r'\u003c')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(HTML.replace('__DATABASE__',serialized),encoding='utf-8')
    return output


HTML=r'''<!doctype html>
<html lang="da"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>EL · Find den rigtige formel · BM4</title>
<style>
*{box-sizing:border-box}body{font:16px/1.45 Calibri,Arial,sans-serif;color:#25343c;background:white;margin:0}main{max-width:1200px;margin:auto;padding:26px}h1,h2{color:#075B70}h1{font-size:30px}h2{font-size:20px;margin:0 0 12px}h3{font-size:17px;color:#075B70}label,button{cursor:pointer}select,input,button{font:inherit}select,input[type=search]{padding:8px;border:1px solid #9aaeb4;border-radius:3px;max-width:100%;background:white}.controls{display:grid;grid-template-columns:1fr 1fr;gap:18px}fieldset{border:1px solid #ccd8dc;padding:15px}legend{font-weight:bold;color:#855515}.known{display:flex;flex-wrap:wrap;gap:8px 20px}.known label{font-size:15px;display:flex;gap:6px;align-items:center}.cards{display:grid;grid-template-columns:1fr 1fr;gap:24px}article{border-top:2px solid #ccd8dc;padding:18px 0;overflow-wrap:anywhere}article p{margin:8px 0}.condition{color:#075B70}.formula{display:block;max-width:100%;max-height:150px;object-fit:contain;margin:16px auto}.missing,.pending{color:#855515}.ready{color:#286044}.note{padding:12px 0;border-top:1px solid #ccd8dc}.subtle{font-size:14px;color:#5b6970}details{margin:12px 0}pre{white-space:pre-wrap;font-size:13px}table{border-collapse:collapse;font-size:14px;width:100%;margin:12px 0}td,th{border-bottom:1px solid #ccd8dc;text-align:left;padding:8px}.links{display:flex;gap:8px;flex-wrap:wrap}.links button{color:#075B70;border:0;background:#f0f5f6;padding:8px 12px}input:focus,select:focus,button:focus{outline:3px solid #286044;outline-offset:2px}@media(max-width:750px){main{padding:16px}.controls,.cards{grid-template-columns:1fr}}@media print{.controls,.links,#known,#filter-options{display:none}.cards{display:block}article{break-inside:avoid}body{font-size:11pt}.formula{max-height:100px}}
.math-line{overflow-x:auto;margin:10px 0}.math-image{display:block;max-width:none;margin:4px 0}.math-search{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}.helper h3{font-size:14px;color:#286044;margin:14px 0 4px}.helper p{margin:5px 0}@media print{.math-line{overflow:visible}}
</style></head><body><main>
<h1>EL · Find den rigtige formel</h1><p>Vælg hvad du søger, hvad du har, og hvilken fysisk situation der gælder. Enheder alene afgør ikke formelvalget.</p>
<p class="subtle">I[A] angiver strømmens talværdi i ampere; I[mA] angiver talværdien i milliampere.</p>
<nav class="links" aria-label="Søgte størrelser" id="groups"></nav>
<div class="controls"><p><label for="seek"><strong>Jeg søger:</strong></label><br><select id="seek"></select></p><p><label for="situation"><strong>Fysisk situation:</strong></label><br><select id="situation"></select></p></div>
<fieldset id="known"><legend>Jeg har opgivet</legend><div class="known" id="givens"></div></fieldset>
<p id="filter-options"><label><input type="checkbox" id="incomplete" checked> Vis også opslag med manglende oplysninger</label> · <label for="search">Søg kode eller tekst:</label> <input id="search" type="search" placeholder="fx I01 eller temperatur"></p>
<p id="status" role="status" aria-live="polite"></p><p class="note" id="model-note"></p><div class="cards" id="results"></div>
<details><summary>Konstanter og materialer fra undervisningen</summary><div id="registers"></div></details>
<p class="note" id="scope"></p><p class="subtle">Virker som én lokal HTML-fil uden internet. Indhold, betingelser og sidetal kommer fra samme formeldatabase som PowerPoint. Dette er formelvalg; der beregnes ikke automatisk med indtastede tal.</p>
<script id="database" type="application/json">__DATABASE__</script><script>
const db=JSON.parse(document.getElementById('database').textContent);
function mathImage(latex,size=18){
 const a=db.math_assets[latex];
 return `<div class="math-line"><span class="math-search">${esc(a.search)}</span><img class="math-image" src="${a.src}" alt="${esc(a.search)}" data-latex="${esc(latex)}" style="width:${a.width*size/25}px;height:${a.height*size/25}px"></div>`;
}
function richField(label,source){
 if(!source)return '';
 return `<section class="helper"><h3>${esc(label)}</h3>`+source.split('$').map((value,i)=>!value.trim()?'':i%2?mathImage(value.trim()):`<p>${esc(value.trim()).replaceAll('\n','<br>')}</p>`).join('')+'</section>';
}

const $=id=>document.getElementById(id),esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let activeGroup='';
function matchEntries(seek,known,situation,query='',includeMissing=true,group=''){
return db.entries.filter(e=>(!seek||e.lookup.seek_key===seek)&&(!group||e.lookup.group===group)&&(!situation||e.lookup.situations.includes(situation))&&(!query||[e.id,e.seek,e.given,e.condition,e.steps,e.conversion,e.pitfall,e.latex,db.search_text[e.id]].join(' ').toLocaleLowerCase('da').includes(query.toLocaleLowerCase('da')))).map(e=>{
 const options=e.lookup.given_sets.map(option=>({option,missing:option.filter(k=>!known.includes(k)),overlap:option.filter(k=>known.includes(k)).length})).sort((a,b)=>a.missing.length-b.missing.length||b.overlap-a.overlap);
 return {entry:e,missing:options[0].missing,option:options[0].option,complete:!options[0].missing.length,situationConfirmed:!!situation};
}).filter(r=>includeMissing||r.complete).sort((a,b)=>a.missing.length-b.missing.length);
}
function candidates(){return db.entries.filter(e=>(!$('seek').value||e.lookup.seek_key===$('seek').value)&&(!activeGroup||e.lookup.group===activeGroup));}
function options(){
 const candidatesList=candidates(),known=[...new Set(candidatesList.flatMap(e=>e.lookup.given_sets.flat()))];
 $('givens').innerHTML=known.map(k=>`<label><input type="checkbox" value="${esc(k)}"> ${esc(db.quantities[k])}</label>`).join('');
 const scenes=[...new Set(candidatesList.flatMap(e=>e.lookup.situations))];
 $('situation').innerHTML='<option value="">Vælg situation – endnu ikke afklaret</option>'+scenes.map(s=>`<option value="${esc(s)}">${esc(db.situations[s])}</option>`).join('')+'<option value="ac_other">Øvrig AC / RLC / trefase – kilder mangler</option>';
 render();
}
function render(){
 const known=[...$('givens').querySelectorAll('input:checked')].map(x=>x.value),situation=$('situation').value;
 const found=matchEntries($('seek').value,known,situation,$('search').value.trim(),$('incomplete').checked,activeGroup);
 $('status').textContent=`${found.length} relevante opslag · ${found.filter(r=>r.complete).length} med alle nødvendige størrelser · ${db.entries.length} i databasen`;
 $('model-note').textContent=situation==='ac_other'?'AC-materialet mangler. Afklar bl.a. kurveform, RMS, effektfaktor og aktiv/tilsyneladende effekt. DC-formlen I=P/U vælges ikke her.':!situation?'Afklar den fysiske situation. Kortene er mulige beregningsveje; givne størrelser er ikke nok til at vælge en formel.':'Situationskategorien er valgt. Kontrollér stadig hvert korts gyldighed, polaritet og enheder.';
 $('results').innerHTML=found.map(({entry:e,missing,option,complete,situationConfirmed})=>`<article data-entry="${esc(e.id)}"><h2>${esc(e.id+' · '+e.seek)}</h2><p><strong>Har:</strong> ${esc(e.given)}</p><p class="condition"><strong>Gælder:</strong> ${esc(e.condition)}</p><p class="${missing.length?'missing':situationConfirmed?'ready':'pending'}">${missing.length?'Mangler mindst: '+missing.map(k=>esc(db.quantities[k])).join(', '):situationConfirmed?'Størrelser og situationskategori passer – kontrollér betingelserne.':'Størrelserne passer; fysisk situation skal afklares.'}</p><p class="subtle">Beregningsvej bruger: ${option.map(k=>esc(db.quantities[k])).join(', ')}</p>${mathImage(e.latex,26)}${richField('Trin',e.steps)}${richField('Omregn',e.conversion)}${richField('Pas på',e.pitfall)}${richField('Eksempel',e.example)}<p class="subtle">PowerPoint side ${e.page} · kilder: ${esc(e.source_locations.join(', '))}</p><details><summary>Formlens LaTeX</summary><pre>${esc(e.latex)}</pre></details></article>`).join('')||'<p>Ingen verificeret beregningsvej matcher valget. Se betingelser, manglende data og afgrænsning.</p>';
}
const seekKeys=[...new Set(db.entries.map(e=>e.lookup.seek_key))];
$('seek').innerHTML='<option value="">Alle størrelser</option>'+seekKeys.map(k=>`<option value="${esc(k)}">${esc(db.quantities[k])}</option>`).join('');
$('groups').innerHTML=db.navigation_groups.map(g=>`<button type="button" data-group="${esc(g.id)}">${esc(g.label)}</button>`).join('')+'<button type="button" data-group="">Alle</button>';
$('groups').addEventListener('click',event=>{const b=event.target.closest('button');if(b){activeGroup=b.dataset.group;$('seek').value='';$('search').value='';options();}});
$('seek').addEventListener('change',()=>{activeGroup='';options();});$('situation').addEventListener('change',render);$('givens').addEventListener('change',render);$('search').addEventListener('input',render);$('incomplete').addEventListener('change',render);
$('scope').textContent=db.scope+' AC/RLC, fasorer, resonans, transformerforhold og trefase er ikke tilføjet som verificeret pensum.';
function table(headers,rows){return '<table><thead><tr>'+headers.map(h=>'<th>'+esc(h)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(row=>'<tr>'+row.map(v=>'<td>'+esc(v)+'</td>').join('')+'</tr>').join('')+'</tbody></table>';}
$('registers').innerHTML=table(['Konstant / værdi','Tal','Enhed','Gyldighed / type','Kilde'],db.constants)+table(['Materiale','ρ [Ω·mm²/m]','α20 [K⁻¹]','Reference / kilde'],db.materials.map(m=>[...m,db.material_reference.temperature+'; '+db.material_reference.source]));
options();
</script></main></body></html>'''
