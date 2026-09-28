"""Regenerate the source-linked lookup plan through PPmaker's existing pipeline."""
from pathlib import Path
import argparse, ast, json, math
from powerpoint_app.domain.models import SlidePlan
from powerpoint_app.projects.store import save_plan
from powerpoint_app.cli import run
ROOT=Path(__file__).resolve().parent

def checked_number(expression):
    def visit(n):
        if isinstance(n,ast.Constant) and type(n.value) in (int,float):return n.value
        if isinstance(n,ast.Name) and n.id=='pi':return math.pi
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.USub,ast.UAdd)):
            return -visit(n.operand) if isinstance(n.op,ast.USub) else visit(n.operand)
        if isinstance(n,ast.BinOp):
            a,b=visit(n.left),visit(n.right)
            if isinstance(n.op,ast.Add):return a+b
            if isinstance(n.op,ast.Sub):return a-b
            if isinstance(n.op,ast.Mult):return a*b
            if isinstance(n.op,ast.Div):return a/b
            if isinstance(n.op,ast.Pow):return a**b
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='sqrt' and len(n.args)==1 and not n.keywords:return math.sqrt(visit(n.args[0]))
        raise ValueError('Unsupported check expression')
    return visit(ast.parse(expression,mode='eval').body)

def build():
    db=json.loads((ROOT/'formula-database.json').read_text());entries=db['entries'];slides=[]
    from powerpoint_app.planning.lookup import index_sections, bind_lookup_navigation
    sections=index_sections(db)
    sources=[{'id':s['id'],'file':'sources/9b17789238de-source-text.md','locator':s['file']} for s in db['source_inventory']]
    sources += [{'id':id,'file':'sources/verified-formulas.md','locator':url} for id,url in db['external_sources'].items()]
    def slide(id,title,layout,elements,notes):
        slides.append(dict(id=id,title=title,layout=layout,elements=elements,speaker_notes=notes))
    def txt(id,value,refs=[]):return dict(id=id,type='text',text=value,source_ids=refs)
    def formula(id,value,refs=[]):return dict(id=id,type='formula',latex=value,source_ids=refs)
    def table(id,headers,rows,refs=[]):return dict(id=id,type='table',headers=headers,rows=rows,source_ids=refs)
    slide('lookup-start','EL · find den rigtige formel','lookup_start',[
        txt('start-guide','Vælg en søgt størrelse. I indekset vælger du både givne oplysninger og fysisk situation.'),
        txt('start-scope','DC, ledere, energi og felter er kildebaserede. Flere AC-emner mangler undervisningskilder.')],
        'Genveje og sidetal beregnes ud fra slideplanens id’er og samme formeldatabase som HTML-opslaget.')
    for section in sections:
        chunk=section['entries'];sid=section['id'];group=section['group']
        rows=[[e['id']+' · '+e['seek'],e['given'],e['condition'],e['latex'],'—'] for e in chunk]
        slide(sid,'Find en beregningsvej · '+group['label']+' · '+sid.rsplit('-',1)[-1],'lookup_table',[
            table(sid+'-table',['Søger','Har opgivet','Situation / betingelse','Formel','Side'],rows),
            txt(sid+'-tip','Klik på en række for at åbne formelkortet. Vælg oplysninger og fysisk model. Knudepunktseksempel: side {nodal_page}.')],
            'Hele indeksrækken er et internt link. Målet er opslagets slide-id; sidetallet beregnes efter opbygning af den komplette plan.')
    card_chunks=[]
    for group in db['navigation_groups']:
        group_entries=[e for e in entries if e['lookup']['group']==group['id']]
        card_chunks.extend((group,group_entries[i:i+2]) for i in range(0,len(group_entries),2))
    for group,chunk in card_chunks:
        elements=[]
        for e in chunk:
            refs=sorted({v.split(':')[0] for v in e['source_locations']})
            header=f"{e['id']} · Søger: {e['seek']}\nHar: {e['given']}\nGælder: {e['condition']}"
            detail='TRIN  '+e['steps']+'\nENH.  '+e['conversion']+'\nPAS PÅ  '+e['pitfall']
            if e['example']:detail+='\nEKS.  '+e['example']
            detail_element=txt(e['id']+'-details',detail,refs);detail_element['math_markup']=True
            elements += [txt(e['id']+'-header',header,refs),formula(e['id']+'-formula',e['latex'],refs),detail_element]
        notes='\n'.join(e['id']+': '+', '.join(e['source_locations']) for e in chunk)+'\nNumeriske eksempler er markerede undervisningseksempler, medmindre de citerer en kildeopgave. Symboler og gyldighed er samlet i registeret.'
        slide('cards-'+chunk[0]['id'],'Opslag · '+group['label']+' · '+', '.join(e['id'] for e in chunk),'lookup_cards',elements,notes)
    slide('nodal-example','Knudepunktsmetoden · to kilder og ét referencepunkt','lookup_nodal',[
        dict(id='nodal-circuit',type='parallel_circuit',voltage=27,resistances=[1,2,8],branch_sources=[27,24,0],source_ids=['EL09']),
        txt('nodal-model','Vælg nederste knude som 0 V. Alle tre strømpile går ud af a. Skriv KCL med spændinger; kilders pluspoler er øverst.'),
        formula('nodal-kcl',r'\frac{V_a-27}{1}+\frac{V_a-24}{2}+\frac{V_a}{8}=0'),
        formula('nodal-voltage',r'V_a=\dfrac{\dfrac{27}{1}+\dfrac{24}{2}}{\dfrac{1}{1}+\dfrac{1}{2}+\dfrac{1}{8}}=24\,\mathrm{V}'),
        formula('nodal-currents',r'I_1=-3\,\mathrm{A},\quad I_2=0,\quad I_3=3\,\mathrm{A}'),
        dict(id='nodal-check',type='text',math_markup=True,text='TRIN  '+r'$(-3+0+3)\,\mathrm{A}=0\,\mathrm{A}$'+'\nPAS PÅ  Den faktiske første grenstrøm løber opad.\nEKS.  '+r'$P_{R_3}=(3\,\mathrm{A})^2\cdot8\,\Omega=72\,\mathrm{W}$ $P_{E_1}=27\,\mathrm{V}\cdot3\,\mathrm{A}=81\,\mathrm{W}$ $P_{R_1}=9\,\mathrm{W}$')],
        'Kilde EL09:4–10. Her hedder grenstrømmene I1, I2 og I3; i originalen I, I1 og I2. Alle pile er bevidst valgt ud af a, så kildegrenen får −3 A i stedet for originalens +3 A. Belastningsresistansen R i originalen kaldes her R3. Begge kildepolariteter følger originalen. Knudepunktsmetoden er den primære løsningsvej; KVL bruges til kontrol.')
    append_registers(db,slides,slide,txt,table)
    bind_lookup_navigation(slides,db)
    plan=SlidePlan.model_validate(dict(schema_version='1.1',deck=dict(title='EL · formelopslag',audience='Maskinmester BM4',duration_minutes=len(slides),page_format='a4_landscape'),sources=sources,slides=slides))
    checks=[]
    for e in entries:
        if e['example_check']:
            c=e['example_check'];actual=checked_number(c['expr']);assert math.isclose(actual,c['expected'],rel_tol=1e-10,abs_tol=1e-12),(e['id'],actual)
            checks.append({'entry':e['id'],'actual':actual,'expected':c['expected']})
    assert math.isclose((27+24/2)/(1+1/2+1/8),24)
    (ROOT/'formula-database.json').write_text(json.dumps(db,ensure_ascii=False,indent=2))
    (ROOT/'review/numeric-checks.json').write_text(json.dumps({'examples':checks,'nodal_voltage':24,'nodal_currents':[-3,0,3],'index_entries':len(entries),'pages':len(slides)},ensure_ascii=False,indent=2))
    save_plan(ROOT,plan)
    previous=set((ROOT/'exports').glob('*.pptx'))
    run(['export',str(ROOT),'--output','EL-cheatsheet-BM4-navigation.pptx','--mode','static'])
    created=set((ROOT/'exports').glob('*.pptx'))-previous
    assert len(created)==1
    generated=created.pop()
    if generated.name!='EL-cheatsheet-BM4-navigation.pptx':
        import shutil
        shutil.copyfile(generated,ROOT/'exports/EL-cheatsheet-BM4-navigation.pptx')
    from powerpoint_app.rendering.lookup_html import export_lookup_html
    export_lookup_html(db,ROOT/'exports/EL-cheatsheet-BM4-opslag.html',ROOT)
    from powerpoint_app.quality.navigation import audit_navigation
    report=audit_navigation(plan,db,ROOT/'exports/EL-cheatsheet-BM4-navigation.pptx')
    (ROOT/'review/navigation-links.json').write_text(json.dumps(report,indent=2))
    return len(slides)

