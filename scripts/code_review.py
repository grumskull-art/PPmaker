from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW_DIR = ROOT / ".review"
REPORT_PATH = REVIEW_DIR / "review-report.md"
SUMMARY_PATH = REVIEW_DIR / "review-summary.json"
PYTHON = sys.executable


@dataclass
class CheckResult:
    name: str
    command: list[str]
    blocking: bool
    returncode: int
    status: str
    output: str


def run_check(name: str, command: list[str], *, blocking: bool = True) -> CheckResult:
    print(f"\n=== {name} ===")
    print("$ " + " ".join(command))
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        output = "\n".join(part for part in (completed.stdout.strip(), completed.stderr.strip()) if part)
        if completed.returncode == 0:
            status = "PASS"
        elif blocking:
            status = "FAIL"
        else:
            status = "WARN"
        print(output or "(ingen output)")
        print(f"[{status}]")
        return CheckResult(name, command, blocking, completed.returncode, status, output)
    except FileNotFoundError as exc:
        output = str(exc)
        status = "FAIL" if blocking else "WARN"
        print(output)
        print(f"[{status}]")
        return CheckResult(name, command, blocking, 127, status, output)


def command_text(command: list[str]) -> str:
    return " ".join(command)


def write_report(mode: str, results: list[CheckResult]) -> None:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    blockers = [result for result in results if result.blocking and result.returncode != 0]
    warnings = [result for result in results if not result.blocking and result.returncode != 0]

    lines = [
        "# PPmaker local code review",
        "",
        f"- Tidspunkt: `{now}`",
        f"- Mode: `{mode}`",
        f"- Python: `{sys.version.split()[0]}`",
        f"- Blokerende fejl: **{len(blockers)}**",
        f"- Advarsler: **{len(warnings)}**",
        "",
        "## Resultater",
        "",
    ]

    for result in results:
        lines.extend(
            [
                f"### {result.status}: {result.name}",
                "",
                f"Blokerende: `{'ja' if result.blocking else 'nej'}`",
                "",
                "```text",
                f"$ {command_text(result.command)}",
                result.output or "(ingen output)",
                "```",
                "",
            ]
        )

    lines.extend(
        [
            "## Fortolkning",
            "",
            "- **FAIL** betyder, at noget bør rettes før ændringen betragtes som teknisk ren.",
            "- **WARN** er et fund, som kræver menneskelig vurdering. Vulture og kompleksitetsmålinger kan give falske positiver.",
            "- Rapporten er lavet lokalt. Scriptet kalder ingen AI-tjeneste og bruger ingen Codex-kvote.",
            "",
        ]
    )

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    SUMMARY_PATH.write_text(
        json.dumps(
            {
                "generated_at": now,
                "mode": mode,
                "blocking_failures": len(blockers),
                "warnings": len(warnings),
                "results": [asdict(result) for result in results],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Kør lokal code review uden Codex/API-forbrug.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--quick", action="store_true", help="Kør hurtige checks: compile, diff, tests og Ruff.")
    mode.add_argument("--full", action="store_true", help="Kør hele review-pakken (standard).")
    args = parser.parse_args()

    selected_mode = "quick" if args.quick else "full"
    results: list[CheckResult] = []

    results.append(run_check("Python compile", [PYTHON, "-m", "compileall", "-q", "src"]))
    results.append(run_check("Git whitespace check", ["git", "diff", "--check"]))
    results.append(run_check("Pytest", [PYTHON, "-m", "pytest", "-q"]))
    results.append(run_check("Ruff lint", [PYTHON, "-m", "ruff", "check", "src", "tests"]))

    if selected_mode == "full":
        results.append(
            run_check(
                "Ruff format check",
                [PYTHON, "-m", "ruff", "format", "--check", "src", "tests"],
                blocking=False,
            )
        )
        results.append(
            run_check(
                "Bandit security",
                [PYTHON, "-m", "bandit", "-q", "-r", "src", "-ll"],
            )
        )
        results.append(
            run_check(
                "Dependency audit",
                [PYTHON, "-m", "pip_audit", "-r", "requirements-lock.txt"],
            )
        )
        results.append(
            run_check(
                "Dead code candidates",
                [PYTHON, "-m", "vulture", "src", "tests", "--min-confidence", "80"],
                blocking=False,
            )
        )
        results.append(
            run_check(
                "Cyclomatic complexity",
                [PYTHON, "-m", "radon", "cc", "src", "-s", "-a"],
                blocking=False,
            )
        )

    write_report(selected_mode, results)
    failures = [result for result in results if result.blocking and result.returncode != 0]

    print(f"\nRapport: {REPORT_PATH}")
    print(f"Maskinlæsbar summary: {SUMMARY_PATH}")
    if failures:
        print(f"Review afsluttet med {len(failures)} blokerende fejl.")
        return 1

    print("Review afsluttet uden blokerende fejl.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
