"""Errors raised by local human approval persistence."""

from pathlib import Path


class ApprovalStoreError(Exception):
    """Base error for approval store failures."""


class ApprovalNotFoundError(ApprovalStoreError):
    """Raised when an approval request cannot be found."""


class ApprovalAlreadyDecidedError(ApprovalStoreError):
    """Raised when recording a decision for a non-pending request."""


class MalformedApprovalRecordLineError(ApprovalStoreError):
    """Raised when an approval JSONL line cannot be decoded safely."""

    def __init__(self, *, path: Path, line_number: int, reason: str) -> None:
        """Initialize a malformed approval record error.

        Args:
            path: JSONL file path.
            line_number: One-based line number.
            reason: Human-readable parse or validation failure reason.
        """

        self.path = path
        self.line_number = line_number
        self.reason = reason
        super().__init__(
            f"Malformed approval record in {path} on line {line_number}: {reason}"
        )
