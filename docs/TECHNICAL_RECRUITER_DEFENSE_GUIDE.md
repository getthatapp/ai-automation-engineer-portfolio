# Technical Recruiter Defense Guide

This guide is the main interview-preparation entry point for the AI Automation
Engineer portfolio. It explains how to defend the architecture, milestone
sequence, prompt history and implementation boundaries in front of a technical
recruiter or engineering reviewer.

Use this guide with:

- [Project 1 Defense](milestone-defense/PROJECT_1_DEFENSE.md)
- [Project 2 Defense](milestone-defense/PROJECT_2_DEFENSE.md)
- [Project 3 Defense](milestone-defense/PROJECT_3_DEFENSE.md)
- [Project 1 Case Study](PROJECT_1_CASE_STUDY.md)
- [Project 2 Case Study](../02-agent-toolkit-mcp/docs/PROJECT_2_CASE_STUDY.md)
- [Project 1 Demo Script](DEMO_SCRIPT.md)
- [Project 2 Demo Script](../02-agent-toolkit-mcp/docs/DEMO_SCRIPT.md)
- [Portfolio Handoff](CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md)

## How to use this guide before an interview

Read this file first to get the portfolio-wide explanation. Then review the
project defense files in order:

1. Project 1: the business workflow and production-style automation pipeline.
2. Project 2: the reusable local MCP-style toolkit, CLI, prompts and guardrails.
3. Project 3: the local AgentOps observability layer currently implemented
   through Milestones 1-3.

For each project, focus on the "How to defend it in an interview", "Likely
recruiter questions" and "Strong answers" sections. Practice answering out
loud without reading every implementation detail. The goal is to show that you
understand the engineering decisions, not to memorize file names.

Before a technical screen, also open the prompt-history files. They are useful
evidence that the work was done through scoped prompts with verification
commands, constraints and milestone-by-milestone handoffs.

## What the portfolio demonstrates

This repository demonstrates practical AI automation engineering, not chatbot
wrapping.

Project 1 shows a controlled marketing operations workflow:

- Playwright browser automation for a local HTML-only panel.
- REST and GraphQL client integrations where APIs exist.
- typed Pydantic models for source and business objects.
- deterministic aggregation into `CampaignSnapshot`.
- deterministic anomaly detection into `AnomalyFinding`.
- deterministic Markdown reporting.
- workflow orchestration, local run history and approval records.
- optional LLM interpretation downstream of validated deterministic outputs.
- approval-aware notification behavior through a deterministic mock provider.
- CI checks for tests, linting, typing, Compose validation and script syntax.

Project 2 shows the agent-tooling layer around AI automation:

- local MCP-style deterministic tools.
- typed Pydantic schemas, path safety and output sanitization.
- a local CLI for reviewer evidence.
- Codex prompt templates and Claude Code command templates.
- runtime permission profile documentation.
- local guardrail and hook examples.
- GitHub Actions CI and local CI mirror checks.

Project 3 shows the start of an AgentOps control tower:

- local ingestion models for Project 1 and Project 2 evidence.
- deterministic parsers for JSONL, Markdown, CLI JSON and guardrail text.
- conservative secret-like redaction for ingested payloads.
- deterministic summaries, health status and timeline events.
- local demo scripts for ingestion and summary views.

Project 3 does not yet implement a UI, dashboard, database, scheduler, deployed
AgentOps service or external integrations.

## How the projects connect

The projects are intentionally staged:

```text
Project 1
Business automation workflow and local runtime artifacts
        ↓
Project 2
Local MCP-style tools, CLI, prompts and guardrails that inspect Project 1
        ↓
Project 3
Local AgentOps summaries and timeline over Project 1 and Project 2 evidence
```

Project 1 produces concrete workflow artifacts: reports, run-history JSONL and
approval-request JSONL. Project 2 reads and validates those artifacts with
deterministic tools. Project 3 ingests both Project 1 artifacts and Project 2
tool/guardrail evidence into local summary and timeline models.

This connection matters in an interview because it shows system thinking:
workflow execution, tool-assisted review and observability are separate
responsibilities.

## High-level architecture explanation

Use this short explanation:

> The portfolio is built as a local, deterministic AI automation ecosystem.
> Project 1 is the workflow: it collects data through Playwright, REST and
> GraphQL, validates and aggregates it, detects anomalies, writes reports,
> records runs and creates approval requests. Project 2 is the reviewer and
> agent-tooling layer: it exposes deterministic local tools and a CLI for
> inspecting those artifacts, plus prompt templates and guardrail examples.
> Project 3 is the AgentOps layer: it ingests local evidence and builds
> summaries and a timeline. LLM use is optional and downstream; deterministic
> code owns scraping, validation, calculation, persistence and audit evidence.

If asked for the most important design rule, say:

