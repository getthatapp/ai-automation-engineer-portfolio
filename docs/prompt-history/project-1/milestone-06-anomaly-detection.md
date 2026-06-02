# Milestone 6 - Deterministic Anomaly Detection

Curated reconstruction based on the implemented milestone.

## Purpose

Detect campaign performance and data quality anomalies from validated snapshots
without relying on an LLM.

## Prompt Used

```text
Continue Project 1: 01-ai-marketing-ops-agent.

Goal:
Implement deterministic anomaly detection over CampaignSnapshot objects.

Implement:
- AnomalyFinding model
- AnomalyDetector service
- configurable anomaly thresholds
- high spend with low conversions detection
- CPA threshold detection
- ROI threshold detection
- mapping of data quality flags into findings
- tests for performance rules and data quality escalation

Constraints:
- Consume CampaignSnapshot objects only.
- Do not use raw scraped rows or raw API payloads directly.
- Do not infer missing metrics.
- Keep findings deterministic and sortable.

After implementation, summarize rules, models and verification results.
```

## Expected Verification

```text
uv run pytest
uv run ruff check .
uv run mypy src
```

## Result Summary

Implemented `AnomalyFinding` and deterministic anomaly detection for performance
thresholds and data quality flags.

Verified status from the handoff:

```text
51 tests passed
ruff clean
mypy clean
```

