# Local Demo Plan

This document outlines how Project 3 can be demonstrated locally as it matures.

Milestone 1 is scaffold-only, so the current demo focuses on orientation and
boundaries.

## Scaffold Walkthrough

1. Open the root `README.md` and show Project 3 as started.
2. Open `03-agentops-control-tower/README.md` and explain the purpose:
   AgentOps Control Tower is a local observability and governance layer for AI
   automation workflows.
3. Show `docs/OBSERVABILITY_MODEL.md` to explain planned signals.
4. Show `docs/DATA_SOURCES.md` to explain how Project 1 and Project 2 will feed
   local evidence into Project 3.
5. Run `03-agentops-control-tower/scripts/run_checks.sh`.

## Future Demo Direction

Future milestones should show:

- ingesting Project 1 run-history JSONL
- listing approval states
- summarizing failure and retry records
- displaying token or cost metadata when available
- summarizing Project 2 guardrail outcomes
- producing a local audit view without external services

## Current Limitations

No ingestion, dashboard, UI, external service or deployed AgentOps control plane
exists in Milestone 1.
