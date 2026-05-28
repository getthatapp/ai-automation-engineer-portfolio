# Codex Handoff: AI Automation Engineer Portfolio

Last updated: 2026-05-28  
Repository: `ai-automation-engineer-portfolio`  
Current project: `01-ai-marketing-ops-agent`  
Current status: Milestones 1-10 completed.  
Next step: Milestone 11 — human approval flow or notification delivery.

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
12. later send reports via Telegram / Slack / email.

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
    ├── mock_services/
    ├── observability/
    ├── reporting/
    └── workflows/
```

---

## 7. AGENTS.md and Skills

There are two levels of `AGENTS.md`:

```text
AGENTS.md
01-ai-marketing-ops-agent/AGENTS.md
```

For Codex skills, prefer:

```text
.agents/skills/
```

Project 1 uses:

```text
01-ai-marketing-ops-agent/.agents/skills/marketing-report/SKILL.md
```

Do not change this to `.skills/` unless explicitly requested.

The `marketing-report` skill should consume:

```text
CampaignSnapshot + AnomalyFinding + deterministic report draft
```

It must not generate reports directly from raw scraped rows, raw REST responses or raw GraphQL responses.

---

## 8. Completed Milestones

### Milestone 1 — Initial Scaffold

Implemented:

- Python 3.12+ uv project scaffold
- project-level README and AGENTS.md
- docs placeholders
- Pydantic models
- async retry utility
- async rate limiter utility
- minimal tests

Verification:

```text
9 tests passed
ruff clean
mypy clean
```

### Milestone 2 — Local Mock Services

Implemented:

- marketing panel without API
- Campaign REST API
- Analytics GraphQL API
- Project Management REST API
- Docker Compose support

Services:

```text
Marketing panel:              http://localhost:8000
Campaign REST API:            http://localhost:8001
Analytics GraphQL API:        http://localhost:8002/graphql
Project Management REST API:  http://localhost:8003
```

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

Client behavior:

- environment-based defaults
- per-call timeout
- translated errors
- retry for timeout/transport/5xx cases
- explicit GraphQL error handling

Verification:

```text
28 tests passed
ruff clean
mypy clean
```

### Milestone 4 — Playwright Marketing Panel Scraper

Implemented:

- `PlaywrightMarketingPanelScraper`
- mock login handling
- mock 2FA handling
- dashboard scraping
- typed scraped rows
- browser-specific custom errors

Verification:

```text
33 tests passed
ruff clean
mypy clean
```

### Milestone 5 — Deterministic Data Aggregation

Implemented:

- `CampaignSnapshot`
- aggregation service
- data quality flags
- explicit missing/mismatched data handling

Data quality flags:

- `missing_campaign_metadata`
- `missing_analytics_metrics`
- `spend_mismatch`
- `conversions_mismatch`
- `revenue_mismatch`
- `stale_data`
- `requires_human_review`

Verification:

```text
41 tests passed
ruff clean
mypy clean
```

### Milestone 6 — Deterministic Anomaly Detection

Implemented:

- `AnomalyFinding`
- deterministic anomaly detector
- high spend / low conversions rule
- CPA threshold rule
- ROI rule
- data quality flag mapping
- human review escalation

Verification:

```text
51 tests passed
ruff clean
mypy clean
```

### Milestone 7 — Deterministic Markdown Reporting

Implemented:

- `ReportMetadata`
- `MarkdownReportWriter`
- `generate_markdown_report`
- deterministic report sections
- stable finding and campaign ordering

Report sections:

- title
- generated timestamp
- executive summary
- campaign health overview
- critical anomalies
- warning anomalies
- data quality issues
- human review required
- campaign snapshot table
- deterministic recommended actions
- limitations / missing data

Verification:

```text
61 tests passed
ruff clean
mypy clean
```

### Milestone 8 — Workflow Orchestration

Implemented:

- `DailyMarketingReportWorkflow(...).run()`
- `run_daily_marketing_report_workflow(...)`
- `build_task_requests(...)`
- `WorkflowExecutionError`
- `DailyMarketingReportResult`

Workflow behavior:

```text
scrape panel
→ fetch Campaign REST API data
→ fetch Analytics GraphQL metrics
→ aggregate snapshots
→ detect anomalies
→ generate Markdown report
→ optionally create deterministic tasks
→ save report locally
```

Report path:

```text
reports/daily-marketing-report-YYYYMMDDTHHMMSSZ.md
```

Verification:

```text
67 tests passed
ruff clean
mypy clean
```

### Milestone 9 — Persistent Run Recording and Observability

Implemented observability package:

```text
src/marketing_ops_agent/observability/
├── __init__.py
├── errors.py
├── models.py
└── run_recorder.py
```

Implemented `WorkflowRunRecord` with:

- `run_id`
- `workflow_name`
- `status`
- `started_at`
- `finished_at`
- `duration_seconds`
- `report_path`
- `snapshot_count`
- `finding_count`
- `critical_finding_count`
- `human_review_required`
- `created_task_ids`
- `task_error_count`
- `data_quality_summary`
- `failure_type`
- `failure_message`

Implemented `LocalRunRecorder` API:

- `append(record)`
- `read_recent(limit=20)`
- `get(run_id)`

Persistence behavior:

- appends structured records to JSONL
- default local path: `run-history/workflow-runs.jsonl`
- creates parent directories on append
- handles malformed JSONL lines explicitly
- does not store secrets
- generated run history files are ignored by git
- only `run-history/.gitkeep` should be committed

Manual successful run verified:

```json
{
  "status": "succeeded",
  "snapshot_count": 3,
  "finding_count": 0,
  "critical_finding_count": 0,
  "human_review_required": false,
  "report_path": "reports/daily-marketing-report-20260528T151506Z.md"
}
```

Verification:

```text
77 tests passed
ruff clean
mypy clean
```

---

## 9. Current Deterministic Pipeline

Project 1 currently has:

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

- Telegram/Slack/email notification
- CI/CD
- final interview demo script

---

## 10. Architectural Decisions

### Keep `src/marketing_ops_agent`

Do not move code to `app/`.

### API first, browser automation second

Use API clients where APIs exist:

- Campaign REST API
- Analytics GraphQL API
- Project Management REST API

Use Playwright only for the local HTML-only panel without API.

### Downstream modules consume validated objects

Downstream modules should consume:

```text
CampaignSnapshot
AnomalyFinding
Markdown report string
DailyMarketingReportResult
WorkflowRunRecord
LLMInterpretationRequest
LLMInterpretationResult
```

They should not consume raw scraped rows, raw REST responses or raw GraphQL responses.

### LLM interpretation boundary

LLM logic now exists only after deterministic workflow and observability.

This condition is satisfied after Milestone 10.

### No real CAPTCHA bypass

Do not implement:

- real CAPTCHA bypass
- anti-bot evasion
- external site scraping
- credential hardcoding

### Deterministic code before agentic code

LLM must not:

- scrape
- validate raw data
- invent missing metrics
- silently resolve mismatches
- perform deterministic calculations

LLM may:

- interpret validated snapshots
- summarize deterministic findings
- propose actions
- classify narrative severity
- draft executive summaries

---

## 11. Quality Standards

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

## 12. Completed Milestone: Milestone 10

### Goal

Implement an optional LLM interpretation layer on top of the deterministic pipeline.

The LLM layer must consume only validated deterministic outputs:

```text
CampaignSnapshot
AnomalyFinding
Markdown report draft
WorkflowRunRecord
```

Do not let the LLM access raw scraped rows, raw REST responses, raw GraphQL responses, credentials or secrets.

### Required behavior

The LLM interpretation layer should:

- generate an executive interpretation from validated snapshots and findings
- summarize business impact
- propose human-readable recommended actions
- explicitly mention missing data and data quality flags
- never invent missing metrics
- never overwrite deterministic findings
- return structured output
- support a safe local/mock mode when no API key is configured
- track token usage if a real provider is used
- be optional and disabled by default unless configured

### Suggested structure

```text
src/marketing_ops_agent/llm/
├── __init__.py
├── interpreter.py
├── models.py
├── prompts.py
├── providers.py
└── errors.py

tests/llm/
└── test_interpreter.py
```

---

## 13. Prompt for Codex: Milestone 11

Use this prompt next:

```text
Read the root AGENTS.md and docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md first.

Continue Project 1: 01-ai-marketing-ops-agent.

Milestone 11: implement the next controlled automation boundary.

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

Goal:
Choose and implement Milestone 11:
- human approval flow for sensitive recommendations, or
- notification delivery through Slack, Telegram or email.

Keep the same quality gate:
- uv run pytest
- uv run ruff check .
- uv run mypy src
```

---

## 14. Future Milestones

```text
Milestone 11 — human approval flow or notifications
Milestone 12 — CI/CD
Project 2    — MCP Automation Server + Claude Code Toolkit
Project 3    — AgentOps Control Tower
```

---

## 15. Demo Commands

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

## 16. What Not To Do

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
- add notifications before LLM interpretation decision is complete
- skip tests
- ignore mypy/ruff failures
