from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ContextEnvelope:
    context_ref: str | None
    upstream_artifacts: list[dict[str, Any]] = field(default_factory=list)


class CognitiveContextBus:
    """
    MAESTRO-mediated stage communication.

    Resources never communicate directly with one another.
    """

    def compile_for_stage(self, plan, stage, artifacts) -> ContextEnvelope:
        upstream = []
        deps = set(stage.depends_on)
        for artifact in artifacts:
            if artifact.stage_id in deps:
                upstream.append({
                    "stage_id": artifact.stage_id,
                    "role": artifact.role.value,
                    "resource_id": artifact.resource_id,
                    "output": artifact.output,
                    "evidence_refs": list(artifact.evidence_refs),
                })
        return ContextEnvelope(plan.context_ref, upstream)
