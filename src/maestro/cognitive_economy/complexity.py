from __future__ import annotations

from .models import MissionComplexity, MissionEconomyProfile


def _b(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


class ComplexityEstimator:
    """
    Deterministic bootstrap estimator.
    Learning may later improve thresholds, never constitutional authority.
    """

    def estimate(
        self,
        *,
        task_id: str,
        risk_score: float,
        uncertainty_score: float,
        reversibility_score: float,
        evidence_demand: float,
        time_sensitivity: float = 0.5,
        metadata: dict | None = None,
    ) -> MissionEconomyProfile:
        risk = _b(risk_score)
        uncertainty = _b(uncertainty_score)
        reversibility = _b(reversibility_score)
        evidence = _b(evidence_demand)
        time = _b(time_sensitivity)

        # Higher reversibility reduces complexity pressure.
        score = (
            risk * 0.30
            + uncertainty * 0.25
            + evidence * 0.25
            + (1.0 - reversibility) * 0.15
            + time * 0.05
        )

        if score < 0.18:
            complexity = MissionComplexity.TRIVIAL
        elif score < 0.38:
            complexity = MissionComplexity.LOW
        elif score < 0.62:
            complexity = MissionComplexity.MEDIUM
        elif score < 0.82:
            complexity = MissionComplexity.HIGH
        else:
            complexity = MissionComplexity.CRITICAL

        return MissionEconomyProfile(
            task_id=task_id,
            complexity=complexity,
            risk_score=risk,
            uncertainty_score=uncertainty,
            reversibility_score=reversibility,
            evidence_demand=evidence,
            time_sensitivity=time,
            metadata={**(metadata or {}), "complexity_score": score},
        )
