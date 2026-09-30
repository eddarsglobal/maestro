from __future__ import annotations


class StrategyDriftDetector:
    """
    Detects when spend/retries increase without corresponding progress/evidence.
    """

    def score(
        self,
        *,
        progress_score: float,
        evidence_score: float,
        retries: int,
        resource_calls: int,
        cost_fraction: float,
        latency_fraction: float,
    ) -> float:
        progress = max(0.0, min(1.0, progress_score))
        evidence = max(0.0, min(1.0, evidence_score))
        retry_pressure = min(1.0, max(0, retries) / 3.0)
        call_pressure = min(1.0, max(0, resource_calls - 1) / 6.0)
        spend_pressure = max(
            max(0.0, min(1.0, cost_fraction)),
            max(0.0, min(1.0, latency_fraction)),
        )

        low_yield = 1.0 - ((progress + evidence) / 2.0)
        drift = (
            low_yield * 0.45
            + retry_pressure * 0.25
            + call_pressure * 0.10
            + spend_pressure * 0.20
        )
        return max(0.0, min(1.0, drift))
