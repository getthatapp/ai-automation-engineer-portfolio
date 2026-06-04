# Project 2 Milestone 7 - CI for Agent Toolkit MCP

## Status

Complete.

## Branch

`feature/project-2-m07-ci`

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
- 02-agent-toolkit-mcp/docs/prompt-history/README.md
- 02-agent-toolkit-mcp/docs/prompt-history/TEMPLATE.md
- 02-agent-toolkit-mcp/docs/prompt-history/milestone-06-cli-interface.md

Continue Project 2: 02-agent-toolkit-mcp.

Milestone 7: CI for Agent Toolkit MCP.

Branch:
feature/project-2-m07-ci

Prompt history requirement:
Create or update:
02-agent-toolkit-mcp/docs/prompt-history/milestone-07-ci.md

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
- Project 1 has GitHub Actions CI.
- Project 2 Milestone 1 scaffold is complete.
- Project 2 Milestone 2 added deterministic local MCP/tool-layer functions.
- Project 2 Milestone 3 added Codex/Claude integration adapters, prompts, commands and examples.
- Project 2 Milestone 4 added runtime configuration docs and permission profiles.
- Project 2 Milestone 5 hardened MCP tools with richer validation and path safety.
- Project 2 Milestone 6 added a local CLI:
  - agent-toolkit-mcp validate-report
  - agent-toolkit-mcp read-run-history
  - agent-toolkit-mcp list-pending-approvals
  - agent-toolkit-mcp check-runtime-clean
  - agent-toolkit-mcp generate-demo-brief
