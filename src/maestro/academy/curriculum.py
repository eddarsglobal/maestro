from __future__ import annotations

from typing import Iterable

from .models import CurriculumItem, Weakness


class CurriculumEngine:
    """
    Converts measured weaknesses into a deterministic training curriculum.

    It never changes production policy; it only creates training priorities.
    """

    def build(
        self,
        weaknesses: Iterable[Weakness],
        *,
        max_items: int = 12,
    ) -> list[CurriculumItem]:
        ordered = sorted(weaknesses, key=lambda w: (w.score, -w.sample_count, w.key))
        curriculum: list[CurriculumItem] = []

        for weakness in ordered[:max_items]:
            if weakness.severity == "CRITICAL":
                difficulty = 2
                repetitions = 12
            elif weakness.severity == "HIGH":
                difficulty = 3
                repetitions = 8
            else:
                difficulty = 4
                repetitions = 4

            task_family = weakness.key if weakness.dimension == "task_family" else "ROUTING"
            curriculum.append(
                CurriculumItem(
                    focus=f"{weakness.dimension}:{weakness.key}",
                    task_family=task_family,
                    difficulty=difficulty,
                    repetitions=repetitions,
                    reason=f"Measured score {weakness.score:.3f} over {weakness.sample_count} samples.",
                    tags={"academy", "targeted", weakness.severity.lower()},
                )
            )

        return curriculum
