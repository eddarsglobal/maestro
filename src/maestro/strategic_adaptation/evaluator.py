from __future__ import annotations

from .models import StrategyEvaluation


def _b(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


class StrategyEvaluator:
    """
    Scores strategy candidates by expected verified value per operational mass.
    """

    def evaluate(
        self,
        candidate,
        *,
        risk_score: float,
        evidence_urgency: float,
        cost_pressure: float,
        latency_pressure: float,
    ) -> StrategyEvaluation:
        risk = _b(risk_score)
        evidence = _b(evidence_urgency)
        cost_pressure = _b(cost_pressure)
        latency_pressure = _b(latency_pressure)

        quality = _b(candidate.expected_quality)
        evidence_gain = _b(candidate.expected_evidence_gain)
        cost_eff = 1.0 - _b(candidate.expected_cost)
        latency_eff = 1.0 - _b(candidate.expected_latency)

        score = (
            quality * (0.30 + risk * 0.10)
            + evidence_gain * (0.25 + evidence * 0.15)
            + cost_eff * (0.15 + cost_pressure * 0.05)
            + latency_eff * (0.10 + latency_pressure * 0.05)
        )
        normalizer = (
            (0.30 + risk * 0.10)
            + (0.25 + evidence * 0.15)
            + (0.15 + cost_pressure * 0.05)
            + (0.10 + latency_pressure * 0.05)
        )
        score = score / normalizer
        confidence = min(1.0, 0.55 + abs(score - 0.5) * 0.7)

        return StrategyEvaluation(
            strategy_id=candidate.strategy_id,
            score=score,
            confidence=confidence,
            expected_quality=quality,
            expected_evidence_gain=evidence_gain,
            expected_cost=_b(candidate.expected_cost),
            expected_latency=_b(candidate.expected_latency),
            reversible=bool(candidate.reversible),
            rationale={
                "risk_score": risk,
                "evidence_urgency": evidence,
                "cost_pressure": cost_pressure,
                "latency_pressure": latency_pressure,
            },
        )
