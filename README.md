# AI Automation Engineer Portfolio

Production-oriented portfolio demonstrating practical AI automation engineering: browser automation, API integrations, deterministic workflow orchestration, data validation, anomaly detection, reporting, observability, optional LLM interpretation, human approval flow, and MCP-style local tool extensions.

This repository is not a chatbot demo. It is a staged AI automation ecosystem built to automate real business workflows safely and observably.

---

## Current Status

### Project 1: AI Marketing Operations Agent

Status: **Portfolio-ready / case-study-ready**

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
- optional LLM interpretation layer
- deterministic/mock LLM provider for safe local use
- LLM prompt safety rules and token usage capture
- deterministic human approval flow
- local JSONL approval queue for high-risk outputs
- optional approval-aware notification delivery
- deterministic/mock notification provider for local runs and tests
- GitHub Actions CI for Project 1 quality checks

Current pipeline:

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
        ↓
Optional LLM interpretation over validated outputs
        ↓
Human approval requests for high-risk outputs
        ↓
Optional approval-aware notification summary
```

Next milestone:

```text
Project 2 Milestone 8 — Claude Code hook examples or local runtime packaging
```

### Project 2: Agent Toolkit for Codex and Claude Code

Status: **Local MCP-style tool CLI and CI implemented**

Project 2 supports both Codex and Claude Code by providing reusable prompt
templates, Claude Code command templates, shared skills, safety documentation
lightweight reviewer scripts and a Python deterministic local MCP tool layer.
It also documents local Codex and Claude Code permission profiles for read-only,
workspace-write and approval-required workflows.
The MCP tools now return richer structured validation outputs, including report
summaries, warnings, record counts, artifact counts and readiness checks.
Project 2 also exposes these tools through the local `agent-toolkit-mcp` CLI so
reviewers can print JSON evidence and use status-check exit codes without
writing Python.
Project 2 has GitHub Actions CI plus a local CI mirror script for scaffold,
MCP server, shell syntax and read-only CLI smoke checks.
It is a toolkit for agentic automation workflows, not another business workflow
app.

See [Project 2 README](02-agent-toolkit-mcp/README.md).

---

## Repository Structure

```text
ai-automation-engineer-portfolio/
├── 01-ai-marketing-ops-agent/
├── 02-agent-toolkit-mcp/
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
8. persist structured workflow run history,
9. optionally produce LLM-based business interpretation over validated outputs,
10. create approval requests for critical findings, human-review findings and high-risk LLM recommendations,
11. optionally send an approval-aware notification summary through the deterministic mock provider.

The LLM layer is intentionally downstream of deterministic validation. It must not invent metrics, replace deterministic findings, or access raw credentials/source payloads.

The approval layer is intentionally upstream of notification delivery. High-risk recommendations are not treated as approved work unless explicitly approved, and notifications clearly identify pending approval requests as not approved actions.

## Project 1 Case Study and Demo Docs

Project 1 is portfolio-ready and case-study-ready. For a reviewer-friendly walkthrough, see:

- [Project 1 Case Study](docs/PROJECT_1_CASE_STUDY.md)
- [Demo Script](docs/DEMO_SCRIPT.md)
- [Requirements Coverage Matrix](docs/REQUIREMENTS_COVERAGE_MATRIX.md)
- [Project 1 Prompt History](docs/prompt-history/project-1/README.md)

### 02 — Agent Toolkit for Codex and Claude Code

Project focused on:

- Python deterministic local MCP tools
- Codex prompt workflows
- Claude Code commands
- shared skills
- `AGENTS.md` and `CLAUDE.md` guidance
- shell wrappers for both Codex and Claude Code
- safety model and tool permissions

Current MCP tools inspect Project 1 artifacts locally and read-only:

- validate Markdown report sections
- read sanitized workflow run history
- list sanitized pending approvals
- report generated runtime files without deleting them
- generate a deterministic Project 1 demo readiness brief

Run the local CLI from the Project 2 MCP package:

