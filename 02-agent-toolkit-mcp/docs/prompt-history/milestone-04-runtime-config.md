# Project 2 Milestone 4 - Runtime Configuration Examples and Permission Profiles

## Status

Complete.

## Branch

`feature/project-2-m04-runtime-config`

## Full Prompt

```text
Read the root AGENTS.md and docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md first.
Then read:
- 02-agent-toolkit-mcp/AGENTS.md
- 02-agent-toolkit-mcp/README.md
- 02-agent-toolkit-mcp/docs/ARCHITECTURE.md
- 02-agent-toolkit-mcp/docs/CODEX_USAGE.md
- 02-agent-toolkit-mcp/docs/CLAUDE_CODE_USAGE.md
- 02-agent-toolkit-mcp/docs/SAFETY_MODEL.md
- 02-agent-toolkit-mcp/docs/ROADMAP.md
- 02-agent-toolkit-mcp/docs/prompt-history/README.md
- 02-agent-toolkit-mcp/docs/prompt-history/TEMPLATE.md

Continue Project 2: 02-agent-toolkit-mcp.

Milestone 4: MCP runtime configuration examples and permission profiles.

Branch:
feature/project-2-m04-runtime-config

Prompt history requirement:
Create or update:
02-agent-toolkit-mcp/docs/prompt-history/milestone-04-runtime-config.md

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
- Project 2 currently has deterministic local tools:
  - validate_report
  - read_run_history
  - list_pending_approvals
  - check_runtime_clean
  - generate_demo_brief
- The tools are local, read-only and inspect Project 1 artifacts.
- This milestone should add runtime configuration examples and permission-profile documentation for using the toolkit safely with Codex and Claude Code.
- Do not modify Project 1 code.
- Do not change Project 1 runtime behavior.
- Do not add external integrations.
- Do not call external APIs.
- Do not require secrets.
- Do not implement destructive tools.
- Do not add frontend UI.
- Do not overclaim that a real external MCP deployment exists if it does not.

Goal:
Add clear runtime configuration examples and permission profiles for running Project 2 tooling safely with Codex and Claude Code.

Implement:

1. Add runtime configuration docs under:
   02-agent-toolkit-mcp/docs/runtime/

Suggested files:
- MCP_RUNTIME_CONFIGURATION.md
- CODEX_PERMISSION_PROFILES.md
- CLAUDE_CODE_PERMISSION_PROFILES.md
- LOCAL_ONLY_SECURITY_BOUNDARIES.md
- TROUBLESHOOTING.md

2. Add example configuration files under:
   02-agent-toolkit-mcp/examples/runtime-config/

Suggested files:
- codex-read-only-example.md
- codex-workspace-write-example.md
- claude-code-read-only-example.md
- claude-code-approval-required-example.md
- mcp-server-local-example.md

These should be documentation/examples only. Do not include real secrets.

3. Add permission profile documentation:
Explain at least these profiles:
- read-only inspection
- workspace-write development
- approval-required operations
- blocked/destructive operation policy

For each profile explain:
- purpose
- allowed operations
- blocked operations
- suggested Codex usage
- suggested Claude Code usage
- when to use it
- when not to use it

4. Add local runtime examples:
Document how to run or conceptually connect:
- Project 2 MCP/tool checks
- Codex prompt templates
- Claude Code command templates
- Project 1 artifact inspection

Include commands where applicable:
- 02-agent-toolkit-mcp/scripts/run_checks.sh
- 02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
- 02-agent-toolkit-mcp/scripts/demo_mcp_tools.sh
- 02-agent-toolkit-mcp/scripts/run_project1_tool_review.sh

5. Add or update scripts only if useful:
Suggested optional script:
- 02-agent-toolkit-mcp/scripts/show_permission_profiles.sh

Behavior:
- print the available local permission profiles
- print where docs live
- no external calls
- no mutations
- bash with set -euo pipefail
- executable

6. Update Project 2 README.md:
- add a section about runtime configuration and permission profiles
- link to new runtime docs
- keep it concise

7. Update Project 2 docs:
- docs/ARCHITECTURE.md
- docs/CODEX_USAGE.md
- docs/CLAUDE_CODE_USAGE.md
- docs/SAFETY_MODEL.md
- docs/ROADMAP.md

8. Update root docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md:
- mark Project 2 Milestone 4 as in progress/completed as appropriate
- record that runtime configuration examples and permission profiles exist
- set next recommended milestone to Project 2 Milestone 5: MCP tool hardening and richer validation, unless a better next milestone is clearly justified

9. Update root README.md only if needed:
- add a concise mention that Project 2 now documents Codex and Claude Code permission profiles
- do not bloat root README

10. Update run_checks.sh:
- verify the new runtime docs/examples exist
- include bash syntax check for any new script

Rules:
- Documentation-first milestone.
- Do not modify Project 1 code.
- Do not change MCP tool behavior unless absolutely required.
- Do not add real credentials.
- Do not add external integrations.
- Do not claim destructive operations are supported.
- Do not call real external services.
- Keep all docs in English.
- Keep scripts executable.
- Add comments to shell scripts where useful.
- Add Google-style docstrings only if Python functions/classes are added or modified.
- Keep prompt history current.

Expected verification:
Run:
- 02-agent-toolkit-mcp/scripts/run_checks.sh
- 02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
- bash -n 02-agent-toolkit-mcp/scripts/*.sh
- git diff --check

If Python code changes, also run:
- cd 02-agent-toolkit-mcp/mcp-server
- uv run pytest
- uv run ruff check .
- uv run mypy src

After implementation, summarize:
1. files created/changed
2. runtime docs added
3. permission profiles documented
4. config examples added
5. scripts added/updated
6. README updates
7. handoff updates
8. prompt history update
9. verification results
10. recommended next milestone
```

