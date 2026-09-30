from __future__ import annotations

from pathlib import Path

from .attribution import OutcomeAttributor
from .bridge import MissionOutcomeBridge
from .counterfactual import CounterfactualComparator
from .drift import OutcomeDriftDetector
from .ledger import OutcomeLedger
from .market_bridge import OutcomeMarketBridge, OutcomeMarketApplyResult
from .models import (
    AttributionEffect,
    AttributionTarget,
    DimensionResult,
    MarketLearningDirective,
    OutcomeDimension,
    VerifiedOutcome,
)
from .outcomes import OutcomeFinalizer
from .priors import OutcomePriorEngine
from .scorecards import OutcomeScoreCardEngine


class OutcomeIntelligence:
    """Composition root for verified-outcome attribution and advisory learning."""

    def __init__(self, ledger_path: str | Path | None = None):
        self.ledger = OutcomeLedger(ledger_path)
        self.ledger.load()
        self.attributor = OutcomeAttributor()
        self.bridge = MissionOutcomeBridge()
        self.finalizer = OutcomeFinalizer(self.attributor)
        self.counterfactual = CounterfactualComparator()
        self.scorecards = OutcomeScoreCardEngine()
        self.priors = OutcomePriorEngine()
        self.drift = OutcomeDriftDetector()
        self.market_bridge = OutcomeMarketBridge()

    def capture_from_mission(
        self,
        mission,
        *,
        task_family: str,
        resource_id: str | None,
        dimensions: list[DimensionResult] | tuple[DimensionResult, ...],
        metadata: dict | None = None,
    ) -> VerifiedOutcome:
        outcome = self.bridge.from_mission(
            mission,
            task_family=task_family,
            resource_id=resource_id,
            dimensions=dimensions,
            metadata=metadata,
        )
        self.finalizer.finalize(outcome)
        self.ledger.record(outcome)
        return outcome

    def market_directive(self, outcome: VerifiedOutcome) -> MarketLearningDirective:
        if not outcome.ay_verified:
            return MarketLearningDirective(outcome.resource_id, outcome.task_family, False, None, None, 0.0, "outcome is not AY-verified")

        resource = outcome.attribution(AttributionTarget.RESOURCE)
        if resource is None:
            return MarketLearningDirective(outcome.resource_id, outcome.task_family, False, None, None, 0.0, "no resource attribution")

        if resource.effect == AttributionEffect.CREDIT:
            semantic = outcome.dimension(OutcomeDimension.SEMANTIC_CORRECTNESS)
            quality = semantic.score if semantic and semantic.score is not None else 1.0
            return MarketLearningDirective(outcome.resource_id, outcome.task_family, True, True, quality, resource.confidence, resource.reason)

        if resource.effect == AttributionEffect.BLAME and resource.confidence >= 0.70:
            return MarketLearningDirective(outcome.resource_id, outcome.task_family, True, False, 0.0, resource.confidence, resource.reason)

        return MarketLearningDirective(
            outcome.resource_id,
            outcome.task_family,
            False,
            None,
            None,
            resource.confidence,
            resource.reason,
            {"resource_effect": resource.effect.value},
        )

    def apply_to_market(self, market, outcome: VerifiedOutcome) -> OutcomeMarketApplyResult:
        """Apply an AY-verified, causally eligible outcome to Intelligence Market."""
        directive = self.market_directive(outcome)
        return self.market_bridge.apply(
            market=market,
            outcome=outcome,
            directive=directive,
        )