```bash
cd 02-agent-toolkit-mcp/mcp-server
uv run agent-toolkit-mcp check-runtime-clean ../../01-ai-marketing-ops-agent --pretty
```

Run Project 2 CI locally:

```bash
02-agent-toolkit-mcp/scripts/run_ci_locally.sh
```

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

### Prerequisites

- Python 3.12+
- `uv`
- Docker and Docker Compose

### Setup

```bash
cd 01-ai-marketing-ops-agent
uv sync
uv run playwright install chromium
```

### Start Local Mock Services

```bash
./scripts/start_services.sh
```

This starts the local mock services required by the workflow.

### Run the Deterministic Workflow

In another terminal:

```bash
./scripts/run_workflow.sh
```

### Run Workflow with Mock LLM Interpretation

```bash
./scripts/run_workflow_with_llm.sh
```

### Run Workflow with Mock Notifications

```bash
NOTIFICATION_DELIVERY_ENABLED=true ./scripts/run_workflow.sh
```

The mock notification provider does not call Slack, Telegram, email or any
external API. It adds a summary notification result to the workflow output and
records notification status in run history.

The workflow scripts use local demo marketing panel credentials by default:

```text
MARKETING_PANEL_USERNAME=demo@example.com
MARKETING_PANEL_PASSWORD=local-password
MARKETING_PANEL_2FA_CODE=000000
```

Environment variables can override these defaults. No real secrets are required for the mock demo.

### Inspect Generated Outputs

```text
reports/                                  Markdown reports
run-history/workflow-runs.jsonl           Workflow run history
approval-requests/approval-requests.jsonl Pending approval queue, when present
```

Useful inspection commands:

```bash
ls -lt reports/
sed -n '1,220p' "$(ls -t reports/*.md | head -n 1)"
tail -n 5 run-history/workflow-runs.jsonl
tail -n 20 approval-requests/approval-requests.jsonl
```

### Run Quality Checks

```bash
./scripts/run_checks.sh
```

Equivalent commands:

```bash
uv run pytest
uv run ruff check .
uv run mypy src
```

### Run CI Locally

Project 1 CI runs the local verification set from `01-ai-marketing-ops-agent`:

```bash
./scripts/run_ci_locally.sh
```

This mirrors the GitHub Actions workflow: dependency sync, Playwright Chromium
install, pytest, ruff, mypy, Docker Compose config validation and Bash syntax
checks for scripts. CI uses mock/disabled LLM and notification settings, does
not require secrets and does not call real external APIs.

Current status:

```text
105 tests passing
ruff clean
mypy clean
```

### Clean Generated Runtime Files

```bash
./scripts/clean_runtime.sh
```

### Stop Services

```bash
docker compose down
```

Generated reports, run history and approval request files are ignored by git.

### Manual Equivalent Workflow Command

```bash
MARKETING_PANEL_USERNAME=demo@example.com \
MARKETING_PANEL_PASSWORD=local-password \
MARKETING_PANEL_2FA_CODE=000000 \
uv run python -m marketing_ops_agent.workflows.daily_marketing_report
```

---

## Engineering Principles

- API first where stable APIs exist.
- Playwright only where no API exists.
- Deterministic validation before LLM interpretation.
- Missing data must be explicit.
- LLM must not invent metrics.
- LLM must not replace deterministic findings.
- Human review must be triggered for unsafe or incomplete automation.
- Sensitive or high-risk outputs require approval before external action.
- Workflow behavior must be testable and observable.
- CI should validate tests, linting, typing, Compose configuration and helper scripts.
- Generated reports, run history and approval request files are not committed.

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

02-agent-toolkit-mcp/docs/
├── ARCHITECTURE.md
├── CODEX_USAGE.md
├── CLAUDE_CODE_USAGE.md
├── SAFETY_MODEL.md
└── ROADMAP.md
```

---

## Current Roadmap

```text
Project 2     — Milestone 2: MCP server implementation
Project 3     — AgentOps Control Tower
```
