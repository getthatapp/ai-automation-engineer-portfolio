"""Deterministic anomaly detection package."""

from marketing_ops_agent.anomaly.detector import AnomalyDetector
from marketing_ops_agent.anomaly.models import AnomalyFinding, AnomalySeverity, AnomalyType
from marketing_ops_agent.anomaly.rules import AnomalyThresholds, calculate_cpa, calculate_roi

__all__ = [
    "AnomalyDetector",
    "AnomalyFinding",
    "AnomalySeverity",
    "AnomalyThresholds",
    "AnomalyType",
    "calculate_cpa",
    "calculate_roi",
]
