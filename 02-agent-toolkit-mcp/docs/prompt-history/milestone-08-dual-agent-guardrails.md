# Project 2 Milestone 8 - Dual-Agent Hook and Guardrail Examples

## Status

Complete.

## Branch

`feature/project-2-m08-dual-agent-guardrails`

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
- 02-agent-toolkit-mcp/docs/runtime/CODEX_PERMISSION_PROFILES.md
- 02-agent-toolkit-mcp/docs/runtime/CLAUDE_CODE_PERMISSION_PROFILES.md
- 02-agent-toolkit-mcp/docs/runtime/LOCAL_ONLY_SECURITY_BOUNDARIES.md
- 02-agent-toolkit-mcp/docs/prompt-history/README.md
- 02-agent-toolkit-mcp/docs/prompt-history/TEMPLATE.md
- 02-agent-toolkit-mcp/docs/prompt-history/milestone-07-ci.md

Continue Project 2: 02-agent-toolkit-mcp.

Milestone 8: dual-agent hook and guardrail examples for Codex and Claude Code.

Branch:
feature/project-2-m08-dual-agent-guardrails

Prompt history requirement:
Create or update:
02-agent-toolkit-mcp/docs/prompt-history/milestone-08-dual-agent-guardrails.md

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
- Project 2 Milestone 6 added a local CLI.
- Project 2 Milestone 7 added GitHub Actions CI and a local CI mirror.
- Project 2 supports both Codex and Claude Code.
- This milestone should add dual-agent hook/guardrail examples.
- Do not modify Project 1 code.
- Do not change Project 1 runtime behavior.
- Do not add external integrations.
- Do not call external APIs.
- Do not require secrets.
- Do not implement destructive tools.
- Do not add frontend UI.
- Do not overclaim that Codex has the same lifecycle hook model as Claude Code.

Important distinction:
- Claude Code can use hook-style lifecycle examples.
- Codex should use hook-equivalent guardrail wrappers, preflight checks, post-run checks, prompt-history checks and permission-profile patterns.
- Do not claim exact hook parity between Codex and Claude Code.

Goal:
Add local, deterministic, read-only guardrail and hook examples for both Codex and Claude Code.

Implement:

1. Add hooks/guardrails directory structure:

02-agent-toolkit-mcp/hooks/
├── README.md
├── claude-code/
│   ├── README.md
│   ├── pre-tool-use-check.sh
│   ├── post-tool-use-audit.sh
│   └── stop-on-dirty-runtime.sh
├── codex/
│   ├── README.md
│   ├── preflight-codex-run.sh
│   ├── postrun-codex-audit.sh
│   └── require-prompt-history.sh
└── shared/
    ├── README.md
    ├── check-no-secrets.sh
    ├── check-runtime-clean.sh
    └── check-prompt-history-updated.sh

2. Hook/guardrail behavior:
- All scripts must use bash with set -euo pipefail.
- All scripts must be local-only.
- All scripts must be deterministic.
- All scripts must be read-only unless explicitly documented as future work.
- Scripts must not delete files.
- Scripts must not mutate Project 1 or Project 2 source files.
- Scripts must not call external APIs.
- Scripts must not require secrets.
- Scripts should print clear pass/fail output.
- Scripts should return non-zero exit codes when guardrails fail.
- Scripts should be executable.

3. Shared scripts:

shared/check-no-secrets.sh:
- Scan selected project files for obvious secret-like patterns.
- Keep scope conservative.
- Avoid false claims of complete secret scanning.
- Should fail if it finds obvious tokens, API keys or password-like assignments.
- Should ignore expected demo credentials only if clearly documented and safe.
- Should not print secret values; print file path and generic finding type.

shared/check-runtime-clean.sh:
- Use existing Project 2 CLI if practical:
  agent-toolkit-mcp check-runtime-clean <project-path>
- Should default to checking ../../01-ai-marketing-ops-agent when run from hooks/shared or support PROJECT_1_PATH override.
- Must be read-only.
- Should fail when runtime artifacts are present.

shared/check-prompt-history-updated.sh:
- Verify that a prompt-history file exists for the current milestone or supplied PROMPT_HISTORY_FILE path.
- Should support PROMPT_HISTORY_FILE env var.
- Should check for sections:
  - Full Prompt or Prompt Used
  - Expected Verification
  - Result Summary
  - Verification Results
- Should fail clearly if missing.

4. Codex guardrail scripts:

