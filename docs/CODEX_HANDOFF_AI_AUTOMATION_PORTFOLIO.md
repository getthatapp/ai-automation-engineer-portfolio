# Codex Handoff: AI Automation Engineer Portfolio

Last updated: 2026-05-28  
Repository: `ai-automation-engineer-portfolio`  
Current project: `01-ai-marketing-ops-agent`  
Current status: Milestones 1-10 completed.  
Next step: Milestone 11 — human approval flow.

---

## 1. Purpose

This file is the primary handoff for Codex / AI coding agents working on this portfolio.

Codex should read this document together with the root `AGENTS.md` before making changes.

---

## 2. Recruitment Context

The portfolio is being built for the role:

**AI Automation Developer / Senior AI Automation Developer**

The role is about practical AI automation engineering, not ML research or data science.

The candidate is expected to build working systems:

- AI agents
- workflow automation
- Claude Code tooling
- MCP servers
- skills
- hooks
- memory systems
- scheduled tasks
- bots
- Playwright automation
- API integrations
- monitoring
- logging
- retry/fallback behavior
- documentation of decisions

Candidate positioning:

> I am not an ML engineer. I am an automation engineer who turns repetitive business processes into controlled, testable and observable AI-powered workflows.

---

## 3. Portfolio Strategy

Build one coherent AI Automation mini-ecosystem consisting of three projects:

```text
ai-automation-engineer-portfolio/
├── 01-ai-marketing-ops-agent/
├── 02-mcp-automation-server-claude-toolkit/
├── 03-agentops-control-tower/
├── docs/
│   ├── CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md
│   ├── PORTFOLIO_OVERVIEW.md
│   ├── REQUIREMENTS_COVERAGE_MATRIX.md
│   ├── ARCHITECTURE_OVERVIEW.md
│   └── INTERVIEW_DEMO_SCRIPT.md
├── AGENTS.md
└── README.md
```

Main portfolio narrative:

> I built a production-oriented AI automation ecosystem: an AI agent executes a real business workflow, an MCP server exposes tools for Claude Code, and a Control Tower monitors workflow runs, errors, token usage, retries and human approvals.

---

## 4. Repository Notes

The correct repository root is:

```text
/Users/gtest/Projects/aiPortfolio/ai-automation-engineer-portfolio
```

Do not initialize Git above this folder.

Root-level documentation describes the full portfolio:

```text
docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md
README.md
AGENTS.md
```

Project-level documentation describes Project 1:

```text
01-ai-marketing-ops-agent/docs/
├── ARCHITECTURE.md
├── DECISIONS.md
└── RUNBOOK.md
```

---

## 5. Project 1: AI Marketing Operations Agent

Project 1 is the active project.

Business goal:

An agent-like automation workflow for a Head of Marketing that can:

1. log into a mock marketing panel using Playwright,
2. collect campaign data from an HTML-only panel without an API,
3. collect campaign metadata from Campaign REST API,
4. collect analytics metrics from Analytics GraphQL API,
5. aggregate and validate data,
6. detect anomalies,
7. generate a deterministic Markdown report,
8. create tasks in a mock Project Management API,
9. save workflow output locally,
10. persist workflow run history,
11. interpret deterministic outputs with an optional LLM layer,
12. require human approval for sensitive or high-risk automation,
13. later send reports via Telegram / Slack / email.

Project 1 demonstrates:

- Python
- Playwright
- panels without API
- scraping
- REST
- GraphQL
- typed clients
- retry logic
- rate limiting
- deterministic data validation
- deterministic anomaly detection
- deterministic reporting
- workflow orchestration
- local observability
- optional LLM interpretation over validated outputs
- monitoring/logging foundation
- Docker
- decision documentation

---

## 6. Current Project 1 Structure

Project 1 uses a `src/` layout. Do not move code to `app/`.

```text
01-ai-marketing-ops-agent/
├── AGENTS.md
├── README.md
├── .env.example
├── pyproject.toml
├── uv.lock
├── compose.yaml
├── Dockerfile.mock
├── reports/
│   └── .gitkeep
├── run-history/
│   └── .gitkeep
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DECISIONS.md
│   └── RUNBOOK.md
├── .agents/
│   └── skills/
│       └── marketing-report/
│           └── SKILL.md
├── src/
│   └── marketing_ops_agent/
│       ├── aggregation/
│       ├── anomaly/
│       ├── browser/
│       ├── clients/
│       ├── llm/
│       ├── mock_services/
│       ├── observability/
│       ├── reporting/
│       ├── workflows/
│       └── utils/
└── tests/
    ├── aggregation/
    ├── anomaly/
    ├── browser/
    ├── clients/
    ├── llm/
    ├── mock_services/
    ├── observability/
    ├── reporting/
    └── workflows/
```

---

## 7. Completed Milestones

### Milestone 1 — Initial Scaffold

