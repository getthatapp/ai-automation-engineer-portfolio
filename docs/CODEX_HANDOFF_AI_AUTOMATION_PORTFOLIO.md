# Codex Handoff: AI Automation Engineer Portfolio

Last updated: 2026-06-02
Repository: `ai-automation-engineer-portfolio`  
Current project: `02-agent-toolkit-mcp`
Current status: Project 1 complete / portfolio-ready. Project 2 started with Milestone 1 scaffold.
Next step: Project 2 Milestone 2 — MCP server implementation.

---

## 1. Purpose

This file is the primary handoff for Codex / AI coding agents working on this portfolio.

Codex should read this document together with the root `AGENTS.md` before making changes.

Future projects should preserve curated milestone prompts under
`docs/prompt-history/<project-slug>/` using the same structure as Project 1.

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
- optional approval-aware notification delivery
- deterministic mock notification provider
- GitHub Actions CI for Project 1
- curated Project 1 prompt history under `docs/prompt-history/project-1/`

Project 2 now includes:

- project scaffold under `02-agent-toolkit-mcp/`
- Project 2 `README.md`, `AGENTS.md` and `CLAUDE.md`
- architecture, Codex usage, Claude Code usage, safety model and roadmap docs
- reusable Codex prompt templates
- reusable Claude Code command templates
- shared skill documentation
- lightweight scaffold scripts
- Project 1 example positioning page

Current verified status after Milestone 13:

```text
105 tests passing
ruff clean
mypy clean
docker compose config validates
bash script syntax clean
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
optional approval-aware notification summary
        ↓
persistent run recording + local JSONL history
```

Project 1 does not yet have:

- Telegram/Slack/email notification
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

### Approval-aware notifications before real providers

Project 1 now sends optional summary-only notifications through a deterministic
mock provider. Notifications include pending approval request IDs when present
and explicitly state that pending approvals are not approved actions.

---

### Milestone 12 — Approval-Aware Notifications

Implemented:

- `NotificationRequest`
- `NotificationResult`
- `NotificationStatus`
- `NotificationChannel`
- `NotificationPriority`
- `NotificationProvider`
- `DeterministicMockNotificationProvider`
- `NotificationService`
- optional workflow integration with `notification_result`
- optional run-history fields for notification status and count
- local env toggle through `NOTIFICATION_DELIVERY_ENABLED`

Behavior:

- sends deterministic workflow summaries only after workflow completion when enabled
- includes run ID, report path, workflow counts and pending approval request IDs
- states pending approval requests are not approved actions
- avoids raw source payloads, credentials, secrets and approved-action claims
- does not call real Slack, Telegram, email or external notification APIs
- fails safely without breaking workflow runs

Verification:

```text
105 tests passed
ruff clean
mypy clean
```

---

## 6. Completed Milestone: Milestone 13

### Goal

Add CI/CD for Project 1 verification.

### Milestone 13 — CI/CD

Implemented:

- `.github/workflows/project-1-ci.yml`
- path-filtered triggers for pull requests and pushes to `main`
- Python 3.12 setup
- uv setup and dependency sync
- Playwright Chromium install
- pytest, ruff and mypy
- Docker Compose config validation
- Bash syntax checks for helper scripts
- local mirror script: `scripts/run_ci_locally.sh`

CI behavior:

- runs from `01-ai-marketing-ops-agent`
- does not start long-lived Docker Compose services
- does not call real external APIs
- does not require secrets
- does not send real notifications
- keeps runtime reports, run history and approval records out of git

Verification:

```text
105 tests passed
ruff clean
mypy clean
docker compose config validates
bash script syntax clean
git diff --check clean
```

---

## 7. Prompt for Codex: Project 2 Milestone 2

Use this prompt next:

```text
Read the root AGENTS.md and docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md first.

Continue Project 2: 02-agent-toolkit-mcp.

Goal:
Implement Project 2 Milestone 2: initial MCP server implementation.

Current state:
- Project 1 is complete and portfolio-ready.
- Project 2 Milestone 1 scaffold is complete.
- Do not modify Project 1 unless the task explicitly requires it.
- Do not hardcode secrets.
- Do not add real external service credentials.

Implementation guidance:
- Prefer TypeScript / Node.js for the MCP tooling.
- Add the initial MCP server structure and deterministic local tools.
- Keep MCP tools deterministic with typed inputs, validation and auditable outputs.
- Do not place vague LLM reasoning inside tool implementations.
- Maintain Codex and Claude Code support in docs and examples.
- Add tests and explicit verification commands.
- Update README files and this handoff.
- Keep generated files out of git.

After implementation, summarize files created, commands to run, verification results and next steps.
```

Project 2 permanent rules:

- every new function, method and class created by Codex must include a clear Google-style docstring
- every milestone must update relevant README files
- every milestone must update this handoff
- use branch-based workflow and do not assume direct work on `main`
- do not hardcode secrets or add real external credentials
- do not modify Project 1 code unless explicitly requested

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

Run workflow with mock notifications:

```bash
NOTIFICATION_DELIVERY_ENABLED=true ./scripts/run_workflow.sh
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

Run Project 1 CI locally:

```bash
./scripts/run_ci_locally.sh
```

---

## 9. Future Milestones

```text
Project 2     — Milestone 2: MCP server implementation
Project 3     — AgentOps Control Tower
```
