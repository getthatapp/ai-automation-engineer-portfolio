"""Minimal deterministic MCP server registry for local tool discovery."""

from __future__ import annotations

from typing import Any

from agent_toolkit_mcp.models import ToolDefinition
from agent_toolkit_mcp.tools import call_tool

TOOL_DEFINITIONS = [
    ToolDefinition(
        name="validate_report",
        description="Validate required sections in a local Project 1 Markdown report.",
    ),
    ToolDefinition(
        name="read_run_history",
        description="Read recent sanitized records from a local Project 1 workflow JSONL file.",
    ),
    ToolDefinition(
        name="list_pending_approvals",
        description="List sanitized pending approval summaries from a local Project 1 JSONL queue.",
    ),
    ToolDefinition(
        name="check_runtime_clean",
        description="Report generated Project 1 runtime artifacts without deleting them.",
    ),
    ToolDefinition(
        name="generate_demo_brief",
        description="Generate a deterministic local-only Project 1 demo readiness brief.",
    ),
]


def list_tools() -> list[ToolDefinition]:
    """List deterministic local tools exposed by this package.

    Returns:
        Tool definitions with names and descriptions.
    """

    return TOOL_DEFINITIONS


def invoke_tool(tool_name: str, arguments: dict[str, Any]) -> Any:
    """Invoke a deterministic local tool through the minimal registry.

    Args:
        tool_name: Name of the tool to call.
        arguments: Keyword arguments for the tool.

    Returns:
        Tool result model.
    """

    return call_tool(tool_name, arguments)


def main() -> None:
    """Print registered local tools for manual inspection."""

    for definition in list_tools():
        print(f"{definition.name}: {definition.description}")


if __name__ == "__main__":
    main()
