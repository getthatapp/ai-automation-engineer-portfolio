# Summarize Project 1 Demo Readiness

## Current State

Project 2 can generate a deterministic local-only Project 1 demo brief and
inspect runtime artifacts. The brief is not an LLM evaluation and should not be
treated as proof of production readiness.

## Goal

Summarize whether Project 1 is ready for a local portfolio demo using only
deterministic local tool outputs and documented repository state.

## Inputs

- Project 1 path: `01-ai-marketing-ops-agent`
- Demo script: `02-agent-toolkit-mcp/scripts/demo_mcp_tools.sh`
- Review script: `02-agent-toolkit-mcp/scripts/run_project1_tool_review.sh`

## Steps

1. Run the demo script or review script when local execution is appropriate.
2. Use `generate_demo_brief` output for expected files and local commands.
3. Use runtime and approval outputs to identify visible demo evidence and
   reviewer follow-up items.
4. Separate readiness for a local demo from unsupported claims about deployed
   services or real external integrations.

## Constraints

- Do not modify Project 1.
- Do not create runtime artifacts just to make the demo appear ready.
- Do not call external APIs, require credentials or claim real notification
  provider integration.
- Do not invent missing run history, reports or approval queue entries.

## Expected Summary

Return:

- demo readiness status;
- present and missing expected files;
- available local commands;
- runtime evidence available;
- limitations and recommended next milestone.
