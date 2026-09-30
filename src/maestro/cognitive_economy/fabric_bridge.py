from __future__ import annotations

from maestro.cognitive_fabric import CognitiveBudget


class CognitiveEconomyFabricBridge:
    """
    Converts a mission spend plan into Cognitive Fabric hard limits.
    """

    def to_cognitive_budget(self, spend_plan) -> CognitiveBudget:
        # Output-char budget remains separate from token budget.
        return CognitiveBudget(
            max_stages=spend_plan.max_stages,
            max_resource_calls=spend_plan.max_resource_calls,
            max_parallel_candidates_per_stage=spend_plan.max_parallel_candidates,
            max_total_output_chars=max(10_000, spend_plan.max_total_tokens * 4),
        )
