# Project 2 Milestone 5 - MCP Tool Hardening and Richer Validation

## Status

Complete.

## Branch

`feature/project-2-m05-tool-hardening`

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
- 02-agent-toolkit-mcp/docs/runtime/MCP_RUNTIME_CONFIGURATION.md
- 02-agent-toolkit-mcp/docs/runtime/LOCAL_ONLY_SECURITY_BOUNDARIES.md
- 02-agent-toolkit-mcp/docs/prompt-history/README.md
- 02-agent-toolkit-mcp/docs/prompt-history/TEMPLATE.md
- 02-agent-toolkit-mcp/docs/prompt-history/milestone-04-runtime-config.md

Continue Project 2: 02-agent-toolkit-mcp.

Milestone 5: MCP tool hardening and richer validation.

Branch:
feature/project-2-m05-tool-hardening

Prompt history requirement:
Create or update:
02-agent-toolkit-mcp/docs/prompt-history/milestone-05-tool-hardening.md

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
- Current deterministic local tools include:
  - validate_report
  - read_run_history
  - list_pending_approvals
  - check_runtime_clean
  - generate_demo_brief
- Tools are local, read-only and inspect Project 1 artifacts.
- This milestone should harden the existing MCP/tool layer with richer validation, better typed results, stronger path safety and more edge-case tests.
- Do not modify Project 1 code.
- Do not change Project 1 runtime behavior.
- Do not add external integrations.
- Do not call external APIs.
- Do not require secrets.
- Do not implement destructive tools.
- Do not add frontend UI.
- Do not overclaim that a real external MCP deployment exists if it does not.

Goal:
Improve reliability, safety and usefulness of the Project 2 deterministic local MCP tools.

Implement:

1. Harden path safety:
   - Review 02-agent-toolkit-mcp/mcp-server/src/agent_toolkit_mcp/path_safety.py.
   - Ensure tools reject invalid paths clearly.
   - Ensure project_path based checks only inspect expected child paths under the provided project_path.
   - Ensure tools do not mutate or delete files.
   - Ensure symlink handling is explicit and safe.
   - Add tests for invalid paths, directory/file mismatches and path traversal-like inputs where applicable.

2. Improve validate_report(report_path):
   - Keep required section validation.
   - Add optional summary extraction for:
     - generated timestamp,
     - campaigns processed,
     - critical findings,
     - warning findings,
     - campaigns requiring human review.
   - Return structured warnings for suspicious but non-fatal cases, for example:
     - empty report,
     - missing generated timestamp,
     - duplicated required section heading.
   - Do not infer missing metrics.
   - Do not call LLM.
   - Add tests for duplicate section headings, empty report and summary extraction.

3. Improve read_run_history(jsonl_path, limit=5):
   - Validate limit boundaries.
   - Add clear behavior for limit <= 0 and very large limit.
   - Return total records read if practical.
   - Preserve recent-record ordering deterministically.
   - Redact secret-like values from returned records.
   - Add tests for limit validation, ordering and redaction.

4. Improve list_pending_approvals(jsonl_path):
   - Return only pending records.
   - Include useful summary fields without exposing full sensitive payloads.
   - Handle approved/rejected records correctly.
   - Redact secret-like values.
   - Add tests for mixed statuses and redaction.

5. Improve check_runtime_clean(project_path):
   - Include counts by artifact type:
     - reports
     - run_history
     - approval_requests
     - pycache
     - pyc
   - Return deterministic sorted paths.
   - Add tests for multiple artifact types and stable ordering.

6. Improve generate_demo_brief(project_path):
   - Include a structured readiness checklist if not already present:
     - README exists,
     - reviewer scripts exist,
     - Project 1 docs exist,
     - CI workflow exists,
     - runtime directories exist.
   - Return missing items explicitly.
   - Add tests for missing expected files and successful readiness.

7. Typed models:
   - Strengthen Pydantic models if already used.
   - Avoid breaking existing public APIs unless tests and docs are updated.
   - Keep outputs structured and serializable.
   - Keep all new functions/classes documented with Google-style docstrings.

8. Error handling:
   - Improve custom errors where useful.
   - Error messages should be explicit but should not leak secrets.
   - Add tests for malformed JSONL errors if needed.

