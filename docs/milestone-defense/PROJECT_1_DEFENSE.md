# Project 1 Technical Defense

Project 1 is the AI Marketing Operations Agent. It is portfolio-ready and
case-study-ready. The core defense is that deterministic automation owns the
workflow facts, while optional LLM interpretation is downstream, bounded and
never the source of truth.

## Milestone 1 — Initial Scaffold

### What was built

The initial Python 3.12+ project scaffold was created under
`01-ai-marketing-ops-agent/`. It included `pyproject.toml`, project README,
project `AGENTS.md`, `.env.example`, docs placeholders, a skill folder, basic
Pydantic models, retry and rate limiter utilities and minimal tests.

### Why this milestone existed

Engineering-wise, this created a typed, testable foundation before adding
workflow complexity. Portfolio-wise, it showed that the project would be built
as production-oriented automation rather than a one-off script.

### What the prompt enforced

The prompt enforced small initial scope, Python 3.12+, `uv`, Pydantic v2,
pytest, ruff and mypy readiness. It explicitly avoided the full Playwright
workflow, hardcoded secrets and premature runtime behavior. It required docs,
configuration examples and minimal verification.

### Key technical decisions

The important decision was to start with utilities and models before services
or browser automation. Retry and rate limiter utilities were introduced early
because external-call boundaries would become central later.

### How to defend it in an interview

Say: "I started by creating the project skeleton, typed models, local config
shape and basic reliability utilities. That gave later milestones a stable
place to add services, clients and workflow code without mixing setup work with
business logic."

### Likely recruiter questions

- Why did you start with a scaffold instead of the workflow?
- Why use Pydantic so early?
- Was this already production code?

### Strong answers

- Starting with the scaffold kept the later work organized and testable.
- Pydantic made input and output contracts explicit from the beginning.
- It was not production-deployed code; it was a production-oriented local
  foundation with tests, typing and config hygiene.

### Verification evidence

Recorded verification was 9 tests passing, ruff clean and mypy clean.

### Limitations

This milestone did not implement mock services, Playwright scraping, service
clients, aggregation, reporting or workflow execution.

### What came next

The next milestone added local mock services so later integrations could be
tested without real credentials or external SaaS dependencies.

## Milestone 2 — Local Mock Services

### What was built

Local FastAPI mock services were added for the marketing panel, Campaign REST
API, Analytics GraphQL API and Project Management REST API. Docker Compose
support was included for local service startup and validation.

### Why this milestone existed

Engineering-wise, the mocks created realistic integration surfaces without
external dependencies. Portfolio-wise, they made the demo reviewer-safe and
runnable without secrets.

### What the prompt enforced

The prompt enforced local-only services, no real external service calls, no
real credentials and explicit verification. It kept the milestone focused on
mock surfaces rather than clients, scraping or workflow orchestration.

### Key technical decisions

The marketing panel was deliberately HTML-only to justify Playwright later.
Campaign and project management data used REST, while analytics used GraphQL,
so the project could demonstrate choosing the right integration method.

### How to defend it in an interview

Say: "The mock services are not fake shortcuts; they are controlled local
stand-ins for real integration boundaries. They let a recruiter run the system
without credentials while still seeing REST, GraphQL and browser-only surfaces."

### Likely recruiter questions

- Why build mock services instead of using real APIs?
- Why include both REST and GraphQL?
- Why make the panel browser-only?

### Strong answers

- Real APIs would require secrets and external accounts; mocks keep the demo
  safe and reproducible.
- REST and GraphQL show different integration patterns and client contracts.
- The browser-only panel creates a legitimate reason to use Playwright only
  where no API exists.

### Verification evidence

Recorded verification was 19 tests passing, ruff clean, mypy clean and Docker
Compose config validation.

### Limitations

The services are local mocks, not real marketing, analytics or task-management
providers.

### What came next

Typed service clients were added to consume the REST and GraphQL services
through explicit contracts.

