# Architecture Decisions

Initial decisions:

- Use Python 3.12+ with `uv`.
- Use Pydantic v2 for typed input and workflow data validation.
- Keep retry, rate limiting and validation deterministic.
- Defer Playwright implementation until mock services and workflow contracts are defined.

## Deterministic Aggregation Before LLM Analysis

Decision: aggregate panel rows, Campaign REST API data and Analytics GraphQL
metrics with deterministic Python code before any LLM step.

Reasoning:

- Joining by `campaign_id` is deterministic application logic.
- Missing data and metric mismatches must be explicit and testable.
- An LLM should not decide which numeric source is correct.
- Preserving all source records keeps auditability for later reports.

Consequences:

- `CampaignSnapshot` stores panel, REST and GraphQL data separately.
- Data quality flags drive `requires_human_review`.
- Missing or mismatched records remain visible in output.
- Later anomaly detection and report generation can build on validated
  snapshots without re-fetching source data.

## Deterministic Anomaly Detection Before Report Generation

Decision: detect campaign anomalies with explicit Python rules over
`CampaignSnapshot` objects before any LLM interpretation or Markdown report
generation.

Reasoning:

- CPA, ROI, threshold checks and data quality escalation are deterministic
  business logic.
- Findings must be typed and testable so later reports can cite exact evidence.
- An LLM should not invent missing metrics or decide whether source mismatches
  are acceptable.
- Human review requirements should be represented as structured data before any
  downstream action is taken.

Consequences:

- `AnomalyDetector` is synchronous and has no external service calls.
- `AnomalyThresholds` provides safe defaults and explicit overrides.
- `AnomalyFinding` preserves `campaign_id`, severity, anomaly type, message,
  source and source evidence.
- Later LLM and report-writing milestones should consume anomaly findings rather
  than recalculate business rules.

## Deterministic Markdown Report Writer Before LLM Interpretation

Decision: generate the first Markdown report with deterministic Python code over
`CampaignSnapshot` and `AnomalyFinding` objects.

Reasoning:

- Report structure, ordering and missing-data handling must be testable.
- The writer should not consume raw scraped rows, raw REST responses or raw
  GraphQL responses after aggregation has produced validated business objects.
- Missing metrics must remain explicit instead of being inferred for readability.
- Human review gates should be visible before any LLM-written interpretation or
  external notification is added.

Consequences:

- `MarkdownReportWriter` and `generate_markdown_report` return plain Markdown
  strings with no external dependencies.
- `ReportMetadata` lets tests and workflow code provide a stable title and
  timestamp.
- Findings are sorted by severity, campaign ID, anomaly type, message and
  source; campaigns are sorted by `campaign_id`.
- Future LLM output should be layered after this deterministic report baseline
  and clearly separated from facts and rule-based recommendations.

## Deterministic Workflow Orchestration Before Agentic Workflow

Decision: implement a deterministic daily report workflow that connects the
scraper, typed API clients, aggregator, anomaly detector and Markdown report
writer before adding any LLM interpretation or notification delivery.

Reasoning:

- The end-to-end pipeline should be executable and testable with fakes at every
  boundary.
- Report generation must remain reproducible before LLM-written summaries are
  layered on top.
- Partial source-data failures should continue through existing data quality
  flags instead of becoming workflow failures.
- Only unrecoverable steps, such as scraper failure, aggregation failure,
  detector failure, report writer failure or report file persistence failure,
  should raise workflow errors.
- Optional project-management tasks should be deterministic and limited to
  critical or human-review findings.

Consequences:

- `DailyMarketingReportWorkflow` uses dependency injection for scraper, clients,
  detector, report writer and optional task client.
- `DailyMarketingReportResult` returns run metadata, counts, snapshots,
  findings, report path, created tasks and task creation errors.
- Reports are saved locally under `reports/` with deterministic timestamped
  filenames and are ignored by git except for `.gitkeep`.
- Task creation deduplicates by `(campaign_id, anomaly_type)` within a single
  run.
- LLM analysis and external notifications remain separate later milestones.

## JSONL Local Run Recording Before External Observability

Decision: persist daily workflow run records locally as JSONL before adding any
external monitoring, database or notification integration.

Reasoning:

- Run history should be deterministic, inspectable and easy to test in a local
  portfolio environment.
- JSONL gives append-only behavior without introducing a database dependency for
  this milestone.
- The workflow should record enough operational metadata for auditability while
  avoiding raw source payloads, environment variables and secrets.
- Malformed history lines should surface explicitly instead of being silently
  ignored.

Consequences:

- `WorkflowRunRecord` is the typed persisted observability contract.
- `LocalRunRecorder` appends records to `run-history/workflow-runs.jsonl` and
  reads recent runs or a specific run ID.
- Successful workflow runs and unrecoverable workflow failures are recorded when
  a recorder is configured.
- Failed workflow recording preserves original exception behavior by re-raising
  the original `WorkflowExecutionError`.
- Failure messages are sanitized for common inline credential shapes before
  they are persisted.
- Generated run history is ignored by git except for `run-history/.gitkeep`.

## Optional LLM Interpretation After Deterministic Reporting

Decision: add an optional LLM interpretation layer after deterministic
aggregation, anomaly detection, Markdown reporting and run recording contracts
exist.

Reasoning:

- The LLM should interpret business meaning, not collect, join, validate or
  recalculate data.
- Prompts must use validated `CampaignSnapshot`, `AnomalyFinding`,
  deterministic report summary and optional `WorkflowRunRecord` inputs only.
- Missing metrics, source mismatches and human-review flags must stay explicit
  because they are audit and approval signals.
- Tests should not call external LLM APIs, require API keys or depend on
  nondeterministic model output.

Consequences:

- `marketing_ops_agent.llm` exposes typed request/result/recommendation/token
  usage models.
- `LLMInterpretationProvider` is a Protocol so future real providers can be
  added without changing workflow code.
- `DeterministicMockLLMProvider` is the default provider for tests and local
  no-key runs.
- Prompt construction redacts common inline secret shapes and includes
  anti-hallucination rules.
- `DailyMarketingReportWorkflow` can call an optional interpreter but does not
  require LLM output for workflow success.
- LLM recommendations remain separate from deterministic recommended actions
  in the Markdown report.

## Local Human Approval Queue Before Notifications

Decision: persist human approval requests locally before adding Slack,
Telegram, email or other notification delivery.

Reasoning:

- Critical findings, human-review flags and high-risk LLM recommendations
  should require explicit human approval before external follow-up.
- Approval records must be deterministic, auditable and easy to inspect in a
  local portfolio environment.
- JSONL gives append-only history without adding a database dependency.
- Malformed approval records should surface explicitly because approval state
  is an audit artifact.

Consequences:

- `ApprovalRequest`, `ApprovalDecision`, `ApprovalStatus`,
  `ApprovalRiskLevel` and `ApprovalSource` define the approval contract.
- `LocalApprovalStore` persists approval states under
  `approval-requests/approval-requests.jsonl`.
- `ApprovalService` creates pending approval requests for critical findings,
  human-review findings and high-risk LLM recommended actions.
- Workflow integration is non-blocking; approval persistence failures are
  logged and do not replace deterministic report generation.
- Generated approval files are ignored by git except for
  `approval-requests/.gitkeep`.
