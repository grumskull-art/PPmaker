---
name: formula-web-app
description: Build or improve a browser-based technical formula tool when equations, SI units, engineering inputs, or scientific plots shape the user experience.
---

# Formula and technical web apps

Use this workflow for HTML, CSS, and JavaScript apps that calculate or teach technical topics.

## Workflow

1. Inspect the existing framework, package scripts, lockfile, and conventions. Reuse existing math, chart, and test libraries; do not add a competing formatter.
2. State each equation with named symbols, SI units, sign convention, and valid input range. Keep display math readable and pair symbols with plain-language labels.
3. Make input, result, assumptions, and units easy to scan. Validate empty, non-finite, boundary, and physically invalid values; show actionable errors rather than plausible-looking numbers.
4. Make plots label axes, units, series, and assumptions. Preserve meaningful precision and distinguish measured inputs from derived values.
5. Keep secrets server-side and out of browser bundles, logs, and committed environment files.

## Validate

Run the project's existing lint, type-check, build, and test scripts. Start the app and inspect the actual browser UI at desktop and narrow widths. Exercise representative, boundary, and invalid inputs and compare at least one result with an independent hand calculation. If browser automation is unavailable, state that browser behavior was not verified.
