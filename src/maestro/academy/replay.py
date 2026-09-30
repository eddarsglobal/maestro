from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from .models import AcademyScenario, PolicyVariant, ScenarioResult
from .scoring import score_result


Runner = Callable[[PolicyVariant, AcademyScenario], ScenarioResult]


@dataclass(slots=True)
class ReplayReport:
    baseline_policy_id: str
    candidate_policy_id: str
    scenarios: int
    baseline_score: float
    candidate_score: float
    regressions: int
    improvements: int
    unchanged: int
    delta: float
    regression_scenarios: list[str]


class HistoricalReplay:
    def compare(
        self,
        *,
        baseline: PolicyVariant,
        candidate: PolicyVariant,
        scenarios: Iterable[AcademyScenario],
        runner: Runner,
        regression_tolerance: float = 0.02,
    ) -> ReplayReport:
        baseline_scores = []
        candidate_scores = []
        regressions = []
        improvements = 0
        unchanged = 0

        for scenario in scenarios:
            b = score_result(scenario, runner(baseline, scenario)).total
            c = score_result(scenario, runner(candidate, scenario)).total
            baseline_scores.append(b)
            candidate_scores.append(c)

            if c + regression_tolerance < b:
                regressions.append(scenario.scenario_id)
            elif c > b + regression_tolerance:
                improvements += 1
            else:
                unchanged += 1

        base = sum(baseline_scores) / len(baseline_scores) if baseline_scores else 0.0
        cand = sum(candidate_scores) / len(candidate_scores) if candidate_scores else 0.0

        return ReplayReport(
            baseline_policy_id=baseline.policy_id,
            candidate_policy_id=candidate.policy_id,
            scenarios=len(baseline_scores),
            baseline_score=base,
            candidate_score=cand,
            regressions=len(regressions),
            improvements=improvements,
            unchanged=unchanged,
            delta=cand - base,
            regression_scenarios=regressions,
        )
