# Project 2 Demo Script

This walkthrough is designed for a 5-10 minute recruiter or technical reviewer
demo. It assumes the repository is already checked out and dependencies have
been installed with `uv` where needed.

## 1. Opening Explanation

Project 2 is the reusable agent-tooling layer for the portfolio. Project 1 is
the business automation workflow; Project 2 shows how to inspect, review and
guard that workflow with deterministic local tools, reusable prompts, CLI
commands, permission profiles, CI and dual-agent examples for Codex and Claude
Code.

Talking point:

- "This is not a chatbot or a deployed external MCP service. It is a local,
  deterministic toolkit that makes agent workflows reviewable and safer."

## 2. Relationship to Project 1

Show the two project directories:

```bash
ls
ls 01-ai-marketing-ops-agent
ls 02-agent-toolkit-mcp
```

Talking point:

- "Project 2 reads Project 1 artifacts such as reports, run history and
  approval queues. It does not change Project 1 code or runtime behavior."

## 3. Repository Structure

Show the toolkit shape:

```bash
find 02-agent-toolkit-mcp -maxdepth 2 -type d | sort
```

Highlight:

- `mcp-server/` for typed deterministic tools and CLI;
- `codex-prompts/` for Codex prompt workflows;
- `claude-commands/` for Claude Code command workflows;
- `hooks/` for guardrail and hook examples;
- `docs/runtime/` for permission profiles;
- `scripts/` for local reviewer checks.

## 4. MCP Tools

Open or show the local tool package:

```bash
ls 02-agent-toolkit-mcp/mcp-server/src/agent_toolkit_mcp
```

Talking point:

- "The tools are deterministic Python functions with typed inputs and outputs.
  They inspect local files, sanitize outputs where appropriate and avoid
  external APIs, secrets and destructive behavior."

Tool list:

- `validate_report`
- `read_run_history`
- `list_pending_approvals`
- `check_runtime_clean`
- `generate_demo_brief`

## 5. CLI Invocation

Run the CLI help and a read-only demo brief:

```bash
cd 02-agent-toolkit-mcp/mcp-server
uv run agent-toolkit-mcp --help
uv run agent-toolkit-mcp generate-demo-brief ../../01-ai-marketing-ops-agent --pretty
uv run agent-toolkit-mcp check-runtime-clean ../../01-ai-marketing-ops-agent --pretty
cd ../..
```

Talking point:

- "The CLI lets reviewers invoke the same tool layer without writing Python.
  It prints JSON evidence and uses process exit codes for status checks."

## 6. Codex Prompt Templates

Preview Codex prompt templates:

```bash
cd 02-agent-toolkit-mcp
./scripts/run_codex_prompt.sh inspect-project1-runtime
./scripts/run_codex_prompt.sh summarize-project1-demo-readiness
cd ..
```

Talking point:

- "Codex workflows are prompt-driven and `AGENTS.md`-oriented. The prompt
  templates instruct the agent to use deterministic tool output as evidence."

## 7. Claude Code Command Templates

Preview Claude Code command templates:

```bash
cd 02-agent-toolkit-mcp
./scripts/run_claude_command.sh inspect-project1-runtime
./scripts/run_claude_command.sh summarize-project1-demo-readiness
cd ..
```

Talking point:

- "Claude Code workflows use command templates and `CLAUDE.md` guidance. The
  commands mirror the Codex review flows while staying local-only."

## 8. Permission Profiles

Show local permission profile docs and preview helper:

```bash
cd 02-agent-toolkit-mcp
./scripts/show_permission_profiles.sh
cd ..
```

Talking point:

- "The repo documents read-only, workspace-write and approval-required
  profiles. These are operating guidance examples, not a claim of a deployed
  policy engine."

## 9. Guardrails and Hook Examples

Show the guardrail directories:

```bash
find 02-agent-toolkit-mcp/hooks -maxdepth 2 -type f | sort
```

Run the guardrail checks:

```bash
02-agent-toolkit-mcp/scripts/run_guardrail_checks.sh
```

Talking point:

- "Claude Code can use hook-style lifecycle examples. Codex uses
  hook-equivalent wrappers such as preflight and post-run checks. The scripts
  are local, deterministic and read-only, but they are not complete security
  enforcement."

## 10. Local CI Mirror

Run the local CI mirror:

```bash
02-agent-toolkit-mcp/scripts/run_ci_locally.sh
```

Talking point:

- "This mirrors the GitHub Actions checks as closely as practical. It runs
  scaffold checks, Python tests, linting, typing, shell syntax checks and CLI
  smoke checks without secrets or external APIs."

## 11. GitHub Actions Workflow

Show the workflow file:

```bash
sed -n '1,220p' .github/workflows/project-2-ci.yml
```

Talking point:

- "The workflow is path-filtered for Project 2 and shared docs. It runs on
  pull requests and pushes to main, installs Python 3.12 and uv, then runs the
  same deterministic checks."

## 12. Closing Talking Points

- "Project 2 demonstrates the tooling layer around agentic automation:
  deterministic tools, local CLI access, prompt workflows, permission guidance,
  guardrails and CI."
- "It integrates with Project 1 by inspecting real local artifacts rather than
  inventing evidence."
- "It intentionally avoids overclaiming: no external MCP deployment, no
  external APIs, no secrets, no destructive tools and no complete security
  enforcement."
- "The next portfolio step is Project 3: AgentOps Control Tower, focused on
  observability, run tracking and operational control."
