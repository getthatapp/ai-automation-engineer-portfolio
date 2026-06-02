Read the root AGENTS.md and docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md first.

Continue Project 1: 01-ai-marketing-ops-agent.

Milestone 12: implement approval-aware notification delivery.

Current state:
- Mock FastAPI services exist.
- Typed httpx clients exist.
- Async Playwright scraper exists.
- Deterministic aggregation exists.
- CampaignSnapshot model exists.
- Deterministic anomaly detection exists.
- AnomalyFinding model exists.
- Deterministic Markdown report writer exists.
- Daily workflow orchestration exists.
- Persistent run recording exists.
- WorkflowRunRecord exists.
- Optional LLM interpretation layer exists.
- LLM token usage is captured when available.
- Deterministic human approval flow exists.
- Approval requests are persisted locally.
- Tests pass.
- Project-level AGENTS.md includes docstring rules.
- Do not move existing files.
- Do not replace deterministic reporting.
- Do not let LLM access raw scraped rows, raw REST responses, raw GraphQL responses, credentials or secrets.
- Do not hardcode notification credentials.

Goal:
Add optional, deterministic, approval-aware notification delivery.

Implement:
1. Typed notification models.
2. Provider abstraction with deterministic/mock provider by default.
3. Notification service that sends report summaries and pending approval references.
4. Optional workflow integration that does not block successful runs.
5. Tests for:
   - mock provider delivery
   - disabled mode
   - approval-aware message content
   - no secrets in persisted or sent payloads
   - workflow continues when notification delivery fails
6. Documentation updates:
   - README.md
   - docs/ARCHITECTURE.md
   - docs/DECISIONS.md
   - docs/RUNBOOK.md
   - .agents/skills/marketing-report/SKILL.md

Implementation guidance:
- Use Pydantic models.
- Use timezone-aware UTC timestamps.
- Keep tests deterministic.
- Do not call real notification APIs in tests.
- Real provider configuration should use environment variables only.
- Keep mypy clean.
- Add Google-style docstrings to all new functions, methods and classes.
- Ensure:
  - uv run pytest passes
  - uv run ruff check . passes
  - uv run mypy src passes

Suggested structure:
- 01-ai-marketing-ops-agent/src/marketing_ops_agent/notifications/
  - __init__.py
  - models.py
  - providers.py
  - service.py
  - errors.py
- 01-ai-marketing-ops-agent/tests/notifications/
  - test_notifications.py

After implementation, summarize:
1. files created/changed
2. notification models
3. provider abstraction
4. notification service behavior
5. workflow integration behavior
6. test coverage added
7. configuration behavior
8. what should be built next
