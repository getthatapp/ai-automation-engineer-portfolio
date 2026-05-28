# Codex Handoff: AI Automation Engineer Portfolio

Last updated: 2026-05-28  
Repository: `ai-automation-engineer-portfolio`  
Current project: `01-ai-marketing-ops-agent`  
Current status: Milestones 1–8 completed.  
Next step: Milestone 9 — persistent run recording and observability.

---

# 1. Purpose of this document

This file is the primary handoff for Codex / AI coding agents working on this portfolio.

Codex should read this document together with the root `AGENTS.md` before making changes.

This document describes:

- recruitment context,
- portfolio strategy,
- repository structure,
- current implementation status,
- architectural decisions,
- engineering standards,
- future milestones,
- ready-to-use Codex prompts.

---

# 2. Recruitment context

The portfolio is being built for the role:

**AI Automation Developer / Senior AI Automation Developer**

The role is about practical AI automation engineering, not ML research or data science.

The candidate is expected to build working systems:

- AI agents,
- workflow automation,
- Claude Code tooling,
- MCP servers,
- skills,
- hooks,
- memory systems,
- scheduled tasks,
- bots,
- Playwright automation,
- API integrations,
- monitoring,
- logging,
- retry/fallback behavior,
- documentation of decisions.

Candidate positioning:

> I am not an ML engineer. I am an automation engineer who turns repetitive business processes into controlled, testable and observable AI-powered workflows.

---

# 3. Candidate profile

The candidate has a background in:

- QA Engineering / QA Automation,
- Python,
- Playwright,
- Selenium,
- Behave,
- REST API testing,
- Postman,
- SQL,
- Jenkins / CI/CD,
- GitHub Actions,
- test automation,
- logging,
- validation,
- retry logic,
- edge case analysis,
- fintech / banking / telecom environments.

Main strengths:

- practical automation,
- Playwright and browser automation,
- API/integration thinking,
- quality mindset,
- stability,
- observability,
- testability,
- identifying inconsistencies and risks.

Portfolio gaps to close:

- TypeScript / Node.js,
- MCP,
- Claude Code,
- skills,
- hooks,
- production-grade agent architecture,
- async/concurrency,
- agent monitoring,
- AWS/serverless.

---

# 4. Portfolio strategy

Do not build random AI applications.

