# Project 2 Milestone 2 - MCP Server Implementation

## Full Prompt

```text
Read the root AGENTS.md and docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md first.
Then read:
- 02-agent-toolkit-mcp/AGENTS.md
- 02-agent-toolkit-mcp/README.md
- 02-agent-toolkit-mcp/docs/ARCHITECTURE.md
- 02-agent-toolkit-mcp/docs/ROADMAP.md
- 02-agent-toolkit-mcp/docs/SAFETY_MODEL.md

Continue Project 2: 02-agent-toolkit-mcp.

Milestone 2: initial MCP server implementation with deterministic local tools.

Branch workflow:
- This work is being done on a feature branch.
- Do not assume direct work on main.
- Keep changes scoped to Project 2 and portfolio documentation.
- Do not modify Project 1 code unless explicitly required for read-only examples.
- Do not change Project 1 runtime behavior.

Permanent Project 2 rules:
- Every new function, method and class created by Codex must include a clear Google-style docstring.
- Every milestone must update relevant README.md files.
- Every milestone must update docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md.
- Documentation must stay in English.
- Do not hardcode secrets.
- Do not add real external service credentials.
- Do not overclaim features that are not implemented.
- Keep verification commands explicit.

Current state:
- Project 1 is complete and portfolio-ready.
- Project 2 Milestone 1 scaffold exists.
- Project 2 supports both Codex and Claude Code through documentation, prompts, commands and shared skills.
- Project 2 does not yet have an MCP server implementation.
- This milestone should add the first local deterministic MCP server.
- Do not add external integrations.
- Do not call external APIs.
- Do not require secrets.
- Do not implement any destructive tools.
- Do not add notification integrations.
- Do not add cloud deployment.
- Do not add frontend UI.

Goal:
Implement the initial MCP server for Project 2 with deterministic local read-only tools that can inspect Project 1 artifacts.

Technology decision:
- Use Python for this first MCP server unless the existing Project 2 docs strongly require TypeScript.
- Use a simple, testable Python project under:
  - 02-agent-toolkit-mcp/mcp-server/
- Prefer a lightweight implementation.
- If adding an MCP SDK dependency is practical, use it.
- If not, implement the core tool logic as plain Python functions and keep the MCP transport layer minimal/stubbed but documented.
- The deterministic tool logic and tests are more important than external MCP runtime complexity in this milestone.

Implement:
1. Create MCP server project structure:
   - 02-agent-toolkit-mcp/mcp-server/pyproject.toml
   - 02-agent-toolkit-mcp/mcp-server/README.md
   - 02-agent-toolkit-mcp/mcp-server/src/agent_toolkit_mcp/
   - 02-agent-toolkit-mcp/mcp-server/tests/

2. Add package modules, suggested:
   - src/agent_toolkit_mcp/__init__.py
   - src/agent_toolkit_mcp/server.py
   - src/agent_toolkit_mcp/tools.py
   - src/agent_toolkit_mcp/models.py
   - src/agent_toolkit_mcp/errors.py
   - src/agent_toolkit_mcp/path_safety.py

3. Implement deterministic local tools:
   - validate_report(report_path)
   - read_run_history(jsonl_path, limit=5)
   - list_pending_approvals(jsonl_path)
   - check_runtime_clean(project_path)
   - generate_demo_brief(project_path)

4. Tool behavior:
   validate_report(report_path):
   - Accepts path to a Markdown report.
   - Validates the file exists.
   - Confirms required report sections exist:
     - Executive Summary
     - Campaign Health Overview
     - Critical Anomalies
     - Warning Anomalies
     - Data Quality Issues
     - Human Review Required
     - Campaign Snapshot Table
     - Deterministic Recommended Actions
     - Limitations / Missing Data
   - Returns structured result with missing sections and boolean valid flag.
   - Does not call LLM.

   read_run_history(jsonl_path, limit=5):
   - Reads workflow run JSONL.
   - Returns recent records up to limit.
   - Handles missing file safely.
   - Handles malformed JSONL lines explicitly.
   - Does not expose secrets.

   list_pending_approvals(jsonl_path):
   - Reads approval JSONL.
   - Returns pending approval IDs and summary fields.
   - Handles missing file safely.
   - Handles malformed JSONL lines explicitly.
   - Does not expose secrets.

   check_runtime_clean(project_path):
   - Checks whether generated runtime files are present:
     - reports/daily-marketing-report-*.md
     - run-history/workflow-runs.jsonl
     - approval-requests/approval-requests.jsonl
     - __pycache__/
     - *.pyc
   - Returns structured result with clean flag and found paths.
   - Read-only. It must not delete files.

   generate_demo_brief(project_path):
   - Produces a deterministic text summary of Project 1 demo readiness.
   - Uses local files only.
   - Summarizes whether expected docs/scripts exist.
   - Mentions how to run Project 1 locally.
   - Does not call LLM.

5. Path safety:
   - Tools must use pathlib.
   - Inputs must be validated.
   - Tools must not read outside explicitly provided paths except where needed for child paths under project_path.
   - Avoid destructive operations.
   - Avoid following unsafe assumptions.
   - Add clear errors for invalid paths.

6. Typed models:
   - Use Pydantic models for tool inputs/outputs if dependency already exists or is acceptable.
   - Otherwise use dataclasses with clear type hints.
   - Prefer Pydantic because Project 1 already uses it, but this is a separate project.

7. Tests:
   Add tests for:
   - valid report with all required sections
   - invalid report with missing sections
   - missing report path
   - read run history happy path
   - read run history missing file
   - malformed run history line
   - pending approvals happy path
   - pending approvals missing file
   - runtime clean true
   - runtime clean false with generated files
   - demo brief includes expected local commands
   - no secret-like values are returned in outputs

8. Scripts:
   Add or update:
   - 02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
   This should:
   - cd into mcp-server
   - run tests
   - run ruff if configured
   - run mypy if configured
   - run bash -n for Project 2 scripts where practical

9. Documentation updates:
   - 02-agent-toolkit-mcp/README.md
   - 02-agent-toolkit-mcp/docs/ARCHITECTURE.md
   - 02-agent-toolkit-mcp/docs/ROADMAP.md
   - 02-agent-toolkit-mcp/docs/SAFETY_MODEL.md
   - 02-agent-toolkit-mcp/docs/CODEX_USAGE.md
   - 02-agent-toolkit-mcp/docs/CLAUDE_CODE_USAGE.md
   - docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md
   - root README.md if needed

10. Documentation should explain:
   - what the MCP server currently does
   - which tools exist
   - that tools are deterministic and local/read-only
   - how Codex can use the tools conceptually
   - how Claude Code can use the tools conceptually
   - how this connects to Project 1
   - what is not implemented yet

Rules:
- Keep all new code typed.
- Add Google-style docstrings to every new function, method and class.
- Keep tests deterministic.
- Do not call external services.
- Do not require API keys.
- Do not mutate Project 1 artifacts.
- Do not delete runtime files; only report them.
- Keep generated files out of git.
- Keep changes scoped.
- Do not create large binaries.
- Do not over-engineer the transport layer in this milestone.
- A well-tested deterministic tool layer is acceptable even if the MCP runtime wrapper is minimal.

Quality gate:
Run from root or project as appropriate:
- 02-agent-toolkit-mcp/scripts/run_checks.sh
- 02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
- bash -n 02-agent-toolkit-mcp/scripts/*.sh
- git diff --check

If the MCP server has its own package checks, run:
- cd 02-agent-toolkit-mcp/mcp-server
- uv run pytest
- uv run ruff check .
- uv run mypy src

After implementation, summarize:
1. files created/changed
2. MCP server structure
3. tools implemented
4. path safety behavior
5. tests added
6. scripts added
7. docs updated
8. verification results
9. recommended next milestone
```

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
```

## Result Summary

- Created Python MCP server package under `02-agent-toolkit-mcp/mcp-server/`.
- Added typed Pydantic models, path safety helpers, deterministic tools and a minimal local registry.
- Implemented local read-only tools for report validation, run history inspection, pending approval summaries, runtime artifact checks and demo readiness briefs.
- Added tests for report validation, JSONL handling, malformed lines, pending approvals, runtime cleanliness, demo brief commands and secret redaction.
- Added `02-agent-toolkit-mcp/scripts/run_mcp_checks.sh`.
- Updated Project 2 README/docs, root README and the portfolio handoff.
- Preserved Project 1 runtime behavior and avoided external integrations, secrets and destructive tools.

## Verification Results

```text
02-agent-toolkit-mcp/scripts/run_checks.sh: passed
02-agent-toolkit-mcp/scripts/run_mcp_checks.sh: passed
bash -n 02-agent-toolkit-mcp/scripts/*.sh: passed
git diff --check: passed

uv run pytest: 12 passed
uv run ruff check .: clean
uv run mypy src: clean
```

## Commit / PR Reference

- Commit: `TBD`
- PR: `TBD`