## Milestone 3 — Typed Service Clients

### What was built

Typed `httpx` clients were implemented for campaign metadata, analytics
metrics and project-management tasks. The clients introduced service-boundary
error handling and typed responses.

### Why this milestone existed

Engineering-wise, it separated API integration from downstream business logic.
Portfolio-wise, it demonstrated API-first automation before browser
automation.

### What the prompt enforced

The prompt enforced using API integration where APIs existed, not using
Playwright for API-backed services, avoiding hardcoded secrets or production
URLs and verifying the client behavior with tests, linting and typing.

### Key technical decisions

Clients were kept distinct by service responsibility. This avoided mixing REST,
GraphQL and task creation behavior into a single workflow object.

### How to defend it in an interview

Say: "The clients keep network integration behind typed boundaries. The
workflow later consumes validated client outputs instead of ad hoc HTTP
responses."

### Likely recruiter questions

- Why not call APIs directly from the workflow?
- Why use `httpx` clients?
- How did you avoid hardcoded endpoints?

### Strong answers

- Direct calls in the workflow would make testing and error handling harder.
- `httpx` supports async HTTP and clean timeout/error boundaries.
- Endpoints are supplied through configuration and local defaults, not real
  production credentials.

### Verification evidence

Recorded verification was 28 tests passing, ruff clean and mypy clean.

### Limitations

The clients target local mock services. They do not integrate with real
third-party marketing platforms.

### What came next

The next milestone added Playwright scraping for the one surface that
deliberately had no API.

## Milestone 4 — Playwright Marketing Panel Scraper

### What was built

An async Playwright scraper was implemented for the local marketing panel. It
handled local login, deterministic mock 2FA and typed dashboard row extraction.

### Why this milestone existed

Engineering-wise, it demonstrated browser automation only where an API was not
available. Portfolio-wise, it showed practical Playwright usage without unsafe
CAPTCHA bypass or real credentials.

### What the prompt enforced

The prompt enforced no CAPTCHA bypass, no hardcoded real credentials and a
local mock target. It kept Playwright limited to the panel and required tests,
linting and typing.

### Key technical decisions

The scraper returns typed rows rather than raw HTML. The 2FA field is a
deterministic local mock, not a real security bypass.

### How to defend it in an interview

Say: "I used Playwright because the panel intentionally has no API. I did not
use browser automation where REST or GraphQL existed, and I did not implement
CAPTCHA bypass."

### Likely recruiter questions

- Why use Playwright at all?
- Is this scraping a real system?
- Did you bypass CAPTCHA or real 2FA?

### Strong answers

- Playwright is appropriate for the browser-only panel.
- It targets a local mock panel for reviewer-safe execution.
- No. The 2FA is deterministic local mock behavior, and there is no CAPTCHA
  bypass.

### Verification evidence

Recorded verification was 33 tests passing, ruff clean and mypy clean.

### Limitations

The scraper does not handle arbitrary real-world panel changes or production
authentication flows.

### What came next

The next milestone aggregated scraped rows with API data into a typed business
object.

## Milestone 5 — Deterministic Data Aggregation

### What was built

`CampaignSnapshot`, deterministic aggregation and data quality flags were
implemented. The aggregator joined scraped rows, Campaign REST metadata and
Analytics GraphQL metrics by campaign ID.

### Why this milestone existed

Engineering-wise, it created the validated business object used by downstream
modules. Portfolio-wise, it showed that source disagreements are preserved
rather than hidden.

### What the prompt enforced

The prompt enforced no LLM calls, no invented missing metrics and no silent
dropping of mismatched rows. It required explicit data quality handling and
verification.

### Key technical decisions

Each snapshot preserves source records separately and attaches flags such as
missing metadata, missing analytics metrics, spend mismatch, conversions
mismatch, revenue mismatch, stale data and human review.

### How to defend it in an interview

