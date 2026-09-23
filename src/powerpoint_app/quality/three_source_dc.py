"""Exact topology from the user-supplied BM4 exam diagram, not a general circuit solver.

Reference C is 0 V. E1 raises L above C, E2 raises B above C, and E3 raises
D above the end of R3. Currents are oriented L->A, A->C, A->D, D->C, B->D.
"""
from dataclasses import dataclass

from powerpoint_app.domain.models import ThreeSourceCircuitElement


@dataclass(frozen=True)
class ThreeSourceSolution:
    va: float
    vd: float
    vab: float
    currents: tuple[float, float, float, float, float]
    resistor_powers: tuple[float, float, float, float, float]
    total_power: float
    source_power: float


def solve_three_source_dc(circuit: ThreeSourceCircuitElement) -> ThreeSourceSolution:
    e1, e2, e3 = circuit.sources
    r1, r2, r3, r4, r5 = circuit.resistances
    # KCL at A and the supernode around E3. This avoids guessing mesh directions.
    aa = 1/r1 + 1/r2 + 1/r3
    ad = -1/r3
    dd = 1/r3 + 1/r4 + 1/r5
    first = e1/r1 - e3/r3
    second = e3/r3 + e2/r5
    det = aa*dd - ad*ad
    va = (first*dd - ad*second)/det
    vd = (aa*second - ad*first)/det
    currents = ((e1-va)/r1, va/r2, (va-vd+e3)/r3, vd/r4, (e2-vd)/r5)
    powers = tuple(i*i*r for i, r in zip(currents, circuit.resistances))
    return ThreeSourceSolution(va, vd, va-e2, currents, powers, sum(powers),
                               e1*currents[0] + e2*currents[4] + e3*currents[2])


def circuit_quantities(circuit: ThreeSourceCircuitElement) -> dict[str, tuple[float, str]]:
    """Names that a calculation check can bind to the editable diagram."""
    solution = solve_three_source_dc(circuit)
    values = {f"E{i}": (e, "V") for i, e in enumerate(circuit.sources, 1)}
    values.update({f"R{i}": (r, "ohm") for i, r in enumerate(circuit.resistances, 1)})
    values.update({"VA": (solution.va, "V"), "VD": (solution.vd, "V"),
                   "VB": (circuit.sources[1], "V"), "VL": (circuit.sources[0], "V"),
                   "UAB": (solution.vab, "V"), "PTOTAL": (solution.total_power, "W")})
    values.update({f"I{i}": (value, "A") for i, value in enumerate(solution.currents, 1)})
    values.update({f"P{i}": (value, "W") for i, value in enumerate(solution.resistor_powers, 1)})
    return values