Build one coherent AI Automation mini-ecosystem consisting of 3 projects:

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
├── README.md
└── .gitignore
```

Main portfolio narrative:

> I built a production-oriented AI automation ecosystem: an AI agent executes a real business workflow, an MCP server exposes tools for Claude Code, and a Control Tower monitors workflow runs, errors, token usage, retries and human approvals.

---

# 5. GitHub repository

Use one main repository:

```text
ai-automation-engineer-portfolio
```

## 5.1 Why one repository

One repository communicates that the portfolio is a coherent ecosystem, not a set of unrelated demos.

The repository should show:

- working style,
- structure,
- documentation,
- tests,
- CI/CD,
- commit history,
- architecture,
- gradual development from MVP to a more advanced automation system.

## 5.2 Repository visibility

Start as:

```text
private
```

After a working MVP of Project 1, consider:

- making the repository public,
- or sharing access with selected recruiters / hiring managers.

## 5.3 Documentation levels

There are two documentation levels.

### Global portfolio documentation

```text
docs/
├── CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md
├── PORTFOLIO_OVERVIEW.md
├── REQUIREMENTS_COVERAGE_MATRIX.md
├── ARCHITECTURE_OVERVIEW.md
└── INTERVIEW_DEMO_SCRIPT.md
```

Root `docs/` describes the whole portfolio.

### Project-level documentation

```text
01-ai-marketing-ops-agent/docs/
├── ARCHITECTURE.md
├── DECISIONS.md
└── RUNBOOK.md
```

Project-level `docs/` describes a specific application.

This structure is intentional and should be preserved.

## 5.4 Commit strategy

Use small, logical commits.

Example commit history:

```text
Initial portfolio planning and Codex handoff
Add initial AI Marketing Operations Agent scaffold
Add local mock services for marketing operations agent
Add typed clients for mock marketing services
Add Playwright scraper for mock marketing panel
Add campaign data aggregation layer
Add deterministic anomaly detection
Add markdown report writer
Add daily marketing report workflow
Add persistent run recording and observability
Add LLM interpretation layer
Add notification tools
Add GitHub Actions CI
Add portfolio requirements coverage matrix
```

---

# 6. Target projects

## 6.1 Project 1: AI Marketing Operations Agent

Currently implemented project.

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
10. later record richer workflow observability,
11. later add LLM interpretation,
12. later send reports via Telegram / Slack / email.

Project 1 should demonstrate:

- Python,
- Playwright,
- panels without API,
- scraping,
- REST,
- GraphQL,
- auth,
- retry logic,
- rate limiting,
- prompt engineering later,
- tool use later,
- guardrails,
- context window awareness later,
- hallucination control later,
- scheduled reports later,
- bot notifications later,
- monitoring/logging,
- Docker,
- CI/CD,
- decision documentation.

## 6.2 Project 2: MCP Automation Server + Claude Code Toolkit

Goal:

Build a TypeScript/Node.js MCP server exposing tools for Claude Code.

Planned elements:

- MCP server,
- tools,
- resources,
- prompts,
- Claude Code skills,
- slash commands,
- hooks,
- memory files,
- permission rules,
- input validation,
- tests.

## 6.3 Project 3: AgentOps Control Tower

Goal:

Build a dashboard/API for monitoring AI agents and automation workflows.

Planned elements:

- workflow status,
- retry failed run,
- pause/resume workflow,
- human approval queue,
- token usage,
- latency,
- error rate,
- tool call history,
- incident summary,
- alerting,
- observability.

---

# 7. Current Project 1 structure

Project 1 uses a `src/` layout.

This is an accepted architectural decision. Do not move code to `app/`.

Current structure:

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
│       ├── __init__.py
│       ├── config.py
│       ├── models.py
│       ├── aggregation/
│       ├── anomaly/
│       ├── browser/
│       ├── clients/
│       ├── mock_services/
│       ├── reporting/
│       ├── workflows/
│       └── utils/
└── tests/
    ├── aggregation/
    ├── anomaly/
    ├── browser/
    ├── clients/
    ├── mock_services/
    ├── reporting/
    ├── workflows/
    ├── test_models.py
    ├── test_rate_limiter.py
    └── test_retry.py
```

---

# 8. AGENTS.md

There are two levels of `AGENTS.md`.

## 8.1 Root `AGENTS.md`

The root `AGENTS.md` defines rules for the whole portfolio.

It should point to:

```text
docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md
```

## 8.2 Project-level `AGENTS.md`

Project 1 has:

```text
01-ai-marketing-ops-agent/AGENTS.md
```

It defines rules for Project 1 only:

- Python 3.12+,
- uv,
- Pydantic v2,
- FastAPI,
- Playwright,
- pytest,
- ruff,
- mypy,
- Docker Compose,
- no secrets,
- no real CAPTCHA bypass,
- deterministic code for scraping, validation, aggregation, anomaly detection, reporting and workflow orchestration,
- LLM only for interpretation/summarization/recommendations after deterministic workflow exists.

---

# 9. Skills

For Codex, prefer:

```text
.agents/skills/
```

Project 1 uses:

```text
01-ai-marketing-ops-agent/
└── .agents/
    └── skills/
        └── marketing-report/
            └── SKILL.md
```

Do not change this to `.skills/` unless explicitly requested.

The `marketing-report` skill should describe:

- report format,
- expected inputs,
- anti-hallucination rules,
- handling missing data,
- separating facts from recommendations,
- cases requiring human review.

Expected downstream input for this skill:

```text
CampaignSnapshot + AnomalyFinding
```

Do not generate reports directly from raw scraped rows, raw REST responses or raw GraphQL responses.

---

# 10. Implementation status

## 10.1 Milestone 1 completed: Initial scaffold

Implemented:

- Python 3.12+ uv project scaffold,
- `pyproject.toml`,
- `uv.lock`,
- `.env.example`,
- project-level `README.md`,
- project-level `AGENTS.md`,
- docs placeholders,
- marketing report skill placeholder,
- Pydantic campaign/workflow/report models,
- async retry utility,
- async rate limiter utility,
- minimal tests.

Verification at completion:

```text
9 tests passed
ruff clean
mypy clean
```

## 10.2 Milestone 2 completed: Local mock services

Implemented mock FastAPI services:

