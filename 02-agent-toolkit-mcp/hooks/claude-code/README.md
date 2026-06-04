# Claude Code Hook Examples

These scripts are examples of hook-style checks for Claude Code workflows.

- `pre-tool-use-check.sh`: inspect command-like environment input before tool
  use and block obvious unsafe intent.
- `post-tool-use-audit.sh`: run read-only local checks after tool use.
- `stop-on-dirty-runtime.sh`: fail when Project 1 generated runtime artifacts
  are present.

These examples are deliberately conservative and incomplete. They do not
provide comprehensive security, mutate files, call external APIs or replace
Claude Code's own configuration.
