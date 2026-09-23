from __future__ import annotations

import sys
from pathlib import Path

from powerpoint_app.domain.models import SlidePlan
from powerpoint_app.office.com import _add_animations_direct


def main() -> None:
    output, plan_file = Path(sys.argv[1]), Path(sys.argv[2])
    plan = SlidePlan.model_validate_json(plan_file.read_text(encoding="utf-8"))
    _add_animations_direct(output, plan)


if __name__ == "__main__": main()
