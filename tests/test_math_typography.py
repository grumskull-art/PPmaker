"""Regression checks for searchable Latin I and visible typeset equations."""
import json
from pathlib import Path

from matplotlib import rc_context
from matplotlib.mathtext import MathTextParser

from powerpoint_app.rendering.math_markup import math_blocks, math_search_text
from powerpoint_app.visuals.assets import math_latex


DB = Path('Projects/el-undervisning/cheatsheet/formula-database.json')


def test_current_is_upright_stix_latin_i_in_main_and_indexed_equations():
    source = r'I=U/R, I_1, I_k, I_{\mathrm{total}}'
    with rc_context({'mathtext.fontset': 'stix', 'font.family': 'STIXGeneral'}):
        glyphs = MathTextParser('path').parse('$' + math_latex(source) + '$', dpi=120).glyphs
    currents = [glyph for glyph in glyphs if glyph[2] == ord('I')]
    assert len(currents) == 4
    assert all(glyph[0].family_name == 'STIXGeneral' and glyph[0].style_name == 'Regular' for glyph in currents)
    assert math_latex(math_latex(source)) == math_latex(source)
    assert 'I' in math_search_text(source)
    assert '\u2160' not in math_latex(source)


def test_every_card_helper_equation_is_marked_and_math_renderable():
    entries = json.loads(DB.read_text())['entries']
    assert len(entries) >= 82
    blocks = []
    for entry in entries:
        for field in ('steps', 'conversion', 'pitfall', 'example'):
            for kind, value in math_blocks(entry[field]):
                if kind == 'text':
                    assert not any(char in value for char in '=<>'), (entry['id'], field)
                else:
                    blocks.append((entry['id'], value))
    assert len(blocks) >= 190
    with rc_context({'mathtext.fontset': 'stix', 'font.family': 'STIXGeneral'}):
        for card_id, equation in blocks:
            MathTextParser('agg').parse('$' + math_latex(equation) + '$', dpi=120)


def test_examples_use_real_fractions_and_indexed_symbols():
    entries = {entry['id']: entry for entry in json.loads(DB.read_text())['entries']}
    assert r'\dfrac{|Q|}{e}' in entries['W04']['steps']
    assert r'\dfrac{24\,\mathrm{V}}{12\,\Omega}' in entries['I01']['example']
    assert r'N\dfrac{|\Delta\Phi|}{\Delta t}' in entries['E01']['steps']
