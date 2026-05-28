"""Approval request creation service for high-risk workflow outputs."""

from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from hashlib import sha256
from typing import Protocol

from marketing_ops_agent.anomaly import AnomalyFinding, AnomalySeverity
from marketing_ops_agent.approval.approval_store import approval_text
from marketing_ops_agent.approval.models import (
    ApprovalRequest,
    ApprovalRiskLevel,
    ApprovalSource,
    ApprovalStatus,
)
from marketing_ops_agent.llm import (
    LLMActionPriority,
    LLMInterpretationResult,
    LLMRecommendedAction,
)


class ApprovalRequestStore(Protocol):
    """Store contract needed by the approval service."""

    def create(self, request: ApprovalRequest) -> ApprovalRequest:
        """Persist or return an approval request.

        Args:
            request: Approval request to persist.

        Returns:
            Persisted approval request.
        """
        ...


class ApprovalService:
    """Create deterministic approval requests for high-risk workflow outputs."""

    def __init__(
        self,
        *,
        store: ApprovalRequestStore,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        """Initialize the approval service.

        Args:
            store: Approval request persistence boundary.
            clock: Optional clock used for deterministic creation timestamps.
        """

        self._store = store
        self._clock = clock or (lambda: datetime.now(UTC))

    def create_requests_for_run(
        self,
        *,
        run_id: str | None,
        findings: Sequence[AnomalyFinding],
        llm_interpretation: LLMInterpretationResult | None = None,
    ) -> list[ApprovalRequest]:
        """Create approval requests for findings and high-risk LLM actions.

        Args:
            run_id: Optional workflow run identifier.
            findings: Deterministic anomaly findings.
            llm_interpretation: Optional structured LLM interpretation.

        Returns:
            Approval requests created or found for this run.

        Side Effects:
            Persists approval request states through the configured store.
        """

        requests: list[ApprovalRequest] = []
        seen_ids: set[str] = set()

        for finding in findings:
            if not _finding_requires_approval(finding):
                continue
            request = self._request_from_finding(run_id=run_id, finding=finding)
            if request.approval_id in seen_ids:
                continue
            seen_ids.add(request.approval_id)
            requests.append(self._store.create(request))

        if llm_interpretation is not None:
            for action in llm_interpretation.recommendations:
                if not _llm_action_requires_approval(action):
                    continue
                request = self._request_from_llm_action(run_id=run_id, action=action)
                if request.approval_id in seen_ids:
                    continue
                seen_ids.add(request.approval_id)
                requests.append(self._store.create(request))

        return requests

    def _request_from_finding(
        self,
        *,
        run_id: str | None,
        finding: AnomalyFinding,
    ) -> ApprovalRequest:
        """Build an approval request from a deterministic finding.

        Args:
            run_id: Optional workflow run identifier.
            finding: Deterministic finding that requires approval.

        Returns:
            Pending approval request.
        """

        source_reference = finding.anomaly_type.value
        approval_id = _approval_id(
            run_id=run_id,
            source=ApprovalSource.DETERMINISTIC_FINDING,
            campaign_id=finding.campaign_id,
            source_reference=source_reference,
        )
        return ApprovalRequest(
            approval_id=approval_id,
            run_id=run_id,
            campaign_id=finding.campaign_id,
            source=ApprovalSource.DETERMINISTIC_FINDING,
            source_reference=source_reference,
            risk_level=(
                ApprovalRiskLevel.HIGH
                if finding.severity is AnomalySeverity.CRITICAL
                else ApprovalRiskLevel.MEDIUM
            ),
            status=ApprovalStatus.PENDING,
            title=approval_text(
                f"Approve follow-up for {finding.anomaly_type.value} on "
                f"{finding.campaign_id}"
            ),
            rationale=approval_text(
                "Deterministic finding requires human approval before sensitive "
                f"automation: {finding.message}"
            ),
            source_evidence=dict(finding.source_evidence),
            created_at=self._now(),
        )

    def _request_from_llm_action(
        self,
        *,
        run_id: str | None,
        action: LLMRecommendedAction,
    ) -> ApprovalRequest:
        """Build an approval request from a high-risk LLM recommendation.

        Args:
            run_id: Optional workflow run identifier.
            action: LLM recommended action that requires approval.

        Returns:
            Pending approval request.
        """

        source_reference = ",".join(action.source_anomaly_types) or action.title
        approval_id = _approval_id(
            run_id=run_id,
            source=ApprovalSource.LLM_RECOMMENDATION,
            campaign_id=action.campaign_id,
            source_reference=source_reference,
        )
        return ApprovalRequest(
            approval_id=approval_id,
            run_id=run_id,
            campaign_id=action.campaign_id,
            source=ApprovalSource.LLM_RECOMMENDATION,
            source_reference=source_reference,
            risk_level=(
                ApprovalRiskLevel.HIGH
                if action.priority is LLMActionPriority.HIGH
                else ApprovalRiskLevel.MEDIUM
            ),
            status=ApprovalStatus.PENDING,
            title=approval_text(f"Approve LLM recommendation: {action.title}"),
            rationale=approval_text(action.rationale),
            source_evidence={
                "llm_priority": action.priority.value,
                "requires_human_approval": action.requires_human_approval,
            },
            created_at=self._now(),
        )

    def _now(self) -> datetime:
        """Return the current UTC timestamp for approval creation."""

        value = self._clock()
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)


def _finding_requires_approval(finding: AnomalyFinding) -> bool:
    """Return whether a deterministic finding needs approval.

    Args:
        finding: Deterministic anomaly finding.

    Returns:
        True for critical findings or explicit human-review findings.
    """

    return finding.severity is AnomalySeverity.CRITICAL or finding.requires_human_review


def _llm_action_requires_approval(action: LLMRecommendedAction) -> bool:
    """Return whether an LLM recommendation needs approval.

    Args:
        action: LLM recommended action.

    Returns:
        True for high-priority or explicit human-approval actions.
    """

    return action.priority is LLMActionPriority.HIGH or action.requires_human_approval


def _approval_id(
    *,
    run_id: str | None,
    source: ApprovalSource,
    campaign_id: str | None,
    source_reference: str,
) -> str:
    """Build a deterministic approval ID.

    Args:
        run_id: Optional workflow run identifier.
        source: Approval source type.
        campaign_id: Optional campaign identifier.
        source_reference: Deterministic finding or recommendation reference.

    Returns:
        Stable approval request identifier.
    """

    raw_key = "|".join(
        [
            run_id or "no-run",
            source.value,
            campaign_id or "no-campaign",
            source_reference,
        ]
    )
    return f"approval-{sha256(raw_key.encode('utf-8')).hexdigest()[:16]}"
