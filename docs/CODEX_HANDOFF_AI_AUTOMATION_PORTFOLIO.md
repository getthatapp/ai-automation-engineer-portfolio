# Codex Handoff: AI Automation Engineer Portfolio

Last updated: 2026-06-04
Repository: `ai-automation-engineer-portfolio`  
Current project: `02-agent-toolkit-mcp`
Current status: Project 1 complete / portfolio-ready. Project 2 Milestone 7 implemented.
Next step: Project 2 Milestone 8 — Claude Code hook examples or local runtime packaging.

---

## 1. Purpose

This file is the primary handoff for Codex / AI coding agents working on this portfolio.

Codex should read this document together with the root `AGENTS.md` before making changes.

Future projects should preserve curated milestone prompts under
`docs/prompt-history/<project-slug>/` using the same structure as Project 1.

Starting with Project 2 Milestone 2, every Project 2 milestone must create or
update its own full prompt-history file under
`02-agent-toolkit-mcp/docs/prompt-history/`. Each file must include the full
prompt, expected verification, implementation result summary, verification
results and commit or PR placeholders until the human completes them.

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
- Python MCP server package under `02-agent-toolkit-mcp/mcp-server/`
- deterministic local read-only tools for Project 1 artifact inspection
- typed Pydantic schemas, path safety helpers and output sanitization
- MCP server tests, linting and type checks
- Project 2 prompt history under `02-agent-toolkit-mcp/docs/prompt-history/`
- read-only adapter scripts for Project 1 artifact reviews
- Codex prompts for Project 1 runtime, report and demo-readiness reviews
- Claude Code command templates for the same Project 1 review flows
- examples that explain how to interpret Project 1 reports, run history and
  approval queues
- runtime configuration docs under `02-agent-toolkit-mcp/docs/runtime/`
- Codex and Claude Code permission profile documentation
- local runtime configuration examples under
  `02-agent-toolkit-mcp/examples/runtime-config/`
- hardened MCP tool outputs with report summaries, warnings, record counts,
  artifact counts and readiness checklists
- expanded MCP tests for path safety, malformed inputs, redaction and stable
  ordering
- local `agent-toolkit-mcp` CLI for invoking deterministic tools without
  writing Python
- CLI tests for JSON payloads, pretty output and status-check exit codes
- GitHub Actions CI for Project 2 scaffold, MCP server and CLI checks
- local CI mirror script for Project 2 reviewer verification

Current verified Project 1 status after Milestone 13:

```text
105 tests passing
ruff clean
mypy clean
docker compose config validates
bash script syntax clean
```

Current verified Project 2 MCP status after Milestone 2:

```text
12 MCP server tests passing
ruff clean
mypy clean
bash script syntax clean
git diff --check clean
```

Current verified Project 2 status after Milestone 3:

```text
Project 2 scaffold checks passed
12 MCP server tests passing
ruff clean
mypy clean
bash script syntax clean
git diff --check clean
adapter scripts ran read-only against current Project 1 artifacts
```

Current verified Project 2 status after Milestone 4:

```text
Project 2 scaffold checks passed
12 MCP server tests passing
ruff clean
mypy clean
bash script syntax clean
git diff --check clean
permission profile helper ran read-only
```

Current verified Project 2 status after Milestone 5:

```text
Project 2 scaffold checks passed
21 MCP server tests passing
ruff clean
mypy clean
bash script syntax clean
git diff --check clean
adapter script serialized richer tool outputs
```

Current verified Project 2 status after Milestone 6:

```text
Project 2 scaffold checks passed
32 MCP server tests passing
ruff clean
mypy clean
bash script syntax clean
git diff --check clean
CLI smoke test generated pretty JSON demo-readiness evidence
```

Current verified Project 2 status after Milestone 7:

