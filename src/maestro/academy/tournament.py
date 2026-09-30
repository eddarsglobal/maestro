from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import AcademyScenario, PolicyVariant
from .replay import Runner
from .scoring import score_result


@dataclass(slots=True)
class TournamentStanding:
    policy_id: str
    mean_score: float
    success_rate: float
    mean_cost: float
    mean_latency_ms: float
    total_retries: int
    rank: int = 0


@dataclass(slots=True)
class TournamentReport:
    standings: list[TournamentStanding]
    recommended_policy_id: str | None
    note: str = "Recommendation only. Promotion remains governed by APTE."


class ShadowPolicyTournament:
    def run(
        self,
        *,
        policies: Iterable[PolicyVariant],
        scenarios: Iterable[AcademyScenario],
        runner: Runner,
    ) -> TournamentReport:
        scenarios = list(scenarios)
        standings = []

        for policy in policies:
            scores = []
            successes = 0
            costs = []
            latencies = []
            retries = 0

            for scenario in scenarios:
                result = runner(policy, scenario)
                scores.append(score_result(scenario, result).total)
                successes += int(result.success)
                costs.append(result.cost_units)
                latencies.append(result.latency_ms)
                retries += result.retries

            n = len(scenarios)
            standings.append(
                TournamentStanding(
                    policy_id=policy.policy_id,
                    mean_score=sum(scores) / n if n else 0.0,
                    success_rate=successes / n if n else 0.0,
                    mean_cost=sum(costs) / n if n else 0.0,
                    mean_latency_ms=sum(latencies) / n if n else 0.0,
                    total_retries=retries,
                )
            )

        standings.sort(
            key=lambda x: (
                -x.mean_score,
                -x.success_rate,
                x.total_retries,
                x.mean_cost,
                x.mean_latency_ms,
                x.policy_id,
            )
        )
        for idx, standing in enumerate(standings, 1):
            standing.rank = idx

        return TournamentReport(
            standings=standings,
            recommended_policy_id=standings[0].policy_id if standings else None,
        )
