# Codex Usage

Codex-oriented workflows in this project are guided by `AGENTS.md` and reusable
prompt templates under `codex-prompts/`.

## Prompt Pattern

Each Codex prompt should include:

- current state;
- goal;
- implementation scope;
- safety constraints;
- files or modules to inspect;
- verification commands;
- expected summary format.

## Running a Prompt Template

Preview a prompt from the project directory:

```bash
./scripts/run_codex_prompt.sh review-workflow
./scripts/run_codex_prompt.sh inspect-project1-runtime
./scripts/run_codex_prompt.sh review-project1-report
./scripts/run_codex_prompt.sh summarize-project1-demo-readiness
```

The helper prints the template path and content. It does not invoke Codex or
call external services.

## Safety Expectations

- Use deterministic code for validation, parsing and tool execution.
- Keep LLM reasoning separate from deterministic operations.
- Do not hardcode secrets.
- Do not run destructive commands without explicit approval.
- Keep all changes scoped to the requested project area.
- Select the narrowest documented permission profile for the task.

## MCP Tool Usage

The local MCP tool layer under `mcp-server/` can conceptually support Codex
reviews of Project 1 artifacts. Codex can use the deterministic tools to:

- validate that a generated Markdown report contains the expected sections;
- inspect recent workflow run history without exposing secret-like values;
- list pending approval request summaries;
- report whether generated runtime artifacts are present;
- generate a local-only Project 1 demo readiness brief.

Current transport wiring is intentionally minimal. Run package checks with:

```bash
./scripts/run_mcp_checks.sh
```

Run the full Project 2 CI mirror locally:

```bash
./scripts/run_ci_locally.sh
```

The CI mirror runs local deterministic scaffold, MCP server and CLI smoke
checks. It does not call external APIs, require secrets, run Docker services,
deploy anything or mutate Project 1 artifacts.

Milestone 6 adds direct local CLI invocation for deterministic tool evidence:

```bash
cd 02-agent-toolkit-mcp/mcp-server
uv run agent-toolkit-mcp validate-report ../../01-ai-marketing-ops-agent/reports/example.md
uv run agent-toolkit-mcp read-run-history ../../01-ai-marketing-ops-agent/run-history/workflow-runs.jsonl --limit 5
uv run agent-toolkit-mcp list-pending-approvals ../../01-ai-marketing-ops-agent/approval-requests/approval-requests.jsonl
uv run agent-toolkit-mcp check-runtime-clean ../../01-ai-marketing-ops-agent
uv run agent-toolkit-mcp generate-demo-brief ../../01-ai-marketing-ops-agent --pretty
```

Codex should treat the CLI JSON as deterministic evidence and should preserve
the CLI status code meaning when using it as a local check.

## Project 1 Agent Review Flows

Milestone 3 adds Codex prompt templates for Project 1 artifact reviews:

- `inspect-project1-runtime`: summarize runtime artifacts, run history and
  approval queue evidence.
- `review-project1-report`: validate a local Markdown report and summarize
  missing sections or review risks.
- `summarize-project1-demo-readiness`: use the deterministic demo brief and
  runtime checks to summarize local demo readiness.

Use the local scripts to produce deterministic evidence before asking Codex to
summarize:

```bash
./scripts/demo_mcp_tools.sh
./scripts/run_project1_tool_review.sh
```

These scripts do not invoke Codex, call external APIs or require secrets. Codex
should treat missing reports, run history or approval queue files as missing
evidence and should not invent data to fill those gaps.

## Permission Profiles

Milestone 4 documents Codex runtime profiles in
`docs/runtime/CODEX_PERMISSION_PROFILES.md`:

- read-only inspection;
- workspace-write development;
- approval-required operations;
- blocked/destructive operation policy.

Preview the local profiles:

```bash
./scripts/show_permission_profiles.sh
```

Use read-only inspection for report and artifact reviews. Use workspace-write
only for scoped Project 2 development. Treat dependency resolution, branch
operations and broader local permissions as approval-required. Destructive
operations remain unsupported.
