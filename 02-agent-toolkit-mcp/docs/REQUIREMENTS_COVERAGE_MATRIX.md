# Project 2 Requirements Coverage Matrix

| Requirement / Skill | Evidence in Project 2 | Files / Modules | Demo Talking Point |
| --- | --- | --- | --- |
| MCP tool design | Deterministic local tools with explicit inputs, outputs and status fields | `mcp-server/src/agent_toolkit_mcp/tools.py`, `server.py` | "The tool layer is testable deterministic code, not hidden LLM reasoning." |
| Deterministic local tools | Tools inspect Project 1 reports, run history, approval queues and runtime artifacts from disk | `tools.py`, `models.py` | "Every tool runs locally and produces repeatable JSON evidence." |
| Python package structure | Dedicated package with source layout, tests and package metadata | `mcp-server/pyproject.toml`, `mcp-server/src/`, `mcp-server/tests/` | "This is packaged as reusable Python tooling rather than loose scripts." |
| Typed models | Pydantic models define structured tool inputs and outputs | `mcp-server/src/agent_toolkit_mcp/models.py` | "Structured outputs make the tools easier to validate and consume." |
| Path safety | Local path helpers resolve paths and constrain artifact inspection | `mcp-server/src/agent_toolkit_mcp/path_safety.py`, tests | "Path handling is explicit because local tools should not wander across the filesystem." |
| CLI tooling | `agent-toolkit-mcp` exposes tool functions as reviewer-friendly commands | `mcp-server/src/agent_toolkit_mcp/cli.py`, `mcp-server/pyproject.toml` | "Reviewers can run the tool layer without writing Python." |
| Codex prompt workflows | Codex-oriented templates for workflow review and Project 1 artifact inspection | `codex-prompts/`, `docs/CODEX_USAGE.md` | "Codex prompts instruct the agent to ground answers in deterministic tool evidence." |
| Claude Code command workflows | Claude Code command templates mirror Codex review flows | `claude-commands/`, `docs/CLAUDE_CODE_USAGE.md` | "Both agent surfaces get equivalent review workflows in their own conventions." |
| Shared skills | Reusable workflow review, MCP tool design and runbook-writing instructions | `skills/workflow-review/`, `skills/mcp-tool-design/`, `skills/runbook-writer/` | "Skills capture reusable operating practices for future agent work." |
| Permission profiles | Local read-only, workspace-write and approval-required workflow guidance | `docs/runtime/`, `examples/runtime-config/` | "The toolkit documents expected permission boundaries before agents run." |
| Hooks / guardrails | Codex guardrail wrappers and Claude Code hook-style examples | `hooks/`, `docs/HOOKS_AND_GUARDRAILS.md` | "The examples show preflight, post-run and runtime cleanliness checks." |
| CI/CD | GitHub Actions workflow and local CI mirror run deterministic checks | `.github/workflows/project-2-ci.yml`, `scripts/run_ci_locally.sh` | "CI proves the toolkit can be verified without secrets or external services." |
| Testing | Pytest, ruff and mypy checks cover MCP server behavior | `mcp-server/tests/`, `scripts/run_mcp_checks.sh` | "The deterministic layer has automated tests and static checks." |
| Documentation | Architecture, safety, usage, runtime, guardrail and case-study docs | `docs/`, `README.md` | "The project is packaged for reviewers, not only for the original author." |
| No-secret / local-only safety | Docs and scripts avoid real credentials and external API calls | `docs/SAFETY_MODEL.md`, `hooks/shared/check-no-secrets.sh` | "The demo works without live credentials and avoids external service dependencies." |
| Integration with Project 1 artifacts | Tools inspect Project 1 reports, workflow history, approvals and runtime cleanliness | `scripts/run_project1_tool_review.sh`, CLI examples | "Project 2 adds review tooling around Project 1 without modifying Project 1." |
| Prompt history discipline | Every milestone preserves the full implementation prompt and verification results | `docs/prompt-history/` | "Prompt history makes the agent-assisted development process auditable." |
| Reviewer walkthrough | Case study and demo script explain what to show in a 5-10 minute review | `docs/PROJECT_2_CASE_STUDY.md`, `docs/DEMO_SCRIPT.md` | "A reviewer can understand the project quickly and reproduce the key checks." |
| Clear limitations | Docs state that external MCP deployment, complete security enforcement and Codex/Claude hook parity are not implemented | `docs/PROJECT_2_CASE_STUDY.md`, `docs/SAFETY_MODEL.md`, `docs/CODEX_HOOK_EQUIVALENTS.md` | "The project describes what exists and avoids claiming production integrations that are not present." |
