"""Command-line interface for local AgentOps control tower views."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TextIO, cast

from agentops_control_tower.models import AgentOpsControlTowerView, IngestionError
from agentops_control_tower.reporting import render_agentops_markdown_report
from agentops_control_tower.summaries import build_agentops_control_tower_view

EXIT_SUCCESS = 0
EXIT_INGESTION_ERROR = 1
EXIT_USAGE_ERROR = 2


def main(argv: Sequence[str] | None = None) -> int:
    """Run the `agentops-control-tower` command-line interface.

    Args:
        argv: Optional command arguments. Uses `sys.argv` when omitted.

    Returns:
        Process exit code.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return _dispatch(args, stdout=sys.stdout, stderr=sys.stderr)
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR


def _build_parser() -> argparse.ArgumentParser:
    """Build the top-level CLI argument parser.

    Returns:
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="agentops-control-tower",
        description="Inspect local AgentOps summaries, timelines and reports.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    summary_parser = subcommands.add_parser("summary", help="Print AgentOps summary JSON.")
    _add_source_options(summary_parser)
    summary_parser.add_argument("--pretty", action="store_true", help="Print indented JSON.")
    summary_parser.set_defaults(handler=_handle_summary)

    timeline_parser = subcommands.add_parser("timeline", help="Print AgentOps timeline JSON.")
    _add_source_options(timeline_parser)
    timeline_parser.add_argument("--pretty", action="store_true", help="Print indented JSON.")
    timeline_parser.set_defaults(handler=_handle_timeline)

    report_parser = subcommands.add_parser(
        "export-report",
        help="Render a deterministic local AgentOps Markdown report.",
    )
    _add_source_options(report_parser)
    report_parser.add_argument("--output", type=Path, help="Optional Markdown output path.")
    report_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow --output to replace an existing file.",
    )
    report_parser.set_defaults(handler=_handle_export_report)

    return parser


def _add_source_options(parser: argparse.ArgumentParser) -> None:
    """Add local source path options to a subcommand parser.

    Args:
        parser: Subcommand parser to update.
    """
    parser.add_argument("--run-history", type=Path, help="Project 1 run-history JSONL path.")
    parser.add_argument(
        "--approval-requests",
        type=Path,
        help="Project 1 approval requests JSONL path.",
    )
    parser.add_argument("--report", type=Path, help="Project 1 deterministic Markdown report path.")
    parser.add_argument("--tool-evidence", type=Path, help="Saved Project 2 CLI JSON path.")
    parser.add_argument("--guardrail-output", type=Path, help="Saved guardrail output text path.")


def _dispatch(args: argparse.Namespace, *, stdout: TextIO, stderr: TextIO) -> int:
    """Dispatch parsed CLI arguments to their subcommand handler.

    Args:
        args: Parsed CLI arguments.
        stdout: Stream for successful command output.
        stderr: Stream for user-facing errors.

    Returns:
        Process exit code.
    """
    handler = cast(
        Callable[..., int],
        args.handler,
    )
    return handler(args, stdout=stdout, stderr=stderr)


def _handle_summary(args: argparse.Namespace, *, stdout: TextIO, stderr: TextIO) -> int:
    """Print a local AgentOps summary as JSON.

    Args:
        args: Parsed summary arguments.
        stdout: Stream for JSON output.
        stderr: Stream for user-facing errors.

    Returns:
        Process exit code.
    """
    view = _build_view_from_args(args)
    print(view.summary.model_dump_json(indent=2 if args.pretty else None), file=stdout)
    return _exit_code_for_view_errors(view.ingestion_result.errors, stderr)


def _handle_timeline(args: argparse.Namespace, *, stdout: TextIO, stderr: TextIO) -> int:
    """Print a local AgentOps timeline as JSON.

    Args:
        args: Parsed timeline arguments.
        stdout: Stream for JSON output.
        stderr: Stream for user-facing errors.

    Returns:
        Process exit code.
    """
    view = _build_view_from_args(args)
    print(view.timeline.model_dump_json(indent=2 if args.pretty else None), file=stdout)
    return _exit_code_for_view_errors(view.ingestion_result.errors, stderr)


def _handle_export_report(args: argparse.Namespace, *, stdout: TextIO, stderr: TextIO) -> int:
    """Render or write a deterministic local AgentOps Markdown report.

    Args:
        args: Parsed export-report arguments.
        stdout: Stream for Markdown output when no output path is supplied.
        stderr: Stream for user-facing errors.

    Returns:
        Process exit code.
    """
    view = _build_view_from_args(args)
    report = render_agentops_markdown_report(view)
    if args.output is None:
        print(report, file=stdout, end="")
    else:
        _write_report(args.output, report, overwrite=args.overwrite)
    return _exit_code_for_view_errors(view.ingestion_result.errors, stderr)


def _build_view_from_args(args: argparse.Namespace) -> AgentOpsControlTowerView:
    """Build a control tower view from shared source-path arguments.

    Args:
        args: Parsed command arguments.

    Returns:
        Combined local AgentOps control tower view.
    """
    return build_agentops_control_tower_view(
        run_history_path=args.run_history,
        approval_requests_path=args.approval_requests,
        markdown_report_path=args.report,
        tool_evidence_json_path=args.tool_evidence,
        guardrail_output_text_path=args.guardrail_output,
    )


def _write_report(path: Path, report: str, *, overwrite: bool) -> None:
    """Write a Markdown report to a local file.

    Args:
        path: Destination file path.
        report: Markdown report text.
        overwrite: Whether an existing file may be replaced.

    Raises:
        FileExistsError: If the path exists and overwrite is not enabled.
        OSError: If the file cannot be written.
    """
    if path.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite existing report: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")


def _exit_code_for_view_errors(errors: tuple[IngestionError, ...], stderr: TextIO) -> int:
    """Return the CLI exit code for ingestion errors.

    Args:
        errors: Ingestion errors captured by the local parsers.
        stderr: Stream for concise error summaries.

    Returns:
        Zero when no errors exist, otherwise non-zero.
    """
    if not errors:
        return EXIT_SUCCESS
    print(f"error: ingestion completed with {len(errors)} error(s)", file=stderr)
    return EXIT_INGESTION_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
