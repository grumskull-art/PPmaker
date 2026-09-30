---
name: engineering-calculations
description: Analyze or implement engineering calculations, SI-unit conversions, CSV/Excel results, or scientific diagrams that need traceable assumptions and checks.
---

# Engineering calculations and diagrams

Use this workflow for electrical, thermodynamic, mechanical, and other quantitative engineering work.

## Workflow

1. Record the question, known values, source, assumptions, and applicable operating range before calculating.
2. Define the sign convention and symbols. Convert inputs to consistent SI units and check dimensions at every equation boundary.
3. Preserve intermediate values and enough precision for verification. Round only for presentation; do not imply more certainty than inputs support.
4. Check limiting cases and signs, then independently recompute a representative result. For uncertain data, show sensitivity or bounds instead of a single overconfident answer.
5. In CSV/Excel, keep units and source assumptions visible, use formulas for derived values, and make totals independently auditable. In plots, label axes, units, conditions, and data provenance.

## Validate

Run the repository's existing tests and calculation checks. Compare key values against an independent derivation or authoritative reference. Report unresolved assumptions and any failed check with the result; do not hide them in chart styling or rounding.
