# Architecture

AgentOps Control Tower is planned as a local observability and governance layer
for AI automation workflows.

The control tower will not replace workflow execution. It will aggregate local
evidence produced by other projects and present it in a form that supports
inspection, review and operational decision-making.

## Planned Architecture

```text
Project 1 workflow artifacts
  - run-history JSONL
  - approval requests JSONL
  - generated reports
        ↓
Project 2 local tool evidence
  - MCP-style tool outputs
  - CLI smoke output
  - guardrail check output
        ↓
Project 3 local ingestion models and parsers
        ↓
deterministic summaries and timeline generation
        ↓
control tower views, summaries and audit records
```

## Current Implementation

Milestone 2 implemented typed local ingestion records and deterministic parsers
for selected Project 1 and Project 2 artifacts. Milestone 3 adds deterministic
summary and timeline generation over typed `IngestionResult` objects.

Implemented parser inputs:

- Project 1 run-history JSONL
- Project 1 approval requests JSONL
- Project 1 deterministic Markdown reports
- saved Project 2 CLI JSON evidence
- saved Project 2 guardrail output text

The project still does not implement persistence, dashboards, UI, schedulers or
external integrations.

Implemented derived views:

- `AgentOpsSummary`
- `AgentOpsTimeline`
- `AgentOpsControlTowerView`

The control tower view combines ingestion records, summary counts and timeline
events without persisting data or starting a service.

## Design Principles

- Local-first: read local artifacts before considering any external source.
- Deterministic: normalize and classify observable events with predictable code.
- Auditable: preserve enough source context to explain operational conclusions.
- Non-destructive: inspect workflow evidence without deleting or mutating it.
- Portfolio-focused: demonstrate AgentOps thinking without overclaiming a
  deployed production control plane.
- User-facing ingestion errors: malformed local files produce typed errors
  instead of unhandled exceptions.
- Deterministic derived views: health status and recommended actions are
  generated from local typed records only.

## Relationship to Earlier Projects

Project 1 produces business workflow artifacts. Project 2 provides local tools,
CLI evidence and guardrails for inspecting those artifacts. Project 3 will
aggregate and observe the resulting signals.
