# Project 2 Technical Defense

Project 2 is the Agent Toolkit for Codex and Claude Code. It is
portfolio-ready and case-study-ready. The core defense is that it provides a
local, deterministic agent-tooling layer around Project 1 artifacts without
claiming deployed external MCP infrastructure or complete security enforcement.

## Milestone 1 — Dual-Agent Toolkit Scaffold

### What was built

The initial `02-agent-toolkit-mcp/` scaffold was created with project README,
`AGENTS.md`, `CLAUDE.md`, architecture docs, Codex usage docs, Claude Code
usage docs, safety model, roadmap, reusable Codex prompt templates, Claude Code
command templates, shared skill documentation, examples and lightweight local
scaffold scripts.

### Why this milestone existed

Engineering-wise, it established the shape of a reusable agent workflow
toolkit before implementing tools. Portfolio-wise, it showed that Project 2 was
not another business app; it was the operational layer for reviewing and
guiding AI-assisted work.

### What the prompt enforced

The scaffold rules emphasized local-only behavior, no secrets, no external
service credentials, no overclaiming and documentation-first structure. It
also kept the work separate from Project 1 runtime behavior.

### Key technical decisions

The toolkit supports both Codex and Claude Code while keeping their workflows
distinct. Codex is represented through `AGENTS.md` and prompt templates; Claude
Code is represented through `CLAUDE.md` and command templates.

### How to defend it in an interview

Say: "Project 2 starts by defining a reusable toolkit around agent workflows:
prompts, commands, skills, safety docs and scripts. It does not pretend to be a
deployed tool server on day one."

### Likely recruiter questions

- Why create a second project instead of extending Project 1?
- Why support both Codex and Claude Code?
- Did this milestone implement MCP tools?

### Strong answers

- Project 1 is the workflow; Project 2 is the reviewer and agent-tooling layer.
- Supporting both surfaces shows reusable agent workflow design without tying
  the portfolio to one interface.
- No. It established the scaffold and documentation before tool
  implementation.

### Verification evidence

The scaffold was covered by local scaffold checks and shell syntax checks in
later project verification.

### Limitations

This milestone did not implement the Python MCP-style tool package, CLI,
guardrails or CI.

### What came next

Milestone 2 implemented deterministic local MCP-style tools.

## Milestone 2 — MCP Server Implementation

### What was built

A Python package was created under `02-agent-toolkit-mcp/mcp-server/` with
typed Pydantic models, path safety helpers, deterministic tools and a minimal
local registry. Tools inspect Project 1 reports, run history, pending
approvals, runtime artifacts and demo readiness.

### Why this milestone existed

Engineering-wise, it gave agents and reviewers deterministic evidence instead
of relying on LLM summaries. Portfolio-wise, it demonstrated local MCP-style
tool design with typed inputs and outputs.

### What the prompt enforced

The prompt enforced no direct work on main, no Project 1 code or runtime
behavior changes, no secrets, no external integrations, no external API calls,
no destructive tools, no notification integrations, no cloud deployment, no
frontend UI, no mutation of Project 1 artifacts and no over-engineered
transport layer.

### Key technical decisions

The implementation stayed local and read-only. It used direct Python functions
and a minimal registry rather than claiming full external MCP transport
integration.

### How to defend it in an interview

Say: "The tool layer reads local evidence and returns structured validation
results. It is MCP-style and deterministic, but intentionally not a deployed
external MCP service."

### Likely recruiter questions

- What tools are implemented?
- Do the tools mutate Project 1?
- Is this a real deployed MCP server?

### Strong answers

- `validate_report`, `read_run_history`, `list_pending_approvals`,
  `check_runtime_clean` and `generate_demo_brief`.
- No. They inspect local artifacts read-only.
- No. It is a local MCP-style package and registry; external transport is not
  claimed.

### Verification evidence

Recorded verification included scaffold checks, MCP checks, shell syntax and
`git diff --check`. The MCP package had 12 tests passing, ruff clean and mypy
clean.

### Limitations

No external MCP transport, external service integration, destructive tool or
frontend UI was implemented.

### What came next

Agent integration adapters and prompt/command review flows were added.

## Milestone 3 — Agent Integration Adapters

