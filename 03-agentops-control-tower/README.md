# AgentOps Control Tower

Status: **Ingestion models ready**

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

Milestone 2 adds the first local deterministic ingestion layer.

Project 3 can now parse local evidence into typed records:

- Project 1 run-history JSONL
- Project 1 approval requests JSONL
- Project 1 deterministic Markdown reports
- saved Project 2 CLI JSON evidence
- saved Project 2 guardrail output text

Missing optional files are reported as warnings. Malformed files are reported as
explicit ingestion errors. Parsed payloads are sanitized with conservative
secret redaction before they are stored in internal records.

Project 3 still does not implement:

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

The Milestone 2 ingestion layer remains local-only and read-only. It does not
call LLMs, send notifications, create tasks or modify source artifacts.

## Repository Structure

```text
03-agentops-control-tower/
├── AGENTS.md
├── README.md
├── docs/
├── examples/
├── src/
├── tests/
└── scripts/
```

## Verification

Run the scaffold checks from the repository root:

```bash
03-agentops-control-tower/scripts/run_checks.sh
bash -n 03-agentops-control-tower/scripts/*.sh
git diff --check
```

Run the local ingestion demo:

```bash
03-agentops-control-tower/scripts/run_ingestion_demo.sh
```

## Next Milestone

Project 3 Milestone 3: local AgentOps summaries and timeline.
