"""Path validation helpers for read-only local MCP tools."""

from __future__ import annotations

from pathlib import Path

from agent_toolkit_mcp.errors import InvalidPathError


def resolve_existing_file(path: Path, *, expected_suffix: str | None = None) -> Path:
    """Resolve and validate an existing file path.

    Symlinks are resolved before validation. A symlink is accepted only when its
    target exists and is a file with the expected suffix.

    Args:
        path: Path provided by a tool caller.
        expected_suffix: Optional required file suffix, such as `.md`.

    Returns:
        The resolved file path.

    Raises:
        InvalidPathError: If the path is not an existing file or has the wrong suffix.
    """

    resolved = path.expanduser().resolve(strict=False)
    if not resolved.exists():
        raise InvalidPathError(f"File does not exist: {resolved}")
    if not resolved.is_file():
        raise InvalidPathError(f"Path is not a file: {resolved}")
    if expected_suffix is not None and resolved.suffix != expected_suffix:
        raise InvalidPathError(f"Expected a {expected_suffix} file: {resolved}")
    return resolved


def resolve_optional_file(path: Path) -> Path:
    """Resolve a path that may or may not exist but must not be a directory.

    Symlinks are resolved before validation. A symlink is accepted only when its
    target is absent or points to a file.

    Args:
        path: Path provided by a tool caller.

    Returns:
        The resolved path.

    Raises:
        InvalidPathError: If the path exists and is not a file.
    """

    resolved = path.expanduser().resolve(strict=False)
    if resolved.exists() and not resolved.is_file():
        raise InvalidPathError(f"Path is not a file: {resolved}")
    return resolved


def resolve_existing_directory(path: Path) -> Path:
    """Resolve and validate an existing directory path.

    Symlinks are resolved before validation. A symlink is accepted only when its
    target exists and is a directory.

    Args:
        path: Path provided by a tool caller.

    Returns:
        The resolved directory path.

    Raises:
        InvalidPathError: If the path is not an existing directory.
    """

    resolved = path.expanduser().resolve(strict=False)
    if not resolved.exists():
        raise InvalidPathError(f"Directory does not exist: {resolved}")
    if not resolved.is_dir():
        raise InvalidPathError(f"Path is not a directory: {resolved}")
    return resolved


def safe_relative_path(path: Path, base_path: Path) -> str:
    """Return a path relative to a validated base directory.

    Symlinks are resolved before containment checks so links that point outside
    the base directory are rejected.

    Args:
        path: Path to render.
        base_path: Directory that must contain the path.

    Returns:
        POSIX-style relative path.

    Raises:
        InvalidPathError: If the path is outside the base directory.
    """

    resolved_path = path.resolve(strict=False)
    resolved_base = base_path.resolve(strict=False)
    try:
        return resolved_path.relative_to(resolved_base).as_posix()
    except ValueError as exc:
        raise InvalidPathError(f"Path is outside base directory: {resolved_path}") from exc


def ensure_child_path(path: Path, base_path: Path) -> Path:
    """Validate that a path is inside a base directory.

    Symlinks are resolved before containment checks so links that point outside
    the base directory are rejected.

    Args:
        path: Path to validate.
        base_path: Base directory that should contain the path.

    Returns:
        The resolved child path.

    Raises:
        InvalidPathError: If the path is outside the base directory.
    """

    resolved_path = path.resolve(strict=False)
    resolved_base = base_path.resolve(strict=False)
    try:
        resolved_path.relative_to(resolved_base)
    except ValueError as exc:
        raise InvalidPathError(f"Path is outside base directory: {resolved_path}") from exc
    return resolved_path