Say: "Aggregation is deterministic and audit-friendly. If sources disagree,
the system records that disagreement as a data quality flag instead of picking
a silent source of truth."

### Likely recruiter questions

- Why create `CampaignSnapshot`?
- What happens when data is missing?
- Did the LLM fix mismatches?

### Strong answers

- `CampaignSnapshot` is the stable business object for later analysis.
- Missing or inconsistent data is represented with flags and review notes.
- No. The LLM is not involved in aggregation.

### Verification evidence

Recorded verification was 41 tests passing, ruff clean and mypy clean.

### Limitations

Aggregation uses local mock data and does not implement a production data
warehouse or database.

### What came next

Deterministic anomaly detection was added over validated snapshots.

## Milestone 6 — Deterministic Anomaly Detection

### What was built

`AnomalyFinding` and deterministic anomaly detection were implemented for
performance thresholds and data quality flag mapping.

### Why this milestone existed

Engineering-wise, it separated rule-based analysis from aggregation and
reporting. Portfolio-wise, it showed that factual anomaly counts are not
outsourced to an LLM.

### What the prompt enforced

The prompt enforced consuming `CampaignSnapshot` objects instead of raw rows or
raw payloads, not inferring missing metrics and verifying deterministic rules.

### Key technical decisions

Rules cover high spend with low conversions, CPA above threshold, ROI below
threshold and data quality findings. CPA and ROI are calculated only when the
required denominators are valid.

### How to defend it in an interview

Say: "The anomaly detector is deterministic. It uses explicit thresholds and
source evidence from validated snapshots, so findings can be reproduced and
tested."

### Likely recruiter questions

- Why not ask an LLM to find anomalies?
- How are thresholds handled?
- What happens with missing metrics?

### Strong answers

- Anomaly detection is factual business logic and should be reproducible.
- Thresholds are modeled and can be overridden at detector construction time.
- Missing metrics are not inferred; they become data quality findings when
  appropriate.

### Verification evidence

Recorded verification was 51 tests passing, ruff clean and mypy clean.

### Limitations

The rules are intentionally simple deterministic examples, not a trained
statistical anomaly model.

### What came next

The next milestone rendered findings and snapshots into a deterministic
Markdown report.

## Milestone 7 — Deterministic Markdown Reporting

### What was built

A deterministic Markdown report writer was implemented over
`CampaignSnapshot` and `AnomalyFinding` inputs. It renders summary, anomaly,
data quality, human review, snapshot table, recommended action and limitation
sections.

### Why this milestone existed

Engineering-wise, it created a human-readable artifact from typed workflow
outputs. Portfolio-wise, it gave recruiters and reviewers a concrete report to
inspect.

### What the prompt enforced

The prompt enforced no LLM calls, no anomaly-rule changes, no inferred missing
data and verification through tests, linting and typing.

### Key technical decisions

The report is generated from typed deterministic objects only. It sorts rows
and findings predictably and shows unavailable values as missing rather than
inventing replacements.

### How to defend it in an interview

Say: "The report is deterministic evidence. A reviewer can trace its content
back to snapshots and findings, not to an LLM narrative."

### Likely recruiter questions

- Why Markdown?
- Does the report come from the LLM?
- How are missing values displayed?

### Strong answers

- Markdown is easy for reviewers to inspect and version as an artifact.
- No. The baseline report is deterministic.
- Missing values are shown explicitly as missing.

### Verification evidence

Recorded verification was 61 tests passing, ruff clean and mypy clean.

### Limitations

The report is a local Markdown artifact, not a dashboard or BI integration.

### What came next

The next milestone orchestrated scraping, aggregation, detection and reporting
into a daily workflow.

## Milestone 8 — Workflow Orchestration

### What was built

`DailyMarketingReportWorkflow`, a typed workflow result model, deterministic
task requests and local report saving were implemented.

### Why this milestone existed

Engineering-wise, it connected existing modules without moving their logic into
one monolith. Portfolio-wise, it demonstrated a complete local workflow run.

