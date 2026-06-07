# Observability Model

Project 3 will model operational signals from local AI automation workflows.

The model is planned around the facts that a reviewer or operator needs in
order to understand workflow health, governance state and auditability.

## Implemented Record Types

Milestone 2 adds typed records for:

- `WorkflowRunRecord`
- `ApprovalRequestRecord`
- `ReportSummaryRecord`
- `ToolEvidenceRecord`
- `GuardrailEvidenceRecord`
- `IngestionResult`
- `IngestionWarning`
- `IngestionError`

These records are ingestion outputs for future summaries and dashboards. They
are not a database schema and do not provide UI behavior.

## Implemented Derived Views

Milestone 3 adds:

- `AgentOpsTimelineEvent`
- `AgentOpsTimeline`
- `WorkflowRunSummary`
- `ApprovalSummary`
- `ReportHealthSummary`
- `ToolEvidenceSummary`
- `GuardrailSummary`
- `AgentOpsSummary`
- `AgentOpsControlTowerView`

Timeline event types:

- `workflow_run`
- `approval_request`
- `report_summary`
- `tool_evidence`
- `guardrail_evidence`
- `ingestion_warning`
- `ingestion_error`

Overall health status is derived deterministically:

- `error` when ingestion errors exist
- `needs_attention` when failed or blocked guardrails, pending approvals,
  failed workflow runs or human-review report signals exist
- `warning` when ingestion warnings or unknown statuses exist
- `healthy` otherwise

Recommended actions are deterministic local follow-ups. They are not
LLM-generated recommendations.

## Implemented Export Views

Milestone 4 exposes the derived views through a local CLI:

- `summary` prints `AgentOpsSummary`-compatible JSON.
- `timeline` prints `AgentOpsTimeline`-compatible JSON.
- `export-report` renders a deterministic Markdown report over the combined
  local control tower view.

The Markdown report includes local source paths, overall health, summary
sections, ingestion warnings and errors, timeline events, deterministic
recommended actions and clear limitations or missing-data notes.

CLI exit behavior is tied to deterministic ingestion results:

- ingestion errors return non-zero
- malformed JSON or JSONL returns non-zero
- report write conflicts return non-zero unless `--overwrite` is used
- warnings alone do not return non-zero

## Signal Types

- Workflow runs: run identifiers, timestamps, status and produced artifacts.
- Approval states: pending, approved, rejected or review-required work.
- Failure records: validation errors, runtime failures and failed checks.
- Retry metadata: retry attempts, cadence and eventual outcome.
- Notification status: whether a notification was skipped, pending or sent by a
  local/mock provider.
- LLM metadata: token usage and cost metadata when available from local
  workflow outputs.
- Agent actions: local tool, command or guardrail activity when available.
- Guardrail outcomes: pass/fail/block/unknown results from local safety and
  audit check text.

## Current Non-Goals

Project 3 does not yet implement storage, frontend dashboard views, alerting, a
scheduler, external integrations or a deployed AgentOps platform. Those will be
introduced only if future milestones explicitly add them.

## Auditability Goals

Future implementations should preserve enough evidence to answer:

- What ran?
- What changed state?
- What failed?
- What required human review?
- Which guardrails ran?
- Which artifacts support the conclusion?
