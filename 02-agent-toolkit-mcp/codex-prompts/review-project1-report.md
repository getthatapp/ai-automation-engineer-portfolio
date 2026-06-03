# Review Project 1 Report

## Current State

Project 1 generates deterministic Markdown reports. Project 2 exposes a
read-only `validate_report` tool that checks required report sections without
using an LLM.

## Goal

Review a Project 1 Markdown report using deterministic tool output and produce
a concise engineering review.

## Inputs

- Default report discovery: latest
  `01-ai-marketing-ops-agent/reports/daily-marketing-report-*.md`
- Optional explicit report path supplied by the user.
- Review command:
  `02-agent-toolkit-mcp/scripts/run_project1_tool_review.sh`

## Steps

1. Identify the report path from the user or from the latest local report file.
2. Run the read-only review script with the report path when execution is
   appropriate.
3. Use `validate_report` output for required-section claims.
4. Use `read_run_history` and `list_pending_approvals` only to add local
   workflow context when those artifacts exist.

## Constraints

- Do not rewrite the report unless explicitly asked.
- Do not invent campaign metrics, anomaly counts or approval decisions.
- Do not treat pending approvals as completed or approved work.
- Do not claim external notification delivery unless local artifacts explicitly
  record that status.
- Do not call external services.

## Expected Summary

Return:

- report path reviewed;
- report validity and missing sections;
- run-history context if present;
- approval context if present;
- review risks and local next steps.
