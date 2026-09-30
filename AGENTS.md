# PPmaker project guidance

- Use Python 3.11+ and the existing `.venv`; dependencies and the Linux test set are pinned in `requirements-lock.txt`.
- Run tests with `.venv/bin/python -m pytest -q` and validate the demo with `.venv/bin/powerpoint-app validate examples/demo_project/slide-plan.json --project examples/demo_project`.
- Export with the `powerpoint-app export` CLI; inspect rendered slides and notes before delivery.
- Do not claim native click animations are supported: this repository documents that native COM animation is not integrated. Verify any requested slideshow behavior in Windows PowerPoint.
- Preserve source documents and generated/user files; keep temporary exports outside the repository.
