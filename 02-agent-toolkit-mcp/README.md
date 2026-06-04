# Agent Toolkit for Codex and Claude Code

Project 2 is a reusable toolkit scaffold for building, running and reviewing
agentic automation workflows with both Codex and Claude Code.

This project is not a business workflow app. Project 1 demonstrates a working
marketing operations workflow; Project 2 is the reusable agent-tooling layer
that will support future workflow development.

## Current Status

Status: **Portfolio-ready / case-study-ready**

Milestone 9 is implemented.

Implemented:

- Project documentation for a dual-agent toolkit.
- Codex prompt templates.
- Claude Code command templates.
- Shared skill documentation.
- Lightweight local scripts for scaffold checks and template discovery.
- Safety model for future MCP tools and agent workflows.
- Python MCP server package under `mcp-server/`.
- Deterministic local read-only tools for inspecting Project 1 artifacts.
- Typed Pydantic input and output models.
- Path validation and output sanitization.
- MCP server tests, linting and type checks.
- Read-only adapter scripts for Project 1 artifact reviews.
- Codex prompt templates for Project 1 runtime, report and demo-readiness
  reviews.
- Claude Code command templates that mirror the Codex review flows.
- Project 1 tool-review examples for interpreting reports, run history and
  approval queues.
- Runtime configuration docs and local permission profile guidance for Codex
  and Claude Code.
- Example local runtime configuration docs for read-only, workspace-write and
  approval-required workflows.
- Hardened MCP tool outputs with report summaries, warnings, runtime artifact
  counts, record counts and demo readiness checklists.
- Expanded MCP edge-case tests for path safety, malformed inputs, redaction and
  deterministic ordering.
- Local CLI entrypoint `agent-toolkit-mcp` for invoking deterministic tools
  without writing Python.
- GitHub Actions CI for Project 2 deterministic scaffold, MCP server and CLI
  quality checks.
- Local CI mirror script for running the same Project 2 checks before review.
- Dual-agent hook and guardrail examples for Claude Code and Codex workflows.
- Shared local guardrail checks for prompt history, runtime cleanliness and
  obvious secret-like patterns.
- Recruiter-friendly case study, demo script and requirements coverage matrix.

Not implemented yet:

- External service integrations.
- Real credentials or secret-backed providers.
- Destructive tools, notification integrations or frontend UI.
- Full external MCP SDK transport integration.
- External MCP client transport invocation from Codex or Claude Code.
- Complete security enforcement or exact Codex/Claude Code hook parity.

Reviewer docs:

- [Project 2 Case Study](docs/PROJECT_2_CASE_STUDY.md)
- [Demo Script](docs/DEMO_SCRIPT.md)
- [Requirements Coverage Matrix](docs/REQUIREMENTS_COVERAGE_MATRIX.md)

## Toolkit Concepts

### Codex Prompts

Codex prompts are reusable Markdown prompt templates intended for Codex-style
coding agents. They assume `AGENTS.md`-oriented repository guidance and explicit
task prompts that define goal, scope, constraints and verification.

### Claude Code Commands

Claude Code commands are reusable Markdown command templates intended for
Claude Code workflows. They assume `CLAUDE.md`-oriented project guidance and can
later be paired with Claude Code commands, hooks and skills.

### Shared Skills

Shared skills are reusable instructions for recurring agent tasks such as
workflow review, MCP tool design and runbook writing. They should be useful to
both Codex-style and Claude Code-style agents.

### MCP Tools

MCP tools should contain deterministic operations, typed inputs, validation,
safe error handling and auditable outputs. They should not contain vague LLM
reasoning or hidden business decisions.

The first local tool layer lives in `mcp-server/`. It exposes:

- `validate_report(report_path)`
- `read_run_history(jsonl_path, limit=5)`
- `list_pending_approvals(jsonl_path)`
- `check_runtime_clean(project_path)`
- `generate_demo_brief(project_path)`

These tools inspect local Project 1 artifacts only. They do not call an LLM,
call external APIs, require secrets, delete files or mutate runtime artifacts.

Milestone 5 hardens these tools with richer structured outputs and stronger
edge-case validation while preserving the local-only read-only boundary.

Milestone 6 adds a local console interface for the same deterministic tools:

```bash
cd 02-agent-toolkit-mcp/mcp-server
uv run agent-toolkit-mcp validate-report ../../01-ai-marketing-ops-agent/reports/example.md
uv run agent-toolkit-mcp read-run-history ../../01-ai-marketing-ops-agent/run-history/workflow-runs.jsonl --limit 5
uv run agent-toolkit-mcp list-pending-approvals ../../01-ai-marketing-ops-agent/approval-requests/approval-requests.jsonl
uv run agent-toolkit-mcp check-runtime-clean ../../01-ai-marketing-ops-agent
uv run agent-toolkit-mcp generate-demo-brief ../../01-ai-marketing-ops-agent --pretty
```

