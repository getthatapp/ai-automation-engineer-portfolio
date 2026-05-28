"""Errors raised by local workflow run recording."""

from pathlib import Path


class MalformedRunRecordLineError(ValueError):
    """Raised when a JSONL run-history line cannot be decoded safely."""

    def __init__(self, *, path: Path, line_number: int, reason: str) -> None:
        """Initialize a malformed JSONL line error.

        Args:
            path: JSONL file path.
            line_number: One-based line number.
            reason: Human-readable parse or validation failure reason.
        """
        self.path = path
        self.line_number = line_number
        self.reason = reason
        super().__init__(
            f"Malformed run record in {path} on line {line_number}: {reason}"
        )
