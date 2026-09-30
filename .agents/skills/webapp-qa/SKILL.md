---
name: webapp-qa
description: Inspect and verify a locally running web application's rendered UI with the configured Playwright/browser tools at desktop and mobile sizes, including console, page, and relevant network failures. Use for local UI/browser QA; do not use for building formula tools or for production-site testing.
metadata:
  short-description: QA local web apps in a browser
---

# Local web app QA

Use this skill for ETPH, Socratic Math Tutor, MATMATE, and other local web apps. Diagnose before changing code. A browser failure is evidence to investigate, not permission to edit the application.

## Prepare the project

1. Read applicable `AGENTS.md` files. Inspect `package.json`, project documentation, and existing tasks to find the project's documented dev/preview command, port, and existing test, lint, typecheck, or build scripts. Before startup/navigation, inspect the relevant page/route for automatic external or server-side API calls. If production traffic might happen and cannot be safely disabled with documented local test configuration, stop and report it. Do not invent a new app command or install a browser package.
2. Choose the smallest relevant existing checks. Run them when the request asks for QA or when the change under review needs them; report exactly which checks ran and their results.
3. Prefer the configured Playwright/browser MCP. If its browser cannot start, run `node <skill-dir>/scripts/inspect_local_app.cjs --url <loopback-url>`; this fallback discovers only an already cached `@playwright/mcp`/Playwright package and installed Chromium, and fails without installing anything. It blocks non-loopback requests and records DOM, console, page, and network results at desktop and mobile sizes. Only inspect local URLs; never use production data or call production APIs.

## Start and stop safely

- Probe a documented, harmless local readiness URL first. If the app already responds, reuse it and leave its process alone. Choose a GET route with no side effects.
- If it is not running, start it through `scripts/with_server.py` with the documented command as argv, for example:
  `python <skill-dir>/scripts/with_server.py --url http://127.0.0.1:5173/ -- npm run dev -- --host 127.0.0.1`
- Run the helper in a persistent terminal session. It accepts only loopback HTTP readiness URLs, starts commands without a shell in a new process group, and remains active until stopped. Stop that exact terminal session with Ctrl-C when QA is complete; the helper terminates only the process group it created. If startup fails, it cleans up that owned group. Never use broad `pkill`, process-name kills, or port-wide cleanup.
- If the port is occupied but the readiness URL does not answer, stop and report the conflict. Do not terminate the unknown process.

## Browser inspection

1. Navigate to the local app and inspect its accessibility/DOM snapshot before interacting. Verify the expected page, visible primary content, and any requested flow.
2. Check a representative desktop viewport (usually 1440×900) and mobile viewport (usually 390×844). At each size inspect the rendered snapshot and check for clipped, overlapping, or missing content. Capture screenshots only when visual comparison helps; the fallback creates a unique directory under the OS temp directory with `--screenshots`. Remove only that exact directory after reviewing it.
3. Collect console errors, page errors, and failed requests where the browser tools expose them. When page-error/request-failure event listeners are needed, use `browser_run_code_unsafe` only to attach and read passive listeners (`pageerror`, `console`, `requestfailed`) on a blank/new tab before navigation. Do not run application actions through that tool. If the browser cannot expose an event type, mark it unavailable rather than inferring it.
4. Inspect relevant non-static network failures and DOM/render results. A failed external request is not automatically an app defect; identify the URL and whether the app depends on it.
5. Limit interaction to harmless navigation and reversible UI controls. Do not submit forms, authenticate, upload files, purchase, delete, publish, or perform other irreversible actions.

## Report and cleanup

Report the local URL, commands/checks run, desktop and mobile observations, console/page/network errors with concrete evidence, screenshots if created, and remaining limits. Keep application changes out of scope unless the user authorized them. Stop only a server started in this session. Confirm whether the server was stopped or was a reused user process; do not stop a reused process.

## Dependencies

The server helper uses only Python's standard library. Browser QA uses the already configured Playwright/browser MCP; project checks use dependencies already declared by that project.
