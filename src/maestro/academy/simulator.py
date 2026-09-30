from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from .models import AcademyScenario


class MissionSimulator:
    """
    Deterministic scenario factory.

    v0.4 intentionally does not need an LLM to produce useful training
    missions. LLM-generated scenarios can be added later as an adapter.
    """

    def __init__(self):
        self._templates: list[AcademyScenario] = []

    def register(self, scenario: AcademyScenario) -> None:
        self._templates.append(scenario)

    def templates(self) -> list[AcademyScenario]:
        return list(self._templates)

    def generate(
        self,
        *,
        task_family: str | None = None,
        min_difficulty: int = 1,
        max_difficulty: int = 5,
        limit: int | None = None,
    ) -> list[AcademyScenario]:
        result = [
            s for s in self._templates
            if (task_family is None or s.task_family == task_family)
            and min_difficulty <= s.difficulty <= max_difficulty
        ]
        result.sort(key=lambda s: (s.task_family, s.difficulty, s.scenario_id))
        return result[:limit] if limit is not None else result

    def adversarial_variants(
        self,
        base: AcademyScenario,
        *,
        levels: Iterable[int] = (2, 3, 4, 5),
    ) -> list[AcademyScenario]:
        variants = []
        for level in levels:
            variants.append(
                replace(
                    base,
                    scenario_id=f"{base.scenario_id}-ADV-{level}",
                    difficulty=max(base.difficulty, level),
                    risk=max(base.risk, level),
                    tags=set(base.tags) | {"adversarial", f"level-{level}"},
                    metadata={**base.metadata, "variant_of": base.scenario_id},
                )
            )
        return variants
