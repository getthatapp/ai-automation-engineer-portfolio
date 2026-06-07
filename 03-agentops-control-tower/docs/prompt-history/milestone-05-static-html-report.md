# Project 3 Milestone 5 - Static HTML AgentOps Report

Status: `Complete`
Branch: `feature/project-3-m05-static-html-report`

## Full Prompt

```text
Read the root AGENTS.md and docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md first.
Then read:
- 03-agentops-control-tower/AGENTS.md
- 03-agentops-control-tower/README.md
- 03-agentops-control-tower/docs/ARCHITECTURE.md
- 03-agentops-control-tower/docs/ROADMAP.md
- 03-agentops-control-tower/docs/OBSERVABILITY_MODEL.md
- 03-agentops-control-tower/docs/DATA_SOURCES.md
- 03-agentops-control-tower/docs/SAFETY_MODEL.md
- 03-agentops-control-tower/docs/LOCAL_DEMO_PLAN.md
- 03-agentops-control-tower/docs/prompt-history/README.md
- 03-agentops-control-tower/docs/prompt-history/TEMPLATE.md
- 03-agentops-control-tower/docs/prompt-history/milestone-04-cli-report-export.md

Continue Project 3: 03-agentops-control-tower.

Milestone 5: static HTML AgentOps report / local viewer.

Branch:
feature/project-3-m05-static-html-report

Prompt history requirement:
Create or update:
03-agentops-control-tower/docs/prompt-history/milestone-05-static-html-report.md

The prompt-history file must include:
- title,
- status,
- branch,
- this full prompt,
- expected verification,
- result summary placeholder,
- verification result placeholder,
- commit / PR placeholder,
- notes.

After implementation, update the same prompt-history file with the actual result summary and verification results.

Current state:
- Project 1 is complete and portfolio-ready.
- Project 2 is complete and portfolio-ready.
- Project 3 Milestone 1 scaffold is complete.
- Project 3 Milestone 2 added local deterministic ingestion models and parsers.
- Project 3 Milestone 3 added deterministic AgentOps summaries and timeline generation.
- Project 3 Milestone 4 added local CLI commands and deterministic Markdown report export.
- Project 3 can now expose summary/timeline JSON and Markdown report output from the CLI.
- Project 3 does not yet have a visual static report or local viewer artifact.
- This milestone should add deterministic static HTML report export.
- Do not modify Project 1 code.
- Do not modify Project 2 code unless only documentation links require it.
- Do not change Project 1 or Project 2 runtime behavior.
- Do not add a web server.
- Do not add frontend framework.
- Do not add database.
- Do not add scheduler.
- Do not add external integrations.
- Do not call external APIs.
- Do not require secrets.
- Do not add JavaScript unless absolutely necessary.
- Do not overclaim a deployed dashboard.

Goal:
Add a deterministic static HTML AgentOps report export so reviewers can inspect Project 3 output visually without running a web server or frontend framework.

Implement:

1. Add HTML reporting support.

Suggested file:
- 03-agentops-control-tower/src/agentops_control_tower/html_reporting.py

Suggested function:
- render_agentops_html_report(view: AgentOpsControlTowerView) -> str

Behavior:
- deterministic output
- no wall-clock time
- use parsed report timestamp if available; otherwise show "Unavailable"
- no external CSS, JS, fonts, images or CDN calls
- inline minimal CSS only
- no raw payload dumps
- no secret exposure
- escape all dynamic text with standard-library HTML escaping
- stable ordering
- clear sections

2. Static HTML report sections:

Include:
- title
- generated timestamp / source timestamp
- input source paths
- overall health status
- workflow summary
- approval summary
- report health summary
- tool evidence summary
- guardrail summary
- ingestion warnings
- ingestion errors
- timeline
- deterministic recommended actions
- limitations / missing data

3. Update CLI.

Extend existing command:
- agentops-control-tower export-report

Add option:
- --format markdown|html

Default:
- markdown

Behavior:
- --format markdown uses existing render_agentops_markdown_report
- --format html uses render_agentops_html_report
- stdout by default
- --output PATH writes local file
- create parent directory if needed
- do not overwrite existing file unless --overwrite is passed
- exit code policy remains the same:
  - 0 when command succeeds and ingestion errors are empty
  - non-zero when ingestion errors exist
  - warnings alone do not cause non-zero
  - write conflict returns non-zero unless --overwrite is used

4. Tests.

Add/update tests for:
- HTML report renderer returns deterministic output
- HTML report contains expected sections
- HTML escapes dynamic text
- HTML report does not include external scripts, external stylesheets or CDN links
- CLI export-report --format html prints HTML to stdout
- CLI export-report --format html --output writes local file
- CLI refuses overwrite for HTML output unless --overwrite is passed
- Markdown export still works
- No external API/LLM calls
- Stable repeated rendering

Suggested test file:
- 03-agentops-control-tower/tests/test_html_reporting.py

Update:
- 03-agentops-control-tower/tests/test_cli.py if needed

5. Demo script.

Add:
- 03-agentops-control-tower/scripts/run_html_report_demo.sh

Behavior:
- local-only
- read-only except writing to temporary directory
- use temporary sample files
- run:
  - uv run agentops-control-tower export-report --format html ... --output "$tmp/agentops-report.html"
- print:
  - output path
  - first heading or title
  - file size
- no external APIs
- no secrets
- executable
- bash with set -euo pipefail

6. Update run_checks.sh.

Verify:
- html_reporting.py exists
- tests/test_html_reporting.py exists
- scripts/run_html_report_demo.sh exists
- milestone-05 prompt-history file exists
- run pytest
- run ruff
- run mypy
- run bash syntax checks
- run git diff --check from repo root if practical

7. Documentation updates:
- 03-agentops-control-tower/README.md
- 03-agentops-control-tower/docs/ARCHITECTURE.md
- 03-agentops-control-tower/docs/ROADMAP.md
- 03-agentops-control-tower/docs/OBSERVABILITY_MODEL.md
- 03-agentops-control-tower/docs/LOCAL_DEMO_PLAN.md
- 03-agentops-control-tower/docs/SAFETY_MODEL.md
- docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md
- root README.md only if useful and concise

8. Documentation should explain:
- static HTML report is a local file artifact, not a hosted dashboard
- no web server is required
- no external frontend assets are loaded
- CLI supports markdown and html report formats
- overwrite behavior
- local-only / deterministic boundaries
- what is not implemented yet:
  - no hosted dashboard
  - no web server
  - no database
  - no scheduler
  - no external integrations
  - no deployed AgentOps platform

Rules:
- Keep all docs in English.
- Keep all tools local and deterministic.
- Do not mutate Project 1 files.
- Do not mutate Project 2 files.
- Do not delete generated runtime files.
- Do not add real credentials.
- Do not call external APIs.
- Do not hardcode secrets.
- Do not add frontend framework.
- Do not add database, scheduler or background service.
- Do not overclaim a deployed AgentOps platform.
- Keep scripts executable.
- Add Google-style docstrings to every new or modified Python function, method and class.
- Keep prompt history current.
- Keep tests deterministic.
- Avoid broad refactors unrelated to this milestone.

Expected verification:
Run:
- 03-agentops-control-tower/scripts/run_checks.sh
- 03-agentops-control-tower/scripts/run_ingestion_demo.sh
- 03-agentops-control-tower/scripts/run_summary_demo.sh
- 03-agentops-control-tower/scripts/run_cli_demo.sh
- 03-agentops-control-tower/scripts/run_html_report_demo.sh
- bash -n 03-agentops-control-tower/scripts/*.sh
- git diff --check

Also run from 03-agentops-control-tower:
- uv run pytest
- uv run ruff check .
- uv run mypy src
- uv run agentops-control-tower --help
- uv run agentops-control-tower export-report --help

After implementation, summarize:
1. files created/changed
2. HTML report export behavior
3. CLI format option
4. security/local-only behavior
5. tests added/updated
6. scripts updated/added
7. docs updated
8. prompt history update
9. verification results
10. recommended next milestone
```

