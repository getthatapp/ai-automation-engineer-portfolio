# Codex Handoff: AI Automation Engineer Portfolio

Last updated: 2026-05-28  
Repository: `ai-automation-engineer-portfolio`  
Current project: `01-ai-marketing-ops-agent`  
Current status: Milestones 1-11 completed.  
Next step: Milestone 12 — approval-aware notifications.

---

## 1. Purpose

This file is the primary handoff for Codex / AI coding agents working on this portfolio.

Codex should read this document together with the root `AGENTS.md` before making changes.

---

## 2. Current State

Project 1 now includes:

- local mock marketing panel
- Campaign REST API mock
- Analytics GraphQL API mock
- Project Management API mock
- typed HTTP clients
- Playwright scraper
- deterministic aggregation into `CampaignSnapshot`
- deterministic anomaly detection into `AnomalyFinding`
- deterministic Markdown reporting
- daily workflow orchestration
- persistent JSONL run recording
- optional LLM interpretation over validated outputs
- deterministic human approval flow
- local JSONL approval queue

Current verified status after Milestone 11:

```text
96 tests passing
ruff clean
mypy clean
```

---

## 3. Current Pipeline

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
daily workflow orchestration + local report file + optional LLM interpretation
        ↓
approval request creation for high-risk outputs
        ↓
optional deterministic tasks
        ↓
persistent run recording + local JSONL history
```

Project 1 does not yet have:

- Telegram/Slack/email notification
- CI/CD
- final interview demo script

---

## 4. Completed Milestones

### Milestone 1 — Initial Scaffold

Implemented initial Python project scaffold, docs placeholders, typed models, retry/rate limiter utilities and minimal tests.

Verification:

```text
9 tests passed
ruff clean
mypy clean
```

### Milestone 2 — Local Mock Services

Implemented local FastAPI mock services: marketing panel, Campaign REST API, Analytics GraphQL API and Project Management REST API.

Verification:

```text
19 tests passed
ruff clean
mypy clean
docker compose config validates
```

### Milestone 3 — Typed Service Clients

Implemented typed `httpx` clients: `CampaignClient`, `AnalyticsClient` and `ProjectManagementClient`.

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

Implemented optional LLM interpretation over deterministic outputs. The LLM layer is fail-safe, mockable, token-aware and forbidden from replacing deterministic findings.

Verification:

```text
84 tests passed
ruff clean
mypy clean
```

### Milestone 11 — Human Approval Flow

Implemented:

- `ApprovalRequest`
- `ApprovalDecision`
- `ApprovalStatus`
- `ApprovalRiskLevel`
- `ApprovalSource`
- local JSONL `LocalApprovalStore`
- deterministic `ApprovalService`
- optional workflow integration with approval request IDs
- `approval_request_count` in workflow run history
- deterministic test coverage for approvals, deduplication, high-risk LLM actions, secret sanitization and malformed persistence handling

Human approval behavior:

- creates requests for critical findings
- creates requests for findings requiring human review
- creates requests for high-risk or human-approval LLM recommendations
- never auto-approves high-risk actions
- deduplicates approval requests within a run
- persists records locally under `approval-requests/`
- does not block healthy workflow runs
- fails safely when approval storage is unavailable

Verification:

```text
96 tests passed
ruff clean
mypy clean
```

---

## 5. Architectural Decisions

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

Project 1 now creates local approval requests for sensitive recommendations and high-risk actions before any real notification integrations are added.

---

## 6. Next Milestone: Milestone 12

### Goal

Implement approval-aware notification delivery for completed reports and pending approval requests.

### Required behavior

The notification layer should:

- send deterministic report summaries only after workflow completion
- include pending approval request IDs when approvals exist
- avoid sending sensitive action recommendations as approved work
- support local/mock providers by default
- keep real providers optional and environment-configured
- fail safely without breaking workflow runs
- avoid storing or sending secrets

### Suggested structure

```text
src/marketing_ops_agent/notifications/
├── __init__.py
├── models.py
├── providers.py
├── service.py
└── errors.py

tests/notifications/
└── test_notifications.py
```

Do not add real Slack, Telegram or email credentials. Use `.env.example` for configuration examples only.

---

## 7. Prompt for Codex: Milestone 12

Use this prompt next:

```text
Read the root AGENTS.md and docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md first.

Continue Project 1: 01-ai-marketing-ops-agent.

Milestone 12: implement approval-aware notification delivery.

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
- Deterministic human approval flow exists.
- Approval requests are persisted locally.
- Tests pass.
- Do not move existing files.
- Do not replace deterministic reporting.
- Do not let LLM access raw scraped rows, raw REST responses, raw GraphQL responses, credentials or secrets.
- Do not hardcode notification credentials.

Goal:
Add optional, deterministic, approval-aware notification delivery.

Implement:
1. Typed notification models.
2. Provider abstraction with deterministic/mock provider by default.
3. Notification service that sends report summaries and pending approval references.
4. Optional workflow integration that does not block successful runs.
5. Tests for:
   - mock provider delivery
   - disabled mode
   - approval-aware message content
   - no secrets in persisted or sent payloads
   - workflow continues when notification delivery fails
6. Documentation updates:
   - README.md
   - docs/ARCHITECTURE.md
   - docs/DECISIONS.md
   - docs/RUNBOOK.md
   - .agents/skills/marketing-report/SKILL.md

Implementation guidance:
- Use Pydantic models.
- Use timezone-aware UTC timestamps.
- Keep tests deterministic.
- Do not call real notification APIs in tests.
- Real provider configuration should use environment variables only.
- Keep mypy clean.
- Add Google-style docstrings to all new functions, methods and classes.
- Ensure:
  - uv run pytest passes
  - uv run ruff check . passes
  - uv run mypy src passes

Suggested structure:
- src/marketing_ops_agent/notifications/
  - __init__.py
  - models.py
  - providers.py
  - service.py
  - errors.py
- tests/notifications/
  - test_notifications.py

After implementation, summarize:
1. files created/changed
2. notification models
3. provider abstraction
4. notification service behavior
5. workflow integration behavior
6. test coverage added
7. configuration behavior
8. what should be built next
```

---

## 8. Demo Commands

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

Inspect approval requests:

```bash
tail -n 20 approval-requests/approval-requests.jsonl
```

Generated report, run history and approval request files are ignored by git.

---

## 9. Future Milestones

```text
Milestone 12 — approval-aware notifications
Milestone 13 — CI/CD
Project 2     — MCP Automation Server + Claude Code Toolkit
Project 3     — AgentOps Control Tower
```
