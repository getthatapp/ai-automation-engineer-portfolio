# Reviewer Local-Run Scripts

Curated reconstruction based on the implemented task.

## Purpose

Make Project 1 easy for an external reviewer or recruiter to run locally
without relying on personal shell aliases.

## Prompt Used

```text
Continue Project 1: 01-ai-marketing-ops-agent.

Task:
Improve external reviewer local run experience.

Goal:
Make it easy for an external reviewer or recruiter to run the project locally without relying on personal shell aliases.

Implement scripts under 01-ai-marketing-ops-agent/scripts/:
- run_checks.sh
- run_workflow.sh
- run_workflow_with_llm.sh
- clean_runtime.sh
- start_services.sh if useful

Script requirements:
- use bash with set -euo pipefail
- be safe to run from the project directory
- use demo credentials by default for the mock marketing panel
- allow env vars to override defaults
- do not hardcode real secrets
- do not commit generated reports, history or approval records
- print useful next-step information such as latest report path and latest run record

Documentation:
- update root README.md
- update 01-ai-marketing-ops-agent/README.md
- update docs/RUNBOOK.md if needed

Do not implement notification integrations or change runtime behavior.

After implementation, summarize scripts, local demo flow, docs and verification.
```

## Expected Verification

```text
uv run pytest
uv run ruff check .
uv run mypy src
bash -n scripts/*.sh
git diff --check
```

## Result Summary

Added reviewer-friendly helper scripts for starting services, running the
workflow, running with mock LLM interpretation, cleaning runtime artifacts and
running quality checks. Documentation now includes a local demo flow with safe
demo credentials and generated-output inspection commands.

