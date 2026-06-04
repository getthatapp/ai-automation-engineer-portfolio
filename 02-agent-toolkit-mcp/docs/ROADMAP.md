# Roadmap

## Milestone 1 - Scaffold

Status: complete.

Scope:

- project README and agent guidance;
- Codex prompt templates;
- Claude Code command templates;
- shared skill documentation;
- lightweight local scripts;
- architecture and safety documentation.

## Milestone 2 - MCP Server Implementation

Status: complete.

Implemented scope:

- add the initial MCP server project structure;
- define deterministic local tools;
- add typed input/output schemas;
- add tests and local verification commands;
- document how Codex and Claude Code can use the MCP server.

Milestone 2 should not add real external service integrations or credentials.

## Milestone 3 - Agent Integration Adapters

Status: complete.

Implemented scope:

- add read-only local scripts for Project 1 tool review and MCP tool demos;
- add Codex prompt templates for Project 1 runtime, report and demo-readiness
  reviews;
- add Claude Code command templates that mirror those review flows;
- add examples that explain how to interpret Project 1 reports, run history and
  approval queues;
- keep all adapters local-only, credential-free and non-destructive.

Milestone 3 does not add external MCP client transport wiring, external service
calls or destructive tools.

## Milestone 4 - Runtime Configuration Examples

Status: complete.

Implemented scope:

- add example MCP client configuration for local deterministic tools;
- document permission profiles and read-only boundaries;
- add more explicit Codex and Claude Code setup notes for local tool access;
- keep all examples local-only and credential-free.

Milestone 4 does not add deployed MCP transport, external service calls or
runtime-enforced permission policy.

## Milestone 5 - MCP Tool Hardening and Richer Validation

Status: complete.

Implemented scope:

- tighten deterministic tool validation and error reporting;
- add richer report/run-history/approval schema checks where useful;
- improve local invocation ergonomics without adding destructive tools;
- expand tests around malformed inputs and boundary conditions;
- keep the tool layer local-only and credential-free.

Milestone 5 does not add external MCP transport, destructive tools or Project 1
runtime behavior changes.

## Milestone 6 - MCP Server CLI Interface

Status: complete after this milestone.

Implemented scope:

- add a local package console script for deterministic tool invocation;
- expose report validation, run-history reading, pending approval listing,
  runtime cleanliness checks and demo brief generation as subcommands;
- print JSON evidence by default with optional pretty JSON output;
- return meaningful local status-check exit codes;
- keep deterministic tools read-only and credential-free.

Milestone 6 does not add deployed external MCP transport, external service
calls, destructive tools, Project 1 behavior changes or frontend UI.

## Milestone 7 - CI for Agent Toolkit MCP

Status: complete.

Implemented scope:

- add GitHub Actions CI for Project 2 scaffold, MCP server and CLI checks;
- add a local CI mirror script for reviewer-friendly verification;
- run deterministic local checks only;
- keep CI credential-free and read-only against Project 1 artifacts.

Milestone 7 does not add external service calls, secrets, Docker service runs,
deployment, package publishing, destructive tools or Project 1 behavior
changes.

## Milestone 8 - Dual-Agent Hook and Guardrail Examples

Status: complete.

Implemented scope:

- add Claude Code hook-style examples for local lifecycle guardrails;
- add Codex hook-equivalent guardrail wrappers;
- add shared read-only guardrail checks;
- document differences between Codex and Claude Code lifecycle models.

Milestone 8 does not add external integrations, secrets, destructive tools,
frontend UI, Project 1 behavior changes or complete security enforcement.

## Milestone 9 - Final Demo Package and Recruiter Walkthrough

Status: complete.

Implemented scope:

- add a Project 2 case study for external reviewers;
- add a 5-10 minute demo script;
- add a requirements coverage matrix mapping role skills to repo evidence;
- update README and handoff docs to mark Project 2 portfolio-ready;
- keep the milestone documentation-first without changing Project 1 behavior,
  Project 2 tool behavior, external integrations or CLI behavior.

Milestone 9 does not add deployed external MCP transport, external service
calls, secrets, destructive tools, frontend UI, new dependencies or complete
security enforcement.

## Optional Future Enhancements

Potential future Project 2 maintenance work:

- expanded packaged examples using Project 1 artifacts;
- additional hook or guardrail templates;
- more local deterministic inspection tools;
- external MCP transport wiring only if it is clearly documented, safe and not
  presented as already implemented.

## Next Portfolio Step

Project 3 - AgentOps Control Tower.
