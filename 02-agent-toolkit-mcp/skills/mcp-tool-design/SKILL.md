# MCP Tool Design Skill

Use this skill when designing deterministic MCP tools for agentic automation.

## Design Principles

- Define clear tool purpose and boundaries.
- Use typed inputs and outputs.
- Validate inputs before performing operations.
- Prefer deterministic behavior over open-ended LLM reasoning.
- Make side effects explicit.
- Return auditable results and safe errors.
- Keep secrets in environment variables or secret managers, never in code.

## Tool Specification Checklist

- Tool name and purpose.
- Input schema.
- Output schema.
- Permission requirements.
- Failure modes.
- Audit/logging behavior.
- Test scenarios.

## Safety

Do not design tools that perform destructive operations without explicit
approval gates. Do not include real credentials in examples.

