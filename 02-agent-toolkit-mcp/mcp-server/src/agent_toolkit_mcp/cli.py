"""Command-line interface for deterministic local MCP-style tools."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, cast

from agent_toolkit_mcp.tools import (
    check_runtime_clean,
    generate_demo_brief,
    list_pending_approvals,
    read_run_history,
    validate_report,
)

EXIT_SUCCESS = 0
EXIT_STATUS_FAILED = 1


def main(argv: Sequence[str] | None = None) -> int:
    """Run the local MCP tool CLI.

    Args:
        argv: Optional argument sequence. Uses `sys.argv[1:]` when omitted.

    Returns:
        Process exit code.
    """

    args_list = list(sys.argv[1:] if argv is None else argv)
    pretty, normalized_args = _extract_pretty_flag(args_list)
    parser = _build_parser()
    args = parser.parse_args(normalized_args)
    handler = _namespace_callable(args, "handler")
    exit_code_mapper = _namespace_callable(args, "exit_code_mapper")
    result = handler(args)
    print(_serialize_result(result, pretty=pretty))
    return int(exit_code_mapper(result))


def _build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser and subcommands.

    Returns:
        Configured argument parser.
    """

    parser = argparse.ArgumentParser(
        prog="agent-toolkit-mcp",
        description="Invoke deterministic local read-only Project 2 MCP tools.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print indented JSON output. This flag is accepted before or after subcommands.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate-report",
        help="Validate required sections in a local Project 1 Markdown report.",
    )
    validate_parser.add_argument("report_path", type=Path)
    validate_parser.set_defaults(
        handler=_handle_validate_report,
        exit_code_mapper=_exit_code_for_validate_report,
    )

    history_parser = subparsers.add_parser(
        "read-run-history",
        help="Read recent sanitized workflow run history records from JSONL.",
    )
    history_parser.add_argument("jsonl_path", type=Path)
    history_parser.add_argument("--limit", type=int, default=5)
    history_parser.set_defaults(
        handler=_handle_read_run_history,
        exit_code_mapper=_exit_code_for_jsonl_reader,
    )

    approvals_parser = subparsers.add_parser(
        "list-pending-approvals",
        help="List sanitized pending approval summaries from JSONL.",
    )
    approvals_parser.add_argument("jsonl_path", type=Path)
    approvals_parser.set_defaults(
        handler=_handle_list_pending_approvals,
        exit_code_mapper=_exit_code_for_jsonl_reader,
    )

    runtime_parser = subparsers.add_parser(
        "check-runtime-clean",
        help="Report generated Project 1 runtime artifacts without deleting them.",
    )
    runtime_parser.add_argument("project_path", type=Path)
    runtime_parser.set_defaults(
        handler=_handle_check_runtime_clean,
        exit_code_mapper=_exit_code_for_check_runtime_clean,
    )

    brief_parser = subparsers.add_parser(
        "generate-demo-brief",
        help="Generate a deterministic local-only Project 1 demo readiness brief.",
    )
    brief_parser.add_argument("project_path", type=Path)
    brief_parser.set_defaults(
        handler=_handle_generate_demo_brief,
        exit_code_mapper=_exit_code_for_generate_demo_brief,
    )

    return parser


def _extract_pretty_flag(argv: Sequence[str]) -> tuple[bool, list[str]]:
    """Extract `--pretty` from any CLI position.

    Args:
        argv: Raw argument sequence.

    Returns:
        Tuple of the flag value and arguments without `--pretty`.
    """

    pretty = False
    normalized_args: list[str] = []
    for arg in argv:
        if arg == "--pretty":
            pretty = True
            continue
        normalized_args.append(arg)
    return pretty, normalized_args


def _namespace_callable(args: argparse.Namespace, name: str) -> Callable[[Any], Any]:
    """Read a callable value from parsed CLI arguments.

    Args:
        args: Parsed CLI arguments.
        name: Attribute name expected to contain a callable.

    Returns:
        Callable stored on the namespace.

    Raises:
        TypeError: If the namespace value is missing or not callable.
    """

    value = getattr(args, name)
    if not callable(value):
        raise TypeError(f"CLI parser attribute is not callable: {name}")
    return cast("Callable[[Any], Any]", value)


def _handle_validate_report(args: argparse.Namespace) -> Any:
    """Run the report validation tool.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Tool result model.
    """

    return validate_report(args.report_path)


def _handle_read_run_history(args: argparse.Namespace) -> Any:
    """Run the run-history reader tool.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Tool result model.
    """

    return read_run_history(args.jsonl_path, limit=args.limit)


def _handle_list_pending_approvals(args: argparse.Namespace) -> Any:
    """Run the pending-approvals listing tool.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Tool result model.
    """

    return list_pending_approvals(args.jsonl_path)


def _handle_check_runtime_clean(args: argparse.Namespace) -> Any:
    """Run the runtime cleanliness check tool.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Tool result model.
    """

    return check_runtime_clean(args.project_path)


def _handle_generate_demo_brief(args: argparse.Namespace) -> Any:
    """Run the demo brief generation tool.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Tool result model.
    """

    return generate_demo_brief(args.project_path)


def _exit_code_for_validate_report(result: Any) -> int:
    """Map a report validation result to a process exit code.

    Args:
        result: Tool result model.

    Returns:
        Process exit code.
    """

    return EXIT_SUCCESS if result.valid and not result.errors else EXIT_STATUS_FAILED


def _exit_code_for_jsonl_reader(result: Any) -> int:
    """Map JSONL reader results to a process exit code.

    Args:
        result: Tool result model.

    Returns:
        Process exit code.
    """

    if result.errors or result.malformed_lines:
        return EXIT_STATUS_FAILED
    return EXIT_SUCCESS


def _exit_code_for_check_runtime_clean(result: Any) -> int:
    """Map a runtime cleanliness result to a process exit code.

    Args:
        result: Tool result model.

    Returns:
        Process exit code.
    """

    return EXIT_SUCCESS if result.clean and not result.errors else EXIT_STATUS_FAILED


def _exit_code_for_generate_demo_brief(result: Any) -> int:
    """Map a demo brief result to a process exit code.

    Args:
        result: Tool result model.

    Returns:
        Process exit code.
    """

    return EXIT_SUCCESS if result.ready and not result.errors else EXIT_STATUS_FAILED


def _serialize_result(result: Any, *, pretty: bool) -> str:
    """Serialize a tool result as JSON.

    Args:
        result: Tool result model or plain serializable value.
        pretty: Whether to indent the JSON output.

    Returns:
        JSON string.
    """

    indent = 2 if pretty else None
    return json.dumps(_to_jsonable(result), indent=indent, sort_keys=True)


def _to_jsonable(value: Any) -> Any:
    """Convert Pydantic-style models and common values into JSON-safe data.

    Args:
        value: Value to convert.

    Returns:
        JSON-serializable value.
    """

    if hasattr(value, "model_dump"):
        return _to_jsonable(value.model_dump())
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


if __name__ == "__main__":
    raise SystemExit(main())