9. Documentation updates:
   - 02-agent-toolkit-mcp/mcp-server/README.md
   - 02-agent-toolkit-mcp/README.md
   - 02-agent-toolkit-mcp/docs/ARCHITECTURE.md
   - 02-agent-toolkit-mcp/docs/SAFETY_MODEL.md
   - 02-agent-toolkit-mcp/docs/ROADMAP.md
   - 02-agent-toolkit-mcp/docs/runtime/LOCAL_ONLY_SECURITY_BOUNDARIES.md
   - docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md
   - root README.md only if needed

10. Scripts:
   - Update 02-agent-toolkit-mcp/scripts/run_mcp_checks.sh if needed.
   - Keep 02-agent-toolkit-mcp/scripts/run_checks.sh passing.
   - Do not add destructive scripts.

Rules:
- Keep all docs in English.
- Keep all tools local and read-only.
- Do not mutate Project 1 files.
- Do not delete generated runtime files.
- Do not add real credentials.
- Do not add external APIs.
- Do not hardcode secrets.
- Do not overclaim real deployed MCP integration.
- Keep scripts executable.
- Add Google-style docstrings to every new or modified Python function, method and class.
- Keep prompt history current.
- Keep tests deterministic.
- Avoid broad refactors unrelated to this milestone.

Expected verification:
Run:
- 02-agent-toolkit-mcp/scripts/run_checks.sh
- 02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
- bash -n 02-agent-toolkit-mcp/scripts/*.sh
- git diff --check

Also run:
- cd 02-agent-toolkit-mcp/mcp-server
- uv run pytest
- uv run ruff check .
- uv run mypy src

After implementation, summarize:
1. files created/changed
2. validation hardening added
3. path safety changes
4. tool output/model changes
5. tests added/updated
6. docs updated
7. scripts updated if any
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

cd 02-agent-toolkit-mcp/mcp-server
uv run pytest
uv run ruff check .
uv run mypy src
```

## Result Summary

- Hardened path safety documentation and tool behavior around symlink
  resolution and unsafe child paths.
- Added additive Pydantic output models for report summaries, runtime artifact
  counts and readiness checks.
- Improved `validate_report` with explicit summary extraction and non-fatal
  warnings for empty reports, missing generated timestamps and duplicate
  required headings.
- Improved JSONL tools with total record counts, pending approval counts,
  deterministic ordering, limit validation behavior and redaction coverage.
- Improved `check_runtime_clean` with artifact counts and unsafe symlink error
  reporting.
- Improved `generate_demo_brief` with a structured readiness checklist.
- Expanded MCP tests from 12 to 21 deterministic tests.
- Added test-local `conftest.py` so direct pytest runs can import the
  `src/agent_toolkit_mcp` package without requiring package installation first.
- Added a narrow model fallback for bare system pytest runs where Pydantic is
  not installed, while keeping real Pydantic as the supported runtime path.
- Updated MCP server README, Project 2 README, architecture, safety model,
  roadmap, local security boundaries, root README and root handoff docs.
- Kept Project 1 code and runtime behavior unchanged.

## Verification Results

```text
02-agent-toolkit-mcp/scripts/run_project1_tool_review.sh
Passed. Serialized richer tool outputs against current Project 1 artifacts.

02-agent-toolkit-mcp/scripts/run_checks.sh
Passed. Required files exist and shell script syntax is valid.

02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
Passed. 21 tests passed, ruff clean, mypy clean and shell syntax clean.

bash -n 02-agent-toolkit-mcp/scripts/*.sh
Passed.

git diff --check
Passed.

cd 02-agent-toolkit-mcp/mcp-server && uv run pytest
21 tests passed.

cd 02-agent-toolkit-mcp/mcp-server && uv run ruff check .
Passed.

cd 02-agent-toolkit-mcp/mcp-server && uv run mypy src
Passed with no issues in 6 source files.

/usr/local/Cellar/python@3.10/3.10.9/Frameworks/Python.framework/Versions/3.10/bin/python3.10 -m pytest 02-agent-toolkit-mcp/mcp-server/tests/test_tools.py
Passed. 21 tests passed under direct system pytest without Pydantic installed.
```

## Commit / PR Reference

- Commit: `TBD`
- PR: `TBD`

## Notes

- Tool hardening milestone.
- Keep all tools local, deterministic and read-only.
- Keep Project 1 code and runtime behavior unchanged.
