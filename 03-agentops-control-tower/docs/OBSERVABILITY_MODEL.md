# Observability Model

Project 3 will model operational signals from local AI automation workflows.

The model is planned around the facts that a reviewer or operator needs in
order to understand workflow health, governance state and auditability.

## Planned Signal Types

- Workflow runs: run identifiers, timestamps, status and produced artifacts.
- Approval states: pending, approved, rejected or review-required work.
- Failure records: validation errors, runtime failures and failed checks.
- Retry metadata: retry attempts, cadence and eventual outcome.
- Notification status: whether a notification was skipped, pending or sent by a
  local/mock provider.
- LLM metadata: token usage and cost metadata when available from local
  workflow outputs.
- Agent actions: local tool, command or guardrail activity when available.
- Guardrail outcomes: pass/fail results from local safety and audit checks.

## Non-Goals for the Scaffold

The scaffold does not yet implement event schemas, parsers, storage, dashboard
views or alerting. Those will be introduced in later milestones.

## Auditability Goals

Future implementations should preserve enough evidence to answer:

- What ran?
- What changed state?
- What failed?
- What required human review?
- Which guardrails ran?
- Which artifacts support the conclusion?
