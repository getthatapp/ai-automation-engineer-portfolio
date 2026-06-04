# Safety Model

Project 3 is local-first and deterministic.

The control tower is intended to observe workflow evidence, not execute
business actions or bypass approval flows.

## Current Scaffold Guarantees

- No external APIs are called.
- No secrets are required.
- No dependencies are added.
- No backend ingestion is implemented.
- No dashboard or UI is implemented.
- No Project 1 or Project 2 runtime behavior is changed.

## Planned Safety Principles

- Read-only artifact inspection by default.
- Explicit verification commands for every milestone.
- No destructive cleanup of generated workflow evidence.
- Clear documentation of implemented versus planned features.
- Human approval state should remain visible and should not be treated as
  completed work unless explicitly approved by the source workflow.

## Non-Goals

The scaffold is not a complete security system, policy engine or deployed
AgentOps platform. Future guardrails should be documented as local controls
unless a real external enforcement layer is implemented.
