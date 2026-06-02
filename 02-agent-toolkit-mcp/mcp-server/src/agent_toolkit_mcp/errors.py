"""Custom exceptions for deterministic local MCP tools."""


class AgentToolkitMcpError(Exception):
    """Base error for the Agent Toolkit MCP package."""


class InvalidPathError(AgentToolkitMcpError):
    """Raised when a tool receives an invalid or unsafe filesystem path."""
