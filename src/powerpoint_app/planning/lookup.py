"""Derive lookup sections, page labels and navigation from IDs, never page offsets."""
import re


def validate_catalog(db):
    entries=db['entries'];ids=[e['id'] for e in entries]
    if len(set(ids))!=len(ids):raise ValueError('Dublerede formelkoder.')
    groups={g['id'] for g in db['navigation_groups']}
    for e in entries:
        m=e['lookup']
        if m['group'] not in groups or m['seek_key'] not in db['quantities']:
            raise ValueError('Ukendt opslagstype: '+e['id'])
        if not m['given_sets'] or any(not option or any(k not in db['quantities'] for k in option) for option in m['given_sets']):
            raise ValueError('Ugyldige givne størrelser: '+e['id'])
        if not m['situations'] or any(s not in db['situations'] for s in m['situations']):
            raise ValueError('Ukendt fysisk situation: '+e['id'])
    unavailable=set(db.get('unavailable_targets',{}))
    if not unavailable<=db['quantities'].keys() or unavailable&{e['lookup']['seek_key'] for e in entries}:
        raise ValueError('Kildehuller skal have egne mål uden beregningsmetoder.')


def validate_catalog_sources(db):
    sources={s['id']:s for s in db.get('source_inventory',[])}
    if len(sources)!=len(db.get('source_inventory',[])):
        raise ValueError('Dublerede kildekoder.')
    for entry in [*db['entries'],*db.get('notes',[])]:
        refs=entry.get('source_locations',[])
        if not refs:raise ValueError('Kilde mangler: '+entry.get('id',entry.get('title','')))
        for ref in refs:
            match=re.fullmatch(r'([^:]+):([0-9]+(?:-[0-9]+)?(?:,[0-9]+(?:-[0-9]+)?)*)',ref)
            if not match or match[1] not in sources:
                raise ValueError('Ukendt kildehenvisning: '+ref)
            source=sources[match[1]]
            limit=source.get('pages',len(source.get('slides',[])))
            for part in match[2].split(','):
                pages=[int(n) for n in part.split('-')]
                if not 1<=pages[0]<=pages[-1]<=limit:
                    raise ValueError('Side uden for kilden: '+ref)


def index_sections(db):
    validate_catalog(db)
    sections=[]
    for group in db['navigation_groups']:
        entries=[e for e in db['entries'] if e['lookup']['group']==group['id']]
        for i in range(0,len(entries),10):
            sections.append(dict(id=f"index-{group['id']}-{i//10+1}",group=group,entries=entries[i:i+10]))
    return sections


def bind_lookup_navigation(slides, db):
    validate_catalog(db)
    positions={s['id']:i+1 for i,s in enumerate(slides)}
    if len(positions)!=len(slides):raise ValueError('Dublerede slide-id’er.')
    home=next(s['id'] for s in slides if s['layout']=='lookup_start')
    entries={e['id']:e for e in db['entries']};targets={};indexes={};rows=[]
    def link(id,label,target,placement,**extra):
        return dict(id=id,label=label,target_slide_id=target,placement=placement,**extra)
    for slide in slides:
        slide['navigation']=[]
        for element in slide['elements']:
            if element['type']=='formula' and element['id'].endswith('-formula'):
                code=element['id'][:-8]
                if code in targets:raise ValueError('Flere formelkort for '+code)
                targets[code]=slide['id']
            if element['type']=='table' and element['headers'][0]=='Søger':
                for i,row in enumerate(element['rows']):
                    code=row[0].split(' · ')[0]
                    if code not in entries or code in indexes:raise ValueError('Ugyldigt/dubleret indeksopslag: '+code)
                    indexes[code]=slide['id'];rows.append((slide,element,i,code))
    if set(targets)!=set(entries) or set(indexes)!=set(entries):
        raise ValueError('Indeks og formelkort skal dække samme formeldatabase.')
    for slide,table,i,code in rows:
        e=entries[code];e.update(card_slide_id=targets[code],index_slide_id=indexes[code],page=positions[targets[code]])
        table['rows'][i][-1]=str(e['page'])
        slide['navigation'].append(link('entry-'+code,'Åbn '+code,targets[code],'row',table_id=table['id'],row_index=i,entry_id=code))
    group_targets={}
    for e in entries.values():group_targets.setdefault(e['lookup']['group'],indexes[e['id']])
    index_ids=list(dict.fromkeys(indexes.values()))
    for slide in slides:
        if slide['id']==home:
            for g in db['navigation_groups']:
                if g['id'] in group_targets:
                    slide['navigation'].append(link('group-'+g['id'],g['label']+'\n'+g['description'],group_targets[g['id']],'menu'))
        elif slide['layout']=='lookup_cards':
            first=slide['elements'][0]['id'].removesuffix('-header')
            slide['navigation'].append(link('back-index','Til indeks',indexes[first],'footer'))
            slide['navigation'].append(link('back-start','Til start',home,'footer'))
        elif slide['layout']=='lookup_nodal':
            slide['navigation'].append(link('back-index','Til indeks',group_targets['methods'],'footer'))
            slide['navigation'].append(link('back-start','Til start',home,'footer'))
        else:
            slide['navigation'].append(link('back-start','Til start',home,'footer'))
            if slide['id'] in index_ids and index_ids.index(slide['id'])+1<len(index_ids):
                target=index_ids[index_ids.index(slide['id'])+1]
                slide['navigation'].append(link('next-index','Næste indeks',target,'footer'))
        for element in slide['elements']:
            if element['type']=='text':
                if '{nodal_page}' in element['text']:
                    element['text']=element['text'].replace('{nodal_page}',str(positions['nodal-example']))
    return positions
