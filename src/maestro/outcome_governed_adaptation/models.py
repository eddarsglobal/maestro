from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AdaptationDomain(StrEnum):
    ROUTING = "ROUTING"
    CONTEXT = "CONTEXT"
    TOOL_SELECTION = "TOOL_SELECTION"
    MODEL_SELECTION = "MODEL_SELECTION"
    RETRY_STRATEGY = "RETRY_STRATEGY"
    SKILL = "SKILL"
    STRATEGY = "STRATEGY"


class AdaptationStatus(StrEnum):
    PROPOSED = "PROPOSED"
    ELIGIBLE = "ELIGIBLE"
    SHADOW = "SHADOW"
    EVALUATING = "EVALUATING"
    PROMOTION_READY = "PROMOTION_READY"
    BLOCKED = "BLOCKED"
    REJECTED = "REJECTED"


@dataclass(slots=True)
class OutcomePattern:
    task_family: str
    attribution_target: str
    effect: str
    support_outcome_ids: tuple[str, ...]
    counter_outcome_ids: tuple[str, ...]
    mean_confidence: float
    distinct_tasks: int
    subject_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    pattern_id: str = field(default_factory=lambda: f"PAT-{uuid4().hex[:12].upper()}")

    @property
    def support_count(self) -> int:
        return len(self.support_outcome_ids)

    @property
    def counter_count(self) -> int:
        return len(self.counter_outcome_ids)

    @property
    def counter_ratio(self) -> float:
        total = self.support_count + self.counter_count
        return self.counter_count / total if total else 0.0

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["support_outcome_ids"] = list(self.support_outcome_ids)
        d["counter_outcome_ids"] = list(self.counter_outcome_ids)
        return d


@dataclass(slots=True)
class AdaptationCandidate:
    domain: AdaptationDomain
    task_family: str
    key: str
    statement: str
    proposed_change: dict[str, Any]
    pattern_id: str
    support_outcome_ids: tuple[str, ...]
    counter_outcome_ids: tuple[str, ...] = ()
    confidence: float = 0.0
    status: AdaptationStatus = AdaptationStatus.PROPOSED
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    candidate_id: str = field(default_factory=lambda: f"OGA-{uuid4().hex[:12].upper()}")

    @property
    def support_count(self) -> int:
        return len(self.support_outcome_ids)

    @property
    def counter_count(self) -> int:
        return len(self.counter_outcome_ids)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["domain"] = self.domain.value
        d["status"] = self.status.value
        d["support_outcome_ids"] = list(self.support_outcome_ids)
        d["counter_outcome_ids"] = list(self.counter_outcome_ids)
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AdaptationCandidate":
        row = dict(data)
        row["domain"] = AdaptationDomain(row["domain"])
        row["status"] = AdaptationStatus(row["status"])
        row["support_outcome_ids"] = tuple(row.get("support_outcome_ids", ()))
        row["counter_outcome_ids"] = tuple(row.get("counter_outcome_ids", ()))
        return cls(**row)


@dataclass(frozen=True, slots=True)
class CandidateEligibility:
    eligible: bool
    reason: str
    support_count: int
    counter_count: int
    confidence: float


@dataclass(frozen=True, slots=True)
class PromotionRecommendation:
    candidate_id: str
    ready_for_governance: bool
    reason: str
    replay_delta: float
    regression_count: int
    shadow_success_rate: float
    evaluation_samples: int
    academy_recommended: bool