def append_registers(db,slides,slide,txt,table):
    symbols=[
     ['I, i','Strøm; i(t) ved tidsvariation','A','Konventionel retning; elektroner modsat'],
     ['Q, Ne','Ladning; antal elementarladninger','C; 1','Ne er et antal, ikke en ladningsmængde'],
     ['U, Ukl','Potentialforskel; klemspænding','V','+ og − angiver refereret polaritet'],
     ['E, e, es','Kilde-EMK; induceret og selvinduktions-EMK','V','E i originalen kan også betyde felt; her Ef'],
     ['Ef','Elektrisk feltstyrke','V/m = N/C','I originalens feltkapitel bruges E'],
     ['R, ri, Rs, Rp','Resistans, indre, serie, parallel','Ω','Afhænger af komponent og temperatur'],
     ['ρ','Elektrisk resistivitet','Ω·m eller Ω·mm²/m','Ikke materialets massefylde; samme græske bogstav'],
     ['G','Konduktans for komponent/leder','S','1 S = 1/Ω; ikke ledertværsnittet S'],
     ['γ','Specifik ledningsevne','S/m eller m/(Ω·mm²)','γ = 1/ρ; også kaldet σ i andre bøger'],
     ['S, A','Ledertværsnit; felt-/kerneareal','mm² eller m²','S fra lederkapitlet; A fra magnetkapitlet'],
     ['l, s, h, a, r','Længde, strækning, højde, afstand, radius','m','l i magnetkredsen er feltvejens middellængde'],
     ['t, Δt','Tid, tidsinterval','s eller h','h i tidsenhed er time, ikke løftehøjde'],
     ['T, t, ΔT','Temperatur, reference, ændring','°C; K for ændring','Temperatur t er ikke tidsvariablen t'],
     ['αt','Resistansens temperaturkoefficient','K⁻¹ = °C⁻¹','Hører til angivet referencetemperatur'],
     ['P, Pind, Pud, Ptab','Effekt, tilført, afgivet, tab','W','Effekt er energi pr. tid'],
     ['W','Arbejde/energi, som i kilderne','J, Wh, kWh','Størrelsen W må ikke forveksles med enheden W (watt)'],
     ['η','Virkningsgrad','1 eller %','0,85 = 85 %'],
     ['m, g','Masse; tyngdeacceleration','kg; m/s²','Undervisningens g = 9,82 m/s²'],
     ['F, M','Mekanisk kraft; moment','N; N·m','N·m som moment og J som arbejde holdes adskilt'],
     ['ω, θ, n','Vinkelhastighed, vinkel, omdrejningsfrekvens','rad/s; rad; s⁻¹ eller rpm','n er aldrig rad/s; rpm kræver faktor 1/60'],
     ['Φ','Magnetisk flux','Wb','Ikke magnetisk feltstyrke H'],
     ['B','Magnetisk fluxtæthed','T = Wb/m²','T som enhed er tesla, ikke temperatur'],
     ['H','Magnetisk feltstyrke','A/m','H som enhedssymbol er henry, ikke feltstyrken'],
     ['μ, μ0, μr','Absolut, vakuum, relativ permeabilitet','H/m; H/m; 1','μr er ikke altid konstant for jern'],
     ['Fm','Magnetomotorisk kraft','A (amperevinding)','Ikke mekanisk kraft i newton'],
     ['Rm','Reluktans','A/Wb = H⁻¹','Ikke resistans i ohm'],
     ['N, L','Antal vindinger; induktans','1; H','N er også SI-enheden newton i kraftformler'],
     ['v','Hastighed','m/s','Ved bevægelsesinduktion skal retningen kendes'],
     ['ε, ε0, εr','Absolut, vakuum, relativ permittivitet','F/m; F/m; 1','Ikke den magnetiske permeabilitet μ'],
     ['Ψ','Elektrisk feltflux i kildens notation','V·m','Ikke et fysisk antal linjer; ikke Φ [Wb]'],
     ['k','Coulombkonstant i mediet','N·m²/C²','k = 1/(4πε); ikke kilo-præfikset k'],
     ['Va, Vb, Ik','Knudespændinger og grenstrøm','V; A','Relativt til samme reference; Ik følger valgt pil']]
    for i in range(0,len(symbols),8):
        slide('symbols-'+str(i//8+1),'Symbol- og enhedsregister · '+str(i//8+1),'lookup_table',[table('symbols-table-'+str(i//8+1),['Symbol','Størrelse','Enhed','Betydning / afgrænsning'],symbols[i:i+8])],'Kildenotation prioriteres. Ef og Ne tilføjes for at skelne felt fra EMK og partikelantal fra vindinger. Kilder: EL01–EL16.')
    units=[
     ['T, G, M, k','10¹², 10⁹, 10⁶, 10³','Store præfikser; k er lille'],
     ['m, µ, n, p','10⁻³, 10⁻⁶, 10⁻⁹, 10⁻¹²','milli, mikro, nano, pico'],
     ['mA → A; mV → V','÷ 1000','Omregn før kvadrering'],
     ['mm → m; cm → m','÷ 1000; ÷ 100','Længde omregnes én gang'],
     ['mm² → m²; cm² → m²','× 10⁻⁶; × 10⁻⁴','Areal: længdefaktoren kvadreres'],
     ['ρ: Ω·mm²/m → Ω·m','× 10⁻⁶','Cu: 0,0175 → 1,75·10⁻⁸'],
     ['γ: m/(Ω·mm²) → S/m','× 10⁶','Konduktivitet omregnes modsat resistivitet'],
     ['ms → s; min → s; h → s','÷ 1000; × 60; × 3600','Sekunder i SI-formler'],
     ['1 Ah; 1 Wh; 1 kWh','3600 C; 3600 J; 3,6 MJ','Ah er ladning; Wh og kWh er energi'],
     ['1 kW; 1 kJ; 1 mT; 1 mH','1000 W; 1000 J; 0,001 T; 0,001 H','W, J, T og H i SI-beregninger'],
     ['rpm → s⁻¹ → rad/s','n/60 → 2π·n/60','Rotationshastighed; ikke dokumentation for AC-pensum'],
     ['grader → radianer','θrad = θ°·π/180','45° = π/4; 360° = 2π'],
     ['ΔT [°C] → ΔT [K]','Samme talværdi','Absolut temperatur: TK = T°C + 273,15'],
     ['% → forholdstal','÷ 100','85 % = 0,85'],
     ['1 V; 1 W; 1 T','1 J/C; 1 J/s; 1 Wb/m²','Størrelse og enhedssymbol er forskellige']]
    for i in range(0,len(units),8):
        slide('units-'+str(i//8+1),'Præfikser og omregninger · '+str(i//8+1),'lookup_table',[table('units-table-'+str(i//8+1),['Fra / størrelse','Omregning','Husk'],units[i:i+8])],'SI-enheder og præfikser: BIPM SI Brochure. HK/kcal står særskilt som undervisningsafrundinger. Kildebaseret notation: EL02, EL07, EL10, EL13.')
    for i in range(0,len(db['constants']),6):
        slide('constants-'+str(i//6+1),'Konstanter og undervisningsværdier · '+str(i//6+1),'lookup_table',[table('constants-table-'+str(i//6+1),['Symbol / værdi','Tal','Enhed','Gyldighed / type','Kilde'],db['constants'][i:i+6]),txt('constants-note-'+str(i//6+1),'CODATA 2022: μ0 = 1,25663706127(20)·10⁻⁶ H/m; ε0 = 8,8541878188(14)·10⁻¹² F/m. Værdierne er målebestemte, ikke eksakte.')],'Kontrolleret mod BIPM ampere-definition og NIST CODATA 2022. Links: '+db['external_sources']['BIPM']+' ; '+db['external_sources']['NIST'])
    for i in range(0,len(db['materials']),8):
        rows=[[n,rho,alpha,'20 °C; EL07:4 / EL10:4'] for n,rho,alpha in db['materials'][i:i+8]]
        slide('materials-'+str(i//8+1),'Materialeværdier ved 20 °C · '+str(i//8+1),'lookup_table',[table('material-table-'+str(i//8+1),['Materiale','ρ [Ω·mm²/m]','α20 [K⁻¹]','Reference / kilde'],rows),txt('material-note-'+str(i//8+1),'Kildens tabelværdier, ikke universelle naturkonstanter. Renhed/legering og temperatur ændrer værdierne. Med ρ i Ω·m: gang tabellens ρ med 10⁻⁶.')],'Afskrevet fra EL07:4 og EL10:4, visuelt kontrolleret i originalerne. Tabellen er reproduceret som redigerbare celler. Pt100-standardens kurve må ikke sidestilles ukritisk med en ren platins generelle α.')
    for i in range(0,len(db['source_inventory']),8):
        rows=[]
        for s in db['source_inventory'][i:i+8]:
            families=sorted({e['id'].rstrip('0123456789') for e in db['entries'] if any(v.startswith(s['id']+':') for v in e['source_locations'])})
            rows.append([s['id'],s['title'],str(len(s['slides'])),', '.join(families)])
        slide('sources-'+str(i//8+1),'Kilder og dækningskontrol · '+str(i//8+1),'lookup_table',[table('source-table-'+str(i//8+1),['ID','Original præsentation','Slides','Opslagsfamilier'],rows)],'Alle 160 originale slides er læst som tekst og renderet i Windows PowerPoint. Billedformler er visuelt transskriberet; databasefelterne source_locations peger på konkrete slides. Originalfilernes SHA256 er bevaret i databasen. Laboratorierapporten fra Downloads underbygger praksiskonteksten, men definerer ikke et nyt pensum.')
    corrections=[
     ['EL02:6; EL15:4','Historisk ampere via kraft mellem ledere','SI baseres nu på eksakt elementarladning e; kraftformlen bevares som fysik.'],
     ['EL01:11; EL06:9','μ0 = 4π·10⁻⁷ som eksakt naturkonstant','Bevares som afrunding; efter SI-revisionen er μ0 målebestemt.'],
     ['EL02:9-10','Ohms lov gælder kun DC','U = RI gælder også øjebliksværdier for en ideal ohmsk R; ikke hele vilkårlige AC-belastninger.'],
     ['EL01:10; EL03:9','Flux som felt / antal feltlinjer','Φ [Wb], B [T], H [A/m] og Ψ [V·m] holdes adskilt. Feltlinjer er en tegne-model.'],
     ['EL06:10,13; EL11:3','Ledende materialer og Rm-enhed','Ferromagnetisme er ikke elektrisk ledningsevne. μ er H/m; Rm er A/Wb = H⁻¹.'],
     ['EL13:10','n har [rad/s]; antal omdrejninger/frekvens blandes','n er s⁻¹ eller rpm; ω er rad/s. Rotationsarbejde bruger vinkel eller et antal omdrejninger.'],
     ['EL13:17, opg. 8b','Moment fra elektrisk motor-effekt','Der mangler η eller Pmek. En ideal antagelse η = 1 skal angives; ikke bruges skjult.'],
     ['EL10:3,5,9-10','α og referencetemperatur','αt følger referencen t. α20 kan ikke ubetinget bruges med en anden reference.'],
     ['EL08:9-14','Alle knudepunkter som uafhængige ligninger','Vælg reference. Brug n−1 uafhængige KCL-ligninger; superknude ved relevant spændingskilde.']]
    slide('corrections','Faglige præciseringer i forhold til kilderne','lookup_table',[table('corrections-table',['Kilde','Problem / tvetydighed','Præcisering'],corrections)],'Korrekturer er angivet åbent. BIPM: '+db['external_sources']['BIPM']+' ; NIST: '+db['external_sources']['NIST']+'. Ingen originale præsentationer er ændret.')
    scope=[
     ['Dokumenteret','DC, ledermodstand, temperatur, energi/moment','Elektriske og magnetiske felter, induktion, selvinduktion og magnetiske kræfter.'],
     ['Beregningsvej','Knudepunktsmetoden er primær','KCL med reference/pile → ligninger → grenstrømme. KVL og effektbalance er kontroller.'],
     ['AC-omtale','Induktans nævnes som grundlag for AC','Ingen systematisk dokumentation af sinus, RMS, fase eller effektfaktor i de fundne slides.'],
     ['AC: har P og U','Oplysningerne er utilstrækkelige uden model','Afklar aktiv/tilsyneladende effekt, RMS/kurveform og effektfaktor. DC-opslag I = P/U vælges ikke alene på enheder.'],
     ['Ikke fundet','Kapacitans, reaktans, impedans, fasorer, RLC','Ingen formeldækning påstås for disse emner; kræver relevante undervisningsfiler.'],
     ['Ikke fundet','Resonans, transformerforhold, trefase','Transformerprincippet omtales, men beregningsformler/pensum er ikke dokumenteret.'],
     ['AC-skelnen','Spidsværdi/RMS; fase/linje; effektfaktor/cos φ','Kan ikke sidestilles uden kurveform, topologi og betingelser. Disse emner er ikke udfyldt generisk.'],
     ['Kilder mangler','Henviste bøger, Word-øvelser og Teams-opgaver','Deres indhold er ikke verificeret. Cheatsheetet dækker de faktiske lokale kilder, ikke hele BM4-pensum.'],
     ['Redigerbarhed','Tekst, tabeller, strøm-/kredsløbsfigur er native','Brøkformler er højopløste billeder fra LaTeX. Formeltekst og data bevares i database og slideplan.']]
    slide('scope','Afgrænsning · vælg ikke formel ud fra enheder alene','lookup_table',[table('scope-table',['Status / opslag','Fundet / givet','Afgrænsning / nødvendige oplysninger'],scope)],db['scope']+'\nDe refererede undervisningsfiler om AC, RLC, trefase samt opgavesamlingen er ikke tilgængelige i de gennemgåede lokale mapper. Der er ikke opfundet adgang eller fyldt generiske AC-kapitler ind.')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--pdf',action='store_true');args=parser.parse_args()
    pages=build();print(f'Generated {pages} A4 pages through powerpoint_app.')
    if args.pdf:
        import subprocess,shutil,time
        if not shutil.which('powershell.exe'):raise SystemExit('PowerPoint Windows bridge unavailable; PPTX generated.')
        win_temp=subprocess.check_output(['powershell.exe','-NoProfile','-NonInteractive','-Command','[IO.Path]::GetTempPath()'],text=True).strip()
        wsl_temp=subprocess.check_output(['wslpath','-u',win_temp],text=True).strip()
        work=Path(wsl_temp)/('el-cheatsheet-final-'+str(time.time_ns()));work.mkdir()
        shutil.copyfile(ROOT/'exports/EL-cheatsheet-BM4-navigation.pptx',work/'EL-cheatsheet-BM4-navigation.pptx')
        shutil.copyfile(ROOT/'export_windows.ps1',work/'export_windows.ps1')
        win=win_temp.rstrip('\\')+'\\'+work.name
        subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',win+'\\export_windows.ps1','-WorkDir',win],check=True)
        shutil.copyfile(work/'EL-cheatsheet-BM4-navigation.pdf',ROOT/'exports/EL-cheatsheet-BM4-navigation.pdf')
        preview=ROOT/'exports/navigation-preview';preview.mkdir(exist_ok=True)
        for p in (work/'preview').glob('*.png'):shutil.copyfile(p,preview/p.name)
        shutil.copyfile(work/'windows-layout.json',ROOT/'review/windows-layout.json')
        from powerpoint_app.projects import load_plan
        from powerpoint_app.quality.navigation import audit_navigation
        report=audit_navigation(load_plan(ROOT/'slide-plan.json'),json.loads((ROOT/'formula-database.json').read_text()),ROOT/'exports/EL-cheatsheet-BM4-navigation.pptx',ROOT/'exports/EL-cheatsheet-BM4-navigation.pdf')
        (ROOT/'review/navigation-links.json').write_text(json.dumps(report,indent=2))
        print('PDF and all PowerPoint-rendered pages exported.')
