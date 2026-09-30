from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable

from .models import AcademyScenario, ScenarioResult, Weakness
from .scoring import score_result


@dataclass(slots=True)
class BenchmarkReport:
    overall_score: float
    scenario_count: int
    by_family: dict[str, float]
    council_required_recall: dict[str, float]
    weaknesses: list[Weakness]


class CouncilBenchmark:
    def evaluate(
        self,
        scenarios: Iterable[AcademyScenario],
        results: Iterable[ScenarioResult],
    ) -> BenchmarkReport:
        scenario_map = {x.scenario_id: x for x in scenarios}
        result_map = {x.scenario_id: x for x in results}

        scores = []
        by_family_values: dict[str, list[float]] = defaultdict(list)
        required_counts: dict[str, int] = defaultdict(int)
        selected_when_required: dict[str, int] = defaultdict(int)
        weaknesses: list[Weakness] = []

        for scenario_id, scenario in scenario_map.items():
            if scenario_id not in result_map:
                weaknesses.append(
                    Weakness(
                        dimension="coverage",
                        key=scenario.task_family,
                        score=0.0,
                        sample_count=1,
                        severity="CRITICAL",
                        evidence=[f"Missing result for {scenario_id}"],
                    )
                )
                continue

            result = result_map[scenario_id]
            s = score_result(scenario, result)
            scores.append(s.total)
            by_family_values[scenario.task_family].append(s.total)

            for council in scenario.required_councils:
                required_counts[council] += 1
                if council in result.selected_councils:
                    selected_when_required[council] += 1

        by_family = {
            family: sum(values) / len(values)
            for family, values in by_family_values.items()
        }

        council_recall = {
            council: selected_when_required[council] / count
            for council, count in required_counts.items()
            if count
        }

        for family, score in by_family.items():
            if score < 0.75:
                weaknesses.append(
                    Weakness(
                        dimension="task_family",
                        key=family,
                        score=score,
                        sample_count=len(by_family_values[family]),
                        severity="CRITICAL" if score < 0.50 else "HIGH",
                        evidence=[f"Average score={score:.3f}"],
                    )
                )

        for council, recall in council_recall.items():
            if recall < 0.90:
                weaknesses.append(
                    Weakness(
                        dimension="council_recall",
                        key=council,
                        score=recall,
                        sample_count=required_counts[council],
                        severity="HIGH" if recall >= 0.50 else "CRITICAL",
                        evidence=[f"Required recall={recall:.3f}"],
                    )
                )

        weaknesses.sort(key=lambda x: (x.score, x.dimension, x.key))

        return BenchmarkReport(
            overall_score=sum(scores) / len(scores) if scores else 0.0,
            scenario_count=len(scenario_map),
            by_family=by_family,
            council_required_recall=council_recall,
            weaknesses=weaknesses,
        )
