from __future__ import annotations


class ConfidenceEstimator:
    """
    Estimates operational confidence from observable signals only.
    It does not inspect or persist private chain-of-thought.
    """

    def estimate(
        self,
        *,
        evidence_sufficiency: float,
        contradiction_score: float,
        verified_fraction: float,
        assumption_fraction: float,
        retry_penalty: float,
    ) -> float:
        evidence = max(0.0, min(1.0, evidence_sufficiency))
        contradiction = max(0.0, min(1.0, contradiction_score))
        verified = max(0.0, min(1.0, verified_fraction))
        assumptions = max(0.0, min(1.0, assumption_fraction))
        retry = max(0.0, min(1.0, retry_penalty))

        score = (
            evidence * 0.35
            + verified * 0.30
            + (1.0 - contradiction) * 0.20
            + (1.0 - assumptions) * 0.10
            + (1.0 - retry) * 0.05
        )
        return max(0.0, min(1.0, score))