- marketing panel without API,
- campaign REST API,
- analytics GraphQL API,
- project management REST API.

Services:

```text
Marketing panel:              http://localhost:8000
Campaign REST API:            http://localhost:8001
Analytics GraphQL API:        http://localhost:8002/graphql
Project Management REST API:  http://localhost:8003
```

Mock panel credentials:

```text
Username: demo@example.com
Password: local-password
Mock 2FA code: 000000
```

Verification at completion:

```text
19 tests passed
ruff clean
mypy clean
docker compose config validates
```

## 10.3 Milestone 3 completed: Typed service clients

Implemented typed `httpx` clients:

- `CampaignClient`,
- `AnalyticsClient`,
- `ProjectManagementClient`.

Client behavior:

- environment-based defaults,
- per-call timeout,
- translated errors,
- retry for timeout/transport/5xx cases,
- explicit GraphQL error handling.

Verification at completion:

```text
28 tests passed
ruff clean
mypy clean across 19 source files
```

## 10.4 Milestone 4 completed: Playwright marketing panel scraper

Implemented async Playwright scraper for local HTML-only mock marketing panel.

Scraper API:

- `PlaywrightMarketingPanelScraper.scrape_campaign_rows()`,
- `PlaywrightMarketingPanelScraper.login(page)`,
- `PlaywrightMarketingPanelScraper.scrape_dashboard(page)`,
- `MarketingPanelCredentials`,
- `ScrapedCampaignRow`.

Custom errors:

- `MarketingPanelLoginFailedError`,
- `DashboardUnavailableError`,
- `CampaignTableNotFoundError`,
- `MalformedCampaignRowError`.

Verification at completion:

```text
33 tests passed
ruff clean
mypy clean across 22 source files
```

## 10.5 Milestone 5 completed: Deterministic data aggregation layer

Implemented aggregation package:

```text
src/marketing_ops_agent/aggregation/
├── __init__.py
├── aggregator.py
├── campaign_snapshot.py
├── data_quality.py
└── errors.py
```

Implemented `CampaignSnapshot` model with fields:

- `campaign_id`,
- `scraped_row`,
- `campaign_metadata`,
- `analytics_metrics`,
- `data_quality_flags`,
- `data_quality_notes`,
- `requires_human_review`,
- `aggregated_at`.

Implemented data quality flags:

- `missing_campaign_metadata`,
- `missing_analytics_metrics`,
- `spend_mismatch`,
- `conversions_mismatch`,
- `revenue_mismatch`,
- `stale_data`,
- `requires_human_review`.

Aggregation behavior:

- joins scraped panel rows with Campaign REST API metadata and Analytics GraphQL metrics,
- preserves mismatched source data instead of choosing a silent winner,
- marks missing or inconsistent data explicitly,
- raises `DuplicateCampaignRowsError` for duplicate scraped campaign IDs,
- downstream modules should consume `CampaignSnapshot`, not raw scraped/API data.

Verification at completion:

```text
41 tests passed
ruff clean
mypy clean
```

## 10.6 Milestone 6 completed: Deterministic anomaly detection layer

Implemented anomaly package:

```text
src/marketing_ops_agent/anomaly/
├── __init__.py
├── detector.py
├── models.py
└── rules.py
```

Implemented `AnomalyFinding` model with fields:

- `campaign_id`,
- `anomaly_type`,
- `severity`,
- `message`,
- `source`,
- `source_evidence`,
- `requires_human_review`.

Implemented deterministic anomaly rules:

- high spend with low conversions,
- CPA above threshold,
- negative ROI / ROI below minimum,
- data quality flag mapping for:
  - missing metadata,
  - missing analytics,
  - spend mismatch,
  - conversion mismatch,
  - revenue mismatch,
  - stale data,
  - human review escalation.

Verification at completion:

```text
51 tests passed
ruff clean
mypy clean
```

## 10.7 Milestone 7 completed: Deterministic Markdown reporting

Implemented reporting package:

```text
src/marketing_ops_agent/reporting/
├── __init__.py
├── markdown_report.py
├── models.py
└── templates.py
```

Implemented report writer API:

- `ReportMetadata(title, generated_at)`,
- `MarkdownReportWriter().write(snapshots, findings, metadata)`,
- `generate_markdown_report(snapshots, findings, metadata)`,
- `sort_findings(findings)`.