## Expected Verification

```bash
03-agentops-control-tower/scripts/run_checks.sh
03-agentops-control-tower/scripts/run_ingestion_demo.sh
03-agentops-control-tower/scripts/run_summary_demo.sh
03-agentops-control-tower/scripts/run_cli_demo.sh
03-agentops-control-tower/scripts/run_html_report_demo.sh
bash -n 03-agentops-control-tower/scripts/*.sh
git diff --check

cd 03-agentops-control-tower
uv run pytest
uv run ruff check .
uv run mypy src
uv run agentops-control-tower --help
uv run agentops-control-tower export-report --help
```

## Result Summary

- Added deterministic static HTML report rendering through
  `render_agentops_html_report(view)`.
- Extended `agentops-control-tower export-report` with
  `--format markdown|html`; Markdown remains the default.
- Added HTML report tests for deterministic rendering, required sections,
  dynamic text escaping, no external assets/scripts and unavailable timestamp
  behavior.
- Updated CLI tests for HTML stdout, HTML file output, overwrite protection and
  no external API/LLM imports.
- Added executable `scripts/run_html_report_demo.sh`.
- Updated `scripts/run_checks.sh` to require the new HTML renderer, tests, demo
  script and prompt-history file.
- Updated Project 3 docs, root README and portfolio handoff to describe static
  HTML as a local file artifact, not a hosted dashboard.
