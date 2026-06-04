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
Project 3 local ingestion models
        ↓
deterministic normalization and aggregation
        ↓
control tower views, summaries and audit records
```

## Initial Boundaries

Milestone 1 creates only the scaffold and documentation. It does not implement
ingestion, persistence, dashboards, UI or external integrations.

## Design Principles

- Local-first: read local artifacts before considering any external source.
- Deterministic: normalize and classify observable events with predictable code.
- Auditable: preserve enough source context to explain operational conclusions.
- Non-destructive: inspect workflow evidence without deleting or mutating it.
- Portfolio-focused: demonstrate AgentOps thinking without overclaiming a
  deployed production control plane.

## Relationship to Earlier Projects

Project 1 produces business workflow artifacts. Project 2 provides local tools,
CLI evidence and guardrails for inspecting those artifacts. Project 3 will
aggregate and observe the resulting signals.
