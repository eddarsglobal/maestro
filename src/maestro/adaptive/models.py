from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class PolicyKind(StrEnum):
    ROUTING = "ROUTING"
    CONTEXT = "CONTEXT"
    TOOL_SELECTION = "TOOL_SELECTION"
    MODEL_SELECTION = "MODEL_SELECTION"
    RETRY_STRATEGY = "RETRY_STRATEGY"
    SKILL = "SKILL"
    ARCHETYPE = "ARCHETYPE"


class PolicyStatus(StrEnum):
    CANDIDATE = "CANDIDATE"
    SHADOW = "SHADOW"
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"
    REJECTED = "REJECTED"


@dataclass(slots=True)
class AdaptivePolicy:
    kind: PolicyKind
    version: int
    description: str
    parameters: dict[str, Any]
    parent_policy_id: str | None = None
    status: PolicyStatus = PolicyStatus.CANDIDATE
    created_at: str = field(default_factory=utc_now)
    policy_id: str = field(default_factory=lambda: f"POL-{uuid4().hex[:12].upper()}")

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["kind"] = self.kind.value
        d["status"] = self.status.value
        return d


@dataclass(frozen=True, slots=True)
class PromotionEvidence:
    replay_score: float
    baseline_score: float
    regression_count: int
    shadow_success_rate: float
    evaluation_samples: int
    academy_recommended: bool
    learning_candidate_id: str | None = None

    @property
    def delta(self) -> float:
        return self.replay_score - self.baseline_score


@dataclass(frozen=True, slots=True)
class ActivationRecord:
    policy_id: str
    kind: PolicyKind
    previous_policy_id: str | None
    action: str
    reason: str
    created_at: str = field(default_factory=utc_now)