```text
Project 2 scaffold checks passed
32 MCP server tests passing
ruff clean
mypy clean
bash script syntax clean
git diff --check clean
local CI mirror passed
CLI smoke checks generated pretty JSON demo-readiness and runtime-clean evidence
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

## 7. Completed Project 2 Milestone: Milestone 2

### Goal

Implement the initial deterministic local MCP server layer for Project 2.

### Milestone 2 — MCP Server Implementation

Implemented:

- `02-agent-toolkit-mcp/mcp-server/pyproject.toml`
- Python package under `mcp-server/src/agent_toolkit_mcp/`
- minimal local tool registry in `server.py`
- deterministic tool logic in `tools.py`
- typed Pydantic schemas in `models.py`
- path validation helpers in `path_safety.py`
- local custom errors in `errors.py`
- pytest coverage under `mcp-server/tests/`
- MCP verification script: `02-agent-toolkit-mcp/scripts/run_mcp_checks.sh`
- prompt-history entry:
  `02-agent-toolkit-mcp/docs/prompt-history/milestone-02-mcp-server.md`

Tools:

- `validate_report(report_path)`
- `read_run_history(jsonl_path, limit=5)`
- `list_pending_approvals(jsonl_path)`
- `check_runtime_clean(project_path)`
- `generate_demo_brief(project_path)`

Behavior:

- local and deterministic only
- read-only filesystem inspection
- no LLM calls
- no external API calls
- no credentials required
- no destructive operations
- JSONL output sanitization for secret-like keys and values
- Project-level tools inspect only child paths below the provided project path

Verification:

```text
12 tests passed
ruff clean
mypy clean
bash script syntax clean
git diff --check clean
```

---

## 8. Completed Project 2 Milestone: Milestone 3

### Goal

Add practical local agent integration adapters and demo flows showing how Codex
and Claude Code can use Project 2 deterministic tools against Project 1
artifacts.

### Milestone 3 — Agent Integration Adapters

Implemented:

- read-only script: `02-agent-toolkit-mcp/scripts/demo_mcp_tools.sh`
- read-only script:
  `02-agent-toolkit-mcp/scripts/run_project1_tool_review.sh`
- Codex prompts:
  - `inspect-project1-runtime`
  - `review-project1-report`
  - `summarize-project1-demo-readiness`
- Claude Code commands:
  - `inspect-project1-runtime`
  - `review-project1-report`
  - `summarize-project1-demo-readiness`
- Project 1 examples:
  - `TOOL_REVIEW_FLOW.md`
  - `SAMPLE_AGENT_REVIEW.md`
- prompt-history entry:
  `02-agent-toolkit-mcp/docs/prompt-history/milestone-03-agent-integration.md`

Behavior:

- local and deterministic only
- read-only Project 1 artifact inspection
- no external API calls
- no secrets required
- no destructive tools
- no frontend UI
- no claim of external Codex or Claude Code MCP transport integration
- missing reports, run history and approval queues are treated as missing
  evidence, not invented data

Verification:

```text
Project 2 scaffold checks passed
12 MCP server tests passing
ruff clean
mypy clean
bash script syntax clean
git diff --check clean
adapter scripts ran read-only against current Project 1 artifacts
```

---

## 9. Completed Project 2 Milestone: Milestone 4

### Goal

Add runtime configuration examples and permission-profile documentation for
using Project 2 safely with Codex and Claude Code.

### Milestone 4 — Runtime Configuration Examples and Permission Profiles

Implemented:

- runtime docs under `02-agent-toolkit-mcp/docs/runtime/`
- Codex permission profiles for:
  - read-only inspection
  - workspace-write development
  - approval-required operations
  - blocked/destructive operation policy
- Claude Code permission profiles with matching local-only boundaries
- local runtime configuration examples under
  `02-agent-toolkit-mcp/examples/runtime-config/`
- read-only helper script:
  `02-agent-toolkit-mcp/scripts/show_permission_profiles.sh`
- prompt-history entry:
  `02-agent-toolkit-mcp/docs/prompt-history/milestone-04-runtime-config.md`

Behavior:

- documentation-first only
- local and deterministic only
- no Project 1 code or runtime behavior changes
- no MCP tool behavior changes
- no external API calls
- no secrets required
- no destructive tools
- no claim of deployed external MCP transport

Verification:

```text
Project 2 scaffold checks passed
12 MCP server tests passing
ruff clean
mypy clean
bash script syntax clean
git diff --check clean
permission profile helper ran read-only
```

---

## 10. Completed Project 2 Milestone: Milestone 5

### Goal

Improve reliability, safety and usefulness of the Project 2 deterministic local
MCP tools.

### Milestone 5 — MCP Tool Hardening and Richer Validation

Implemented:

- additive typed output fields for report summaries, report warnings, JSONL
  record counts, pending approval counts, runtime artifact counts and demo
  readiness checks
- explicit symlink handling documentation in path safety helpers
- structured handling for invalid run-history limits
- non-fatal report warnings for empty reports, missing generated timestamps and
  duplicate required headings
- runtime artifact counts for reports, run history, approval requests,
  `__pycache__/` directories and `*.pyc` files
- expanded tests for path safety, malformed inputs, ordering, redaction,
  summaries and readiness behavior
- prompt-history entry:
  `02-agent-toolkit-mcp/docs/prompt-history/milestone-05-tool-hardening.md`

Behavior:

- local and deterministic only
- read-only Project 1 artifact inspection
- no Project 1 code or runtime behavior changes
- no external API calls
- no secrets required
- no destructive tools
- no claim of deployed external MCP transport

Verification:

```text
Project 2 scaffold checks passed
21 MCP server tests passing
ruff clean
mypy clean
bash script syntax clean
git diff --check clean
adapter script serialized richer tool outputs
```

---

## 11. Completed Project 2 Milestone: Milestone 6

### Goal

Make the Project 2 deterministic local MCP-style tools easy to invoke from the
command line without writing Python.

### Milestone 6 — MCP Server CLI Interface

Implemented:

- local `agent-toolkit-mcp` console script under the MCP server package
- CLI subcommands for report validation, run-history reading, pending approval
  listing, runtime cleanliness checks and demo brief generation
- compact JSON output by default and `--pretty` indented JSON output
- status-check exit codes for invalid reports, dirty runtime checks, malformed
  JSONL, invalid limits, invalid paths and incomplete demo-readiness structure
- CLI tests for JSON payloads, pretty output, missing evidence behavior and
  exit codes
- prompt-history entry:
  `02-agent-toolkit-mcp/docs/prompt-history/milestone-06-cli-interface.md`

Behavior:

- local and deterministic only
- read-only Project 1 artifact inspection
- no Project 1 code or runtime behavior changes
- no external API calls
- no secrets required
- no destructive tools
- no claim of deployed external MCP transport

Verification:

```text
Project 2 scaffold checks passed
32 MCP server tests passing
ruff clean
mypy clean
bash script syntax clean
git diff --check clean
CLI smoke test generated pretty JSON demo-readiness evidence
```

---

## 12. Completed Project 2 Milestone: Milestone 7

### Goal

Add GitHub Actions CI for Project 2 so external reviewers can see automated
quality checks for the Agent Toolkit MCP package.

### Milestone 7 — CI for Agent Toolkit MCP

Implemented:

- GitHub Actions workflow for Project 2 scaffold, MCP server and CLI checks
- path-filtered workflow triggers for Project 2, shared repository docs and
  the Project 2 CI workflow file
- local `run_ci_locally.sh` mirror script for reviewer-friendly verification
- scaffold check coverage for the CI workflow, local CI script and Milestone 7
  prompt-history file
- prompt-history entry:
  `02-agent-toolkit-mcp/docs/prompt-history/milestone-07-ci.md`

Behavior:

- local and deterministic checks only
- read-only CLI smoke checks against Project 1 artifacts
- no Project 1 code or runtime behavior changes
- no external API calls
- no secrets required
- no Docker services
- no deployment or package publishing
- no destructive tools

Verification:

```text
Project 2 scaffold checks passed
32 MCP server tests passing
ruff clean
mypy clean
bash script syntax clean
git diff --check clean
local CI mirror passed
CLI smoke checks generated pretty JSON demo-readiness and runtime-clean evidence
```

Project 2 permanent rules:

- every new function, method and class created by Codex must include a clear Google-style docstring
- every milestone must update relevant README files
- every milestone must update this handoff
- every milestone must create or update its own prompt-history file under `02-agent-toolkit-mcp/docs/prompt-history/`
- prompt-history files must include the full prompt, expected verification, result summary, verification results and commit/PR placeholders
- use branch-based workflow and do not assume direct work on `main`
- do not hardcode secrets or add real external credentials
- do not modify Project 1 code unless explicitly requested

---

## 13. Demo Commands

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

Run Project 2 local agent adapter demos:

```bash
02-agent-toolkit-mcp/scripts/demo_mcp_tools.sh
02-agent-toolkit-mcp/scripts/run_project1_tool_review.sh
```

Show Project 2 local permission profiles:

```bash
02-agent-toolkit-mcp/scripts/show_permission_profiles.sh
```

Run Project 2 CI locally:

```bash
02-agent-toolkit-mcp/scripts/run_ci_locally.sh
```

Run Project 2 CLI tool evidence locally:

```bash
cd 02-agent-toolkit-mcp/mcp-server
uv run agent-toolkit-mcp generate-demo-brief ../../01-ai-marketing-ops-agent --pretty
```

---

## 14. Future Milestones

```text
Project 2     — Milestone 8: Claude Code hook examples or local runtime packaging
Project 3     — AgentOps Control Tower
```
