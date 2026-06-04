# Project 3 Milestone 1 - Scaffold

Status: `Complete`
Branch: `feature/project-3-m01-scaffold`

## Full Prompt

```text
Read the root AGENTS.md and docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md first.

Start Project 3 in this portfolio.

Project folder:
03-agentops-control-tower

Project title:
AgentOps Control Tower

Branch:
feature/project-3-m01-scaffold

Context:
- Project 1 is complete and portfolio-ready.
- Project 1 is a working AI Marketing Operations Agent.
- Project 2 is complete and portfolio-ready.
- Project 2 is an Agent Toolkit for Codex and Claude Code with deterministic local MCP-style tools, CLI, CI, guardrails, prompt history and demo docs.
- Project 3 should not duplicate Project 1 or Project 2.
- Project 3 should become a local AgentOps / workflow observability control tower.
- It should eventually monitor workflow runs, approvals, failures, retries, token/cost metadata, agent actions, notification status and human review states.
- This milestone is scaffold/documentation only.
- Do not implement full backend logic yet.
- Do not add frontend UI yet.
- Do not add external integrations.
- Do not require secrets.
- Do not modify Project 1 code.
- Do not modify Project 2 code unless only linking documentation requires it.

Goal:
Create the initial Project 3 scaffold and documentation for AgentOps Control Tower.

Permanent Project 3 rules:
- Work on feature branches, not directly on main.
- Every new function, method and class created by Codex must include a clear Google-style docstring.
- Every milestone must update relevant README.md files.
- Every milestone must update docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md.
- Every milestone must create or update its own prompt-history file under 03-agentops-control-tower/docs/prompt-history/.
- Prompt-history files must include the full prompt, expected verification, result summary, verification results and commit/PR placeholder.
- Documentation must stay in English.
- Do not hardcode secrets.
- Do not add real external service credentials.
- Do not overclaim features that are not implemented.
- Keep verification commands explicit.

Prompt history requirement:
Create:
03-agentops-control-tower/docs/prompt-history/milestone-01-scaffold.md

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

Implement:

1. Create project folder:
   - 03-agentops-control-tower/

2. Add project files:
   - 03-agentops-control-tower/README.md
   - 03-agentops-control-tower/AGENTS.md

3. Add documentation:
   - 03-agentops-control-tower/docs/ARCHITECTURE.md
   - 03-agentops-control-tower/docs/ROADMAP.md
   - 03-agentops-control-tower/docs/OBSERVABILITY_MODEL.md
   - 03-agentops-control-tower/docs/DATA_SOURCES.md
   - 03-agentops-control-tower/docs/SAFETY_MODEL.md
   - 03-agentops-control-tower/docs/LOCAL_DEMO_PLAN.md
   - 03-agentops-control-tower/docs/prompt-history/README.md
   - 03-agentops-control-tower/docs/prompt-history/TEMPLATE.md
   - 03-agentops-control-tower/docs/prompt-history/milestone-01-scaffold.md

4. Add scripts:
   - 03-agentops-control-tower/scripts/run_checks.sh

Script requirements:
- use bash with set -euo pipefail
- be executable
- verify expected scaffold files exist
- run bash syntax checks for project scripts
- print a concise project structure using find
- no external calls
- no mutations outside Project 3

5. Add examples directory:
   - 03-agentops-control-tower/examples/README.md
   - 03-agentops-control-tower/examples/project-1-run-history/README.md
   - 03-agentops-control-tower/examples/project-2-tool-evidence/README.md

These example docs should explain that Project 3 will eventually consume:
- Project 1 run-history JSONL
- Project 1 approval requests JSONL
- Project 1 report files
- Project 2 MCP/CLI evidence
- Project 2 guardrail check outputs

6. Update root README.md:
- Add Project 3 section.
- Mark Project 1 as portfolio-ready / case-study-ready.
- Mark Project 2 as portfolio-ready / case-study-ready.
- Mark Project 3 as started / scaffold ready.
- Link to 03-agentops-control-tower/README.md.
- Keep it concise and recruiter-friendly.

7. Update docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md:
- Set current project to 03-agentops-control-tower.
- Mark Project 3 as started.
- Set next step to Project 3 Milestone 2: local data ingestion models.
- Preserve Project 1 and Project 2 status.
- Add Project 3 permanent rules.
- Mention Project 3 prompt history location.

Content requirements:
- Explain Project 3's purpose clearly:
  "AgentOps Control Tower is a local observability and governance layer for AI automation workflows."
- Explain that Project 3 will focus on:
  - workflow run history,
  - approval states,
  - failure records,
  - retry/cadence metadata,
  - notification status,
  - LLM/token usage metadata when available,
  - guardrail outcomes,
  - local auditability.
- Explain that Project 3 is local-first and deterministic.
- Explain that this scaffold does not yet implement ingestion, dashboards or UI.
- Explain how Project 3 relates to Project 1 and Project 2:
  - Project 1 produces workflow artifacts.
  - Project 2 provides local tools and guardrails.
  - Project 3 will aggregate and observe these signals.

Rules:
- Documentation/scaffold only.
- Do not implement backend ingestion yet.
- Do not add Python/Node package dependencies yet.
- Do not add frontend UI yet.
- Do not call external APIs.
- Do not add secrets.
- Do not change Project 1 code.
- Do not change Project 2 code except root documentation links if needed.
- Keep all docs in English.
- Use professional portfolio tone.
- Do not overclaim implemented features.
- Keep scripts executable.

Expected verification:
Run:
- 03-agentops-control-tower/scripts/run_checks.sh
- bash -n 03-agentops-control-tower/scripts/*.sh
- git diff --check

After implementation, summarize:
1. files created/changed
2. Project 3 purpose
3. scaffold structure
4. docs added
5. scripts added
6. README updates
7. handoff updates
8. prompt history update
9. verification results
10. recommended next milestone
```

## Expected Verification

```bash
03-agentops-control-tower/scripts/run_checks.sh
bash -n 03-agentops-control-tower/scripts/*.sh
git diff --check
```

## Result Summary

- Created the initial `03-agentops-control-tower/` scaffold.
- Added Project 3 README, AGENTS guidance, architecture, roadmap,
  observability model, data source, safety model and local demo plan docs.
- Added prompt-history README, template and Milestone 1 prompt record.
- Added example docs for future Project 1 run-history evidence and Project 2
  tool/guardrail evidence.
- Added executable local scaffold check script.
- Updated root `README.md` and
  `docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md`.
- Preserved scaffold-only scope: no backend ingestion, UI, dependencies,
  external APIs, secrets or Project 1/Project 2 behavior changes.

## Verification Results

```text
03-agentops-control-tower/scripts/run_checks.sh
PASS - Project 3 scaffold checks passed.

bash -n 03-agentops-control-tower/scripts/*.sh
PASS

git diff --check
PASS
```

## Commit / PR Reference

- Commit: `TBD`
- PR: `TBD`

## Notes

- Scaffold and documentation only.
- No backend ingestion, dashboard, UI, dependencies, external APIs or secrets.
