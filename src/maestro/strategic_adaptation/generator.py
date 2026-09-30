from __future__ import annotations

from .models import StrategyCandidate


class StrategyCandidateGenerator:
    """
    Deterministic alternative generation from known strategy archetypes.
    Model-assisted proposals may be added later but remain candidates only.
    """

    def generate(
        self,
        *,
        task_id: str,
        objective: str,
        family: str,
        current_method: str,
        available_capabilities: set[str] | None = None,
    ) -> list[StrategyCandidate]:
        caps = available_capabilities or set()
        candidates = [
            StrategyCandidate(
                strategy_id=f"{task_id}:simplify",
                family=family,
                objective=objective,
                method="SIMPLIFY_SCOPE_AND_RETRY",
                expected_quality=0.70,
                expected_evidence_gain=0.65,
                expected_cost=0.25,
                expected_latency=0.25,
                reversible=True,
            ),
            StrategyCandidate(
                strategy_id=f"{task_id}:evidence_first",
                family=family,
                objective=objective,
                method="EVIDENCE_FIRST_THEN_EXECUTE",
                expected_quality=0.82,
                expected_evidence_gain=0.92,
                expected_cost=0.45,
                expected_latency=0.50,
                reversible=True,
            ),
            StrategyCandidate(
                strategy_id=f"{task_id}:alternate_resource",
                family=family,
                objective=objective,
                method="CHANGE_INTELLIGENCE_RESOURCE",
                expected_quality=0.80,
                expected_evidence_gain=0.70,
                expected_cost=0.50,
                expected_latency=0.45,
                reversible=True,
            ),
        ]

        if "MULTI_RESOURCE" in caps:
            candidates.append(
                StrategyCandidate(
                    strategy_id=f"{task_id}:independent_cross_check",
                    family=family,
                    objective=objective,
                    method="INDEPENDENT_CROSS_CHECK",
                    required_capabilities=("MULTI_RESOURCE",),
                    expected_quality=0.90,
                    expected_evidence_gain=0.90,
                    expected_cost=0.70,
                    expected_latency=0.75,
                    reversible=True,
                )
            )

        # Never return a strategy identical to the current method.
        return [c for c in candidates if c.method != current_method]
