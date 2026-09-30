"""Standalone, offline lookup from source-linked, topic-scoped catalogs."""
from pathlib import Path
import base64, copy, hashlib, json
from powerpoint_app.domain.models import FormulaElement
from powerpoint_app.planning.lookup import validate_catalog, validate_catalog_sources
from powerpoint_app.visuals.assets import formula_png
from powerpoint_app.rendering.theme import load_theme
from powerpoint_app.rendering.math_markup import math_blocks,markup_search_text,math_search_text
from powerpoint_app.visuals.assets import MATH_STYLE
from PIL import Image


def export_lookup_html(db, output: Path, project_root: Path, additional_catalogs=()):
    validate_catalog(db)
    project={}
    project_file=project_root/'project.json'
    if project_file.is_file():
        project=json.loads(project_file.read_text(encoding='utf-8'))
    payload={k:db[k] for k in ('entries','quantities','situations','navigation_groups','scope','constants','materials','material_reference','external_sources')}
    catalogs=[dict(payload,id='el',discipline='EL',topic='Elektroteknik',source_inventory=db.get('source_inventory',[]),notes=[])]
    catalogs.extend(copy.deepcopy(additional_catalogs))
    if len({c['id'] for c in catalogs})!=len(catalogs):
        raise ValueError('Dublerede emnekoder.')
    all_ids=[]
    for catalog in catalogs:
        validate_catalog(catalog)
        validate_catalog_sources(catalog)
        for entry in catalog['entries']:
            if not entry.get('source_locations'):
                raise ValueError('Kilde mangler: '+entry['id'])
            all_ids.append(entry['id'])
        catalog.setdefault('notes',[])
    if len(set(all_ids))!=len(all_ids):
        raise ValueError('Formelkoder skal være unikke på tværs af fag.')
    payload['catalogs']=catalogs
    payload['data_hash']=hashlib.sha256(json.dumps(catalogs,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    payload['cheatsheet_version']=project.get('cheatsheet_version') or payload['data_hash'][:12]
    payload['feedback_email']=project.get('feedback_email','')
    payload['formula_images']={};payload['math_assets']={};payload['math_style']=MATH_STYLE
    for e in (e for catalog in catalogs for e in catalog['entries']):
        asset=formula_png(FormulaElement(id=e['id'],type='formula',latex=e['latex']),project_root/'cache',load_theme(project_root/'theme.json'))
        payload['formula_images'][e['id']]='data:image/png;base64,'+base64.b64encode(asset.read_bytes()).decode()
        sources=[e['latex']]
        for field in ('steps','conversion','pitfall','example'):
            sources.extend(value for kind,value in math_blocks(e.get(field,'')) if kind=='math')
        payload.setdefault('search_text',{})[e['id']]='\n'.join(markup_search_text(e.get(f,'')) for f in ('steps','conversion','pitfall','example'))
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
<title>PPmaker · EL og TM formelopslag · BM4</title>
<style>
*{box-sizing:border-box}body{font:16px/1.45 Calibri,Arial,sans-serif;color:#25343c;background:white;margin:0}main{max-width:1200px;margin:auto;padding:26px}h1,h2{color:#075B70}h1{font-size:30px;margin:0 0 10px}h2{font-size:20px;margin:0 0 12px}h3{font-size:17px;color:#075B70}label,button{cursor:pointer}select,input,button{font:inherit}select,input[type=search]{padding:8px;border:1px solid #9aaeb4;border-radius:3px;max-width:100%;background:white;color:#25343c}.topbar{display:flex;align-items:flex-start;justify-content:space-between;gap:18px}.feedback{margin:2px 0 0;position:relative}.feedback summary,.feedback a{display:inline-block;color:#075B70;background:#f0f5f6;border:1px solid #ccd8dc;border-radius:3px;padding:8px 12px;text-decoration:none;font-weight:bold;cursor:pointer}.feedback-panel{position:absolute;right:0;z-index:2;min-width:260px;margin-top:8px;padding:12px;border:1px solid #ccd8dc;background:white;box-shadow:0 10px 28px #0002}.feedback-panel label{display:block;margin-bottom:10px}.feedback-panel select{width:100%}.feedback a{margin-top:4px}.version{margin-top:4px}.controls{display:grid;grid-template-columns:1fr 1fr;gap:18px}fieldset{border:1px solid #ccd8dc;padding:15px}legend{font-weight:bold;color:#855515}.known{display:flex;flex-wrap:wrap;gap:8px 20px}.known label{font-size:15px;display:flex;gap:6px;align-items:center}.cards{display:grid;grid-template-columns:1fr 1fr;gap:24px}article{border-top:2px solid #ccd8dc;padding:18px 0;overflow-wrap:anywhere}article p{margin:8px 0}.condition{color:#075B70}.formula{display:block;max-width:100%;max-height:150px;object-fit:contain;margin:16px auto}.missing,.pending{color:#855515}.ready{color:#286044}.note{padding:12px 0;border-top:1px solid #ccd8dc}.subtle{font-size:14px;color:#5b6970}details{margin:12px 0}pre{white-space:pre-wrap;font-size:13px}table{border-collapse:collapse;font-size:14px;width:100%;margin:12px 0}td,th{border-bottom:1px solid #ccd8dc;text-align:left;padding:8px}.links{display:flex;gap:8px;flex-wrap:wrap}.links button{color:#075B70;border:0;background:#f0f5f6;padding:8px 12px}input:focus,select:focus,button:focus,a:focus,summary:focus{outline:3px solid #286044;outline-offset:2px}@media(max-width:750px){main{padding:16px}.topbar{display:block}.feedback-panel{position:static;min-width:0}.controls,.cards{grid-template-columns:1fr}}@media print{.controls,.links,#known,#filter-options,.feedback{display:none}.cards{display:block}article{break-inside:avoid}body{font-size:11pt}.formula{max-height:100px}}
.math-line{overflow-x:auto;margin:10px 0}.math-image{display:block;max-width:none;margin:4px 0}.math-search{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}.helper h3{font-size:14px;color:#286044;margin:14px 0 4px}.helper p{margin:5px 0}@media print{.math-line{overflow:visible}}
.controls,.cards{grid-template-columns:repeat(2,minmax(0,1fr))}.controls>p,article{min-width:0}.controls>p{margin:8px 0}.controls select,.controls input[type=search]{width:100%;margin-top:5px}.context{border-top:3px solid #286044;border-bottom:1px solid #ccd8dc;padding:14px 0;margin:18px 0}.links{margin:18px 0}.links button{border-bottom:2px solid transparent}.links button[aria-pressed=true]{border-bottom-color:#286044;font-weight:bold}.choose-method{font:inherit;color:inherit;background:transparent;border:1px solid #9aaeb4;padding:7px 12px;border-radius:3px}.source{overflow-wrap:anywhere}.source span{display:block;margin:4px 0}select:disabled,input:disabled{opacity:.6;cursor:default}#known{margin:16px 0}#scope:empty,#model-note:empty{display:none}[hidden]{display:none!important}#topic-notes{border-top:1px solid #ccd8dc;padding-top:12px}.note-item{max-width:80ch;margin:18px 0}.version{font-variant-numeric:tabular-nums}@media(max-width:750px){.controls,.cards{grid-template-columns:1fr}.context{gap:4px}.topbar{display:flex;flex-wrap:wrap}h1{font-size:25px}.feedback{flex-shrink:0}.feedback-panel{max-width:100%}}@media print{.choose-method{display:none}}
.cards.single{grid-template-columns:minmax(0,1fr)}.cards.single article{max-width:80ch}
@media(prefers-color-scheme:dark){body{color:#dce8eb;background:#11181b}h1,h2,h3,.condition,.links button,.feedback summary,.feedback a{color:#6ec8dc}select,input[type=search]{background:#182328;color:#eef6f8;border-color:#526870}fieldset,td,th,article,.note,.feedback summary,.feedback a,.feedback-panel{border-color:#526870}.links button,.feedback summary,.feedback a{background:#182328}.feedback-panel{background:#11181b;box-shadow:0 10px 28px #0008}.missing,.pending,legend{color:#d6a85e}.ready,.helper h3{color:#7ccf9c}.subtle{color:#a8bbc1}.math-image{filter:brightness(2.4) saturate(.8)}}
</style><style>.selection-text{display:block;padding:8px 0;font-weight:600}.choice-help{display:block;margin-top:4px}.controls>p[hidden]{display:none}</style></head><body><main>
<header class="topbar"><div><h1>PPmaker · Formelopslag</h1><p class="subtle version" id="version"></p></div><details class="feedback"><summary id="feedback-summary">Feedback</summary><div class="feedback-panel"><label for="feedback-type" id="feedback-type-label">Type</label><select id="feedback-type"></select><a id="feedback-link" href="mailto:?subject=EL%20Cheatsheet%20feedback">Åbn mail</a><p class="subtle" id="feedback-help"></p></div></details></header>
<div class="controls context"><p id="discipline-field"><label for="discipline"><strong>Fag</strong></label><select id="discipline"></select><span id="discipline-text" class="selection-text" hidden></span></p><p id="topic-field" hidden><label for="topic"><strong>Emne</strong></label><select id="topic" hidden></select><span id="topic-text" class="selection-text" hidden></span></p></div>
<nav class="links" aria-label="Søgte størrelser" id="groups"></nav>
<div class="controls"><p id="seek-field" hidden><label for="seek"><strong>Jeg søger</strong></label><select id="seek" hidden></select><span id="seek-text" class="selection-text" hidden></span></p><p id="method-field" hidden><label for="method"><strong>Beregningsmetode</strong></label><select id="method" hidden></select><span id="method-text" class="selection-text" hidden></span></p><p id="situation-field" hidden><label for="situation"><strong id="situation-label">Fysisk situation</strong></label><select id="situation" hidden></select><span id="situation-text" class="selection-text" hidden></span></p><p><label for="search"><strong>Søg i emnet</strong></label><input id="search" type="search" disabled></p></div>
<fieldset id="known" hidden><legend>Jeg har opgivet</legend><div class="known" id="givens"></div></fieldset>
<p id="filter-options"><label><input type="checkbox" id="incomplete" checked> Vis også metoder med manglende oplysninger</label> <label id="ac-other-field" hidden><input type="checkbox" id="ac-other"> Vis øvrig AC / RLC / trefase – kilder mangler</label></p>
<p id="status" role="status" aria-live="polite"></p><p class="note" id="model-note"></p><div class="cards" id="results"></div>
<details id="topic-notes" hidden><summary>Faglige noter og kildehuller</summary><div id="notes"></div></details>
<details id="register-section" hidden><summary>Konstanter og materialer fra undervisningen</summary><div id="registers"></div></details>
<p class="note" id="scope"></p>
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
let activeGroup='',currentCatalogId='';
const states=new Map();
function activeCatalog(){return db.catalogs.find(c=>c.id===currentCatalogId);}
function state(){
 if(!states.has(currentCatalogId))states.set(currentCatalogId,{known:new Set(),seek:'',method:'',situation:'',search:'',incomplete:true,group:'',acOther:false});
 return states.get(currentCatalogId);
}
function remember(){if(currentCatalogId)Object.assign(state(),{seek:$('seek').value,method:$('method').value,situation:$('situation').value,search:$('search').value,incomplete:$('incomplete').checked,group:activeGroup,acOther:$('ac-other').checked});}
const feedbackText={da:{type:'Type',open:'Åbn mail',missing:'Modtager mangler i project.json',to:'Modtager',kinds:{bug:'Fejl',missing:'Mangel',wish:'Ønske'}},en:{type:'Type',open:'Open mail',missing:'Recipient is missing in project.json',to:'Recipient',kinds:{bug:'Error',missing:'Missing content',wish:'Wish'}}};
const feedbackKinds=['bug','missing','wish'];
function lang(){return (document.documentElement.lang||'da').toLowerCase().startsWith('en')?'en':'da';}
function selectedOptionText(id){const el=$(id);return el&&el.selectedIndex>=0?el.options[el.selectedIndex].textContent:'';}
function feedbackContext(){
 const c=activeCatalog(),articles=[...document.querySelectorAll('article[data-entry]')],group=c?.navigation_groups.find(g=>g.id===activeGroup);
 const section=articles.length===1?articles[0].querySelector('h2').textContent:group?`Sektion: ${group.label}`:$('seek').value?`Søger: ${selectedOptionText('seek')}`:'Intet opslag valgt';
 const known=[...$('givens').querySelectorAll('input:checked')].map(x=>c?.quantities[x.value]||x.value);
 return {section,topic:c?`${c.discipline} / ${c.topic}`:'Intet emne valgt',method:selectedOptionText('method'),seek:selectedOptionText('seek'),situation:selectedOptionText('situation'),known:known.join(', ')||'Ingen valgt',search:$('search').value.trim()||'Ingen'};
}
function updateFeedbackUi(){
 const t=feedbackText[lang()],current=$('feedback-type').value||'bug';
 $('feedback-summary').textContent='Feedback';$('feedback-type-label').textContent=t.type;$('feedback-link').textContent=t.open;
 $('feedback-type').innerHTML=feedbackKinds.map(k=>`<option value="${k}">${esc(t.kinds[k])}</option>`).join('');$('feedback-type').value=current;
 updateFeedbackLink();
}
function updateFeedbackLink(){
 const t=feedbackText[lang()],kind=$('feedback-type').value||'bug',recipient=(db.feedback_email||'').trim().replace(/[\s?&]/g,''),ctx=feedbackContext();
 const hosted=/^https?:/.test(location.href)?location.href:'';
 const body=[`Type: ${t.kinds[kind]} / ${feedbackText.da.kinds[kind]}`,`Version: ${db.cheatsheet_version}`,`Opslag/sektion: ${ctx.section}`,`URL: ${hosted}`,'','Beskrivelse:','','','Kontekst:',`Fag/emne: ${ctx.topic}`,`Metode: ${ctx.method}`,`Søger: ${ctx.seek}`,`Situation: ${ctx.situation}`,`Opgivet: ${ctx.known}`,`Søgning: ${ctx.search}`].join('\n');
 $('feedback-link').href=`mailto:${recipient}?subject=${encodeURIComponent('EL Cheatsheet feedback')}&body=${encodeURIComponent(body)}`;
 $('feedback-help').textContent=recipient?`${t.to}: ${recipient}`:t.missing;
}
function matchEntries(seek,known,situation,query='',includeMissing=true,group='',catalog=activeCatalog()){
 if(!catalog)return [];
 return catalog.entries.filter(e=>(!seek||e.lookup.seek_key===seek)&&(!group||e.lookup.group===group)&&(!situation||e.lookup.situations.includes(situation))&&(!query||[e.id,e.seek,e.given,e.condition,e.steps,e.conversion,e.pitfall,e.latex,db.search_text[e.id]].join(' ').toLocaleLowerCase('da').includes(query.toLocaleLowerCase('da')))).flatMap(e=>e.lookup.given_sets.map((option,index)=>{
  const missing=option.filter(k=>!known.includes(k));
  return {entry:e,method:e.id+':'+index,missing,option,complete:!missing.length,situationConfirmed:!!situation};
 })).filter(r=>includeMissing||r.complete).sort((a,b)=>a.missing.length-b.missing.length);
}
function optionHtml(value,label,extra=''){return `<option value="${esc(value)}" ${extra}>${esc(label)}</option>`;}
function syncChoice(id,items,value='',placeholder=''){
 const el=$(id),field=$(id+'-field'),text=$(id+'-text');
 el.innerHTML=items.length>1&&placeholder?optionHtml('','Vælg '+placeholder,'disabled selected'):'';
 el.innerHTML+=items.map(x=>optionHtml(x.value,x.label)).join('');
 field.hidden=!items.length;text.hidden=items.length!==1;el.hidden=items.length===1||!items.length;
 text.textContent=items.length===1?items[0].label:'';
 el.value=items.length===1?items[0].value:items.some(x=>x.value===value)?value:'';
 return el.value;
}
function scopedEntries(){
 const c=activeCatalog(),seek=$('seek').value;
 return c&&seek?c.entries.filter(e=>e.lookup.seek_key===seek&&(!activeGroup||e.lookup.group===activeGroup)):[];
}
function routesForControls(){
 return scopedEntries().flatMap(e=>e.lookup.given_sets.map((option,index)=>({entry:e,key:e.id+':'+index,option,label:e.id+' · '+e.seek+(e.lookup.given_sets.length>1?' · vej '+(index+1):'')})));
}
function seekOptions(c){return c?[...new Set([...c.entries.map(e=>e.lookup.seek_key),...Object.keys(c.unavailable_targets||{})])]:[];}
function syncMethods(routes,value){
 const el=$('method'),field=$('method-field'),text=$('method-text');
 el.innerHTML=routes.length>1?optionHtml('','Sammenlign beregningsveje')+routes.map(r=>optionHtml(r.key,r.label)).join(''):routes.map(r=>optionHtml(r.key,r.label)).join('');
 field.hidden=!routes.length;text.hidden=routes.length!==1;el.hidden=routes.length<=1;
 text.textContent=routes.length===1?routes[0].label:'';
 el.value=routes.length===1?routes[0].key:routes.some(r=>r.key===value)?value:'';
 return el.value;
}
function syncSituations(c,routes,value){
 const scenes=[...new Set(routes.flatMap(r=>r.entry.lookup.situations))];
 const items=scenes.map(s=>({value:s,label:c.situations[s]}));
 const selected=syncChoice('situation',items,value,'fysisk situation');
 $('situation-field').hidden=!items.length;
 $('situation-label').textContent=items.length===1?'Forudsætning':'Fysisk situation';
 $('situation-text').hidden=items.length!==1&&!(items.length>1&&selected);
 if(items.length===1)$('situation-text').textContent=items[0].label;
 if(items.length>1){const current=items.find(x=>x.value===selected);$('situation-text').hidden=!current;$('situation-text').textContent=current?'Forudsætning: '+current.label:'';}
 return selected;
}
function options(){
 const c=activeCatalog(),oldMethod=$('method').value,oldSituation=$('situation').value;
 $('ac-other-field').hidden=!c||c.discipline!=='EL'||!$('seek').value;
 if($('ac-other-field').hidden)$('ac-other').checked=false;
 const base=routesForControls(),methodRoutes=$('ac-other').checked?[]:base;
 const method=syncMethods(methodRoutes,oldMethod),chosen=methodRoutes.find(r=>r.key===method);
 syncSituations(c,chosen?[chosen]:base,oldSituation);
 render();
}
function sourceText(ref,c=activeCatalog()){
 const [id,pages]=ref.split(':'),source=c?.source_inventory?.find(s=>s.id===id);
 return source?`${(source.original_file||source.file).split('/').pop()} · ${source.unit||'slide'} ${pages}`:ref;
}
function sources(refs){return `<p class="subtle source"><strong>Kilder</strong>${refs.map(ref=>`<span>${esc(sourceText(ref))}</span>`).join('')}</p>`;}
function render(){
 const c=activeCatalog(),known=[...state().known],situation=$('situation').value,query=$('search').value.trim(),selected=$('method').value;
 const chosen=routesForControls().find(r=>r.key===selected);
 $('known').hidden=!chosen;
 $('givens').innerHTML=chosen?chosen.option.map(k=>`<label><input type="checkbox" value="${esc(k)}" ${state().known.has(k)?'checked':''}> ${esc(c.quantities[k])}</label>`).join(''):'';
 const started=c&&($('seek').value||query),found=started&&!$('ac-other').checked?matchEntries($('seek').value,known,situation,query,$('incomplete').checked,activeGroup).filter(r=>!selected||r.method===selected):[];
 const gap=c?.unavailable_targets?.[$('seek').value];
 $('results').classList.toggle('single',found.length===1);
 $('status').textContent=!c?'Vælg fag og emne.':!started?'Vælg en søgt størrelse, eller søg i '+c.topic+'.':`${found.length} ${found.length===1?'beregningsvej':'beregningsveje'} · ${found.filter(r=>r.complete).length} med de nødvendige størrelser · ${c.topic}`;
 const missing=chosen?.option.filter(k=>!state().known.has(k))||[];
 const missingInCompare=!$('incomplete').checked&&!selected?[...new Set(matchEntries($('seek').value,known,situation,query,true,activeGroup).flatMap(r=>r.missing))]:[];
 $('model-note').textContent=$('ac-other').checked?'AC-materialet mangler. Afklar kurveform, RMS, effektfaktor og aktiv/tilsyneladende effekt. DC-formlen I=P/U vælges ikke her.':gap||(started&&!found.length&&chosen&&missing.length?'Valgt metode mangler oplysninger: '+missing.map(k=>c.quantities[k]).join(', '):started&&!found.length&&missingInCompare.length?'Beregningsvejene mangler oplyste størrelser: '+missingInCompare.map(k=>c.quantities[k]).join(', ')+'. Slå visning af manglende oplysninger til for at se kravene.':started&&!found.length?'Ingen beregningsvej matcher de valgte filtre. Kontrollér emne, søgt størrelse, situation og filtre.':found.length?'Mulige beregningsveje. Kontrollér procesbetingelser, fortegn og enheder.':'');
 $('results').innerHTML=found.map(({entry:e,method,missing,option,situationConfirmed})=>`<article data-entry="${esc(e.id)}" data-method="${esc(method)}"><h2>${esc(e.id+' · '+e.seek)}</h2><p class="condition"><strong>Gælder:</strong> ${esc(e.condition)}</p><p><strong>Denne metode kræver:</strong> ${option.map(k=>esc(c.quantities[k])).join(', ')}</p>${mathImage(e.latex,26)}<p class="${missing.length?'missing':situationConfirmed?'ready':'pending'}">${missing.length?'Mangler: '+missing.map(k=>esc(c.quantities[k])).join(', '):situationConfirmed?'Størrelserne er oplyst; kontrollér stadig betingelserne.':'Størrelserne er oplyst; fysisk situation skal afklares.'}</p>${selected===method?'':`<button class="choose-method" type="button" data-method="${esc(method)}" data-seek="${esc(e.lookup.seek_key)}">Vælg denne metode</button>`}${richField('Trin',e.steps)}${richField('Omregn',e.conversion)}${richField('Pas på',e.pitfall)}${richField('Eksempel',e.example)}${sources(e.source_locations)}${e.page?`<p class="subtle">EL PowerPoint · side ${e.page}</p>`:''}<details><summary>Formlens LaTeX</summary><pre>${esc(e.latex)}</pre></details></article>`).join('')||(started&&!gap?'<p>Ingen kildeunderbygget beregningsvej matcher de valgte filtre.</p>':'');
 const notes=(c?.notes||[]).filter(n=>!query||[n.title,n.text].join(' ').toLocaleLowerCase('da').includes(query.toLocaleLowerCase('da')));
 $('topic-notes').hidden=!notes.length;
 $('notes').innerHTML=notes.map(n=>`<section class="note-item"><h3>${esc(n.title)}</h3><p>${esc(n.text)}</p>${sources(n.source_locations)}</section>`).join('');
 if(query&&notes.length)$('topic-notes').open=true;
 $('groups').querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.group===activeGroup)));
 remember();updateFeedbackLink();
}
function activateTopic(){
 remember();currentCatalogId=$('topic').value;
 const c=activeCatalog(),s=state(),keys=seekOptions(c);
 syncChoice('seek',keys.map(k=>({value:k,label:c.quantities[k]})),s.seek,'søgt størrelse');
 $('search').disabled=!c;$('search').value=s.search;$('incomplete').checked=s.incomplete;$('ac-other').checked=s.acOther;activeGroup=s.group;
 $('groups').innerHTML=c?c.navigation_groups.map(g=>`<button type="button" data-group="${esc(g.id)}">${esc(g.label)}</button>`).join('')+'<button type="button" data-group="">Alle i emnet</button>':'';
 $('groups').hidden=!c||!c.navigation_groups.length;
 $('scope').textContent=c?.scope||'';
 $('register-section').hidden=!c?.constants?.length;
 $('registers').innerHTML=c?.constants?.length?table(['Konstant / værdi','Tal','Enhed','Gyldighed / type','Kilde'],c.constants)+table(['Materiale','ρ [Ω·mm²/m]','α20 [K⁻¹]','Reference / kilde'],c.materials.map(m=>[...m,c.material_reference.temperature+'; '+c.material_reference.source])):'';
 // Seed remembered values; options() keeps only values still available here.
 $('method').innerHTML=optionHtml(s.method,s.method);$('situation').innerHTML=optionHtml(s.situation,s.situation);options();
}
$('discipline').innerHTML='';syncChoice('discipline',[...new Set(db.catalogs.map(c=>c.discipline))].map(d=>({value:d,label:d})),'','fag');
function updateTopics(value=''){
 const discipline=$('discipline').value,catalogs=db.catalogs.filter(c=>c.discipline===discipline);
 syncChoice('topic',catalogs.map(c=>({value:c.id,label:c.topic})),value,'emne');
 $('topic-field').hidden=!discipline||!catalogs.length;activateTopic();
}
$('discipline').addEventListener('change',()=>{remember();updateTopics();});
$('topic').addEventListener('change',activateTopic);
$('groups').addEventListener('click',event=>{const b=event.target.closest('button');if(b){activeGroup=b.dataset.group;options();}});
$('seek').addEventListener('change',()=>{$('method').value='';options();});
$('method').addEventListener('change',options);$('situation').addEventListener('change',options);
$('givens').addEventListener('change',event=>{const input=event.target;if(input.matches('input[type=checkbox]')){input.checked?state().known.add(input.value):state().known.delete(input.value);options();}});
$('search').addEventListener('input',options);$('incomplete').addEventListener('change',options);$('ac-other').addEventListener('change',options);
$('results').addEventListener('click',event=>{const b=event.target.closest('button[data-method]');if(b){$('seek').value=b.dataset.seek;options();$('method').value=b.dataset.method;render();$('known').scrollIntoView({block:'nearest'});}});
$('feedback-type').addEventListener('change',updateFeedbackLink);$('version').textContent=`EL / TM · BM4 · Version ${db.cheatsheet_version}`;
function table(headers,rows){return '<table><thead><tr>'+headers.map(h=>'<th>'+esc(h)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(row=>'<tr>'+row.map(v=>'<td>'+esc(v)+'</td>').join('')+'</tr>').join('')+'</tbody></table>';}
updateFeedbackUi();updateTopics();
</script></main></body></html>'''
