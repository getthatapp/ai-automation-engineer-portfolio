# Project 2 Milestone 6 - MCP Server CLI Interface

## Status

Complete.

## Branch

`feature/project-2-m06-cli-interface`

## Full Prompt

````text
Read the root AGENTS.md and docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md first.
Then read:
- 02-agent-toolkit-mcp/AGENTS.md
- 02-agent-toolkit-mcp/README.md
- 02-agent-toolkit-mcp/docs/ARCHITECTURE.md
- 02-agent-toolkit-mcp/docs/CODEX_USAGE.md
- 02-agent-toolkit-mcp/docs/CLAUDE_CODE_USAGE.md
- 02-agent-toolkit-mcp/docs/SAFETY_MODEL.md
- 02-agent-toolkit-mcp/docs/ROADMAP.md
- 02-agent-toolkit-mcp/docs/runtime/MCP_RUNTIME_CONFIGURATION.md
- 02-agent-toolkit-mcp/docs/runtime/LOCAL_ONLY_SECURITY_BOUNDARIES.md
- 02-agent-toolkit-mcp/docs/prompt-history/README.md
- 02-agent-toolkit-mcp/docs/prompt-history/TEMPLATE.md
- 02-agent-toolkit-mcp/docs/prompt-history/milestone-05-tool-hardening.md

Continue Project 2: 02-agent-toolkit-mcp.

Milestone 6: MCP server CLI / local tool invocation interface.

Branch:
feature/project-2-m06-cli-interface

Prompt history requirement:
Create or update:
02-agent-toolkit-mcp/docs/prompt-history/milestone-06-cli-interface.md

The prompt-history file must include:
- title,
- status,
- branch,
- this full prompt,
- expected verification,
- result summary placeholder,
- verification result placeholder,
- commit / PR placeholder,
- notes.

After implementation, update the same prompt-history file with the actual result summary and verification results.

Current state:
- Project 1 is complete and portfolio-ready.
- Project 2 Milestone 1 scaffold is complete.
- Project 2 Milestone 2 added deterministic local MCP/tool-layer functions.
- Project 2 Milestone 3 added Codex/Claude integration adapters, prompts, commands and examples.
- Project 2 Milestone 4 added runtime configuration docs and permission profiles.
- Project 2 Milestone 5 hardened MCP tools with richer validation and path safety.
- Current deterministic local tools include:
  - validate_report
  - read_run_history
  - list_pending_approvals
  - check_runtime_clean
  - generate_demo_brief
- Tools are local, read-only and inspect Project 1 artifacts.
- This milestone should make the tools easy to invoke from the command line.
- Do not modify Project 1 code.
- Do not change Project 1 runtime behavior.
- Do not add external integrations.
- Do not call external APIs.
- Do not require secrets.
- Do not implement destructive tools.
- Do not add frontend UI.
- Do not overclaim that a real deployed external MCP service exists.

Goal:
Add a local CLI interface for the Project 2 deterministic MCP/tool-layer so external reviewers, Codex workflows and Claude Code workflows can invoke the tools without writing Python.

Implement:

1. Add CLI module under:
   02-agent-toolkit-mcp/mcp-server/src/agent_toolkit_mcp/

Suggested file:
- cli.py

2. Expose console script in:
   02-agent-toolkit-mcp/mcp-server/pyproject.toml

Suggested command name:
- agent-toolkit-mcp

3. Implement CLI subcommands:
   - validate-report
   - read-run-history
   - list-pending-approvals
   - check-runtime-clean
   - generate-demo-brief

Expected examples:

```bash
uv run agent-toolkit-mcp validate-report ../../01-ai-marketing-ops-agent/reports/example.md
uv run agent-toolkit-mcp read-run-history ../../01-ai-marketing-ops-agent/run-history/workflow-runs.jsonl --limit 5
uv run agent-toolkit-mcp list-pending-approvals ../../01-ai-marketing-ops-agent/approval-requests/approval-requests.jsonl
uv run agent-toolkit-mcp check-runtime-clean ../../01-ai-marketing-ops-agent
uv run agent-toolkit-mcp generate-demo-brief ../../01-ai-marketing-ops-agent
```

