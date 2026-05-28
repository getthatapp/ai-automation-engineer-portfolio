# AI Automation Engineer Portfolio

Production-oriented portfolio demonstrating practical AI automation engineering: browser automation, API integrations, deterministic workflow orchestration, data validation, anomaly detection, reporting, observability, and future LLM/MCP extensions.

This repository is not a chatbot demo. It is a staged AI automation ecosystem built to automate real business workflows.

---

## Current Status

### Project 1: AI Marketing Operations Agent

Status: **Milestones 1-9 completed**

Implemented:

- local mock marketing panel without API
- Playwright login and scraping
- Campaign REST API integration
- Analytics GraphQL API integration
- Project Management API integration
- typed HTTP clients with timeout/error handling
- deterministic data aggregation
- `CampaignSnapshot` model
- data quality flags
- deterministic anomaly detection
- `AnomalyFinding` model
- deterministic Markdown report writer
- daily marketing report workflow
- local report generation
- optional deterministic task creation
- persistent workflow run recording
- local JSONL run history

Current deterministic pipeline:

```text
Marketing panel + REST API + GraphQL API
        ↓
Playwright scraper + typed service clients
        ↓
CampaignSnapshot with data quality flags
        ↓
AnomalyFinding objects
        ↓
Markdown report
        ↓
Daily workflow orchestration
        ↓
Persistent run recording
```

Next milestone:

```text
LLM interpretation layer over validated deterministic outputs
```

---

## Repository Structure

```text
ai-automation-engineer-portfolio/
├── 01-ai-marketing-ops-agent/
├── 02-mcp-automation-server-claude-toolkit/
├── 03-agentops-control-tower/
├── docs/
│   └── CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md
├── AGENTS.md
└── README.md
```

---

## Projects

### 01 — AI Marketing Operations Agent

A production-style automation workflow for marketing operations.

It simulates a Head of Marketing workflow:

1. scrape campaign data from an HTML-only marketing panel,
2. enrich it with REST API metadata,
3. enrich it with GraphQL analytics metrics,
4. validate consistency across sources,
5. detect anomalies deterministically,
6. generate a Markdown report,
7. create deterministic project-management tasks,
8. persist structured workflow run history.

### 02 — MCP Automation Server + Claude Code Toolkit

Planned project focused on:

- TypeScript / Node.js
- MCP tools
- Claude Code skills
- hooks
- memory files
- tool permissions
- agent-ready automation commands

### 03 — AgentOps Control Tower

Planned project focused on:

- workflow monitoring
- run history
- retries
- failure records
- human approval queue
- token/cost tracking
- agent observability dashboard

---

## Why This Portfolio Exists

The goal is to demonstrate the practical work expected from an AI Automation Developer:

- choosing API vs browser automation vs deterministic code vs LLM,
- building testable workflow components,
- handling partial failures,
- avoiding hallucinated metrics,
- preserving data quality issues,
- documenting architectural decisions,
- preparing the system for observability and agentic extensions.

---

## How to Run Project 1

```bash
cd 01-ai-marketing-ops-agent
uv sync
uv run playwright install chromium
docker compose up --build
```

In another terminal:

```bash
MARKETING_PANEL_USERNAME=demo@example.com \
MARKETING_PANEL_PASSWORD=local-password \
MARKETING_PANEL_2FA_CODE=000000 \
uv run python -m marketing_ops_agent.workflows.daily_marketing_report
```

Generated reports are saved under:

```text
01-ai-marketing-ops-agent/reports/
```

Run history is saved under:

```text
01-ai-marketing-ops-agent/run-history/workflow-runs.jsonl
```

Inspect run history:

```bash
tail -n 5 run-history/workflow-runs.jsonl
```

---

## Quality Checks

```bash
cd 01-ai-marketing-ops-agent
uv run pytest
uv run ruff check .
uv run mypy src
```

Current status:

```text
77 tests passing
ruff clean
mypy clean
```

---

## Engineering Principles

- API first where stable APIs exist.
- Playwright only where no API exists.
- Deterministic validation before LLM interpretation.
- Missing data must be explicit.
- LLM must not invent metrics.
- Human review must be triggered for unsafe or incomplete automation.
- Workflow behavior must be testable and observable.
- Generated reports and run history are not committed.

---

## Documentation

Global handoff for Codex and AI coding agents:

```text
docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md
```

Project-level documentation:

```text
01-ai-marketing-ops-agent/docs/
├── ARCHITECTURE.md
├── DECISIONS.md
└── RUNBOOK.md
```

---

## Current Roadmap

```text
Milestone 10 — LLM interpretation layer
Milestone 11 — notifications
Milestone 12 — CI/CD
Project 2    — MCP Automation Server + Claude Code Toolkit
Project 3    — AgentOps Control Tower
```
