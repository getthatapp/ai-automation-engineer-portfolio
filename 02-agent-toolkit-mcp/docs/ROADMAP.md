# Roadmap

## Milestone 1 - Scaffold

Status: complete after this milestone.

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

## Milestone 6 - Runtime Packaging or Hook Examples

Planned scope:

- package local MCP runtime configuration examples more explicitly; or
- add Claude Code hook examples that stay local-only and approval-aware;
- keep deterministic tools read-only and credential-free;
- avoid deployed external integrations unless a future milestone explicitly
  implements and verifies them.

## Later Milestones

Potential later work:

- hook examples for Claude Code workflows;
- CI for Project 2;
- expanded integration examples using Project 1 artifacts.
