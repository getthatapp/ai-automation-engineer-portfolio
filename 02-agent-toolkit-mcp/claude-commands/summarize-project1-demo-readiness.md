# Summarize Project 1 Demo Readiness

## Purpose

Summarize local Project 1 demo readiness using Project 2 deterministic local
tools and Claude Code-style command flow.

## Expected Inputs

- Project 1 path: `01-ai-marketing-ops-agent`

## Command Steps

1. Run:

   ```bash
   02-agent-toolkit-mcp/scripts/demo_mcp_tools.sh
   ```

2. If a full artifact review is needed, run:

   ```bash
   02-agent-toolkit-mcp/scripts/run_project1_tool_review.sh
   ```

3. Use `generate_demo_brief` output for demo readiness.
4. Use runtime, run-history and approval outputs as local evidence only.

## Safety Constraints

- Do not modify Project 1.
- Do not create or delete runtime files.
- Do not require credentials.
- Do not call external APIs.
- Do not present local demo readiness as production deployment readiness.

## Review Checklist

- Present expected files are summarized.
- Missing expected files are listed.
- Local demo commands are named.
- Runtime artifacts and approval queue state are interpreted conservatively.