### What the prompt enforced

The prompt enforced no external notification integrations, no approval bypass
for sensitive work and no replacement of deterministic module behavior by
orchestration.

### Key technical decisions

The workflow uses dependency injection for scraper, clients, detector, report
writer and optional task client. Task creation is optional and deterministic,
with duplicate suppression inside a run.

### How to defend it in an interview

Say: "The workflow coordinates components; it does not own all business logic.
That keeps scraping, aggregation, anomaly detection and reporting independently
testable."

### Likely recruiter questions

- What does orchestration add?
- How do you test the workflow?
- Are tasks created automatically?

### Strong answers

- It defines execution order and typed run output.
- Dependencies can be replaced with fakes in tests.
- Optional deterministic tasks are created only for critical or human-review
  findings when a task client is provided.

### Verification evidence

Recorded verification was 67 tests passing, ruff clean and mypy clean.

### Limitations

This milestone did not add persistent run recording or real notifications.

### What came next

Persistent run recording and observability were added.

## Milestone 9 — Persistent Run Recording and Observability

### What was built

`WorkflowRunRecord`, `LocalRunRecorder`, JSONL run history and workflow
integration were implemented. Run records include status, timings, counts,
report path, data quality summaries, task metadata and sanitized failure data.

### Why this milestone existed

Engineering-wise, it added auditability and failure visibility. Portfolio-wise,
it showed that every workflow run can be inspected after execution.

### What the prompt enforced

The prompt enforced no external observability service, no stored secrets, no
committed generated run-history files and explicit verification.

### Key technical decisions

JSONL was chosen as a simple local audit format. Malformed run-history lines
raise explicit errors instead of being skipped silently.

### How to defend it in an interview

Say: "Run history makes the workflow observable. It records what ran, what was
produced, what failed and what required review without depending on an external
service."

### Likely recruiter questions

- Why JSONL instead of a database?
- What happens when recording fails?
- Are failures sanitized?

### Strong answers

- JSONL is enough for local portfolio auditability and easy reviewer
  inspection.
- Recorder persistence errors are logged so they do not replace the original
  workflow result.
- Yes. Failure type and message fields are sanitized.

### Verification evidence

Recorded verification was 77 tests passing, ruff clean and mypy clean.

### Limitations

There is no production observability backend, dashboard or database.

### What came next

Optional LLM interpretation was added downstream of deterministic outputs.

## Milestone 10 — Optional LLM Interpretation Layer

### What was built

An optional, mockable LLM interpretation layer was implemented over validated
snapshots, findings, deterministic report context and optional run records. It
includes prompt safety rules and token usage capture when available.

### Why this milestone existed

Engineering-wise, it demonstrated controlled LLM use without letting the model
own workflow facts. Portfolio-wise, it showed practical AI use beyond a
chatbot: interpretation and recommendations over validated data.

### What the prompt enforced

The prompt enforced optional behavior, downstream placement, fail-safe
handling, validated inputs, no replacement of deterministic findings and safe
prompt construction.

### Key technical decisions

The provider contract supports a deterministic mock provider for local no-key
runs. Prompt payloads are sanitized and instruct the model not to invent
metrics, trends, causes, credentials or source data.

### How to defend it in an interview

Say: "The LLM is intentionally downstream. It can summarize and recommend, but
it cannot scrape, aggregate, validate metrics or change anomaly counts."

### Likely recruiter questions

- What does the LLM do?
- What prevents hallucinated metrics?
- Does the workflow fail if the LLM fails?

### Strong answers

- It interprets deterministic outputs and can produce narrative summaries and
  recommended actions.
- Prompt rules and typed inputs require it to use validated data only.
- No. Interpretation is optional and fail-safe.

### Verification evidence

Recorded verification was 84 tests passing, ruff clean and mypy clean.

### Limitations

The local provider is deterministic/mock. Real provider use would require
careful credential and cost handling.

