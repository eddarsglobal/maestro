from __future__ import annotations

from dataclasses import dataclass


class BudgetViolation(RuntimeError):
    pass


@dataclass(slots=True)
class CognitiveBudget:
    max_stages: int = 6
    max_resource_calls: int = 8
    max_parallel_candidates_per_stage: int = 2
    max_total_output_chars: int = 100_000


class CognitiveBudgetGovernor:
    """
    Preserves MAESTRO lightness by bounding cognitive expansion.
    """

    def __init__(self, budget: CognitiveBudget | None = None):
        self.budget = budget or CognitiveBudget()

    def validate_plan(self, plan) -> None:
        if len(plan.stages) > self.budget.max_stages:
            raise BudgetViolation("Cognitive plan exceeds max_stages.")
        calls = 0
        for stage in plan.stages:
            if stage.candidate_count < 1:
                raise BudgetViolation("candidate_count must be >= 1")
            if stage.candidate_count > self.budget.max_parallel_candidates_per_stage:
                raise BudgetViolation("Stage candidate_count exceeds budget.")
            calls += stage.candidate_count
        if calls > self.budget.max_resource_calls:
            raise BudgetViolation("Cognitive plan exceeds max_resource_calls.")

    def validate_output_mass(self, artifacts) -> None:
        total = sum(len(a.output) for a in artifacts)
        if total > self.budget.max_total_output_chars:
            raise BudgetViolation("Cognitive output mass exceeds budget.")
