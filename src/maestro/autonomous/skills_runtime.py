from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from maestro.adaptive.skills import SkillCandidate


@dataclass(slots=True)
class SkillExecutionPlan:
    skill_id: str
    task_family: str
    councils: list[str]
    strategies: list[str]
    tool_names: list[str]
    inputs: dict[str, Any] = field(default_factory=dict)


class SkillRuntime:
    """
    Compiles approved skill definitions into execution plans.
    It does not create new Council authority.
    """

    def compile(self, skill: SkillCandidate, *, inputs: dict[str, Any] | None = None) -> SkillExecutionPlan:
        return SkillExecutionPlan(
            skill_id=skill.skill_id,
            task_family=skill.task_family,
            councils=list(skill.councils),
            strategies=list(skill.strategies),
            tool_names=list(skill.tool_names),
            inputs=dict(inputs or {}),
        )