## Expected Verification

```bash
02-agent-toolkit-mcp/scripts/run_checks.sh
02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
bash -n 02-agent-toolkit-mcp/scripts/*.sh
git diff --check
```

If Python code changes:

```bash
cd 02-agent-toolkit-mcp/mcp-server
uv run pytest
uv run ruff check .
uv run mypy src
```

## Result Summary

- Added runtime configuration docs under `docs/runtime/` for local MCP/tool
  runtime shape, Codex profiles, Claude Code profiles, local-only boundaries
  and troubleshooting.
- Added runtime configuration examples under `examples/runtime-config/` for
  Codex read-only, Codex workspace-write, Claude Code read-only, Claude Code
  approval-required and local MCP server usage.
- Added read-only helper script: `scripts/show_permission_profiles.sh`.
- Updated Project 2 README, architecture, Codex usage, Claude Code usage,
  safety model, roadmap and prompt-history index.
- Updated root handoff and root README with Milestone 4 status and the
  recommended Milestone 5 direction.
- Updated `scripts/run_checks.sh` to verify the new runtime docs, examples,
  prompt-history file and helper script.
- Kept Project 1 code, Project 1 runtime behavior and MCP tool behavior
  unchanged.

## Verification Results

```text
02-agent-toolkit-mcp/scripts/show_permission_profiles.sh
Passed. Printed local permission profiles and runtime doc paths without
mutation or external calls.

02-agent-toolkit-mcp/scripts/run_checks.sh
Passed. Required files exist and shell script syntax is valid.

02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
Initial sandbox run failed because uv could not resolve hatchling without
network access. Re-run with approved escalation passed:
12 tests passed, ruff clean, mypy clean and shell script syntax clean.

bash -n 02-agent-toolkit-mcp/scripts/*.sh
Passed.

git diff --check
Passed.
```

## Commit / PR Reference

- Commit: `TBD`
- PR: `TBD`

## Notes

- Documentation-first milestone.
- Permission profiles are documentation and operating guidance, not enforced
  runtime policy.
- Keep Project 1 code and runtime behavior unchanged.
- No Python code changed, so the standalone Python package commands were not
  required beyond `run_mcp_checks.sh`.
