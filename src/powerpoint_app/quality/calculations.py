"""Bounded arithmetic and SI dimension checks. No eval, symbolic algebra or code execution."""
import ast
import math
from dataclasses import dataclass

from powerpoint_app.domain.teaching import CalculationCheck

# Dimensions: mass, length, time, current. Temperature/affine units are unsupported.
UNITS = {
    "1": (1., (0, 0, 0, 0)), "kg": (1., (1, 0, 0, 0)), "g": (.001, (1, 0, 0, 0)),
    "m": (1., (0, 1, 0, 0)), "s": (1., (0, 0, 1, 0)), "min": (60., (0, 0, 1, 0)),
    "h": (3600., (0, 0, 1, 0)), "A": (1., (0, 0, 0, 1)), "mA": (.001, (0, 0, 0, 1)),
    "V": (1., (1, 2, -3, -1)), "kV": (1000., (1, 2, -3, -1)),
    "ohm": (1., (1, 2, -3, -2)), "Ω": (1., (1, 2, -3, -2)), "kohm": (1000., (1, 2, -3, -2)),
    "W": (1., (1, 2, -3, 0)), "kW": (1000., (1, 2, -3, 0)),
    "J": (1., (1, 2, -2, 0)), "kJ": (1000., (1, 2, -2, 0)),
    "N": (1., (1, 1, -2, 0)), "Pa": (1., (1, -1, -2, 0)), "bar": (100000., (1, -1, -2, 0)),
    "Hz": (1., (0, 0, -1, 0)), "m2": (1., (0, 2, 0, 0)), "m3": (1., (0, 3, 0, 0)),
}


@dataclass(frozen=True)
class CheckResult:
    status: str  # passed, failed or unsupported
    message: str


class Unsupported(ValueError):
    pass


def verify_calculation(check: CalculationCheck) -> CheckResult:
    def quantity(q):
        if q.unit not in UNITS:
            raise Unsupported(f"Enheden {q.unit!r} understøttes ikke.")
        scale, dimension = UNITS[q.unit]
        return q.value * scale, dimension

    def visit(node):
        if isinstance(node, ast.Name) and node.id in check.quantities:
            result = quantity(check.quantities[node.id])
        elif isinstance(node, ast.Constant) and type(node.value) in (float, int):
            result = float(node.value), (0, 0, 0, 0)
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value, dim = visit(node.operand)
            result = (-value if isinstance(node.op, ast.USub) else value), dim
        elif isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)):
            a, da = visit(node.left); b, db = visit(node.right)
            if isinstance(node.op, (ast.Add, ast.Sub)):
                if da != db:
                    raise ValueError("Addition/subtraktion kræver samme dimensioner.")
                result = (a + b if isinstance(node.op, ast.Add) else a - b), da
            elif isinstance(node.op, ast.Mult):
                result = a * b, tuple(x+y for x, y in zip(da, db))
            elif isinstance(node.op, ast.Div):
                result = a / b, tuple(x-y for x, y in zip(da, db))
            else:
                if any(db) or not b.is_integer() or abs(b) > 6:
                    raise Unsupported("Potenser kræver en dimensionsløs heltalseksponent fra -6 til 6.")
                result = a ** int(b), tuple(x*int(b) for x in da)
        else:
            raise Unsupported("Kun kendte variable, tal og + - * / ** understøttes.")
        if not math.isfinite(result[0]) or abs(result[0]) > 1e100:
            raise Unsupported("Beregningen overskrider den numeriske grænse.")
        return result

    try:
        tree = ast.parse(check.expression, mode="eval")
        if len(list(ast.walk(tree))) > 80:
            raise Unsupported("Udtrykket er for komplekst.")
        actual, dimension = visit(tree.body)
        expected, expected_dimension = quantity(check.expected)
        if dimension != expected_dimension:
            return CheckResult("failed", "Resultatets dimension matcher ikke den angivne enhed.")
        if not math.isclose(actual, expected, rel_tol=check.relative_tolerance, abs_tol=1e-12):
            scale = UNITS[check.expected.unit][0]
            return CheckResult("failed", f"Beregnet {actual/scale:g} {check.expected.unit}, angivet {check.expected.value:g}.")
        return CheckResult("passed", "Det angivne udtryk, talresultat og enhed stemmer. Formelvalg og tekst er ikke verificeret.")
    except Unsupported as exc:
        return CheckResult("unsupported", str(exc))
    except (SyntaxError, RecursionError) as exc:
        return CheckResult("unsupported", f"Udtrykket kan ikke kontrolleres: {type(exc).__name__}.")
    except (ValueError, ArithmeticError) as exc:
        return CheckResult("failed", f"Ugyldig beregning: {exc}")
