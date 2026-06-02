# Milestone 7 - Deterministic Markdown Reporting

Curated reconstruction based on the implemented milestone.

## Purpose

Generate a deterministic Markdown report from validated snapshots and findings.

## Prompt Used

```text
Continue Project 1: 01-ai-marketing-ops-agent.

Goal:
Implement deterministic Markdown reporting.

Implement:
- MarkdownReportWriter
- executive summary
- campaign health overview
- critical anomaly section
- warning anomaly section
- data quality issues section
- human review required section
- campaign snapshot table
- deterministic recommended actions
- limitations and missing data section
- tests for report content and stable ordering

Constraints:
- Do not call an LLM.
- Do not change anomaly detection rules.
- Do not infer missing data.
- Keep report ordering stable and deterministic.

After implementation, summarize report sections and verification results.
```

## Expected Verification

```text
uv run pytest
uv run ruff check .
uv run mypy src
```

## Result Summary

Implemented deterministic Markdown report generation over `CampaignSnapshot`
and `AnomalyFinding` inputs.

Verified status from the handoff:

```text
61 tests passed
ruff clean
mypy clean
```

