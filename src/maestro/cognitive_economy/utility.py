from __future__ import annotations

from .models import MarginalUtilityDecision


class MarginalUtilityEngine:
    """
    Continue only when expected quality/evidence gain justifies extra spend.
    """

    def __init__(self, minimum_gain_to_cost_ratio: float = 0.20):
        self.minimum_gain_to_cost_ratio = minimum_gain_to_cost_ratio

    def decide(
        self,
        *,
        current_quality: float,
        expected_next_quality: float,
        current_evidence: float,
        expected_next_evidence: float,
        added_token_fraction: float,
        added_latency_fraction: float,
        added_cost_fraction: float,
    ) -> MarginalUtilityDecision:
        quality_gain = max(0.0, expected_next_quality - current_quality)
        evidence_gain = max(0.0, expected_next_evidence - current_evidence)
        expected_gain = quality_gain * 0.6 + evidence_gain * 0.4

        marginal_cost = max(
            0.0001,
            max(0.0, added_token_fraction) * 0.40
            + max(0.0, added_latency_fraction) * 0.35
            + max(0.0, added_cost_fraction) * 0.25
        )
        ratio = expected_gain / marginal_cost

        return MarginalUtilityDecision(
            continue_spending=ratio >= self.minimum_gain_to_cost_ratio and expected_gain > 0.0,
            expected_gain=expected_gain,
            marginal_cost=marginal_cost,
            ratio=ratio,
            reason=(
                "marginal gain justifies additional cognition"
                if ratio >= self.minimum_gain_to_cost_ratio and expected_gain > 0.0
                else "stop: marginal cognitive utility too low"
            ),
        )
