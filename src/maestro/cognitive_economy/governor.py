from __future__ import annotations


class EconomyViolation(RuntimeError):
    pass


class CognitiveEconomyGovernor:
    """
    Hard runtime enforcement of spend envelopes.
    """

    def __init__(self, plan):
        self.plan = plan

    def assert_within_budget(
        self,
        *,
        stages_used: int,
        resource_calls: int,
        total_tokens: int,
        elapsed_ms: float,
        cost_score: float,
        parallel_candidates: int = 1,
    ) -> None:
        p = self.plan
        if stages_used > p.max_stages:
            raise EconomyViolation("max_stages exceeded")
        if resource_calls > p.max_resource_calls:
            raise EconomyViolation("max_resource_calls exceeded")
        if total_tokens > p.max_total_tokens:
            raise EconomyViolation("max_total_tokens exceeded")
        if elapsed_ms > p.max_latency_ms:
            raise EconomyViolation("max_latency_ms exceeded")
        if cost_score > p.max_cost_score:
            raise EconomyViolation("max_cost_score exceeded")
        if parallel_candidates > p.max_parallel_candidates:
            raise EconomyViolation("max_parallel_candidates exceeded")

    def can_add_call(
        self,
        *,
        current_resource_calls: int,
        current_total_tokens: int,
        estimated_next_tokens: int,
    ) -> bool:
        return (
            current_resource_calls + 1 <= self.plan.max_resource_calls
            and current_total_tokens + estimated_next_tokens <= self.plan.max_total_tokens
        )
