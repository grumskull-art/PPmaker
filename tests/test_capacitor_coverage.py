"""Check source backed capacitor models at their limiting values."""
import json
import math
from pathlib import Path


DB = Path('Projects/el-undervisning/cheatsheet/formula-database.json')


def test_capacitor_sources_and_scope():
    db = json.loads(DB.read_text())
    entries = {entry['id']: entry for entry in db['entries']}
    assert len([code for code in entries if code.startswith('C')]) == 40
    assert {s['id'] for s in db['source_inventory'] if s['id'] in {'EL17', 'EL18'}} == {'EL17', 'EL18'}
    assert len(next(s for s in db['source_inventory'] if s['id'] == 'EL17')['slides']) == 15
    assert len(next(s for s in db['source_inventory'] if s['id'] == 'EL18')['slides']) == 14
    assert 'Kapacitans, konstantstrøm og RC-transienter er dækket' in db['scope']
    assert 'AC-reaktans, impedans og øvrig AC er fortsat udækket' in db['scope']
    assert all(entry['source_locations'] for code, entry in entries.items() if code.startswith('C'))


def test_rc_boundaries_and_independent_examples():
    voltage = lambda t, u0=623, r=1e6, c=12e-6: u0 * math.exp(-t / (r * c))
    tau = 1e6 * 12e-6
    assert tau == 12  # Ω·F = s
    assert voltage(0) == 623
    assert math.isclose(voltage(tau) / voltage(0), math.exp(-1))
    assert math.isclose(voltage(5 * tau) / voltage(0), math.exp(-5))
    assert math.isclose(math.exp(-5), 0.0067, abs_tol=0.00005)
    assert math.isclose(voltage(10), 270.7546838999097, abs_tol=1e-8)
    assert math.isclose(-tau * math.log(50 / 623), 30.270282160311687, abs_tol=1e-8)
    assert math.isclose(-35 / (12e-6 * math.log(50 / 623)), 1.1562495458297906e6, abs_tol=1e-4)


def test_general_rc_charge_and_energy_equivalence():
    supply, start, r, c = 24, 4, 2e3, 10e-6
    charge = lambda t: supply + (start - supply) * math.exp(-t / (r * c))
    current = lambda t: (supply - start) / r * math.exp(-t / (r * c))
    assert charge(0) == start and current(0) == (supply - start) / r
    assert math.isclose((supply - charge(r * c)) / (supply - start), math.exp(-1))
    assert math.isclose((supply - charge(5 * r * c)) / (supply - start), math.exp(-5))
    q = c * supply
    assert math.isclose(c * supply**2 / 2, q * supply / 2)
    assert math.isclose(q * supply / 2, q**2 / (2 * c))


def test_time_resistance_and_capacitance_isolations():
    supply, start, target, r, c = 24, 4, 20, 2e3, 10e-6
    log_ratio = math.log((supply - target) / (supply - start))
    t = -r * c * log_ratio
    assert math.isclose(-t / (c * log_ratio), r)
    assert math.isclose(-t / (r * log_ratio), c)
    discharge_ratio = math.log(50 / 623)
    discharge_t = -1e6 * 12e-6 * discharge_ratio
    assert math.isclose(-discharge_t / (12e-6 * discharge_ratio), 1e6)
    assert math.isclose(-discharge_t / (1e6 * discharge_ratio), 12e-6)
    assert math.isclose(c * (target - start) / 2e-3, 0.08)  # constant current


def test_electric_flux_density_requires_fixed_voltage_for_dielectric_scaling():
    epsilon0, area, gap, voltage = 8.8541878188e-12, 0.01, 1e-3, 24
    density = epsilon0 * voltage / gap
    assert math.isclose(3 * epsilon0 * voltage / gap, 3 * density)
    charge = density * area
    assert math.isclose(charge / area, density)  # fixed Q and A: D stays fixed
