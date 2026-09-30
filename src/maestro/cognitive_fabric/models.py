from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import StrEnum
from typing import Any

from maestro.sovereign.contracts import IntelligenceCapability


class CognitiveRole(StrEnum):
    SCOUT = "SCOUT"
    PRODUCER = "PRODUCER"
    CRITIC = "CRITIC"
    VERIFIER = "VERIFIER"
    SYNTHESIZER = "SYNTHESIZER"


class StageStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass(slots=True)
class CognitiveStage:
    stage_id: str
    role: CognitiveRole
    capability: IntelligenceCapability
    task_family: str
    council_id: str | None
    instruction: str
    depends_on: tuple[str, ...] = ()
    candidate_count: int = 1
    require_provider_diversity: bool = False
    status: StageStatus = StageStatus.PENDING


@dataclass(slots=True)
class CognitivePlan:
    task_id: str
    stages: list[CognitiveStage]
    context_ref: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def stage_map(self) -> dict[str, CognitiveStage]:
        return {s.stage_id: s for s in self.stages}


@dataclass(slots=True)
class StageArtifact:
    stage_id: str
    role: CognitiveRole
    resource_id: str
    provider_id: str
    model_id: str
    output: str
    success: bool
    quality: float | None = None
    evidence_refs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["role"] = self.role.value
        return d


@dataclass(slots=True)
class CognitiveRunReport:
    task_id: str
    completed: bool
    artifacts: list[StageArtifact]
    failed_stage_ids: list[str]
    used_resources: list[str]
    context_ref: str | None
    metadata: dict[str, Any] = field(default_factory=dict)
