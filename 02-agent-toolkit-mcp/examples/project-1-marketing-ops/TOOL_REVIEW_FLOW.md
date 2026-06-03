# Project 1 Tool Review Flow

This example shows how Project 2 deterministic local tools can support a
review of Project 1 marketing operations artifacts.

## Inspected Artifacts

- Latest local Markdown report under `01-ai-marketing-ops-agent/reports/`.
- Local workflow run history at
  `01-ai-marketing-ops-agent/run-history/workflow-runs.jsonl`.
- Local approval queue at
  `01-ai-marketing-ops-agent/approval-requests/approval-requests.jsonl`.
- Expected Project 1 docs, scripts and workflow files used by
  `generate_demo_brief`.

## Deterministic Tools

- `validate_report`: checks required report sections.
- `read_run_history`: reads recent sanitized workflow records.
- `list_pending_approvals`: lists pending approval summaries.
- `check_runtime_clean`: reports generated runtime artifacts without deleting
  them.
- `generate_demo_brief`: summarizes local demo readiness from expected files.

## Flow

1. Run `02-agent-toolkit-mcp/scripts/demo_mcp_tools.sh` to inspect registered
   tools and Project 1 demo readiness.
2. Run `02-agent-toolkit-mcp/scripts/run_project1_tool_review.sh` to collect
   report, run-history, approval and runtime checks.
3. Review tool outputs before asking an agent to summarize them.
4. Keep the final review grounded in observed local artifacts.

## Reviewer Focus

- Required report sections are present or missing.
- Run history records are well-formed and recent enough for the review.
- Pending approvals are visible and clearly treated as pending.
- Runtime files are present when expected and are not deleted by the review.
- Missing files are reported as missing evidence.

## What Not To Infer

- Do not infer real external API calls, notification delivery or production
  deployment.
- Do not infer approval decisions from pending approval requests.
- Do not infer that missing runtime files mean the workflow has never run.
- Do not invent metrics, anomaly counts or campaign status not present in the
  inspected artifacts.
