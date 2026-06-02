# Milestone 13 - CI/CD

Curated reconstruction based on the implemented milestone.

## Purpose

Add GitHub Actions CI so external reviewers can see automated Project 1 quality
checks on GitHub.

## Prompt Used

```text
Continue Project 1: 01-ai-marketing-ops-agent.

Milestone 13: implement CI/CD for Project 1.

Goal:
Add GitHub Actions CI for Project 1 so external reviewers can see automated quality checks on GitHub.

Implement:
- .github/workflows/project-1-ci.yml
- pull_request trigger
- push to main trigger
- path filters for Project 1 and portfolio docs where practical
- Python 3.12 setup
- uv installation and dependency sync
- Playwright Chromium installation
- pytest, ruff and mypy checks
- docker compose config validation
- bash syntax checks for scripts
- local mirror script at scripts/run_ci_locally.sh
- documentation updates explaining CI and local equivalent commands

Constraints:
- Do not call real external APIs.
- Do not require real secrets.
- Do not send real notifications.
- Do not run long-lived Docker Compose services.
- Do not commit generated runtime files.
- Do not add deployment, image publishing or cloud infrastructure.

After implementation, summarize workflow triggers, jobs, local CI command, docs and verification.
```

## Expected Verification

```text
./scripts/run_ci_locally.sh
git diff --check
```

## Result Summary

Implemented Project 1 GitHub Actions CI and a local CI mirror script covering
dependency sync, Playwright Chromium install, pytest, ruff, mypy, Docker Compose
config validation and Bash syntax checks.

Verified status from the handoff:

```text
105 tests passed
ruff clean
mypy clean
docker compose config validates
bash script syntax clean
git diff --check clean
```