Follow-up decision:
Choose CI-style status checker + JSON evidence printer.

The CLI should always print structured JSON evidence, but it should also return meaningful exit codes.

Rules:
- Default output is JSON.
- --pretty prints indented JSON.
- Tools remain read-only and local-only.
- No external calls.
- No file mutation.
- No deletion.

Exit code policy:
- validate-report exits 0 when valid=true, exits non-zero when valid=false or the report path is invalid/missing.
- check-runtime-clean exits 0 when clean=true, exits non-zero when clean=false.
- read-run-history exits 0 for a valid readable file and for an explicitly handled missing-file result if the existing tool model treats missing files as safe; exits non-zero for malformed JSONL, invalid path or invalid limit.
- list-pending-approvals exits 0 for a valid readable file and for an explicitly handled missing-file result if the existing tool model treats missing files as safe; exits non-zero for malformed JSONL or invalid path.
- generate-demo-brief exits 0 when a brief can be generated; exits non-zero for invalid project_path or missing critical expected project structure.

Keep the CLI thin:
- use existing tool functions and models,
- do not duplicate tool logic,
- centralize JSON serialization and exit-code mapping,
- test both JSON payload and exit codes.
````

## Expected Verification

```bash
02-agent-toolkit-mcp/scripts/run_checks.sh
02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
bash -n 02-agent-toolkit-mcp/scripts/*.sh
git diff --check

cd 02-agent-toolkit-mcp/mcp-server
uv run pytest
uv run ruff check .
uv run mypy src
uv run agent-toolkit-mcp generate-demo-brief ../../01-ai-marketing-ops-agent --pretty
```

## Result Summary

- Added `agent_toolkit_mcp.cli` with argparse subcommands for all five
  deterministic local tools.
- Exposed the `agent-toolkit-mcp` console script through `pyproject.toml`.
- Implemented compact JSON output by default and `--pretty` indented JSON from
  any CLI position.
- Added status-check exit code mapping while preserving JSON evidence output.
- Added CLI tests for payload shape, pretty output, missing evidence behavior,
  malformed JSONL, invalid limits and status-sensitive exit codes.
- Updated Project 2 README, MCP server README, architecture, Codex usage,
  Claude Code usage, safety model, roadmap, runtime docs, prompt-history index,
  root README and Codex handoff.
- Updated `scripts/run_checks.sh` so the CLI module, CLI tests and Milestone 6
  prompt-history file are required scaffold files.
- Kept tools local, deterministic and read-only; Project 1 code and runtime
  behavior were not modified.

## Verification Results

```text
02-agent-toolkit-mcp/scripts/run_checks.sh
Passed. Project 2 scaffold files exist, shell syntax is valid and the new CLI
files are listed in the scaffold output.

02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
Passed. 32 tests passed, ruff clean, mypy clean and shell syntax clean.

bash -n 02-agent-toolkit-mcp/scripts/*.sh
Passed.

git diff --check
Passed.

cd 02-agent-toolkit-mcp/mcp-server && uv run pytest
Passed. 32 tests passed.

cd 02-agent-toolkit-mcp/mcp-server && uv run ruff check .
Passed.

cd 02-agent-toolkit-mcp/mcp-server && uv run mypy src
Passed with no issues in 7 source files.

cd 02-agent-toolkit-mcp/mcp-server && uv run agent-toolkit-mcp generate-demo-brief ../../01-ai-marketing-ops-agent --pretty
Passed. Printed pretty JSON evidence with ready=true for the current Project 1
demo-readiness structure.
```

## Commit / PR Reference

- Commit: `TBD`
- PR: `TBD`

## Notes

- CLI interface milestone.
- Keep all tools local, deterministic and read-only.
- Keep Project 1 code and runtime behavior unchanged.
