# Report Polish - Data Quality Issues Readability

Curated reconstruction based on the implemented task.

## Purpose

Improve deterministic Markdown report readability when data quality flags and
related anomaly findings describe the same campaign-level issue.

## Prompt Used

```text
Continue Project 1: 01-ai-marketing-ops-agent.

Task:
Polish deterministic Markdown report readability after CI/CD.

Goal:
Improve the deterministic Markdown report's readability, especially the Data Quality Issues section, while preserving all existing deterministic facts and test coverage.

Expected behavior:
- keep the report deterministic
- keep all important facts visible
- avoid duplicate or overly repetitive lines
- group data quality issues by campaign
- show quality flags, quality notes, related finding types/severities and human review status
- do not remove evidence from Critical Anomalies or Warning Anomalies sections
- do not hide stale_data or requires_human_review
- do not infer missing metrics
- do not change report inputs
- do not let LLM affect this report

Constraints:
- Do not change business logic.
- Do not change anomaly detection logic.
- Do not change data quality flag generation.
- Do not change workflow behavior.
- Do not change persistence formats.
- Do not add features.
- Do not modify generated reports under reports/.

After implementation, summarize files changed, report rendering changes, unchanged behavior, tests and verification.
```

## Expected Verification

```text
./scripts/run_ci_locally.sh
git diff --check
```

## Result Summary

Updated deterministic Markdown report rendering so Data Quality Issues are
grouped by campaign, preserving flags, notes, related finding types/severities
and human-review status without duplicating full finding evidence. Business
logic, anomaly detection, workflow behavior and persistence formats remained
unchanged.

