from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from maestro.academy.models import ScenarioResult
from maestro.autonomous.shadow import ShadowObservation


@dataclass(slots=True)
class OnlineFeedbackBatch:
    scenario_results: list[ScenarioResult] = field(default_factory=list)
    shadow_observations: list[ShadowObservation] = field(default_factory=list)


class OnlineAcademyFeedback:
    """
    Collects production-shaped feedback without directly modifying active policy.
    """

    def __init__(self):
        self._batch = OnlineFeedbackBatch()

    def record_scenario_result(self, result: ScenarioResult) -> None:
        self._batch.scenario_results.append(result)

    def record_shadow(self, observation: ShadowObservation) -> None:
        self._batch.shadow_observations.append(observation)

    def snapshot(self) -> OnlineFeedbackBatch:
        return OnlineFeedbackBatch(
            scenario_results=list(self._batch.scenario_results),
            shadow_observations=list(self._batch.shadow_observations),
        )

    def clear(self) -> None:
        self._batch = OnlineFeedbackBatch()
