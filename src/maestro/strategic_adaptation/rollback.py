from __future__ import annotations


class StrategyRollbackManager:
    """
    Provides reversible return to the previous strategy when an adaptation underperforms.
    """

    def should_rollback(
        self,
        *,
        baseline_quality: float,
        new_quality: float,
        baseline_evidence: float,
        new_evidence: float,
        baseline_cost: float,
        new_cost: float,
    ) -> bool:
        quality_regressed = new_quality + 0.05 < baseline_quality
        evidence_regressed = new_evidence + 0.05 < baseline_evidence
        cost_exploded = new_cost > max(0.10, baseline_cost * 1.75)
        return quality_regressed or evidence_regressed or cost_exploded
