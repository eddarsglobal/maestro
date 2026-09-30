from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Iterable

from maestro.councils.registry import get_council
from maestro.enums import CouncilId
from maestro.models import Evidence, Mission
from maestro.orchestration.dag import DagNode, DagEngine


@dataclass(slots=True)
class CouncilContext:
    task_id: str
    council: CouncilId
    objective: str
    scope: str
    requested_output: str
    assigned_action: str
    acceptance_criteria: list[str]
    dependency_outputs: dict[str, Any]
    evidence: list[dict[str, Any]]
    authority: str
    cannot_own: list[str]
    constitutional_rules: list[str]
    metadata: dict[str, Any]
    truncated: bool = False

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["council"] = self.council.value
        return d


class ContextCompiler:
    """
    Least-context compiler.

    It deliberately compiles structured, auditable context instead of
    passing entire prior conversations or hidden reasoning to Councils.
    """

    CORE_RULES = [
        "All governed routing/state changes go through EX.",
        "AY alone may issue SYSTEM verdicts.",
        "Specialist Councils issue DOMAIN verdicts.",
        "Do not persist private chain-of-thought; persist evidence and concise rationale only.",
    ]

    def __init__(self, max_chars: int = 24000):
        if max_chars < 1000:
            raise ValueError("max_chars is unreasonably small.")
        self.max_chars = max_chars

    @staticmethod
    def _criteria_for_node(mission: Mission, node: DagNode) -> list[str]:
        if not node.criteria_ids:
            return list(mission.acceptance_criteria)

        selected: list[str] = []
        for criterion in mission.acceptance_criteria:
            if any(
                criterion.startswith(cid) or criterion == cid
                for cid in node.criteria_ids
            ):
                selected.append(criterion)
        return selected

    @staticmethod
    def _evidence_for_council(
        evidence: Iterable[Evidence],
        council: CouncilId,
        dependency_councils: set[CouncilId],
    ) -> list[dict[str, Any]]:
        allowed = {council, *dependency_councils, CouncilId.AY, CouncilId.EX}
        return [item.to_dict() for item in evidence if item.council in allowed]

    def compile(
        self,
        mission: Mission,
        node: DagNode,
        dag: DagEngine,
        evidence: Iterable[Evidence],
        extra_metadata: dict[str, Any] | None = None,
    ) -> CouncilContext:
        spec = get_council(node.council)

        dependency_outputs = {
            dep_id: dag.nodes[dep_id].output
            for dep_id in sorted(node.depends_on)
            if dag.nodes[dep_id].output
        }
        dependency_councils = {dag.nodes[dep_id].council for dep_id in node.depends_on}

        context = CouncilContext(
            task_id=mission.task_id,
            council=node.council,
            objective=mission.objective,
            scope=mission.scope,
            requested_output=mission.requested_output,
            assigned_action=node.action,
            acceptance_criteria=self._criteria_for_node(mission, node),
            dependency_outputs=dependency_outputs,
            evidence=self._evidence_for_council(evidence, node.council, dependency_councils),
            authority=spec.primary_authority,
            cannot_own=list(spec.cannot_own),
            constitutional_rules=list(self.CORE_RULES),
            metadata=dict(extra_metadata or {}),
        )

        # Deterministic least-context truncation: evidence is lowest-priority payload here.
        rendered = str(context.to_dict())
        if len(rendered) > self.max_chars:
            context.truncated = True
            while context.evidence and len(str(context.to_dict())) > self.max_chars:
                context.evidence.pop()
            while context.dependency_outputs and len(str(context.to_dict())) > self.max_chars:
                last = sorted(context.dependency_outputs)[-1]
                context.dependency_outputs.pop(last)

        if len(str(context.to_dict())) > self.max_chars:
            raise ValueError(
                "Context remains over budget after removable evidence/dependencies were pruned."
            )

        return context
