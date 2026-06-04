# MCP Runtime Configuration

Project 2 currently provides a deterministic local MCP-style tool layer, local
adapter scripts, Codex prompt templates and Claude Code command templates.

This is not a deployed external MCP service. The current runtime is local-only:
Python tool functions live under `mcp-server/`, and shell scripts call local
checks or print reusable templates.

## Local Runtime Shape

```text
Codex prompt templates       Claude Code command templates
          \                         /
           local adapter scripts
                    |
          deterministic tool package
                    |
        local Project 1 artifacts only
```

The available deterministic tools are:

- `validate_report`
- `read_run_history`
- `list_pending_approvals`
- `check_runtime_clean`
- `generate_demo_brief`

They inspect local Project 1 artifacts. They do not call an LLM, call external
APIs, require secrets, delete files or mutate approval/run-history records.

Milestone 6 exposes the same local tools through the `agent-toolkit-mcp`
console script. This is a local package CLI, not a deployed MCP service.

## Local Commands

Run Project 2 scaffold checks:

```bash
02-agent-toolkit-mcp/scripts/run_checks.sh
```

Run MCP package tests, linting and typing:

```bash
02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
```

Preview local deterministic tools and Project 1 demo readiness:

```bash
02-agent-toolkit-mcp/scripts/demo_mcp_tools.sh
```

Review local Project 1 artifacts:

```bash
02-agent-toolkit-mcp/scripts/run_project1_tool_review.sh
```

Show local permission profile documentation:

```bash
02-agent-toolkit-mcp/scripts/show_permission_profiles.sh
```

Invoke deterministic tools directly from the package directory:

```bash
cd 02-agent-toolkit-mcp/mcp-server
uv run agent-toolkit-mcp validate-report ../../01-ai-marketing-ops-agent/reports/example.md
uv run agent-toolkit-mcp read-run-history ../../01-ai-marketing-ops-agent/run-history/workflow-runs.jsonl --limit 5
uv run agent-toolkit-mcp list-pending-approvals ../../01-ai-marketing-ops-agent/approval-requests/approval-requests.jsonl
uv run agent-toolkit-mcp check-runtime-clean ../../01-ai-marketing-ops-agent
uv run agent-toolkit-mcp generate-demo-brief ../../01-ai-marketing-ops-agent --pretty
```

The CLI prints JSON evidence and returns non-zero status codes for failed local
status checks such as invalid reports, dirty runtime artifacts, malformed JSONL
or incomplete demo readiness.

## Codex Usage

Use Codex prompt templates as reusable review instructions:

```bash
02-agent-toolkit-mcp/scripts/run_codex_prompt.sh inspect-project1-runtime
02-agent-toolkit-mcp/scripts/run_codex_prompt.sh review-project1-report
02-agent-toolkit-mcp/scripts/run_codex_prompt.sh summarize-project1-demo-readiness
```

Codex should treat deterministic script/tool output as evidence. It should not
invent missing reports, run history, approval records or external integration
status.

## Claude Code Usage

Use Claude Code command templates as reusable local command guidance:

```bash
02-agent-toolkit-mcp/scripts/run_claude_command.sh inspect-project1-runtime
02-agent-toolkit-mcp/scripts/run_claude_command.sh review-project1-report
02-agent-toolkit-mcp/scripts/run_claude_command.sh summarize-project1-demo-readiness
```

Claude Code usage should stay within the selected permission profile and should
not claim deployed MCP transport, hooks or external service invocation unless a
future milestone implements and verifies those capabilities.

## What Is Not Implemented

- External MCP deployment.
- External Codex or Claude Code tool invocation.
- External MCP client transport.
- Real service integrations.
- Secrets-backed providers.
- Destructive tools.
- Frontend UI.
