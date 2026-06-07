"""Display helpers for local AgentOps artifact paths."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def format_display_path(path: str | Path, base_path: Path | None = None) -> str:
    """Format a local path for deterministic reviewer-facing display.

    Args:
        path: Local path to display.
        base_path: Optional base path used for relative display. Defaults to the
            Project 3 root.

    Returns:
        Project-relative path text when possible; otherwise a stable readable
        path string.
    """
    source_path = Path(path)
    if not source_path.is_absolute():
        return source_path.as_posix()

    resolved_base = (base_path or PROJECT_ROOT).resolve(strict=False)
    resolved_path = source_path.resolve(strict=False)
    try:
        return resolved_path.relative_to(resolved_base).as_posix()
    except ValueError:
        return source_path.as_posix()
