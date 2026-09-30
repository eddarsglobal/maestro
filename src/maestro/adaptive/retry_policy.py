from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict

from .models import AdaptivePolicy, PolicyKind


@dataclass(slots=True)
class RetryStrategyObservation:
    failure_family: str
    strategy: str
    success: bool
    retries_to_resolution: int
    cost_units: float


@dataclass(slots=True)
class RetryStrategyScore:
    strategy: str
    score: float
    success_rate: float
    observations: int


class RetryStrategyLearner:
    def __init__(self):
        self.observations: list[RetryStrategyObservation] = []

    def observe(self, observation: RetryStrategyObservation) -> None:
        self.observations.append(observation)

    def rank(
        self,
        *,
        failure_family: str,
        excluded_strategies: set[str] | None = None,
    ) -> list[RetryStrategyScore]:
        excluded = excluded_strategies or set()
        grouped: dict[str, list[RetryStrategyObservation]] = defaultdict(list)

        for obs in self.observations:
            if obs.failure_family == failure_family and obs.strategy not in excluded:
                grouped[obs.strategy].append(obs)

        out = []
        for strategy, obs in grouped.items():
            success = sum(int(x.success) for x in obs) / len(obs)
            retries = sum(x.retries_to_resolution for x in obs) / len(obs)
            cost = sum(x.cost_units for x in obs) / len(obs)
            score = success - min(0.20, retries * 0.03) - min(0.15, cost / 100.0)
            out.append(RetryStrategyScore(strategy, max(0.0, score), success, len(obs)))

        return sorted(out, key=lambda x: (-x.score, -x.observations, x.strategy))

    def propose_policy(
        self,
        *,
        version: int,
        best_by_failure: dict[str, list[str]],
        parent_policy_id: str | None = None,
    ) -> AdaptivePolicy:
        return AdaptivePolicy(
            kind=PolicyKind.RETRY_STRATEGY,
            version=version,
            parent_policy_id=parent_policy_id,
            description="Retry strategy preferences learned from verified remediation outcomes.",
            parameters={"best_by_failure": best_by_failure},
        )