- Preserved local-only deterministic behavior: no web server, frontend
  framework, JavaScript, external assets, database, scheduler, external
  integrations, LLM calls, API calls or secrets.

## Verification Results

```text
PASS - 03-agentops-control-tower/scripts/run_checks.sh
PASS - 03-agentops-control-tower/scripts/run_ingestion_demo.sh
PASS - 03-agentops-control-tower/scripts/run_summary_demo.sh
PASS - 03-agentops-control-tower/scripts/run_cli_demo.sh
PASS - 03-agentops-control-tower/scripts/run_html_report_demo.sh
PASS - bash -n 03-agentops-control-tower/scripts/*.sh
PASS - git diff --check

PASS - uv run pytest
       58 tests passed
PASS - uv run ruff check .
       All checks passed
PASS - uv run mypy src
       Success: no issues found in 11 source files
PASS - uv run agentops-control-tower --help
       Help lists summary, timeline and export-report commands.
PASS - uv run agentops-control-tower export-report --help
       Help lists --format {markdown,html}.

Note: shell scripts initially failed inside the sandbox because uv could not
open its cache under /Users/gtest/.cache/uv. The same commands were rerun with
approved escalation and passed.
```

## Commit / PR Reference

- Commit: `TBD`
- PR: `TBD`

## Notes

- Static HTML report export is scoped as a local file artifact, not a hosted dashboard.
- Polish after Milestone 5: demo scripts were updated to use a shared richer
  deterministic dataset with succeeded, failed and needs-approval workflow runs;
  pending, approved and rejected approvals; two Markdown reports; ready and
  not-ready tool evidence; and passed plus blocked guardrail outputs. The main
  reviewer demo remains valid and exit-zero, with malformed/error cases left to
  tests.
- Follow-up polish: added `scripts/run_reviewer_demo.sh` as the reviewer-facing
  wrapper for the richer dataset. It generates summary JSON, timeline JSON,
  Markdown and static HTML reports in a preserved temporary directory so the
  reviewer can inspect artifacts after the script exits.
- Follow-up polish: updated `scripts/run_reviewer_demo.sh` to write stable
  project-local artifacts under `exports/reviewer-demo/`, including
  `summary.json`, `timeline.json`, `agentops-report.md`,
  `agentops-report.html` and deterministic sample inputs under `input/`.
  The script now prints `open exports/reviewer-demo/agentops-report.html`, uses
  `--overwrite` for report outputs and the generated `exports/` directory is
  ignored by git.
- Follow-up polish: Markdown and HTML report renderers now display paths under
  the Project 3 root as project-relative paths, including reviewer-demo input
  files and file-backed timeline identifiers. Paths outside the project root
  remain readable and do not fail rendering.
- Follow-up verification: `uv run pytest` passed with 62 tests, `uv run ruff
  check .` passed, `uv run mypy src` passed, `run_reviewer_demo.sh` regenerated
  reports with relative source paths, `run_checks.sh` passed and `git diff
  --check` passed.
- Follow-up polish: CLI timeline JSON now formats Project 3-local file-backed
  identifiers as project-relative paths for `markdown_report`, `tool_evidence`
  and `guardrail_output` events. Internal timeline construction still preserves
  raw identifiers, while reviewer-facing `timeline.json` generated by
  `run_reviewer_demo.sh` now shows clean paths such as
  `exports/reviewer-demo/input/daily-marketing-report-review.md`.
- Follow-up verification: `uv run pytest` passed with 63 tests, `uv run ruff
  check .` passed, `uv run mypy src` passed, `run_reviewer_demo.sh` regenerated
  `exports/reviewer-demo/timeline.json` with relative file identifiers,
  `run_checks.sh` passed, `bash -n 03-agentops-control-tower/scripts/*.sh`
  passed and `git diff --check` passed.
