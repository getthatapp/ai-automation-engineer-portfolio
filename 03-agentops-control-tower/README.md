# AgentOps Control Tower

Status: **Started / scaffold ready**

AgentOps Control Tower is a local observability and governance layer for AI
automation workflows.

This project is the third portfolio project. It is designed to observe signals
from the earlier projects without duplicating their responsibilities:

- Project 1 produces workflow artifacts such as run history, approval requests
  and generated reports.
- Project 2 provides deterministic local MCP-style tools, CLI evidence,
  guardrails and reviewer checks.
- Project 3 will aggregate and inspect those signals as a local AgentOps
  control tower.

## Planned Focus

Project 3 will focus on:

- workflow run history
- approval states
- failure records
- retry and cadence metadata
- notification status
- LLM and token usage metadata when available
- guardrail outcomes
- local auditability

## Current Milestone

Milestone 1 is scaffold and documentation only.

This scaffold does not yet implement:

- backend ingestion
- database persistence
- dashboards
- frontend UI
- external integrations
- notification providers
- deployed AgentOps services

## Local-First Boundaries

Project 3 is planned as local-first and deterministic. The initial scaffold does
not require secrets, call external APIs, mutate Project 1 artifacts or mutate
Project 2 artifacts.

## Repository Structure

```text
03-agentops-control-tower/
├── AGENTS.md
├── README.md
├── docs/
├── examples/
└── scripts/
```

## Verification

Run the scaffold checks from the repository root:

```bash
03-agentops-control-tower/scripts/run_checks.sh
bash -n 03-agentops-control-tower/scripts/*.sh
git diff --check
```

## Next Milestone

Project 3 Milestone 2: local data ingestion models.