Implemented report sections:

- title,
- generated timestamp,
- executive summary,
- campaign health overview,
- critical anomalies,
- warning anomalies,
- data quality issues,
- human review required,
- campaign snapshot table,
- deterministic recommended actions,
- limitations / missing data.

Verification at completion:

```text
61 tests passed
ruff clean
mypy clean
```

## 10.8 Milestone 8 completed: Workflow orchestration

Implemented workflow orchestration package:

```text
src/marketing_ops_agent/workflows/
├── __init__.py
├── daily_marketing_report.py
└── models.py
```

Implemented workflow API:

- `DailyMarketingReportWorkflow(...).run()`,
- `run_daily_marketing_report_workflow(...)`,
- `build_task_requests(...)`,
- `WorkflowExecutionError`.

Implemented `DailyMarketingReportResult` with:

- run ID,
- status,
- timestamps,
- report path,
- counts,
- snapshots,
- findings,
- created tasks,
- task errors,
- human-review state.

Report output behavior:

```text
reports/daily-marketing-report-YYYYMMDDTHHMMSSZ.md
```

Generated reports are ignored by git. Only `reports/.gitkeep` should be committed.

Task creation behavior:

- optional deterministic task creation,
- tasks are created only for critical findings or human-review findings,
- tasks are deduplicated by `(campaign_id, anomaly_type)` within one run,
- task text is deterministic.

Manual run with mock services running:

```bash
MARKETING_PANEL_USERNAME=demo@example.com \
MARKETING_PANEL_PASSWORD=local-password \
MARKETING_PANEL_2FA_CODE=000000 \
uv run python -m marketing_ops_agent.workflows.daily_marketing_report
```

Verification at completion:

```text
67 tests passed
ruff clean
mypy clean
```

---

# 11. Current state summary

Project 1 currently has:

- local mock marketing panel,
- local Campaign REST API,
- local Analytics GraphQL API,
- local Project Management API,
- Docker Compose environment,
- typed `httpx` clients,
- async retry utility,
- async rate limiter,
- async Playwright scraper,
- typed scraped rows,
- deterministic aggregation,
- `CampaignSnapshot`,
- data quality flags,
- deterministic anomaly detection,
- `AnomalyFinding`,
- deterministic Markdown reporting,
- daily marketing report workflow orchestration,
- deterministic project management task creation,
- generated reports saved locally,
- custom domain/client/browser/aggregation/workflow errors,
- tests,
- docs,
- project-level AGENTS.md,
- Codex-compatible `.agents/skills/marketing-report/SKILL.md`.

Project 1 does not yet have:

- persistent run recorder,
- richer observability,
- token usage tracking,
- LLM interpretation layer,
- Telegram/Slack/email notification,
- CI/CD,
- final interview demo script.

Current deterministic pipeline:

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
daily workflow orchestration + local report file + optional deterministic tasks
        ↓
