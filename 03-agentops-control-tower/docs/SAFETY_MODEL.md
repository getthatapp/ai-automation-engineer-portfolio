# Safety Model

Project 3 is local-first and deterministic.

The control tower is intended to observe workflow evidence, not execute
business actions or bypass approval flows.

## Current Guarantees

- No external APIs are called.
- No secrets are required.
- Only a minimal local Python package dependency is added: Pydantic.
- Ingestion reads local files and returns typed records, warnings and errors.
- No dashboard or UI is implemented.
- No Project 1 or Project 2 runtime behavior is changed.
- Malformed source files are reported as typed ingestion errors.
- Missing optional source files are reported as warnings.
- Secret-like keys and inline credential values are conservatively redacted.

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

The ingestion layer does not call LLMs, infer missing metrics, send
notifications, create tasks, delete runtime artifacts or mutate source files.