Implemented initial Python project scaffold, docs placeholders, typed models, retry/rate limiter utilities and minimal tests.

Verification:

```text
9 tests passed
ruff clean
mypy clean
```

### Milestone 2 — Local Mock Services

Implemented local FastAPI mock services:

- marketing panel without API
- Campaign REST API
- Analytics GraphQL API
- Project Management REST API

Verification:

```text
19 tests passed
ruff clean
mypy clean
docker compose config validates
```

### Milestone 3 — Typed Service Clients

Implemented typed `httpx` clients:

- `CampaignClient`
- `AnalyticsClient`
- `ProjectManagementClient`

Verification:

```text
28 tests passed
ruff clean
mypy clean
```

### Milestone 4 — Playwright Marketing Panel Scraper

Implemented `PlaywrightMarketingPanelScraper`, mock login, mock 2FA handling, dashboard scraping and typed scraped rows.

Verification:

```text
33 tests passed
ruff clean
mypy clean
```

### Milestone 5 — Deterministic Data Aggregation

Implemented `CampaignSnapshot`, aggregation service and data quality flags.

Verification:

```text
41 tests passed
ruff clean
mypy clean
```

### Milestone 6 — Deterministic Anomaly Detection

Implemented `AnomalyFinding`, deterministic anomaly detector and data quality flag mapping.

Verification:

```text
51 tests passed
ruff clean
mypy clean
```

### Milestone 7 — Deterministic Markdown Reporting

Implemented deterministic Markdown report writer with executive summary, anomaly sections, data quality issues, human review section and campaign snapshot table.

Verification:

```text
61 tests passed
ruff clean
mypy clean
```

### Milestone 8 — Workflow Orchestration

Implemented `DailyMarketingReportWorkflow`, `DailyMarketingReportResult`, deterministic task requests and local report saving.

Verification:

```text
67 tests passed
ruff clean
mypy clean
```

### Milestone 9 — Persistent Run Recording and Observability

Implemented `WorkflowRunRecord`, `LocalRunRecorder`, JSONL run history and workflow integration.

Verification:

```text
77 tests passed
ruff clean
mypy clean
```

### Milestone 10 — Optional LLM Interpretation Layer

Implemented:

- `LLMInterpretationRequest`
- `LLMInterpretationResult`
- `LLMRecommendedAction`
- `LLMTokenUsage`
- `LLMInterpretationProvider` protocol
- deterministic mock LLM provider
- prompt builder with anti-hallucination and secret-safety rules
- fail-safe interpreter service
- optional workflow integration
- deterministic test coverage for prompt safety, missing data, disabled mode and token usage

LLM interpretation behavior:

- consumes only validated deterministic outputs
- does not replace deterministic reporting
- does not overwrite deterministic findings
- does not access raw scraped rows, raw REST responses, raw GraphQL responses, credentials or secrets
- is optional and safe to disable
- captures token usage when the provider returns it

Verification:

```text
84 tests passed
ruff clean
mypy clean
```

---

## 8. Current Pipeline

```text
mock panel / REST API / GraphQL API
        ↓
Playwright scraper + typed service clients
        ↓
CampaignSnapshot with data quality flags
        ↓
AnomalyFinding objects
        ↓
deterministic Markdown report
        ↓
daily workflow orchestration + local report file + optional LLM interpretation + optional deterministic tasks
        ↓
persistent run recording + local JSONL history
```

Project 1 does not yet have:

- human approval records / approval queue
- Telegram/Slack/email notification
- CI/CD
- final interview demo script

---

## 9. Architectural Decisions

### Deterministic code before agentic code

LLM must not:

- scrape
- validate raw data
- invent missing metrics
- silently resolve mismatches
- perform deterministic calculations
- replace deterministic findings

LLM may:

- interpret validated snapshots
- summarize deterministic findings
- propose actions
- classify narrative severity
- draft executive summaries

### Human approval before external action

Before adding real notifications or external side effects, Project 1 should add a human approval flow for sensitive recommendations and high-risk actions.

---

## 10. Quality Standards

Codex must maintain:

```bash
uv run pytest
uv run ruff check .
uv run mypy src
```

Current verified status after Milestone 10:

```text
84 tests passing
ruff clean
mypy clean
```

---

## 11. Next Milestone: Milestone 11

### Goal

Implement a human approval flow for sensitive recommendations and high-risk automation.

Notifications should come after this milestone.

### Required behavior

The human approval layer should:

- create approval requests for high-risk recommendations
- create approval requests for critical findings
- create approval requests for findings that require human review
- persist approval records locally
- support statuses such as `pending`, `approved`, `rejected`, `expired`
- never auto-approve high-risk actions
- be deterministic and testable
- integrate with the existing workflow without making approval mandatory for healthy runs
- prepare the system for approval-aware notifications later

### Suggested structure

