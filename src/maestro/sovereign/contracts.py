from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol


class IntelligenceCapability(StrEnum):
    DIRECT = "DIRECT"
    GENERAL_REASONING = "GENERAL_REASONING"
    CODE = "CODE"
    HEAVY_CODE = "HEAVY_CODE"
    HEAVY_REASONING = "HEAVY_REASONING"
    VISION = "VISION"
    AUDIO = "AUDIO"
    EMBEDDING = "EMBEDDING"
    TOOL_USE = "TOOL_USE"


class ResourceStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(slots=True)
class ResourceDescriptor:
    resource_id: str
    provider_id: str
    model_id: str
    capabilities: frozenset[IntelligenceCapability]
    status: ResourceStatus = ResourceStatus.AVAILABLE
    local: bool = False
    cost_score: float = 0.0
    latency_score: float = 0.0
    quality_score: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class InferenceExecutionProfile:
    # Provider-neutral execution controls owned by MAESTRO.
    temperature: float | None = None
    seed: int | None = None
    thinking: bool | str | None = None
    profile_ref: str | None = None

    @property
    def deterministic(self) -> bool:
        return (
            self.temperature is not None
            and float(self.temperature) == 0.0
            and self.seed is not None
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "temperature": (
                None
                if self.temperature is None
                else float(self.temperature)
            ),
            "seed": None if self.seed is None else int(self.seed),
            "thinking": self.thinking,
            "profile_ref": self.profile_ref,
            "deterministic": self.deterministic,
        }


@dataclass(slots=True)
class IntelligenceRequest:
    task_id: str
    capability: IntelligenceCapability
    instruction: str
    context_ref: str | None = None
    max_tokens: int | None = None
    requires_tools: bool = False
    preferred_local: bool = True
    forbidden_resources: frozenset[str] = frozenset()
    metadata: dict[str, Any] = field(default_factory=dict)
    execution_profile: InferenceExecutionProfile | None = None


@dataclass(slots=True)
class IntelligenceResponse:
    resource_id: str
    provider_id: str
    model_id: str
    output: str
    success: bool
    metadata: dict[str, Any] = field(default_factory=dict)


class IntelligenceResourceAdapter(Protocol):
    resource_id: str
    provider_id: str
    model_id: str

    def execute(self, request: IntelligenceRequest) -> IntelligenceResponse:
        ...
