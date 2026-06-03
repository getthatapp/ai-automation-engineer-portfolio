# Project 2 Milestone 3 - Agent Integration Adapters

## Status

Complete.

## Branch

`feature/project-2-m03-agent-integration`

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

Milestone 3: agent integration adapters for Codex and Claude Code.

Branch:
feature/project-2-m03-agent-integration

Prompt history requirement:
Create or update:
02-agent-toolkit-mcp/docs/prompt-history/milestone-03-agent-integration.md

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
- Project 2 Milestone 2 added the initial deterministic local MCP server/tool layer.
- Existing Project 2 MCP tools inspect Project 1 artifacts:
  - validate_report
  - read_run_history
  - list_pending_approvals
  - check_runtime_clean
  - generate_demo_brief
- Project 2 supports both Codex and Claude Code conceptually through docs, prompts, commands and shared skills.
- This milestone should make the MCP/tool layer easier to use from Codex and Claude Code workflows.
- Do not modify Project 1 code.
- Do not change Project 1 runtime behavior.
- Do not add external integrations.
- Do not call external APIs.
- Do not require secrets.
- Do not implement destructive tools.
- Do not add frontend UI.

Goal:
Add practical agent integration adapters and demo flows showing how Codex and Claude Code can use the Project 2 deterministic local tools against Project 1 artifacts.

Implement:

1. Add integration scripts under:
   02-agent-toolkit-mcp/scripts/

Suggested scripts:
- demo_mcp_tools.sh
- run_project1_tool_review.sh

Behavior:
- Scripts must use bash with set -euo pipefail.
- Scripts must be read-only.
- Scripts must not delete runtime files.
- Scripts must not call external APIs.
- Scripts should show how to run the MCP/tool checks against Project 1 paths.
- Scripts should print clear next-step information.
- Scripts should fail clearly if expected files or directories are missing.

2. Add or update Codex prompt templates under:
   02-agent-toolkit-mcp/codex-prompts/

Suggested files:
- inspect-project1-runtime.md
- review-project1-report.md
- summarize-project1-demo-readiness.md

These prompts should instruct Codex to use deterministic local tool outputs conceptually and avoid inventing data.

3. Add or update Claude Code command templates under:
   02-agent-toolkit-mcp/claude-commands/

Suggested files:
- inspect-project1-runtime.md
- review-project1-report.md
- summarize-project1-demo-readiness.md

These commands should mirror the Codex prompts but be framed for Claude Code usage.

4. Add examples under:
   02-agent-toolkit-mcp/examples/project-1-marketing-ops/

Suggested files:
- TOOL_REVIEW_FLOW.md
- SAMPLE_AGENT_REVIEW.md

These examples should explain:
- what Project 1 artifacts are inspected,
- which deterministic tools are used,
- what a reviewer should look for,
- what not to infer,
- how approval queue and run history should be interpreted.

5. Update docs:
- 02-agent-toolkit-mcp/docs/CODEX_USAGE.md
- 02-agent-toolkit-mcp/docs/CLAUDE_CODE_USAGE.md
- 02-agent-toolkit-mcp/docs/ARCHITECTURE.md
- 02-agent-toolkit-mcp/docs/ROADMAP.md
- 02-agent-toolkit-mcp/README.md
- docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md

Docs should explain:
- how Codex can use the new prompt templates and scripts,
- how Claude Code can use the command templates and scripts,
- how the MCP/tool layer connects to Project 1 runtime artifacts,
- that tools remain deterministic and read-only,
- that this is still local-only and does not call external services.

6. Update or add tests only if Python logic changes.
If this milestone only adds scripts/docs/templates, do not modify Python code unnecessarily.

7. Update scripts/run_checks.sh if needed so it verifies new files exist and script syntax is valid.

Rules:
- Keep all docs in English.
- Do not overclaim real MCP runtime integrations if not implemented.
- Do not claim external tool invocation from Codex or Claude Code if this milestone only provides adapters/templates.
- Do not hardcode secrets.
- Do not add real credentials.
- Do not mutate Project 1 files.
- Do not delete generated runtime files.
- Keep scripts executable.
- Add comments to shell scripts where useful.
- Add Google-style docstrings only if Python functions/classes are added or modified.

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
2. scripts added
3. Codex prompts added
4. Claude Code commands added
5. examples added
6. docs updated
7. prompt history update
8. verification results
9. recommended next milestone
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

- Merged `feature/project-2-m02-mcp-server` into
  `feature/project-2-m03-agent-integration` so Milestone 3 builds on the
  deterministic MCP/tool layer.
- Added read-only adapter scripts:
  `scripts/demo_mcp_tools.sh` and `scripts/run_project1_tool_review.sh`.
- Added Codex prompt templates:
  `inspect-project1-runtime`, `review-project1-report` and
  `summarize-project1-demo-readiness`.
- Added Claude Code command templates with matching Project 1 review flows.
- Added Project 1 examples:
  `TOOL_REVIEW_FLOW.md` and `SAMPLE_AGENT_REVIEW.md`.
- Updated Project 2 README, architecture, usage, safety, roadmap, prompt
  history and root handoff docs.
- Updated `scripts/run_checks.sh` to verify the Milestone 3 files and script
  syntax.
- Kept Project 1 code and runtime behavior unchanged.

## Verification Results

```text
02-agent-toolkit-mcp/scripts/demo_mcp_tools.sh
Passed. Printed registered deterministic tools, generated a local demo brief and
reported existing Project 1 runtime artifacts without mutation.

02-agent-toolkit-mcp/scripts/run_project1_tool_review.sh
Passed. Validated the current local report, read run history and listed three
pending approval records without mutation.

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

cd 02-agent-toolkit-mcp/mcp-server && uv run pytest
12 tests passed.

cd 02-agent-toolkit-mcp/mcp-server && uv run ruff check .
Passed.

cd 02-agent-toolkit-mcp/mcp-server && uv run mypy src
Passed with no issues in 6 source files.
```

## Commit / PR Reference

- Commit: `TBD`
- PR: `TBD`

## Notes

- Milestone 2 was merged into this branch first because the Milestone 3 branch
  initially did not contain the deterministic MCP server/tool layer.
- Keep Project 1 code and runtime behavior unchanged.
- The adapter scripts use the local MCP server virtualenv and `PYTHONPATH=src`
  to avoid resolving package build dependencies during demo execution.
