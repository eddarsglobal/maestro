from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ExplorationDecision:
    explore: bool
    reason: str


class ExplorationController:
    """
    Deterministic bounded exploration.

    Avoids vendor/model lock-in by periodically allowing under-tested eligible
    resources to receive evaluation traffic.
    """

    def __init__(self, min_samples: int = 3):
        self.min_samples = min_samples

    def should_explore(self, sample_counts: dict[str, int]) -> ExplorationDecision:
        if not sample_counts:
            return ExplorationDecision(False, "no resources")
        under_tested = [rid for rid, count in sample_counts.items() if count < self.min_samples]
        if under_tested:
            return ExplorationDecision(True, "eligible resource lacks sufficient observations")
        return ExplorationDecision(False, "all eligible resources sufficiently sampled")

    def choose_under_tested(self, sample_counts: dict[str, int]) -> str:
        if not sample_counts:
            raise LookupError("No resources.")
        return min(sample_counts, key=lambda rid: (sample_counts[rid], rid))