- Current local verification passes:
  - 02-agent-toolkit-mcp/scripts/run_checks.sh
  - 02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
  - bash -n 02-agent-toolkit-mcp/scripts/*.sh
  - uv run pytest
  - uv run ruff check .
  - uv run mypy src
  - uv run agent-toolkit-mcp --help
- Project 2 does not yet have GitHub Actions CI.
- Do not modify Project 1 code.
- Do not change Project 1 runtime behavior.
- Do not add external integrations.
- Do not call external APIs.
- Do not require secrets.
- Do not implement destructive tools.
- Do not add frontend UI.

Goal:
Add GitHub Actions CI for Project 2 so external reviewers can see automated quality checks for the Agent Toolkit MCP package.

Implement:

1. Add GitHub Actions workflow:
   - .github/workflows/project-2-ci.yml

2. Workflow triggers:
   - pull_request
   - push to main
   - path-filtered to relevant Project 2 and shared docs files if practical:
     - 02-agent-toolkit-mcp/**
     - .github/workflows/project-2-ci.yml
     - README.md
     - AGENTS.md
     - docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md

3. CI job should:
   - run on ubuntu-latest
   - checkout repository
   - set up Python 3.12
   - install uv in a standard stable way
   - run Project 2 scaffold checks:
     - 02-agent-toolkit-mcp/scripts/run_checks.sh
   - run Project 2 MCP server checks:
     - 02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
   - run Bash syntax checks:
     - bash -n 02-agent-toolkit-mcp/scripts/*.sh
   - run CLI smoke checks from 02-agent-toolkit-mcp/mcp-server:
     - uv run agent-toolkit-mcp --help
     - uv run agent-toolkit-mcp generate-demo-brief ../../01-ai-marketing-ops-agent --pretty
     - uv run agent-toolkit-mcp check-runtime-clean ../../01-ai-marketing-ops-agent --pretty

4. CI should not:
   - call real external APIs,
   - require secrets,
   - mutate Project 1,
   - delete runtime files,
   - run Docker services,
   - deploy anything,
   - publish packages.

5. Add or update local CI helper:
   - 02-agent-toolkit-mcp/scripts/run_ci_locally.sh

Behavior:
   - mirror GitHub Actions as closely as practical,
   - run:
     - scripts/run_checks.sh,
     - scripts/run_mcp_checks.sh,
     - bash -n scripts/*.sh,
     - CLI help smoke check,
     - generate-demo-brief smoke check,
     - check-runtime-clean smoke check.
   - use bash with set -euo pipefail,
   - be executable,
   - avoid external APIs,
   - avoid secrets,
   - avoid mutations.

6. Update Project 2 docs:
   - 02-agent-toolkit-mcp/README.md
   - 02-agent-toolkit-mcp/docs/ROADMAP.md
   - 02-agent-toolkit-mcp/docs/ARCHITECTURE.md if needed
   - 02-agent-toolkit-mcp/docs/CODEX_USAGE.md if useful
   - 02-agent-toolkit-mcp/docs/CLAUDE_CODE_USAGE.md if useful
   - 02-agent-toolkit-mcp/docs/runtime/MCP_RUNTIME_CONFIGURATION.md if useful

7. Update root docs:
   - README.md if needed
   - docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md

8. Documentation should explain:
   - what Project 2 CI validates,
   - how to run the same checks locally,
   - that CI uses only local deterministic checks,
   - that CI does not require secrets,
   - that CI does not call external APIs,
   - that CLI smoke checks are read-only.

9. Update run_checks.sh if needed:
   - verify run_ci_locally.sh exists,
   - verify project-2-ci.yml exists,
   - keep checks lightweight.

Rules:
- Keep all docs in English.
- Do not modify Project 1 code.
- Do not change MCP tool behavior unless absolutely required for CI compatibility.
- Do not add real credentials.
- Do not add external APIs.
- Do not hardcode secrets.
- Do not overclaim real deployed MCP integration.
- Keep scripts executable.
- Add comments to shell scripts where useful.
- Add Google-style docstrings only if Python functions/classes are added or modified.
- Keep prompt history current.
- Avoid broad refactors unrelated to this milestone.

Expected verification:
Run:
- 02-agent-toolkit-mcp/scripts/run_checks.sh
- 02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
- 02-agent-toolkit-mcp/scripts/run_ci_locally.sh
- bash -n 02-agent-toolkit-mcp/scripts/*.sh
- git diff --check

Also run from 02-agent-toolkit-mcp/mcp-server:
- uv run pytest
- uv run ruff check .
- uv run mypy src
- uv run agent-toolkit-mcp --help
- uv run agent-toolkit-mcp generate-demo-brief ../../01-ai-marketing-ops-agent --pretty
- uv run agent-toolkit-mcp check-runtime-clean ../../01-ai-marketing-ops-agent --pretty

After implementation, summarize:
1. files created/changed
2. CI workflow triggers
3. CI job steps
4. local CI mirror script
5. docs updated
6. prompt history update
7. verification results
8. recommended next milestone
````

## Expected Verification

```bash
02-agent-toolkit-mcp/scripts/run_checks.sh
02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
02-agent-toolkit-mcp/scripts/run_ci_locally.sh
bash -n 02-agent-toolkit-mcp/scripts/*.sh
git diff --check

cd 02-agent-toolkit-mcp/mcp-server
uv run pytest
uv run ruff check .
uv run mypy src
uv run agent-toolkit-mcp --help
uv run agent-toolkit-mcp generate-demo-brief ../../01-ai-marketing-ops-agent --pretty
uv run agent-toolkit-mcp check-runtime-clean ../../01-ai-marketing-ops-agent --pretty
```

## Result Summary

- Added `.github/workflows/project-2-ci.yml` for Project 2 scaffold, MCP server
  and CLI quality checks.
- Configured workflow triggers for pull requests and pushes to `main` with path
  filters for Project 2, the Project 2 workflow and shared repository docs.
- Added `02-agent-toolkit-mcp/scripts/run_ci_locally.sh` as an executable local
  mirror for the GitHub Actions job.
- Updated `scripts/run_checks.sh` so the Project 2 CI workflow, local CI script
  and Milestone 7 prompt-history file are required scaffold artifacts.
- Updated Project 2 README, roadmap, architecture, Codex usage, Claude Code
  usage, runtime configuration docs, prompt-history index, root README and
  Codex handoff.
- Kept CI local-only and deterministic: no secrets, no external APIs, no Docker
  services, no deployment, no package publishing, no destructive tools and no
  Project 1 code or runtime behavior changes.

## Verification Results

```text
02-agent-toolkit-mcp/scripts/run_checks.sh
Passed. Project 2 scaffold files exist, shell syntax is valid and the new CI
artifacts are listed in the scaffold output.

02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
Passed. 32 tests passed, ruff clean, mypy clean and shell syntax clean.

02-agent-toolkit-mcp/scripts/run_ci_locally.sh
Passed. Ran scaffold checks, MCP server checks, shell syntax checks and CLI
smoke checks.

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

cd 02-agent-toolkit-mcp/mcp-server && uv run agent-toolkit-mcp --help
Passed. Printed CLI help.

cd 02-agent-toolkit-mcp/mcp-server && uv run agent-toolkit-mcp generate-demo-brief ../../01-ai-marketing-ops-agent --pretty
Passed. Printed pretty JSON evidence with ready=true for the current Project 1
demo-readiness structure.

cd 02-agent-toolkit-mcp/mcp-server && uv run agent-toolkit-mcp check-runtime-clean ../../01-ai-marketing-ops-agent --pretty
Passed. Printed pretty JSON evidence with clean=true for the current Project 1
runtime artifact state.
```

## Commit / PR Reference

- Commit: `TBD`
- PR: `TBD`

## Notes

- CI milestone.
- Keep checks local, deterministic and credential-free.
- Keep Project 1 code and runtime behavior unchanged.