### What was built

Read-only adapter scripts were added for tool discovery and Project 1 artifact
review. Codex prompt templates and Claude Code command templates were added
for runtime inspection, report review and demo-readiness summaries.

### Why this milestone existed

Engineering-wise, it made the deterministic tools usable in agent-assisted
review flows. Portfolio-wise, it showed how agents should consume evidence
instead of inventing it.

### What the prompt enforced

The prompt enforced no Project 1 code changes, no Project 1 runtime behavior
changes, no external integrations, no external API calls, no secrets, no
destructive tools, no frontend UI, no real MCP runtime overclaims, no claimed
external tool invocation from Codex or Claude Code and no deletion of runtime
files.

### Key technical decisions

The scripts are local adapters around the Python tool package. The prompt and
command templates instruct agents to use deterministic tool outputs as
evidence.

### How to defend it in an interview

Say: "This milestone connected the tool layer to practical review workflows,
but it stayed honest: the scripts and templates are local adapters, not proof
of live external MCP client invocation."

### Likely recruiter questions

- How does Codex use these tools?
- How does Claude Code use them?
- Did this mutate Project 1 artifacts?

### Strong answers

- Through reusable prompt templates that tell Codex what evidence to collect.
- Through matching command templates and local scripts.
- No. The adapters are read-only.

### Verification evidence

Recorded verification included `demo_mcp_tools.sh`,
`run_project1_tool_review.sh`, scaffold checks, MCP checks, shell syntax,
`git diff --check`, 12 tests passing, ruff clean and mypy clean.

### Limitations

The milestone did not implement external MCP client transport invocation from
Codex or Claude Code.

### What came next

Runtime configuration and permission profile documentation were added.

## Milestone 4 — Runtime Configuration and Permission Profiles

### What was built

Runtime docs were added for local MCP/tool shape, Codex profiles, Claude Code
profiles, local-only security boundaries and troubleshooting. Example local
runtime configuration files and a read-only profile preview script were added.

### Why this milestone existed

Engineering-wise, it documented safe operating modes for local agent workflows.
Portfolio-wise, it showed awareness of permissions, approvals and destructive
operation boundaries.

### What the prompt enforced

The prompt enforced no Project 1 code changes, no Project 1 runtime behavior
changes, no external integrations, no external API calls, no secrets, no
destructive tools, no frontend UI, no deployed MCP overclaims, no real
credentials and no unnecessary MCP tool behavior changes.

### Key technical decisions

Permission profiles are documentation and operating guidance, not runtime
policy enforcement. This distinction is important and should be stated clearly
in interviews.

### How to defend it in an interview

Say: "The profiles define safe local usage patterns: read-only review,
workspace-write development, approval-required operations and blocked
destructive operations. They are guidance examples, not a deployed policy
engine."

### Likely recruiter questions

- Are these permissions enforced in code?
- Why document permission profiles?
- Did you add real credentials?

### Strong answers

- No. They are operating guidance and examples.
- Agent workflows need explicit boundaries, especially around write and
  destructive actions.
- No. The examples are local and credential-free.

### Verification evidence

Recorded verification included `show_permission_profiles.sh`, scaffold checks,
MCP checks, shell syntax and `git diff --check`. MCP tests remained at 12
passing with ruff and mypy clean.

### Limitations

There is no deployed permission engine or external MCP runtime enforcement.

### What came next

The MCP-style tools were hardened with richer validation and outputs.

## Milestone 5 — MCP Tool Hardening and Richer Validation

### What was built

Path safety and tool outputs were hardened. The tools gained richer Pydantic
models for report summaries, runtime artifact counts, readiness checks,
warnings, record counts, pending approval counts, deterministic ordering and
expanded redaction behavior.

### Why this milestone existed

Engineering-wise, it improved safety and reviewer usefulness without changing
Project 1. Portfolio-wise, it demonstrated edge-case thinking around local
tooling.

### What the prompt enforced

The prompt enforced no Project 1 code or runtime changes, no external
integrations, no API calls, no secrets, no destructive tools, no frontend UI,
no deployed MCP overclaims, no inferred missing metrics, no LLM calls, no
runtime artifact deletion and no real credentials.

