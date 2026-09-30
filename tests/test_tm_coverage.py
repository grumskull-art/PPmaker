"""Scope and provenance checks for the uploaded TM material."""
import copy
import json
from pathlib import Path

import pytest
from matplotlib.mathtext import MathTextParser

from powerpoint_app.planning.lookup import validate_catalog, validate_catalog_sources
from powerpoint_app.visuals.assets import math_latex


CATALOGS = json.loads(Path('Projects/TM1/formula-database.json').read_text())['catalogs']


def test_tm_topics_have_local_quantities_and_valid_source_pages():
    assert {c['topic'] for c in CATALOGS} == {'Varmelære', 'Motorlære'}
    heat, engine = CATALOGS
    assert 'I' not in heat['quantities'] and 'I' not in engine['quantities']
    assert 'Pi' not in heat['quantities'] and 'steam_h' not in engine['quantities']
    for catalog in CATALOGS:
        validate_catalog(catalog)
        validate_catalog_sources(catalog)
        for entry in catalog['entries']:
            MathTextParser('agg').parse('$' + math_latex(entry['latex']) + '$', dpi=100)


@pytest.mark.parametrize('ref', ['MISSING:1', 'VH1:26', 'VH1:0', 'VH1:7-3'])
def test_missing_or_invalid_source_locations_are_rejected(ref):
    catalog = copy.deepcopy(CATALOGS[0])
    catalog['entries'][0]['source_locations'] = [ref]
    with pytest.raises(ValueError):
        validate_catalog_sources(catalog)


def test_source_holes_cannot_become_calculation_methods():
    heat = copy.deepcopy(CATALOGS[0])
    assert {'cn', 'steam_h'} <= heat['unavailable_targets'].keys()
    assert not any(e['lookup']['seek_key'] in {'cn', 'steam_h'} for e in heat['entries'])
    heat['entries'][0]['lookup']['seek_key'] = 'cn'
    with pytest.raises(ValueError, match='Kildehuller'):
        validate_catalog(heat)


def test_work_signs_and_engine_cycle_factors_remain_explicit():
    heat = {e['id']: e for e in CATALOGS[0]['entries']}
    engine = {e['id']: e for e in CATALOGS[1]['entries']}
    assert heat['VH08']['latex'] == r'\Delta U=Q+W'
    assert heat['VH10']['latex'] == r'W=-p\Delta V'
    assert 'på systemet positivt' in heat['VH16']['condition']
    assert 'leveret af systemet positivt' in heat['VH26']['condition']
    assert engine['MO03']['latex'].endswith(r'\frac{n}{60}')
    assert engine['MO04']['latex'].endswith(r'\frac{n}{120}')
    assert 'kg/kWh' in engine['MO13']['conversion']
    assert 'kJ/kg' in engine['MO13']['conversion']
