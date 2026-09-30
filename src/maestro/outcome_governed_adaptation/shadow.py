from __future__ import annotations

from maestro.academy import MaestroAcademy
from maestro.academy.learning_grade import LearningGradeAcademyRunner
from maestro.academy.models import AcademyScenario, PolicyVariant
from maestro.academy.replay import Runner


class OutcomeShadowEvaluator:
    "Thin bridge to the existing Academy; recommendation remains non-authoritative."

    def __init__(self, academy: MaestroAcademy | None = None):
        self.academy = academy or MaestroAcademy()

    def learning_grade_runner(
        self,
        registry,
        evaluation_profile,
        resource_resolver,
    ) -> LearningGradeAcademyRunner:
        return LearningGradeAcademyRunner(
            registry,
            evaluation_profile,
            resource_resolver,
        )

    def compare(
        self,
        baseline: PolicyVariant,
        candidate: PolicyVariant,
        scenarios: list[AcademyScenario],
        runner: Runner,
    ):
        replay = self.academy.compare_policy(baseline, candidate, scenarios, runner)
        tournament = self.academy.tournament_policies([baseline, candidate], scenarios, runner)
        return replay, tournament
