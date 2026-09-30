from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class OutcomeDimension(StrEnum):
    SEMANTIC_CORRECTNESS = "SEMANTIC_CORRECTNESS"
    FORMAT_COMPLIANCE = "FORMAT_COMPLIANCE"
    TOOL_EXECUTION = "TOOL_EXECUTION"
    CONTEXT_FIT = "CONTEXT_FIT"
    RESOURCE_EXECUTION = "RESOURCE_EXECUTION"
    STRATEGY_EXECUTION = "STRATEGY_EXECUTION"
    LATENCY_BUDGET = "LATENCY_BUDGET"
    EVIDENCE_SUFFICIENCY = "EVIDENCE_SUFFICIENCY"
    VALIDATOR_INTEGRITY = "VALIDATOR_INTEGRITY"


class AttributionTarget(StrEnum):
    RESOURCE = "RESOURCE"
    PROMPT = "PROMPT"
    FORMAT = "FORMAT"
    CONTEXT = "CONTEXT"
    TOOL = "TOOL"
    STRATEGY = "STRATEGY"
    VALIDATOR = "VALIDATOR"
    EXTERNAL = "EXTERNAL"
    UNKNOWN = "UNKNOWN"


class AttributionEffect(StrEnum):
    CREDIT = "CREDIT"
    BLAME = "BLAME"
    NEUTRAL = "NEUTRAL"
    INSUFFICIENT = "INSUFFICIENT"


@dataclass(slots=True)
class DimensionResult:
    dimension: OutcomeDimension
    passed: bool | None
    score: float | None = None
    evidence_ref: str | None = None
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["dimension"] = self.dimension.value
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DimensionResult":
        row = dict(data)
        row["dimension"] = OutcomeDimension(row["dimension"])
        return cls(**row)


@dataclass(slots=True)
class AttributionFinding:
    target: AttributionTarget
    effect: AttributionEffect
    confidence: float
    reason: str
    confounders: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["target"] = self.target.value
        d["effect"] = self.effect.value
        d["confounders"] = list(self.confounders)
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AttributionFinding":
        row = dict(data)
        row["target"] = AttributionTarget(row["target"])
        row["effect"] = AttributionEffect(row["effect"])
        row["confounders"] = tuple(row.get("confounders", ()))
        return cls(**row)


@dataclass(slots=True)
class VerifiedOutcome:
    task_id: str
    task_family: str
    system_verdict: str
    ay_verified: bool
    resource_id: str | None = None
    dimensions: tuple[DimensionResult, ...] = ()
    attributions: tuple[AttributionFinding, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    outcome_id: str = field(default_factory=lambda: f"OUT-{uuid4().hex[:12].upper()}")

    @property
    def system_success(self) -> bool:
        return self.system_verdict == "JUSTE"

    def dimension(self, name: OutcomeDimension) -> DimensionResult | None:
        for item in self.dimensions:
            if item.dimension == name:
                return item
        return None

    def attribution(self, target: AttributionTarget) -> AttributionFinding | None:
        for item in self.attributions:
            if item.target == target:
                return item
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_family": self.task_family,
            "system_verdict": self.system_verdict,
            "ay_verified": self.ay_verified,
            "resource_id": self.resource_id,
            "dimensions": [x.to_dict() for x in self.dimensions],
            "attributions": [x.to_dict() for x in self.attributions],
            "evidence_ids": list(self.evidence_ids),
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
            "outcome_id": self.outcome_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VerifiedOutcome":
        row = dict(data)
        row["dimensions"] = tuple(DimensionResult.from_dict(x) for x in row.get("dimensions", ()))
        row["attributions"] = tuple(AttributionFinding.from_dict(x) for x in row.get("attributions", ()))
        row["evidence_ids"] = tuple(row.get("evidence_ids", ()))
        return cls(**row)


@dataclass(slots=True)
class MarketLearningDirective:
    resource_id: str | None
    task_family: str
    eligible: bool
    success: bool | None
    quality: float | None
    confidence: float
    reason: str
    metadata: dict[str, Any] = field(default_factory=dict)
