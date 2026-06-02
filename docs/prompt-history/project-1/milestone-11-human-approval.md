# Milestone 11 - Human Approval Flow

Curated reconstruction based on the implemented milestone.

## Purpose

Introduce deterministic human approval checkpoints for critical findings,
human-review data quality cases and high-risk LLM recommendations.

## Prompt Used

```text
Continue Project 1: 01-ai-marketing-ops-agent.

Goal:
Implement deterministic human approval flow.

Implement:
- ApprovalRequest
- ApprovalDecision
- ApprovalStatus
- ApprovalRiskLevel
- ApprovalSource
- LocalApprovalStore backed by JSONL under approval-requests/
- ApprovalService
- workflow integration with approval request IDs
- approval_request_count in run history
- tests for creation, deduplication, persistence, decisions and failure behavior

Constraints:
- Never auto-approve high-risk actions.
- Create requests for critical findings, human-review findings and high-risk LLM recommendations.
- Do not store credentials, raw scraped rows, raw REST responses or raw GraphQL responses.
- Approval persistence failures must fail safely.
- Do not commit generated approval request files.

After implementation, summarize approval behavior and verification results.
```

## Expected Verification

```text
uv run pytest
uv run ruff check .
uv run mypy src
```

## Result Summary

Implemented approval models, local JSONL approval storage, deterministic
approval request creation and workflow/run-history integration.

Verified status from the handoff:

```text
96 tests passed
ruff clean
mypy clean
```

