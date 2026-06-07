# Local Demo Plan

This document outlines how Project 3 can be demonstrated locally as it matures.

Milestone 4 adds a local CLI demo using temporary sample files and deterministic
report export.

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
9. Explain that the demos create temporary local evidence, parse it into typed
   records and print deterministic ingestion and summary counts.
10. Show that the CLI can print JSON for `summary` and `timeline`, then export
    a deterministic Markdown report to a temporary local file.

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
- overwrite protection by implementation contract, with `--overwrite` available
  for explicit replacement

Future milestones should show:

- retry and failure summaries
- token or cost metadata summaries when available
- Project 2 tool evidence summaries
- a local dashboard surface only if explicitly scoped

## Current Limitations

No dashboard, UI, database, external service, scheduler or deployed AgentOps
control plane exists in Milestone 4.