### What came next

The next milestone added human approval records for sensitive outputs.

## Milestone 11 — Human Approval Flow

### What was built

Approval models, local JSONL approval storage, deterministic approval request
creation and workflow/run-history integration were implemented. Requests are
created for critical findings, human-review findings and high-risk LLM
recommendations.

### Why this milestone existed

Engineering-wise, it added a governance gate before sensitive automated
follow-up. Portfolio-wise, it demonstrated that automation can be powerful
without silently approving risky actions.

### What the prompt enforced

The prompt enforced no stored credentials, no raw scraped rows, no raw REST or
GraphQL responses and no committed generated approval files. It required
deduplication, safe persistence and verification.

### Key technical decisions

High-risk actions are never auto-approved. Approval requests store sanitized
text, run ID, campaign ID, source type, risk level and evidence, not raw source
payloads.

### How to defend it in an interview

Say: "The approval layer separates finding a problem from authorizing a
sensitive action. Pending approvals are explicit local records and are not
treated as completed work."

### Likely recruiter questions

- What requires approval?
- Can high-risk actions be auto-approved?
- Where are approvals stored?

### Strong answers

- Critical findings, human-review findings and high-risk LLM recommendations.
- No. High-risk actions remain pending until reviewed.
- Locally in JSONL under `approval-requests/`, with generated files ignored by
  git.

### Verification evidence

Recorded verification was 96 tests passing, ruff clean and mypy clean.

### Limitations

Approval storage is local JSONL. There is no shared approval UI or production
approval service.

### What came next

Notifications were made approval-aware and kept mock/local.

## Milestone 12 — Approval-Aware Notifications

### What was built

Notification models, a provider contract, deterministic mock provider,
notification service and optional workflow integration were implemented.
Notifications include workflow summary fields and pending approval request IDs
when present.

### Why this milestone existed

Engineering-wise, it introduced post-workflow communication without bypassing
approval gates. Portfolio-wise, it showed how to design notification behavior
without prematurely adding real Slack, Telegram or email integrations.

### What the prompt enforced

The prompt enforced no real Slack, Telegram, email or external notification
API calls in tests, no hardcoded notification credentials and no claims that
sensitive pending recommendations were approved work.

### Key technical decisions

The current provider is deterministic and mock-only. Notification content
consumes workflow metadata, not raw source payloads or sensitive action
recommendations.

### How to defend it in an interview

Say: "Notifications are summary-only and approval-aware. They can mention that
approval requests exist, but they explicitly do not present pending approvals
as approved actions."

### Likely recruiter questions

- Does it send Slack or email?
- What information is sent?
- Can notification failures break the workflow?

### Strong answers

- No. Project 1 uses a deterministic mock provider.
- Run ID, report path, counts, review status and pending approval IDs.
- No. Notification delivery is optional and fail-safe.

### Verification evidence

Recorded verification was 105 tests passing, ruff clean and mypy clean.

### Limitations

Real Slack, Telegram and email providers are intentionally not implemented.

### What came next

CI/CD was added for repeatable project verification.

## Milestone 13 — CI/CD

### What was built

Project 1 GitHub Actions CI and a local CI mirror script were added. Checks
cover dependency sync, Playwright Chromium install, pytest, ruff, mypy, Docker
Compose config validation and Bash syntax checks.

### Why this milestone existed

Engineering-wise, CI made quality checks repeatable. Portfolio-wise, it gave
reviewers visible evidence that the project can be verified without manual
guesswork.

### What the prompt enforced

The prompt enforced no real external APIs, no real secrets, no real
notifications, no long-lived Compose services, no committed runtime files and
no deployment, image publishing or cloud infrastructure.

### Key technical decisions

CI is path-filtered and local-safe. It validates Compose configuration without
starting long-running services or requiring credentials.

### How to defend it in an interview

