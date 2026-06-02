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

## Milestone 3 - Runtime Configuration Examples

Planned scope:

- add example MCP client configuration for local deterministic tools;
- document permission profiles and read-only boundaries;
- add reviewer demo prompts that use Project 1 artifacts through the tool layer;
- keep all examples local-only and credential-free.

## Later Milestones

Potential later work:

- hook examples for Claude Code workflows;
- CI for Project 2;
- reviewer demo scripts;
- integration examples using Project 1 artifacts.
