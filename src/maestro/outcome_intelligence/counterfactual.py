from __future__ import annotations

from dataclasses import dataclass

from .models import VerifiedOutcome


@dataclass(slots=True)
class CounterfactualAssessment:
    comparable: bool
    confidence: float
    reason: str


class CounterfactualComparator:
    """Conservative baseline comparability check; never claims causation by itself."""

    def compare(self, current: VerifiedOutcome, baseline: VerifiedOutcome | None) -> CounterfactualAssessment:
        if baseline is None:
            return CounterfactualAssessment(False, 0.0, "no baseline")
        if current.task_family != baseline.task_family:
            return CounterfactualAssessment(False, 0.0, "task family differs")
        if current.resource_id == baseline.resource_id:
            return CounterfactualAssessment(True, 0.35, "same resource and family; uncontrolled confounders remain")
        return CounterfactualAssessment(True, 0.20, "family matches but resource changed; confounders remain")