The CLI prints structured JSON evidence. It returns non-zero status codes for
invalid reports, dirty runtime artifact checks, malformed JSONL, invalid paths,
invalid limits or incomplete demo-readiness structure.

## Agent Integration Adapters

Milestone 3 adds practical local adapters for agent-assisted reviews. These are
scripts and templates, not a claim of live external MCP client integration.

Run a local tool registry and demo-readiness preview:

```bash
./scripts/demo_mcp_tools.sh
```

Run a read-only Project 1 artifact review:

```bash
./scripts/run_project1_tool_review.sh
```

Both scripts default to `../01-ai-marketing-ops-agent` when run from Project 2.
They fail clearly if expected directories are missing, report missing runtime
artifacts as missing evidence and never delete Project 1 files.

## Runtime Configuration and Permission Profiles

Milestone 4 documents safe local runtime profiles for using Project 2 with
Codex and Claude Code. These profiles are operating guidance and examples, not
enforced runtime policy.

Runtime docs:

- [MCP runtime configuration](docs/runtime/MCP_RUNTIME_CONFIGURATION.md)
- [Codex permission profiles](docs/runtime/CODEX_PERMISSION_PROFILES.md)
- [Claude Code permission profiles](docs/runtime/CLAUDE_CODE_PERMISSION_PROFILES.md)
- [Local-only security boundaries](docs/runtime/LOCAL_ONLY_SECURITY_BOUNDARIES.md)
- [Troubleshooting](docs/runtime/TROUBLESHOOTING.md)

Preview the local permission profiles:

```bash
./scripts/show_permission_profiles.sh
```

## Project Structure

```text
02-agent-toolkit-mcp/
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── claude-commands/
├── codex-prompts/
├── docs/
├── examples/
├── hooks/
├── mcp-server/
├── scripts/
└── skills/
```

## Local Checks

Run lightweight scaffold checks from the project directory:

```bash
./scripts/run_checks.sh
```

From the repository root:

```bash
02-agent-toolkit-mcp/scripts/run_checks.sh
```

The current checks verify expected scaffold files, validate shell script syntax
and print the Project 2 structure.

Run MCP server checks from the project directory:

```bash
./scripts/run_mcp_checks.sh
```

From the repository root:

```bash
02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
```

The MCP checks run pytest, ruff, mypy and shell script syntax validation.

Run the Project 2 CI mirror locally:

```bash
./scripts/run_ci_locally.sh
```

From the repository root:

```bash
02-agent-toolkit-mcp/scripts/run_ci_locally.sh
```

The local CI mirror runs scaffold checks, MCP server tests/lint/type checks,
shell syntax validation and read-only CLI smoke checks. These checks do not
call external APIs, require secrets, run Docker services, deploy anything,
publish packages or mutate Project 1 runtime artifacts.

Run local guardrail checks:

```bash
./scripts/run_guardrail_checks.sh
```

From the repository root:

```bash
02-agent-toolkit-mcp/scripts/run_guardrail_checks.sh
```

Guardrail docs:

- [Hooks and guardrails](docs/HOOKS_AND_GUARDRAILS.md)
- [Codex hook equivalents](docs/CODEX_HOOK_EQUIVALENTS.md)
- [Claude Code hooks](docs/CLAUDE_CODE_HOOKS.md)

## Prompt and Command Helpers

Preview a Codex prompt template:

```bash
./scripts/run_codex_prompt.sh review-workflow
./scripts/run_codex_prompt.sh inspect-project1-runtime
./scripts/run_codex_prompt.sh review-project1-report
./scripts/run_codex_prompt.sh summarize-project1-demo-readiness
```

Preview a Claude Code command template:

```bash
./scripts/run_claude_command.sh review-workflow
./scripts/run_claude_command.sh inspect-project1-runtime
./scripts/run_claude_command.sh review-project1-report
./scripts/run_claude_command.sh summarize-project1-demo-readiness
```

These scripts do not invoke Codex, Claude Code or external services. They are
scaffold helpers for reviewers and future development.

## Safety Defaults

- Do not hardcode secrets.
- Do not add real external credentials.
- Do not perform destructive actions without explicit approval.
- Validate inputs before future MCP tools execute operations.
- Preserve auditability through clear inputs, outputs and logs.
- Keep README and handoff documentation current for every milestone.

## Next Portfolio Step

Project 2 is portfolio-ready. The next major portfolio step is Project 3:
AgentOps Control Tower.