```text
src/marketing_ops_agent/approval/
├── __init__.py
├── models.py
├── approval_store.py
├── service.py
└── errors.py

tests/approval/
└── test_approval_flow.py

approval-requests/
└── .gitkeep
```

Generated approval request files should be ignored by git. Only `.gitkeep` should be committed.

---

## 12. Prompt for Codex: Milestone 11

Use this prompt next:

```text
Read the root AGENTS.md and docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md first.

Continue Project 1: 01-ai-marketing-ops-agent.

Milestone 11: implement human approval flow.

Current state:
- Mock FastAPI services exist.
- Typed httpx clients exist.
- Async Playwright scraper exists.
- Deterministic aggregation exists.
- CampaignSnapshot model exists.
- Deterministic anomaly detection exists.
- AnomalyFinding model exists.
- Deterministic Markdown report writer exists.
- Daily workflow orchestration exists.
- Persistent run recording exists.
- WorkflowRunRecord exists.
- Optional LLM interpretation layer exists.
- LLM token usage is captured when available.
- Tests pass.
- Do not move existing files.
- Do not replace deterministic reporting.
- Do not let LLM access raw scraped rows, raw REST responses, raw GraphQL responses, credentials or secrets.
- Do not add notification integrations yet.

Goal:
Add a deterministic human approval flow for sensitive recommendations and high-risk automation.

Implement:
1. Typed approval models:
   - ApprovalRequest
   - ApprovalDecision
   - ApprovalStatus enum
   - ApprovalRiskLevel enum
2. Local approval store:
   - append/create approval request
   - list pending approvals
   - get approval by id
   - record approve/reject decision
   - persist records locally, preferably JSONL or JSON files
3. Approval service that:
   - creates approval requests for critical findings
   - creates approval requests for findings requiring human review
   - creates approval requests for high-risk LLM recommended actions if available
   - never auto-approves high-risk actions
   - deduplicates approval requests within one run
4. Optional workflow integration:
   - create approval requests after deterministic findings and optional LLM interpretation
   - do not block healthy workflow runs
   - include approval request IDs in workflow result if appropriate
5. Tests for:
   - creating approval request
   - listing pending approvals
   - approving request
   - rejecting request
   - deduplication
   - critical finding creates approval request
   - human-review finding creates approval request
   - healthy run creates no approval request
   - no secrets are persisted
6. Documentation updates:
   - README.md
   - docs/ARCHITECTURE.md
   - docs/DECISIONS.md
   - docs/RUNBOOK.md
   - .agents/skills/marketing-report/SKILL.md

Implementation guidance:
- Prefer local persistence for this milestone.
- Use Pydantic models.
- Use pathlib.
- Use timezone-aware UTC timestamps.
- Generated approval files must not be committed.
- Add or update .gitignore if needed.
- Keep tests deterministic.
- Do not add Slack/Telegram/email yet.
- Keep mypy clean.
- Ensure:
  - uv run pytest passes
  - uv run ruff check . passes
  - uv run mypy src passes

Suggested structure:
- src/marketing_ops_agent/approval/
  - __init__.py
  - models.py
  - approval_store.py
  - service.py
  - errors.py
- tests/approval/
  - test_approval_flow.py
- approval-requests/
  - .gitkeep

After implementation, summarize:
1. files created/changed
2. approval models
3. approval store API
4. approval service behavior
5. workflow integration behavior
6. test coverage added
7. how to inspect approval requests manually
8. what should be built next
```

---

## 13. Future Milestones

```text
Milestone 11 — human approval flow
Milestone 12 — notifications
Milestone 13 — CI/CD
Project 2     — MCP Automation Server + Claude Code Toolkit
Project 3     — AgentOps Control Tower
```

---

## 14. Demo Commands

Run mock services:

```bash
cd 01-ai-marketing-ops-agent
docker compose up --build
```

Run workflow manually:

```bash
MARKETING_PANEL_USERNAME=demo@example.com \
MARKETING_PANEL_PASSWORD=local-password \
MARKETING_PANEL_2FA_CODE=000000 \
uv run python -m marketing_ops_agent.workflows.daily_marketing_report
```

Inspect generated report:

```bash
ls -lt reports/
cat "$(ls -t reports/*.md | head -1)"
```

Inspect run history:

```bash
tail -n 5 run-history/workflow-runs.jsonl
```

Generated report and run history files are ignored by git.

---

## 15. What Not To Do

Do not:

- build a chatbot as the main project
- add a frontend too early
- train ML models
- bypass real CAPTCHA
- scrape external websites
- hardcode secrets
- let LLM invent metrics
- silently drop mismatched data
- put all code in one file
- move `src/marketing_ops_agent` to `app`
- change `.agents/skills` to `.skills`
- let LLM replace deterministic logic
- add notifications before human approval flow
- skip tests
- ignore mypy/ruff failures