codex/preflight-codex-run.sh:
- Run before a Codex milestone execution.
- Check branch is not main unless ALLOW_MAIN=true is set.
- Check worktree state and print warning or fail if dirty depending on STRICT_WORKTREE env var.
- Check prompt-history file exists when PROMPT_HISTORY_FILE is provided.
- Run shared prompt-history check when applicable.
- Print recommended Codex execution mode, e.g. sandboxed / approval-aware.
- Do not invoke Codex.

codex/postrun-codex-audit.sh:
- Run after Codex implementation.
- Run Project 2 checks:
  - scripts/run_checks.sh
  - scripts/run_mcp_checks.sh
  - scripts/run_ci_locally.sh if present
  - bash -n scripts/*.sh
  - git diff --check
- Run shared no-secrets check.
- Do not commit automatically.
- Do not modify files.

codex/require-prompt-history.sh:
- Enforce that a prompt-history file exists and contains required sections.
- Thin wrapper around shared/check-prompt-history-updated.sh.
- Supports PROMPT_HISTORY_FILE env var.
- Does not modify files.

5. Claude Code hook examples:

claude-code/pre-tool-use-check.sh:
- Example hook-style script for pre-tool-use checks.
- Check no obvious unsafe command intent if TOOL_INPUT or COMMAND env vars are provided.
- Block obvious destructive commands such as rm -rf /, sudo destructive operations, credential exfiltration patterns.
- Keep it conservative and document limitations.
- Do not claim complete security.

claude-code/post-tool-use-audit.sh:
- Example hook-style script for post-tool-use audit.
- Run safe local checks:
  - git diff --check
  - bash -n scripts/*.sh where applicable
  - shared no-secrets check
- Do not mutate files.
- Do not commit automatically.

claude-code/stop-on-dirty-runtime.sh:
- Example hook-style script that fails if Project 1 generated runtime artifacts are present.
- Use shared/check-runtime-clean.sh.
- Read-only.

6. Documentation:

Create or update:
- 02-agent-toolkit-mcp/docs/HOOKS_AND_GUARDRAILS.md
- 02-agent-toolkit-mcp/docs/CODEX_HOOK_EQUIVALENTS.md
- 02-agent-toolkit-mcp/docs/CLAUDE_CODE_HOOKS.md

Docs should explain:
- shared concept: preflight, permission profile, command/tool execution, post-run validation, audit output;
- Claude Code hook-style examples;
- Codex hook-equivalent guardrail wrappers;
- differences between Codex and Claude Code;
- how to run scripts locally;
- how scripts integrate with prompt-history process;
- local-only/read-only boundaries;
- limitations and non-goals.

7. Update existing docs:
- 02-agent-toolkit-mcp/README.md
- 02-agent-toolkit-mcp/docs/ARCHITECTURE.md
- 02-agent-toolkit-mcp/docs/CODEX_USAGE.md
- 02-agent-toolkit-mcp/docs/CLAUDE_CODE_USAGE.md
- 02-agent-toolkit-mcp/docs/SAFETY_MODEL.md
- 02-agent-toolkit-mcp/docs/ROADMAP.md
- 02-agent-toolkit-mcp/docs/runtime/MCP_RUNTIME_CONFIGURATION.md
- docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md
- root README.md only if useful and concise

8. Update checks:
- Update 02-agent-toolkit-mcp/scripts/run_checks.sh so it verifies:
  - new hooks directories exist,
  - new hook/guardrail scripts exist,
  - new docs exist,
  - Milestone 8 prompt-history file exists,
  - bash syntax check covers hook scripts too.

9. Add optional helper script if useful:
- 02-agent-toolkit-mcp/scripts/run_guardrail_checks.sh

Behavior:
- Run shared no-secrets check.
- Run shared prompt-history check for Milestone 8 if prompt-history file exists.
- Run Codex postrun audit or the same safe checks directly.
- Run bash -n over scripts and hooks.
- Must be read-only.
- Must be executable.
- Must use bash with set -euo pipefail.

10. Do not add Python code unless necessary.
If Python code is added or modified:
- Add Google-style docstrings to every new or modified function, method and class.
- Run MCP server Python checks.

Rules:
- Keep all docs in English.
- Keep scripts local and read-only.
- Do not mutate Project 1 files.
- Do not mutate Project 2 source files.
- Do not delete generated runtime files.
- Do not add real credentials.
- Do not call external APIs.
- Do not hardcode secrets.
- Do not overclaim complete security.
- Do not claim Codex has identical hook lifecycle behavior to Claude Code.
- Keep scripts executable.
- Add clear comments in shell scripts where useful.
- Keep prompt history current.
- Avoid broad refactors unrelated to this milestone.

Expected verification:
Run:
- 02-agent-toolkit-mcp/scripts/run_checks.sh
- 02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
- 02-agent-toolkit-mcp/scripts/run_ci_locally.sh
- 02-agent-toolkit-mcp/scripts/run_guardrail_checks.sh if added
- bash -n 02-agent-toolkit-mcp/scripts/*.sh
- bash -n 02-agent-toolkit-mcp/hooks/**/*.sh if supported by shell, otherwise find hooks -name '*.sh' -exec bash -n {} \;
- git diff --check

