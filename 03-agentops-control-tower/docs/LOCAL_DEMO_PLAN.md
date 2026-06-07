# Local Demo Plan

This document outlines how Project 3 can be demonstrated locally as it matures.

Milestone 5 adds a local static HTML report demo using temporary sample files
and deterministic report export. The demo scripts now use a richer deterministic
local dataset instead of a tiny smoke-test fixture.

## Scaffold Walkthrough

1. Open the root `README.md` and show Project 3 as started.
2. Open `03-agentops-control-tower/README.md` and explain the purpose:
   AgentOps Control Tower is a local observability and governance layer for AI
   automation workflows.
3. Show `docs/OBSERVABILITY_MODEL.md` to explain planned signals.
4. Show `docs/DATA_SOURCES.md` to explain how Project 1 and Project 2 will feed
   local evidence into Project 3.
5. Run `03-agentops-control-tower/scripts/run_checks.sh`.
6. Run `03-agentops-control-tower/scripts/run_ingestion_demo.sh`.
7. Run `03-agentops-control-tower/scripts/run_summary_demo.sh`.
8. Run `03-agentops-control-tower/scripts/run_cli_demo.sh`.
9. Run `03-agentops-control-tower/scripts/run_html_report_demo.sh`.
10. Run `03-agentops-control-tower/scripts/run_reviewer_demo.sh`.
11. Explain that the demos create temporary local evidence, parse it into typed
   records and print deterministic ingestion and summary counts.
12. Show that the CLI can print JSON for `summary` and `timeline`, then export
    a deterministic Markdown report to a temporary local file.
13. Show that the HTML demo creates a self-contained `.html` artifact that can
    be opened directly in a browser without a web server.
14. Use the reviewer demo output directory `exports/reviewer-demo/` to inspect
    generated `summary.json`, `timeline.json`, Markdown and HTML report
    artifacts after the script exits.
15. Open the stable local HTML report path:
    `open exports/reviewer-demo/agentops-report.html`.

## Future Demo Direction

Current ingestion demo shows:

- parsing run-history JSONL
- parsing approval request JSONL
- parsing a deterministic Markdown report
- parsing guardrail output text
- returning one combined local ingestion result

Current CLI demo shows:

- `agentops-control-tower summary --pretty`
- `agentops-control-tower timeline --pretty`
- `agentops-control-tower export-report --output PATH`
- `agentops-control-tower export-report --format html --output PATH`
- overwrite protection by implementation contract, with `--overwrite` available
  for explicit replacement

Current reviewer demo shows:

- a concise terminal summary for the richer deterministic dataset
- paths to generated `summary.json`, `timeline.json`, Markdown and HTML reports
- a stable project-local output directory under `exports/reviewer-demo/`
- the reviewer-friendly command `open exports/reviewer-demo/agentops-report.html`

## Rich Demo Dataset

The demo scripts generate deterministic sample files with:

- three workflow runs: one succeeded, one needs approval and one failed
- three approval requests: one pending, one approved and one rejected
- stable timestamps that produce an ordered timeline
- finding counts, critical finding counts and human-review flags
- two deterministic Markdown reports: one review-focused report and one healthy
  comparison report
- two Project 2-style tool evidence files: one ready and one not ready
- two guardrail outputs: one passed and one blocked

The main reviewer-facing commands use the review-focused report, not-ready tool
evidence and blocked guardrail output so `needs_attention` states are visible.
Project 3 currently accepts one Markdown report path, one tool evidence JSON path
and one guardrail output path per CLI invocation, so the additional comparison
files are generated and documented but not ingested in the main CLI command.

The main demo dataset avoids malformed JSON, malformed JSONL and missing
required report sections. Error cases remain covered by tests rather than by
reviewer-facing demos.

The reviewer demo writes generated artifacts under `exports/reviewer-demo/` and
may recreate only that directory. The generated export directory is ignored by
git so reviewer outputs are not committed accidentally.
Generated Markdown and HTML reports render source paths relative to the
Project 3 root when inputs are under `03-agentops-control-tower/`, keeping
reviewer artifacts free of machine-specific absolute paths.

Future milestones should show:

- retry and failure summaries
- token or cost metadata summaries when available
- Project 2 tool evidence summaries
- a hosted dashboard surface only if explicitly scoped

## Current Limitations

No hosted dashboard, web server, frontend framework, database, external service,
scheduler or deployed AgentOps control plane exists in Milestone 5.