Say: "CI proves the local workflow layers stay testable. It checks tests,
linting, typing, browser runtime installation, Compose configuration and shell
scripts without deploying or calling real external services."

### Likely recruiter questions

- What does CI verify?
- Does CI need secrets?
- Why no deployment?

### Strong answers

- Tests, ruff, mypy, Playwright install, Compose config and script syntax.
- No. The workflow is designed to run locally without real credentials.
- Deployment was out of scope; the portfolio demonstrates local automation
  architecture and verification first.

### Verification evidence

Recorded verification was 105 tests passing, ruff clean, mypy clean, Docker
Compose config validation, Bash syntax clean and `git diff --check` clean.

### Limitations

CI does not deploy, publish images or validate production provider credentials.

### What came next

The project received documentation and report-readability polish for portfolio
presentation.

## Milestone 14 — Report Data Quality Polish

### What was built

The deterministic Markdown report rendering was polished so Data Quality
Issues are grouped by campaign. The update preserves flags, notes, related
finding types and severities and human-review status.

### Why this milestone existed

Engineering-wise, it improved report readability without changing workflow
truth. Portfolio-wise, it made the report easier for a recruiter to scan and
discuss.

### What the prompt enforced

The prompt enforced no business logic changes, no anomaly detection changes,
no data quality flag changes, no workflow behavior changes, no persistence
format changes, no new features and no modification of generated reports under
`reports/`.

### Key technical decisions

The polish stayed in deterministic rendering. It did not alter how findings or
data quality flags are generated.

### How to defend it in an interview

Say: "This was presentation polish only. The data quality facts stayed the
same; the report became easier to read by grouping issues by campaign."

### Likely recruiter questions

- Did this change anomaly logic?
- Why polish reports after CI?
- Were generated reports committed?

### Strong answers

- No. It changed deterministic rendering readability only.
- A portfolio artifact must be technically correct and easy to review.
- No. Generated runtime reports remain ignored by git.

### Verification evidence

The prompt-history result records no business logic, anomaly detection,
workflow behavior or persistence format changes. Verification expectations
included normal checks and `git diff --check`.

### Limitations

This was not a new feature and did not add dashboards or external reporting.

### What came next

Reviewer-facing local run and demo documentation were prepared.

## Milestone 15 — Project 1 Demo Documentation Package

### What was built

Reviewer-friendly scripts and documentation were added for starting services,
running the workflow, running with mock LLM interpretation, cleaning runtime
artifacts and running quality checks. The root docs include a Project 1 case
study, demo script, requirements coverage matrix and prompt-history index.

### Why this milestone existed

Engineering-wise, it made the project reproducible for external reviewers.
Portfolio-wise, it turned the implementation into a defensible case study.

### What the prompt enforced

The related prompt enforced no notification integration implementation and no
runtime behavior changes. The documentation also had to keep safe demo
credentials explicit and generated-output inspection commands clear.

### Key technical decisions

The scripts use local mock defaults and allow environment overrides. The demo
docs emphasize deterministic workflow artifacts and avoid claiming real
external provider integrations.

### How to defend it in an interview

Say: "The demo package lets a reviewer run and inspect the project without
knowing my local aliases. It documents exactly what to show: reports, run
history, approvals, optional mock LLM interpretation, mock notifications and
CI."

### Likely recruiter questions

- Why spend time on demo scripts?
- Are the credentials real?
- What should a reviewer inspect?

### Strong answers

- A portfolio project needs reproducible review steps, not just code.
- No. They are local mock credentials.
- The report, run-history JSONL, approval-request JSONL, case study and CI
  checks.

### Verification evidence

The repository includes local helper scripts, Project 1 case study, demo
script, requirements coverage matrix and prompt-history records. Project 1's
final recorded verification remains 105 tests passing with ruff, mypy, Compose
and script checks clean.

### Limitations

The demo package does not add production deployment or real notification
providers.

### What came next

Project 2 built the reusable agent-tooling layer around Project 1 artifacts.

