"""Small Markdown rendering helpers used by deterministic reports."""

from collections.abc import Sequence


def heading(level: int, text: str) -> str:
    """Return a Markdown heading."""

    if level < 1:
        raise ValueError("heading level must be positive")
    return f"{'#' * level} {text}"


def bullet(text: str) -> str:
    """Return a Markdown bullet line."""

    return f"- {text}"


def table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    """Return a GitHub-flavored Markdown table."""

    rendered_rows = [
        "| " + " | ".join(_escape_table_cell(header) for header in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    rendered_rows.extend(
        "| " + " | ".join(_escape_table_cell(cell) for cell in row) + " |" for row in rows
    )
    return "\n".join(rendered_rows)


def _escape_table_cell(value: str) -> str:
    """Escape Markdown table cell separators and newlines."""
    return value.replace("|", r"\|").replace("\n", " ")