Next: persistent run recording and observability
```

---

# 12. Current architectural decisions

## 12.1 Keep `src/marketing_ops_agent`

The project uses:

```text
src/marketing_ops_agent/
```

Do not move code to `app/`.

## 12.2 API first, browser automation second

Use API clients where APIs exist:

- Campaign REST API,
- Analytics GraphQL API,
- Project Management REST API.

Use Playwright only for:

- local HTML-only marketing panel without API.

## 12.3 Downstream modules consume validated objects

Downstream modules should consume:

```text
CampaignSnapshot
AnomalyFinding
Markdown report string
DailyMarketingReportResult
```

They should not consume raw scraped rows, raw REST responses or raw GraphQL responses.

## 12.4 LLM later

Do not add LLM workflow until deterministic workflow orchestration and observability exist.

Correct order:

```text
mock services
→ typed clients
→ Playwright scraper
→ deterministic aggregation
→ anomaly detection
→ report writer
→ workflow orchestration
→ run recorder / observability
→ LLM interpretation
→ notifications
```

## 12.5 No real CAPTCHA bypass

The mock panel may contain a mock 2FA field.

Do not implement:

- real CAPTCHA bypass,
- anti-bot evasion,
- external site scraping,
- credential hardcoding.

## 12.6 Deterministic code before agentic code

LLM should not:

- scrape,
- validate raw data,
- invent missing metrics,
- silently resolve mismatches,
- perform deterministic calculations.

LLM may later:

- interpret validated snapshots,
- generate summaries,
- propose actions,
- classify severity,
- draft reports.

---

# 13. Quality standards

Codex must maintain:

```bash
uv run pytest
uv run ruff check .
uv run mypy src
```

All should pass before a milestone is considered complete.

Standards:

- Python 3.12+,
- uv,
- typed code,
- Pydantic v2,
- FastAPI for mock services,
- httpx for clients,
- Playwright async API,
- pytest,
- ruff,
- mypy-clean source,
- no secrets,
- `.env.example` for examples,
- no external API dependency for tests,
- deterministic tests.

---

# 14. Next milestone: Milestone 9

## 14.1 Goal

Implement persistent run recording and observability.

The current workflow returns a typed result and writes a report file, but it does not yet persist structured run history.

Milestone 9 should record:

- workflow run metadata,
- status history,
- start/end timestamps,
- duration,
- generated report path,
- snapshot count,
- anomaly count,
- critical finding count,
- human-review state,
- created task IDs,
- task errors,
- failure records,
- data quality summary,
- retry/attempt metadata where available.

Do not implement LLM interpretation yet.

## 14.2 Required behavior

Add a lightweight local persistence layer for workflow run records.

Prefer a simple local JSONL or SQLite implementation. For this portfolio stage, JSONL is acceptable if well typed and tested.

The run recorder should:

- save one structured run record per workflow run,
- support appending completed/failed run records,
- support reading recent runs,
- support reading a run by run ID,
- never store secrets,
- not store raw credentials,
- preserve failure messages safely,
- be testable with temporary directories,
- integrate with the daily marketing report workflow.

## 14.3 Suggested structure

```text
src/marketing_ops_agent/observability/
├── __init__.py
├── run_recorder.py
├── models.py
└── errors.py

tests/observability/
└── test_run_recorder.py
```

Optional workflow tests:

```text
tests/workflows/test_daily_marketing_report_observability.py
```

Suggested local data directory:

```text
run-history/
└── .gitkeep
```

Generated run history files should be gitignored. Only `.gitkeep` should be committed.

## 14.4 Documentation updates

Update:

```text
README.md
docs/ARCHITECTURE.md
docs/DECISIONS.md
docs/RUNBOOK.md
```

Optional:

```text
docs/DEMO_SCRIPT.md
```

---

# 15. Prompt for Codex: Milestone 9

Use this prompt next:

```text
Read the root AGENTS.md and docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md first.

Continue Project 1: 01-ai-marketing-ops-agent.

Milestone 9: implement persistent run recording and observability.

Current state:
- Mock FastAPI services exist.
- Typed httpx clients exist.
- Async Playwright scraper exists.
- Deterministic aggregation layer exists.
- Deterministic anomaly detection exists.
- Deterministic Markdown report writer exists.
- Daily workflow orchestration exists.
- DailyMarketingReportResult exists.
- Tests pass.
- Do not move existing files.
- Do not implement the LLM agent workflow yet.
- Do not add notification integrations yet.
- Do not add external services.
- Keep persistence local, deterministic and testable.

Goal:
Add persistent local run recording and observability for the daily marketing report workflow.

Implement:
1. A typed WorkflowRunRecord model that captures:
   - run_id,
   - workflow_name,
   - status,
   - started_at,
   - finished_at,
   - duration_seconds,
   - report_path,
   - snapshot_count,
   - finding_count,
   - critical_finding_count,
   - human_review_required,
   - created_task_ids,
   - task_error_count,
   - data_quality_summary,
   - failure_type,
   - failure_message.
2. A local run recorder that:
   - appends run records to a local JSONL file,
   - reads recent run records,
   - reads one run by run_id,
   - creates the storage directory if needed,
   - never stores secrets,
   - handles malformed JSONL lines explicitly and safely.
3. Integration with DailyMarketingReportWorkflow:
   - record successful runs,
   - record failed unrecoverable workflow runs,
   - preserve the original exception behavior where appropriate,
   - do not hide failures.
4. Tests for:
   - appending a successful run record,
   - reading recent records,
   - reading by run_id,
   - missing run_id behavior,
   - malformed line handling,
   - workflow success records a run,
   - workflow failure records a failed run,
   - no secrets are stored in run records.
