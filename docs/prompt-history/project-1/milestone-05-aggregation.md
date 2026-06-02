# Milestone 5 - Deterministic Aggregation

Curated reconstruction based on the implemented milestone.

## Purpose

Join scraped panel rows with REST metadata and GraphQL metrics into a validated
business object for downstream modules.

## Prompt Used

```text
Continue Project 1: 01-ai-marketing-ops-agent.

Goal:
Implement deterministic campaign data aggregation.

Implement:
- CampaignSnapshot model
- CampaignAggregator service
- joins between scraped rows, Campaign REST API metadata and Analytics GraphQL metrics
- explicit data_quality_flags and data_quality_notes
- requires_human_review marking for unsafe or incomplete data
- tests for complete, missing and mismatched data

Constraints:
- Do not call an LLM.
- Do not invent missing metrics.
- Do not silently drop mismatched rows.
- Preserve source records for auditability.
- Keep ordering deterministic.

After implementation, summarize aggregation behavior and verification results.
```

## Expected Verification

```text
uv run pytest
uv run ruff check .
uv run mypy src
```

## Result Summary

Implemented `CampaignSnapshot`, deterministic aggregation and explicit data
quality flags for missing, mismatched, stale and human-review cases.

Verified status from the handoff:

```text
41 tests passed
ruff clean
mypy clean
```

