from __future__ import annotations

from dataclasses import dataclass

from .scorecards import OutcomeScoreCard


@dataclass(slots=True)
class AdvisoryPrior:
    task_family: str
    resource_id: str | None
    strength: float
    confidence: float
    advisory_only: bool = True


class OutcomePriorEngine:
    def derive(self, card: OutcomeScoreCard) -> AdvisoryPrior:
        sample_confidence = min(1.0, card.samples / 12.0)
        semantic = card.semantic_pass_rate if card.semantic_pass_rate is not None else card.system_success_rate
        return AdvisoryPrior(
            task_family=card.task_family,
            resource_id=card.resource_id,
            strength=max(0.0, min(1.0, semantic)),
            confidence=sample_confidence,
            advisory_only=True,
        )