### Key technical decisions

The tools stayed additive and read-only. Symlink resolution and child path
validation were emphasized to reduce unsafe local path handling.

### How to defend it in an interview

Say: "Hardening made the local tools more useful and safer while preserving
their boundary: they inspect local files, validate structure, redact sensitive
looking data and do not mutate artifacts."

### Likely recruiter questions

- What changed during hardening?
- Why care about path safety?
- Did the tools start making business inferences?

### Strong answers

- Outputs became richer and edge-case handling improved.
- Local tools can still be risky if paths are not validated.
- No. They validate and summarize evidence; they do not invent missing metrics.

### Verification evidence

Recorded verification included `run_project1_tool_review.sh`, scaffold checks,
MCP checks, shell syntax and `git diff --check`. Test coverage expanded from
12 to 21 tests, with ruff and mypy clean.

### Limitations

The hardening is not complete security enforcement and does not add deployed
external tool transport.

### What came next

A CLI was added so reviewers could invoke tools without writing Python.

## Milestone 6 — MCP Tool CLI

### What was built

The `agent-toolkit-mcp` CLI was added with argparse subcommands for all five
deterministic tools. It supports compact and pretty JSON output and maps tool
status to useful process exit codes.

### Why this milestone existed

Engineering-wise, it made the tool layer easy to invoke from shell scripts and
CI. Portfolio-wise, it gave recruiters a simple way to generate evidence.

### What the prompt enforced

The prompt enforced no Project 1 code changes, no Project 1 runtime behavior
changes, no external integrations, no external API calls, no secrets, no
destructive tools, no frontend UI and no real deployed external MCP service
overclaims.

### Key technical decisions

The CLI is a thin wrapper around deterministic tools. It prints JSON evidence
even when status-sensitive exit codes indicate invalid or incomplete evidence.

### How to defend it in an interview

Say: "The CLI lowers the barrier for review. A recruiter can run a command and
see structured JSON evidence without writing Python or trusting a model
summary."

### Likely recruiter questions

- What can the CLI do?
- Why JSON output?
- Does the CLI change files?

### Strong answers

- It runs the same five local deterministic tools.
- JSON is easy for scripts, CI and reviewers to inspect.
- No. It remains read-only.

### Verification evidence

Recorded verification included scaffold checks, MCP checks, shell syntax,
`git diff --check`, CLI smoke checks, 32 tests passing, ruff clean and mypy
clean.

### Limitations

The CLI does not add external MCP transport or external service calls.

### What came next

CI was added for the Project 2 scaffold, MCP server and CLI.

## Milestone 7 — CI for Agent Toolkit MCP

### What was built

Project 2 GitHub Actions CI and a local `run_ci_locally.sh` mirror were added.
The checks cover scaffold validation, MCP server tests, linting, typing, shell
syntax and read-only CLI smoke checks.

### Why this milestone existed

Engineering-wise, it made verification repeatable. Portfolio-wise, it gave
reviewers confidence that the toolkit quality checks are not manual-only.

### What the prompt enforced

The prompt enforced no Project 1 code changes, no Project 1 runtime behavior
changes, no external integrations, no API calls, no secrets, no destructive
tools, no frontend UI, no unnecessary MCP behavior changes and no deployed MCP
overclaims.

### Key technical decisions

CI stays local, deterministic and credential-free. It does not run Docker
services, deploy packages, publish artifacts or mutate Project 1.

### How to defend it in an interview

Say: "The CI checks exactly what this project claims: local scaffold health,
Python tool quality, CLI behavior and shell syntax. It does not imply a
deployed service."

### Likely recruiter questions

- What does CI validate?
- Does CI call external APIs?
- Why include a local CI mirror?

### Strong answers

- Scaffold checks, tests, ruff, mypy, script syntax and CLI smoke checks.
- No. It is credential-free and local-only.
- Reviewers can reproduce the GitHub Actions checks locally.

### Verification evidence

Recorded verification included scaffold checks, MCP checks, local CI mirror,
shell syntax, `git diff --check`, 32 tests passing, ruff clean, mypy clean and
CLI smoke checks.

### Limitations

CI does not deploy an MCP service or validate external client integrations.

