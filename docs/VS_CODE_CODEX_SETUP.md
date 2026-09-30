# VS Code and Codex setup

**Change log — 2026-09-30.** Active development runs in Windows VS Code 1.139.1 connected to WSL2 Ubuntu 24.04.3; the remote extension host and integrated shell run in WSL. Codex CLI 0.155.0-alpha.16.3 is supplied by the WSL OpenAI extension and reads `/home/grumsky/.codex/config.toml`.

Created a curated Windows VS Code profile `Thore` (profile ID `78eb88ee`) with Codex, WSL, Python, Jupyter, GitHub, Markdown, CSV, TOML, Tailwind, and ESLint support. VS Code's CLI did not register the requested em-dash label `Thore — udvikling`; rename the profile in the Profiles editor if that exact display name is needed. The original default profile and its installed extensions remain installed. The profile's Codex extension is 26.917.62051; its bundled WSL CLI still reports `0.155.0-alpha.16.3`. Profile settings disable format-on-save and autosave and preserve existing theme customizations. VS Code has local Settings Sync data; changes are confined to the separate profile and project workspaces.

Added PPmaker debug, validation, export, and test tasks using its existing `.venv`. Added workspace flows for ETPH, the Python laboratory, Socratic Math Tutor and its private Python math engine, MATMATE, and BM4 Emergency Power Factory. The laboratory's staged settings and launch files and MMCS's existing edits were preserved. No formatter was introduced where a project has none; format-on-save stays off. PPmaker documents that native PowerPoint COM animations are not integrated.

Six personal skills live in `PPmaker/.agents/skills/` and are linked from `~/.agents/skills/`:

| Skill | Use | Source and dependencies |
|---|---|---|
| `pptx-didactic` | Didactic PowerPoint structure and review | Maintained here; PPmaker tooling when exporting |
| `formula-web-app` | Formula banks and technical formula web apps | Maintained here; project dependencies only |
| `engineering-calculations` | Traceable engineering calculations and units | Maintained here; project dependencies only |
| `codebase-recon` | Unfamiliar repos, architecture kickoff, Git history, refactor hotspots | Upstream MIT skill, locally routed; Git and standard shell tools |
| `gh-fix-ci` | GitHub Actions PR check failures and logs | Upstream Apache-2.0 helper, locally safety-edited; Python 3 and `gh` read access |
| `webapp-qa` | Local browser QA at desktop and mobile sizes | Maintained here; Python standard library, configured Playwright/browser MCP, or an already cached Playwright/Chromium fallback |

Codex discovers skills from `~/.agents/skills` and repository `.agents/skills`, loading metadata first and `SKILL.md` when selected ([official skill guidance](https://learn.chatgpt.com/docs/customization/overview#skills)). Codex discovered all six skills. `codebase-recon` uses read-only Git commands and only writes an optional report when requested. `gh-fix-ci` does not depend on a separate planning skill or login/escalation workflow. `webapp-qa` starts only a server it owns and never stops a reused user server. No integrations or MCPs were added. During this verification, the Playwright MCP tool reported missing `/opt/google/chrome/chrome`; the new skill's no-install fallback used the existing cached Playwright/Chromium successfully.

Test with the bundled `quick_validate.py` for each skill; exercise `codebase-recon` with read-only Git history, `gh-fix-ci` with `--help` and `gh auth status`, and `webapp-qa` with its server helper plus desktop/mobile browser inspection.

## Verification and open issues

- PPmaker: 67 tests passed; demo plan validated; PowerPoint opened and rendered the seven-slide export. The render was visually checked. Native click animation behavior remains unverified and unsupported by PPmaker.
- Python laboratory: 34 tests passed; Jupyter 4.7.0a1 and its kernel are available.
- Socratic Math Tutor: 133 tests passed, 1 skipped; math engine 61 tests passed; typecheck and build passed. Production preview renders; its unit converter displayed 1 bar = 100,000 Pa. The dev preview is blank because strict CSP blocks the Vite React preamble/HMR. The full server also needs a local `DATABASE_URL`; no credential was read or added.
- MATMATE: typecheck and build passed. BM4: 59 tests passed. ETPH: lint, typecheck, and build passed; desktop and 390px browser layouts were inspected without a live carrier lookup.
- Existing warnings: upstream matplotlib/pyparsing deprecations in PPmaker; Express cookie deprecation in Socratic tests; large Vite chunks in Socratic/MATMATE; old Browserslist data and missing favicon in ETPH.
- Full Windows/WSL extension ID/version decisions are in the private `extension-audit.csv` beside the backup. No global extension was uninstalled; extensions not selected for `Thore` remain in the original profile.

## Open

Use the VS Code profile picker to choose **Thore**, then open `\\wsl.localhost\Ubuntu\home\grumsky\PPmaker`. In PPmaker, `Ctrl+Shift+P` → **Tasks: Run Task** shows tests, demo validation, and export; `F5` opens the UI/debug configurations. In ETPH, the default build task runs `npm run verify`.

## Restore

The private, mode-700 backup is `/home/grumsky/.local/share/codex-env-backups/2026-09-30-before-vscode-codex-setup/`. It contains prior Windows settings, Codex config, changed project configs, extension inventories, and the full audit. To restore, copy `windows/settings.json` back to `%APPDATA%\Code\User\settings.json`; restore Codex files from `wsl/`; use **Profiles: Delete Profile** for `Thore` if desired; remove the three `~/.agents/skills/` links and the added PPmaker skills; remove the added `.vscode/` files and `AGENTS.md` files documented here. Do not restore the laboratory's staged files from backup over their current versions.

Original extensions were not globally uninstalled. For the full per-extension host/version/decision ledger, see the private `extension-audit.csv` beside the backup.