Also run from 02-agent-toolkit-mcp/mcp-server:
- uv run pytest
- uv run ruff check .
- uv run mypy src
- uv run agent-toolkit-mcp --help

After implementation, summarize:
1. files created/changed
2. Claude Code hook examples added
3. Codex guardrail wrappers added
4. shared guardrail scripts added
5. docs updated
6. scripts/checks updated
7. prompt history update
8. verification results
9. recommended next milestone
````

## Expected Verification

```bash
02-agent-toolkit-mcp/scripts/run_checks.sh
02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
02-agent-toolkit-mcp/scripts/run_ci_locally.sh
02-agent-toolkit-mcp/scripts/run_guardrail_checks.sh
bash -n 02-agent-toolkit-mcp/scripts/*.sh
find 02-agent-toolkit-mcp/hooks -name '*.sh' -exec bash -n {} \;
git diff --check

cd 02-agent-toolkit-mcp/mcp-server
uv run pytest
uv run ruff check .
uv run mypy src
uv run agent-toolkit-mcp --help
```

## Result Summary

- Added `hooks/` directory structure with shared guardrails, Codex
  hook-equivalent wrappers and Claude Code hook-style examples.
- Added shared read-only scripts for conservative no-secrets scanning, Project
  1 runtime cleanliness checks and prompt-history structure checks.
- Added Codex wrappers for preflight checks, post-run audits and prompt-history
  enforcement without claiming Claude Code hook parity.
- Added Claude Code hook-style examples for pre-tool-use checks, post-tool-use
  audits and stop-on-dirty-runtime checks.
- Added `scripts/run_guardrail_checks.sh` and updated `scripts/run_checks.sh`
  to verify hook directories, guardrail scripts, docs and hook shell syntax.
- Added docs for hooks and guardrails, Codex hook equivalents and Claude Code
  hooks.
- Updated Project 2 README, architecture, Codex usage, Claude Code usage,
  safety model, roadmap, runtime docs, permission profiles, local-only
  boundaries, prompt-history index, root README and Codex handoff.
- Kept all examples local, deterministic and read-only with no Project 1 code
  or runtime behavior changes.

## Verification Results

```text
02-agent-toolkit-mcp/scripts/run_checks.sh
Passed. Project 2 scaffold files exist and script plus hook syntax validation
passed.

02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
Passed. 32 tests passed, ruff clean, mypy clean and shell syntax clean.

02-agent-toolkit-mcp/scripts/run_ci_locally.sh
Passed. Scaffold checks, MCP checks, shell syntax checks and CLI smoke checks
passed.

02-agent-toolkit-mcp/scripts/run_guardrail_checks.sh
Passed. Shared no-secrets check, prompt-history check, script syntax checks,
hook syntax checks and Codex post-run audit passed.

bash -n 02-agent-toolkit-mcp/scripts/*.sh
Passed.

find 02-agent-toolkit-mcp/hooks -name '*.sh' -exec bash -n {} \;
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

PROMPT_HISTORY_FILE=02-agent-toolkit-mcp/docs/prompt-history/milestone-08-dual-agent-guardrails.md 02-agent-toolkit-mcp/hooks/codex/require-prompt-history.sh
Passed. Prompt-history guardrail passed.

COMMAND='rm -rf /' 02-agent-toolkit-mcp/hooks/claude-code/pre-tool-use-check.sh
Passed as fail-closed behavior. The script returned non-zero and blocked the
obvious destructive command intent.
```

## Commit / PR Reference

- Commit: `TBD`
- PR: `TBD`

## Notes

- Dual-agent hook and guardrail examples milestone.
- Keep examples local, deterministic and read-only.
- Do not claim Codex has exact Claude Code hook parity.