5. Documentation updates:
   - README.md,
   - docs/ARCHITECTURE.md,
   - docs/DECISIONS.md,
   - docs/RUNBOOK.md.

Implementation guidance:
- Prefer JSONL for this milestone unless the existing code strongly favors SQLite.
- Use Pydantic models.
- Use pathlib.
- Use timezone-aware UTC timestamps.
- Do not add external dependencies unless necessary.
- Generated run history files must not be committed.
- Add or update .gitignore if needed.
- Keep mypy clean.
- Ensure:
  - uv run pytest passes,
  - uv run ruff check . passes,
  - uv run mypy src passes.

Suggested structure:
- src/marketing_ops_agent/observability/
  - __init__.py
  - run_recorder.py
  - models.py
  - errors.py
- tests/observability/
  - test_run_recorder.py
- run-history/
  - .gitkeep

After implementation, summarize:
1. files created/changed,
2. run record model fields,
3. recorder API,
4. workflow integration behavior,
5. storage path behavior,
6. test coverage added,
7. how to inspect run history manually,
8. what should be built next.
```

---

# 16. Future milestones

## Milestone 10: LLM interpretation layer

Goal:

Only after deterministic workflow and observability exist, add LLM for:

- executive interpretation,
- recommended actions,
- incident summary,
- concise business summary.

Rules:

- LLM receives validated snapshots/anomalies/report draft,
- LLM must not invent metrics,
- LLM output should be structured,
- missing data must remain explicit,
- include token usage tracking.

## Milestone 11: Notifications

Goal:

Add Telegram/Slack/email notification tool.

Start with safe local/mock behavior if credentials are absent.

## Milestone 12: CI/CD

Goal:

Add GitHub Actions:

- pytest,
- ruff,
- mypy,
- optional Docker Compose validation.

---

# 17. Demo narrative for Project 1

Current Project 1 can already be demoed as a deterministic automation workflow.

Demo steps:

1. Start local mock services:

```bash
cd 01-ai-marketing-ops-agent
docker compose up --build
```

2. Run workflow:

```bash
MARKETING_PANEL_USERNAME=demo@example.com \
MARKETING_PANEL_PASSWORD=local-password \
MARKETING_PANEL_2FA_CODE=000000 \
uv run python -m marketing_ops_agent.workflows.daily_marketing_report
```

3. Show:

- mock marketing panel,
- Playwright scraper,
- REST API client,
- GraphQL client,
- aggregation output,
- data quality flags,
- anomaly detection,
- Markdown report under `reports/`,
- created project management tasks,
- soon: persisted run history.

4. Say:

> API is used where a stable API exists. Playwright is used only for the panel without API. LLM is used only after deterministic validation, reporting and observability. The workflow is testable, observable and designed for failure handling.

---

# 18. What not to do

Do not:

- build a chatbot as the main project,
- add a frontend too early,
- train ML models,
- bypass real CAPTCHA,
- scrape external websites,
- hardcode secrets,
- let LLM invent metrics,
- silently drop mismatched data,
- put all code in one file,
- move `src/marketing_ops_agent` to `app`,
- change `.agents/skills` to `.skills`,
- implement LLM before observability,
- add notifications before observability,
- skip tests,
- ignore mypy/ruff failures.

---

# 19. Current command checklist

From project directory:

```bash
cd 01-ai-marketing-ops-agent
uv run pytest
uv run ruff check .
uv run mypy src
```

Run mock services:

```bash
docker compose up --build
```

Run workflow manually:

```bash
MARKETING_PANEL_USERNAME=demo@example.com \
MARKETING_PANEL_PASSWORD=local-password \
MARKETING_PANEL_2FA_CODE=000000 \
uv run python -m marketing_ops_agent.workflows.daily_marketing_report
```

Generated reports:

```text
reports/daily-marketing-report-YYYYMMDDTHHMMSSZ.md
```

---

# 20. Next immediate action

The next Codex task is:

```text
Milestone 9: implement persistent run recording and observability.
```

Use the prompt from section 15.

Do not implement LLM yet.
Do not implement notifications yet.
Do not implement Control Tower yet.

The correct next architecture step is:

```text
daily marketing report workflow
        ↓
persistent run recording + observability
```
