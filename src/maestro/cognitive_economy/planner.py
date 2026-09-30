from __future__ import annotations

from .models import CognitiveSpendPlan
from .policy import CognitiveEconomyPolicy


class CognitiveSpendPlanner:
    def __init__(self, policy: CognitiveEconomyPolicy | None = None):
        self.policy = policy or CognitiveEconomyPolicy()

    def plan(self, profile) -> CognitiveSpendPlan:
        tier = self.policy.tier_for_complexity(profile.complexity)
        limits = self.policy.limits(tier)

        # High risk/evidence may force critic/verifier inside same tier envelope.
        require_critic = limits.require_critic or profile.risk_score >= 0.75
        require_verifier = limits.require_verifier or profile.evidence_demand >= 0.65

        return CognitiveSpendPlan(
            task_id=profile.task_id,
            tier=tier,
            max_stages=limits.max_stages,
            max_resource_calls=limits.max_resource_calls,
            max_parallel_candidates=limits.max_parallel_candidates,
            max_tokens_per_call=limits.max_tokens_per_call,
            max_total_tokens=limits.max_total_tokens,
            max_latency_ms=limits.max_latency_ms,
            max_cost_score=limits.max_cost_score,
            require_critic=require_critic,
            require_verifier=require_verifier,
            allow_multi_resource=limits.allow_multi_resource,
            stop_on_sufficient_evidence=True,
            rationale={
                "complexity": profile.complexity.value,
                "risk": profile.risk_score,
                "uncertainty": profile.uncertainty_score,
                "evidence_demand": profile.evidence_demand,
                "reversibility": profile.reversibility_score,
            },
        )