> APIs are used when APIs exist, Playwright is used only for browser-only
> surfaces, deterministic code owns factual workflow behavior, and LLMs are
> limited to interpretation over validated outputs.

## Answering "Did AI build this or did you understand it?"

Use a direct answer:

> I used AI assistance as a coding and documentation partner, but the work was
> controlled through explicit milestone prompts, architecture rules and
> verification. The prompt history shows the constraints I enforced: local-only
> behavior, no real secrets, no external service claims, deterministic logic
> before LLM interpretation, tests, linting, typing and handoff updates. I can
> explain why each layer exists, what it does, what it does not do and how it
> was verified.

Then give one concrete example:

> For example, in Project 1 the LLM layer was deliberately added after
> scraping, typed clients, aggregation, anomaly detection, reporting and run
> recording. That means the LLM cannot invent metrics or replace deterministic
> findings. It can summarize and recommend over validated inputs only.

Do not say that AI "did everything." Do not pretend AI was not involved. The
strong position is controlled AI-assisted engineering: human-defined scope,
bounded prompts, deterministic verification and clear limitations.

## Controlled AI-assisted engineering

Controlled AI-assisted engineering means the agent was not given vague product
instructions and left to improvise. Each milestone prompt constrained:

- scope: what to build and what not to build.
- boundaries: local-only, no secrets, no real external services unless
  explicitly planned.
- architecture: deterministic logic before optional LLM interpretation.
- safety: no CAPTCHA bypass, no destructive tools, approval gates for sensitive
  actions.
- documentation: README, handoff and prompt-history updates.
- verification: tests, linting, typing, shell syntax, CI mirrors or smoke
  checks.

This is a defensible engineering pattern because each prompt narrows risk and
each milestone has evidence of completion.

## How prompt history proves structured engineering

The prompt-history files are not decorative. They prove that the portfolio was
built through a repeatable workflow:

- define the milestone goal.
- preserve permanent project rules.
- state negative constraints, such as no external APIs or no runtime behavior
  changes.
- require tests and verification.
- record result summaries and verification outcomes.
- update the handoff so future work has context.

That pattern is visible across:

- `docs/prompt-history/project-1/`
- `02-agent-toolkit-mcp/docs/prompt-history/`
- `03-agentops-control-tower/docs/prompt-history/`

If a recruiter asks whether the prompts were random, answer:

> No. The prompt history is milestone-based. Each prompt has scope, constraints,
> expected verification and result tracking. The sequence also shows dependency
> order: scaffold before services, services before clients, clients before
> aggregation, aggregation before anomaly detection, and deterministic outputs
> before optional LLM interpretation.

## What not to overclaim

Be explicit about current limitations:

- Project 1 uses local mock providers for services and notifications.
- Project 1 does not implement real Slack, Telegram or email providers.
- Project 1's LLM layer is optional and mockable; deterministic outputs remain
  the source of truth.
- Project 2 is a local MCP-style toolkit and CLI, not a deployed external MCP
  service.
- Project 2 uses Codex hook-equivalent wrappers, not exact Claude Code hook
  lifecycle parity.
- Project 2 guardrails are examples, not complete security enforcement.
- Project 3 has local ingestion, summaries and timeline only.
- Project 3 does not yet have a UI, dashboard, database, scheduler or deployed
  AgentOps service.

Overclaiming weakens the portfolio. The strongest defense is precise scope.

## Short recruiter-ready pitch

> This portfolio demonstrates AI automation engineering across three layers.
> Project 1 is a working local marketing operations workflow with browser
> automation, API clients, deterministic validation, anomaly detection,
> reporting, observability, approvals and optional LLM interpretation. Project
> 2 is the local agent-tooling layer with deterministic MCP-style tools, CLI
> evidence, reusable prompts, permission docs, guardrail examples and CI.
> Project 3 starts the AgentOps layer by ingesting local evidence and producing
> deterministic summaries and timeline events. The architecture keeps factual
> workflow behavior deterministic and uses AI only in controlled, documented
> places.

## Strong answer patterns

When asked about architecture:

> I separated collection, validation, analysis, reporting, approval and
> observability so each layer can be tested and defended independently.

When asked about LLM usage:

> The LLM is downstream and optional. It interprets validated outputs; it does
> not scrape, validate, calculate or decide workflow truth.

When asked about mocks:

> The mocks are deliberate. They make the portfolio runnable by reviewers
> without secrets while preserving realistic integration boundaries.

When asked about security:

> The project avoids real secrets, keeps generated artifacts out of git, uses
> local-only tools, documents permission profiles and requires human approval
> before sensitive action. The guardrails are examples, not a complete security
> platform.

When asked about verification:

> Verification is tracked per milestone. The repository includes pytest, ruff,
> mypy, shell syntax checks, Compose validation where relevant, CI workflows and
> local CI mirror scripts.

