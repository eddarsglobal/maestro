from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import hashlib

from maestro.learning.models import ExperienceRecord


@dataclass(slots=True)
class MissionArchetype:
    archetype_id: str
    signature: str
    task_families: list[str]
    common_councils: list[str]
    common_strategies: list[str]
    support_experience_ids: list[str]
    support_count: int


class ArchetypeDiscovery:
    """
    Lightweight structural discovery without a resident ML dependency.
    """

    def discover(
        self,
        experiences: Iterable[ExperienceRecord],
        *,
        min_support: int = 3,
    ) -> list[MissionArchetype]:
        groups: dict[str, list[ExperienceRecord]] = {}

        for exp in experiences:
            if not exp.verified:
                continue
            structural = "|".join([
                ",".join(sorted(exp.councils)),
                ",".join(sorted(exp.tool_names)),
                ",".join(exp.strategies),
            ])
            sig = hashlib.sha256(structural.encode("utf-8")).hexdigest()[:16]
            groups.setdefault(sig, []).append(exp)

        out = []
        for sig, items in groups.items():
            if len(items) < min_support:
                continue
            families = sorted({x.task_family for x in items})
            councils = sorted(set.intersection(*(set(x.councils) for x in items))) if items else []
            strategies = sorted(set.intersection(*(set(x.strategies) for x in items))) if items else []
            out.append(
                MissionArchetype(
                    archetype_id=f"ARCH-{sig.upper()}",
                    signature=sig,
                    task_families=families,
                    common_councils=councils,
                    common_strategies=strategies,
                    support_experience_ids=[x.experience_id for x in items],
                    support_count=len(items),
                )
            )
        return sorted(out, key=lambda x: (-x.support_count, x.archetype_id))
