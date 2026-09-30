from __future__ import annotations

from dataclasses import dataclass

from maestro.adaptive.skills import SkillCandidate
from maestro.enums import CouncilId
from maestro.orchestration.dag import DagEngine, DagNode


class SkillDagCompiler:
    """
    Turns an approved skill into a governed DAG skeleton.

    The skill determines reusable sequencing, not Council authority.
    """

    def compile(self, skill: SkillCandidate) -> DagEngine:
        dag = DagEngine()
        previous_id = None

        for index, council_name in enumerate(skill.councils, start=1):
            council = CouncilId(council_name)
            node_id = f"{skill.skill_id.lower()}-{index:02d}-{council.value.lower()}"
            depends = {previous_id} if previous_id else set()
            action = skill.strategies[min(index - 1, len(skill.strategies) - 1)] if skill.strategies else "EXECUTE_SKILL_STEP"
            dag.add_node(
                DagNode(
                    node_id=node_id,
                    council=council,
                    action=action,
                    depends_on=depends,
                )
            )
            previous_id = node_id

        return dag
