from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable
from uuid import uuid4

from maestro.learning.models import ExperienceRecord, OutcomeStatus
from .models import AdaptivePolicy, PolicyKind


@dataclass(slots=True)
class SkillCandidate:
    name: str
    task_family: str
    councils: list[str]
    strategies: list[str]
    tool_names: list[str]
    support_experience_ids: list[str]
    acceptance_requirements: list[str] = field(default_factory=list)
    skill_id: str = field(default_factory=lambda: f"SKL-{uuid4().hex[:12].upper()}")

    @property
    def support_count(self) -> int:
        return len(self.support_experience_ids)


class SkillFactory:
    """
    Builds reusable skill candidates from repeated verified successes.
    It never installs a skill directly.
    """

    def discover(
        self,
        experiences: Iterable[ExperienceRecord],
        *,
        min_support: int = 3,
    ) -> list[SkillCandidate]:
        groups: dict[tuple, list[ExperienceRecord]] = {}

        for exp in experiences:
            if not exp.verified or exp.outcome is not OutcomeStatus.SUCCESS:
                continue
            key = (
                exp.task_family,
                tuple(sorted(exp.councils)),
                tuple(exp.strategies),
                tuple(sorted(exp.tool_names)),
            )
            groups.setdefault(key, []).append(exp)

        candidates = []
        for key, items in groups.items():
            if len(items) < min_support:
                continue
            family, councils, strategies, tools = key
            candidates.append(
                SkillCandidate(
                    name=f"{family}_SKILL",
                    task_family=family,
                    councils=list(councils),
                    strategies=list(strategies),
                    tool_names=list(tools),
                    support_experience_ids=[x.experience_id for x in items],
                )
            )
        return sorted(candidates, key=lambda x: (x.task_family, x.name))

    def to_policy(
        self,
        skill: SkillCandidate,
        *,
        version: int,
        parent_policy_id: str | None = None,
    ) -> AdaptivePolicy:
        return AdaptivePolicy(
            kind=PolicyKind.SKILL,
            version=version,
            parent_policy_id=parent_policy_id,
            description=f"Reusable skill candidate: {skill.name}",
            parameters={
                "skill_id": skill.skill_id,
                "task_family": skill.task_family,
                "councils": skill.councils,
                "strategies": skill.strategies,
                "tool_names": skill.tool_names,
                "support_experience_ids": skill.support_experience_ids,
            },
        )
