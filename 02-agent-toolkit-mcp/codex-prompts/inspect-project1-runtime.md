# Inspect Project 1 Runtime

## Current State

Project 2 provides deterministic local read-only tools for inspecting Project 1
artifacts. Use tool outputs as evidence. Do not invent missing runtime data.

## Goal

Inspect the Project 1 runtime artifact state and summarize what is present,
what is missing and what requires reviewer attention.

## Inputs

- Project 1 path: `01-ai-marketing-ops-agent`
- Runtime check script: `02-agent-toolkit-mcp/scripts/run_project1_tool_review.sh`
- Demo script: `02-agent-toolkit-mcp/scripts/demo_mcp_tools.sh`

## Steps

1. Read the root `AGENTS.md`, Project 2 `AGENTS.md` and relevant Project 2
   usage docs before making claims.
2. Run the read-only Project 1 tool review script if local execution is
   appropriate for the task.
3. Use deterministic outputs from `check_runtime_clean`, `read_run_history` and
   `list_pending_approvals` as the source of truth.
4. Clearly distinguish observed files, missing files, malformed JSONL lines and
   inferred next steps.

## Constraints

- Do not modify Project 1 code or runtime behavior.
- Do not delete reports, run history, approval requests, caches or local files.
- Do not call external APIs or require secrets.
- Do not claim that Codex invoked external MCP transport unless that is actually
  implemented and verified.
- Do not infer that a missing artifact means the workflow never ran.

## Expected Summary

Return:

- runtime artifacts observed;
- pending approvals observed;
- recent run-history status if available;
- missing evidence;
- recommended local next steps.
