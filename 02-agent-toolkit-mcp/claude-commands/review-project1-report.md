# Review Project 1 Report

## Purpose

Review a Project 1 Markdown report with deterministic local tool output from
the Project 2 MCP/tool layer.

## Expected Inputs

- Optional report path. If omitted, use the latest
  `01-ai-marketing-ops-agent/reports/daily-marketing-report-*.md` discovered by
  the review script.

## Command Steps

1. Run:

   ```bash
   02-agent-toolkit-mcp/scripts/run_project1_tool_review.sh
   ```

   Or pass an explicit report path:

   ```bash
   02-agent-toolkit-mcp/scripts/run_project1_tool_review.sh \
     01-ai-marketing-ops-agent \
     01-ai-marketing-ops-agent/reports/daily-marketing-report-example.md
   ```

2. Use `validate_report` output for section completeness.
3. Use run history and approval outputs only as local supporting evidence.
4. Summarize findings, missing evidence and safe next steps.

## Safety Constraints

- Do not edit the report unless explicitly asked.
- Do not invent campaign data or approval decisions.
- Do not infer external notification delivery without local evidence.
- Do not call external services.

## Review Checklist

- Report path is named.
- Missing report sections are listed.
- Pending approvals are not described as approved actions.
- Unsupported production or external-integration claims are avoided.
