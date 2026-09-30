from __future__ import annotations

from .models import EconomyTier


class AdaptiveDepthController:
    """
    Learns whether a task family regularly succeeds at lower spend.
    Produces recommendations only; active policy remains governed.
    """

    ORDER = [
        EconomyTier.MINIMAL,
        EconomyTier.STANDARD,
        EconomyTier.DEEP,
        EconomyTier.MAX_GOVERNED,
    ]

    def recommend_tier(self, observations, default_tier: EconomyTier) -> EconomyTier:
        if len(observations) < 3:
            return default_tier

        successful = [
            o for o in observations
            if o.success and o.quality >= 0.85 and o.evidence_sufficient
        ]
        if len(successful) < 3:
            return default_tier

        by_tier = {}
        for o in successful:
            by_tier.setdefault(o.tier, []).append(o)

        for tier in self.ORDER:
            rows = by_tier.get(tier, [])
            if len(rows) >= 3:
                return tier

        return default_tier
