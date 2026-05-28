"""JSONL-backed local approval request store."""

import json
from collections import OrderedDict
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from pydantic import ValidationError

from marketing_ops_agent.approval.errors import (
    ApprovalAlreadyDecidedError,
    ApprovalNotFoundError,
    MalformedApprovalRecordLineError,
)
from marketing_ops_agent.approval.models import (
    ApprovalDecision,
    ApprovalRequest,
    ApprovalStatus,
)
from marketing_ops_agent.observability import sanitize_observability_text

DEFAULT_APPROVAL_RECORDS_PATH = Path("approval-requests") / "approval-requests.jsonl"


class LocalApprovalStore:
    """Append and read human approval requests from a local JSONL file."""

    def __init__(
        self,
        path: Path | str = DEFAULT_APPROVAL_RECORDS_PATH,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        """Initialize the local approval store.

        Args:
            path: JSONL path used to persist approval records.
            clock: Optional clock used when recording decisions.
        """

        self.path = Path(path)
        self._clock = clock or (lambda: datetime.now(UTC))

    def create(self, request: ApprovalRequest) -> ApprovalRequest:
        """Persist a new approval request unless it already exists.

        Args:
            request: Approval request to persist.

        Returns:
            Existing request with the same ID, or the newly persisted request.

        Side Effects:
            Creates the parent directory and appends one JSON line to disk.
        """

        existing = self.get(request.approval_id)
        if existing is not None:
            return existing
        self._append(request)
        return request

    def list_pending(self) -> list[ApprovalRequest]:
        """Return all pending approval requests in creation order.

        Returns:
            Pending approval requests.

        Raises:
            MalformedApprovalRecordLineError: If persisted JSONL is malformed.
        """

        return [
            request
            for request in self.list_all()
            if request.status is ApprovalStatus.PENDING
        ]

    def list_all(self) -> list[ApprovalRequest]:
        """Return the latest state for every approval request.

        Returns:
            Approval requests in first-seen order with later JSONL entries
            collapsed by approval ID.

        Raises:
            MalformedApprovalRecordLineError: If persisted JSONL is malformed.
        """

        if not self.path.exists():
            return []
        requests: OrderedDict[str, ApprovalRequest] = OrderedDict()
        for request in self._read_all_versions():
            requests[request.approval_id] = request
        return list(requests.values())

    def get(self, approval_id: str) -> ApprovalRequest | None:
        """Return one approval request by ID.

        Args:
            approval_id: Approval request identifier.

        Returns:
            Latest approval request state, or `None` when absent.

        Raises:
            MalformedApprovalRecordLineError: If persisted JSONL is malformed.
        """

        normalized_id = approval_id.strip()
        if not normalized_id or not self.path.exists():
            return None
        matching: ApprovalRequest | None = None
        for request in self._read_all_versions():
            if request.approval_id == normalized_id:
                matching = request
        return matching

    def approve(
        self,
        approval_id: str,
        *,
        decided_by: str,
        reason: str = "",
    ) -> ApprovalRequest:
        """Record an approve decision for a pending request.

        Args:
            approval_id: Approval request identifier.
            decided_by: Human reviewer identifier.
            reason: Optional decision reason.

        Returns:
            Updated approval request.

        Raises:
            ApprovalNotFoundError: If the approval ID is absent.
            ApprovalAlreadyDecidedError: If the request is not pending.

        Side Effects:
            Appends the updated request state to the JSONL file.
        """

        return self._record_decision(
            approval_id,
            status=ApprovalStatus.APPROVED,
            decided_by=decided_by,
            reason=reason,
        )

    def reject(
        self,
        approval_id: str,
        *,
        decided_by: str,
        reason: str = "",
    ) -> ApprovalRequest:
        """Record a reject decision for a pending request.

        Args:
            approval_id: Approval request identifier.
            decided_by: Human reviewer identifier.
            reason: Optional decision reason.

        Returns:
            Updated approval request.

        Raises:
            ApprovalNotFoundError: If the approval ID is absent.
            ApprovalAlreadyDecidedError: If the request is not pending.

        Side Effects:
            Appends the updated request state to the JSONL file.
        """

        return self._record_decision(
            approval_id,
            status=ApprovalStatus.REJECTED,
            decided_by=decided_by,
            reason=reason,
        )

    def _record_decision(
        self,
        approval_id: str,
        *,
        status: ApprovalStatus,
        decided_by: str,
        reason: str,
    ) -> ApprovalRequest:
        """Record a terminal decision and persist the updated request.

        Args:
            approval_id: Approval request identifier.
            status: Terminal approval status.
            decided_by: Human reviewer identifier.
            reason: Optional decision reason.

        Returns:
            Updated approval request.
        """

        request = self.get(approval_id)
        if request is None:
            raise ApprovalNotFoundError(f"Approval request not found: {approval_id}")
        if request.status is not ApprovalStatus.PENDING:
            raise ApprovalAlreadyDecidedError(
                f"Approval request is already {request.status.value}: {approval_id}"
            )

        decision = ApprovalDecision(
            status=status,
            decided_at=self._normalize_datetime(self._clock()),
            decided_by=decided_by,
            reason=reason,
        )
        updated = request.model_copy(update={"status": status, "decision": decision})
        self._append(updated)
        return updated

    def _append(self, request: ApprovalRequest) -> None:
        """Append one approval request state to local JSONL storage.

        Args:
            request: Approval request state to persist.

        Side Effects:
            Creates the parent directory and appends one JSON line to disk.
        """

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as file:
            file.write(f"{request.model_dump_json()}\n")

    def _read_all_versions(self) -> list[ApprovalRequest]:
        """Read every approval request state from JSONL storage.

        Returns:
            Approval request states in file order.

        Raises:
            MalformedApprovalRecordLineError: If any line is empty or malformed.
        """

        records: list[ApprovalRequest] = []
        with self.path.open(encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                stripped = line.strip()
                if not stripped:
                    raise MalformedApprovalRecordLineError(
                        path=self.path,
                        line_number=line_number,
                        reason="empty JSONL line",
                    )
                records.append(self._parse_line(stripped, line_number))
        return records

    def _parse_line(self, line: str, line_number: int) -> ApprovalRequest:
        """Parse one JSONL line into an approval request.

        Args:
            line: Non-empty JSONL line.
            line_number: One-based line number used for diagnostics.

        Returns:
            Validated approval request.

        Raises:
            MalformedApprovalRecordLineError: If JSON decoding or validation fails.
        """

        try:
            decoded: Any = json.loads(line)
        except json.JSONDecodeError as exc:
            raise MalformedApprovalRecordLineError(
                path=self.path,
                line_number=line_number,
                reason="invalid JSON",
            ) from exc

        if not isinstance(decoded, dict):
            raise MalformedApprovalRecordLineError(
                path=self.path,
                line_number=line_number,
                reason="JSON value is not an object",
            )

        try:
            return ApprovalRequest.model_validate(cast(dict[str, object], decoded))
        except ValidationError as exc:
            raise MalformedApprovalRecordLineError(
                path=self.path,
                line_number=line_number,
                reason="record schema validation failed",
            ) from exc

    @staticmethod
    def _normalize_datetime(value: datetime) -> datetime:
        """Normalize a datetime to UTC, treating naive values as UTC.

        Args:
            value: Datetime to normalize.

        Returns:
            Timezone-aware UTC datetime.
        """

        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)


def approval_text(value: str) -> str:
    """Sanitize text used by approval request builders.

    Args:
        value: Raw approval text.

    Returns:
        Stripped and redacted approval text.
    """

    return sanitize_observability_text(value.strip())
