# Claude Code Usage

Claude Code-oriented workflows in this project are guided by `CLAUDE.md`,
command templates under `claude-commands/` and shared skills under `skills/`.

## Command Pattern

Each Claude Code command should include:

- purpose;
- expected inputs;
- safety constraints;
- execution steps;
- review checklist;
- verification commands.

## Running a Command Template

Preview a command from the project directory:

```bash
./scripts/run_claude_command.sh review-workflow
```

The helper prints the template path and content. It does not invoke Claude Code
or call external services.

## Claude Code Positioning

Claude Code commands should be useful for repeatable engineering tasks such as
reviewing workflows, generating runbooks and investigating CI failures. Future
milestones may add hooks and executable command integration.

