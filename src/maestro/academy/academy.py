from __future__ import annotations

from dataclasses import dataclass

from .benchmarks import CouncilBenchmark, BenchmarkReport
from .curriculum import CurriculumEngine
from .models import AcademyScenario, CurriculumItem, PolicyVariant, ScenarioResult
from .replay import HistoricalReplay, ReplayReport, Runner
from .simulator import MissionSimulator
from .tournament import ShadowPolicyTournament, TournamentReport


@dataclass(slots=True)
class AcademyAssessment:
    benchmark: BenchmarkReport
    curriculum: list[CurriculumItem]


class MaestroAcademy:
    def __init__(self):
        self.simulator = MissionSimulator()
        self.benchmark = CouncilBenchmark()
        self.curriculum = CurriculumEngine()
        self.replay = HistoricalReplay()
        self.tournament = ShadowPolicyTournament()

    def assess(
        self,
        scenarios: list[AcademyScenario],
        results: list[ScenarioResult],
    ) -> AcademyAssessment:
        report = self.benchmark.evaluate(scenarios, results)
        return AcademyAssessment(
            benchmark=report,
            curriculum=self.curriculum.build(report.weaknesses),
        )

    def compare_policy(
        self,
        baseline: PolicyVariant,
        candidate: PolicyVariant,
        scenarios: list[AcademyScenario],
        runner: Runner,
    ) -> ReplayReport:
        return self.replay.compare(
            baseline=baseline,
            candidate=candidate,
            scenarios=scenarios,
            runner=runner,
        )

    def tournament_policies(
        self,
        policies: list[PolicyVariant],
        scenarios: list[AcademyScenario],
        runner: Runner,
    ) -> TournamentReport:
        return self.tournament.run(
            policies=policies,
            scenarios=scenarios,
            runner=runner,
        )
