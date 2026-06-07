# Project 3 Milestone 4 - Local CLI Report Export

Status: `Complete`
Branch: `feature/project-3-m04-cli-report-export`

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
- 03-agentops-control-tower/docs/prompt-history/milestone-03-summaries-timeline.md

Continue Project 3: 03-agentops-control-tower.

Milestone 4: local report export and dashboard-ready CLI.

Branch:
feature/project-3-m04-cli-report-export

Prompt history requirement:
Create or update:
03-agentops-control-tower/docs/prompt-history/milestone-04-cli-report-export.md

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
- Project 3 can now ingest local artifacts and build typed summary/timeline views.
- Project 3 does not yet expose a reviewer-friendly CLI or exportable report.
- This milestone should add a local CLI and deterministic report export.
- Do not modify Project 1 code.
- Do not modify Project 2 code unless only documentation links require it.
- Do not change Project 1 or Project 2 runtime behavior.
- Do not add frontend UI.
- Do not add database.
- Do not add scheduler.
- Do not add external integrations.
- Do not call external APIs.
- Do not require secrets.

Goal:
Add a local command-line interface and deterministic export layer for Project 3 so reviewers can inspect AgentOps summaries and timelines without writing Python.

Implement:

1. Add CLI module under:
   03-agentops-control-tower/src/agentops_control_tower/

Suggested file:
- cli.py

2. Expose console script in:
   03-agentops-control-tower/pyproject.toml

Suggested command:
- agentops-control-tower

3. CLI commands:
- summary
- timeline
- export-report

4. CLI input options:
Support local optional paths:
- --run-history PATH
- --approval-requests PATH
- --report PATH
- --tool-evidence PATH
- --guardrail-output PATH

These paths should map to the same sources accepted by ingest_local_agentops_sources.

5. CLI output behavior:
summary:
- prints compact JSON by default
- supports --pretty
- returns AgentOpsSummary-compatible data

timeline:
- prints compact JSON by default
- supports --pretty
- returns AgentOpsTimeline-compatible data

export-report:
- prints deterministic Markdown to stdout by default
- supports --output PATH to write report locally
- if writing to file, create parent directory if needed
- do not overwrite existing file unless --overwrite is passed
- must not mutate Project 1 or Project 2 artifacts
- report should include:
  - title
  - generated timestamp
  - input source paths
  - overall health status
  - workflow summary
  - approval summary
  - report health summary
  - tool evidence summary
  - guardrail summary
  - ingestion warnings
  - ingestion errors
  - timeline section
  - deterministic recommended actions
  - limitations / missing data

6. Add export module:
Suggested file:
- 03-agentops-control-tower/src/agentops_control_tower/reporting.py

Suggested function:
- render_agentops_markdown_report(view)

Rules:
- deterministic output
- no LLM calls
- no external APIs
- no inferred facts
- no secret exposure
- stable ordering
- clear missing-data sections

7. Exit code policy:
- CLI exits 0 when command succeeds and ingestion has no errors.
- CLI exits non-zero when ingestion errors exist.
- CLI exits non-zero for invalid paths, malformed input files or report write conflicts.
- Warnings alone should not cause non-zero exit.
- --output write conflict should return non-zero unless --overwrite is used.

8. Tests:
Add tests for:
- CLI help
- summary JSON output
- summary --pretty output
- timeline JSON output
- export-report stdout Markdown
- export-report --output writes file
- export-report refuses overwrite by default
- export-report overwrites with --overwrite
- non-zero exit for malformed JSONL
- warnings do not force non-zero exit
- report includes deterministic recommended actions
- report includes limitations / missing data
- no external APIs or LLM calls
- render_agentops_markdown_report deterministic ordering

Suggested test files:
- tests/test_cli.py
- tests/test_reporting.py

9. Scripts:
Add:
- 03-agentops-control-tower/scripts/run_cli_demo.sh

Behavior:
- local-only
- read-only except for writing to a temporary directory
- use temporary sample files
- run summary, timeline and export-report commands
- print concise demo output
- no external APIs
- no secrets
- executable
- bash with set -euo pipefail

Update:
- 03-agentops-control-tower/scripts/run_checks.sh

It should verify new files exist and run:
- pytest
- ruff
- mypy
- bash syntax checks
- git diff --check from repo root if practical

10. Documentation updates:
- 03-agentops-control-tower/README.md
- 03-agentops-control-tower/docs/ARCHITECTURE.md
- 03-agentops-control-tower/docs/ROADMAP.md
- 03-agentops-control-tower/docs/OBSERVABILITY_MODEL.md
- 03-agentops-control-tower/docs/LOCAL_DEMO_PLAN.md
- docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md
- root README.md only if useful and concise

11. Documentation should explain:
- available CLI commands
- local source path options
- JSON output for summary/timeline
- Markdown output for export-report
- report write behavior and overwrite protection
- exit code behavior
- what is not implemented yet:
  - no dashboard/UI
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
- Do not add frontend UI.
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
- bash -n 03-agentops-control-tower/scripts/*.sh
- git diff --check

Also run from 03-agentops-control-tower:
- uv run pytest
- uv run ruff check .
- uv run mypy src
- uv run agentops-control-tower --help

After implementation, summarize:
1. files created/changed
2. CLI commands added
3. report export behavior
4. exit code behavior
5. tests added
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
bash -n 03-agentops-control-tower/scripts/*.sh
git diff --check

cd 03-agentops-control-tower
uv run pytest
uv run ruff check .
uv run mypy src
uv run agentops-control-tower --help
```

## Result Summary

- Added `agentops-control-tower` CLI with `summary`, `timeline` and
  `export-report` commands.
- Added deterministic Markdown report rendering through
  `render_agentops_markdown_report(view)`.
- Added console script metadata in `pyproject.toml`.
- Added CLI and reporting tests for JSON output, pretty output, Markdown stdout,
  file output, overwrite protection, malformed JSONL exit behavior, warning-only
  exit behavior, deterministic ordering and no external API/LLM imports.
- Added executable `scripts/run_cli_demo.sh` and updated `scripts/run_checks.sh`
  to require the new milestone files.
- Updated Project 3 docs, root README and portfolio handoff with CLI commands,
  source path options, report export behavior, exit code behavior and non-goals.
- Preserved local-only deterministic behavior: no frontend UI, database,
  scheduler, external integrations, LLM calls, API calls or secrets.

## Verification Results

```text
PASS - 03-agentops-control-tower/scripts/run_checks.sh
PASS - 03-agentops-control-tower/scripts/run_ingestion_demo.sh
PASS - 03-agentops-control-tower/scripts/run_summary_demo.sh
PASS - 03-agentops-control-tower/scripts/run_cli_demo.sh
PASS - bash -n 03-agentops-control-tower/scripts/*.sh
PASS - git diff --check

PASS - uv run pytest
       48 tests passed
PASS - uv run ruff check .
       All checks passed
PASS - uv run mypy src
       Success: no issues found in 10 source files
PASS - uv run agentops-control-tower --help
       Help lists summary, timeline and export-report commands.

Note: direct script runs initially failed inside the sandbox because uv could not
open its cache under /Users/gtest/.cache/uv. The same commands were rerun with
approved escalation and passed.
```

## Commit / PR Reference

- Commit: `TBD`
- PR: `TBD`

## Notes

- The prompt was repeated in the user message; the milestone content is captured above without semantic omission.