### What came next

Dual-agent hook and guardrail examples were added.

## Milestone 8 — Dual-Agent Hooks and Guardrails

### What was built

Hook and guardrail example directories were added for shared checks, Codex
hook-equivalent wrappers and Claude Code hook-style examples. Scripts check
prompt-history structure, runtime cleanliness and obvious secret-like patterns.

### Why this milestone existed

Engineering-wise, it demonstrated how local guardrails can wrap agent
workflows. Portfolio-wise, it showed safety awareness without claiming a
complete security product.

### What the prompt enforced

The prompt enforced no Project 1 code or runtime changes, no external
integrations, no external API calls, no secrets, no destructive tools, no
frontend UI, no exact hook parity claim between Codex and Claude Code, read-only
behavior, executable Bash scripts, no automatic commits, no file mutation and
no complete-security overclaims.

### Key technical decisions

Claude Code examples use hook-style lifecycle scripts. Codex examples are
hook-equivalent wrappers such as preflight, post-run audit and prompt-history
checks. They are not claimed to be identical lifecycle hooks.

### How to defend it in an interview

Say: "These guardrails are local examples. Claude Code has hook-style examples;
Codex has wrapper scripts that provide similar preflight or audit behavior, but
I do not claim exact hook parity."

### Likely recruiter questions

- Are these guardrails complete security enforcement?
- Does Codex have the same hooks as Claude Code here?
- What do the scripts check?

### Strong answers

- No. They are examples and local checks.
- No. Codex uses hook-equivalent wrappers, not exact Claude Code lifecycle
  parity.
- Prompt-history structure, runtime cleanliness, shell syntax and obvious
  secret-like patterns.

### Verification evidence

Recorded verification included scaffold checks, MCP checks, local CI mirror,
guardrail suite, hook syntax checks, `git diff --check`, 32 tests passing, ruff
clean, mypy clean and a destructive-command smoke check that failed closed as
expected.

### Limitations

Guardrails are examples, not a complete security system or deployed policy
engine.

### What came next

The final recruiter-facing demo package was added.

## Milestone 9 — Demo Package and Recruiter Walkthrough

### What was built

Project 2 recruiter-facing docs were added: case study, demo script and
requirements coverage matrix. Project docs, root README, roadmap, handoff and
prompt history were updated to mark Project 2 portfolio-ready.

### Why this milestone existed

Engineering-wise, it packaged the toolkit for review without changing runtime
behavior. Portfolio-wise, it made Project 2 defensible in a short recruiter or
technical reviewer walkthrough.

### What the prompt enforced

The prompt enforced no Project 1 code or runtime changes, no Project 2 Python
behavior changes unless absolutely necessary, no CLI behavior changes, no
guardrail behavior changes unless absolutely necessary, no dependencies, no
external integrations, no secrets and no overclaiming.

### Key technical decisions

The docs explain exactly what exists: local deterministic tools, CLI, prompt
templates, permission docs, guardrail examples and CI. They explicitly state
limitations around external MCP deployment, complete security enforcement and
Codex/Claude hook parity.

### How to defend it in an interview

Say: "The demo package turns the toolkit into a reviewable story: how it
relates to Project 1, what deterministic tools exist, how the CLI works, how
Codex and Claude Code workflows differ, and what is intentionally not claimed."

### Likely recruiter questions

- What should a reviewer run?
- Why is this portfolio-ready?
- What are the biggest limitations?

### Strong answers

- The local checks, MCP checks, CI mirror, guardrail checks and CLI demo brief.
- It has working deterministic tools, CLI evidence, docs, CI and a case-study
  walkthrough.
- No deployed external MCP service, no external client transport invocation and
  no complete security enforcement.

### Verification evidence

Recorded verification on 2026-06-04 included scaffold checks, MCP checks, local
CI mirror, guardrail checks, shell and hook syntax, `git diff --check`, 32 tests
passing, ruff clean, mypy clean and CLI smoke checks.

### Limitations

The demo package is documentation-first. It does not add new product features
or runtime behavior.

### What came next

Project 3 started the local AgentOps Control Tower for ingesting and observing
evidence from Projects 1 and 2.

