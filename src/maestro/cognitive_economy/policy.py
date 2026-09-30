from __future__ import annotations

from dataclasses import dataclass, field

from .models import EconomyTier, MissionComplexity


@dataclass(slots=True)
class TierLimits:
    max_stages: int
    max_resource_calls: int
    max_parallel_candidates: int
    max_tokens_per_call: int
    max_total_tokens: int
    max_latency_ms: int
    max_cost_score: float
    require_critic: bool
    require_verifier: bool
    allow_multi_resource: bool


class CognitiveEconomyPolicy:
    """
    Bootstrap spend envelopes.
    These are ceilings, not targets.
    """

    def __init__(self):
        self.tiers = {
            EconomyTier.MINIMAL: TierLimits(
                1, 1, 1, 1024, 1024, 10_000, 0.10, False, False, False
            ),
            EconomyTier.STANDARD: TierLimits(
                3, 3, 1, 4096, 8_000, 45_000, 0.35, False, True, True
            ),
            EconomyTier.DEEP: TierLimits(
                5, 6, 2, 8192, 24_000, 120_000, 0.70, True, True, True
            ),
            EconomyTier.MAX_GOVERNED: TierLimits(
                6, 8, 2, 16384, 48_000, 300_000, 1.00, True, True, True
            ),
        }

    def tier_for_complexity(self, complexity: MissionComplexity) -> EconomyTier:
        if complexity is MissionComplexity.TRIVIAL:
            return EconomyTier.MINIMAL
        if complexity is MissionComplexity.LOW:
            return EconomyTier.MINIMAL
        if complexity is MissionComplexity.MEDIUM:
            return EconomyTier.STANDARD
        if complexity is MissionComplexity.HIGH:
            return EconomyTier.DEEP
        return EconomyTier.MAX_GOVERNED

    def limits(self, tier: EconomyTier) -> TierLimits:
        return self.tiers[tier]
