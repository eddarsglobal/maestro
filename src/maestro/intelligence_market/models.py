from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import StrEnum
from typing import Any


class MarketMetric(StrEnum):
    QUALITY = "QUALITY"
    SUCCESS = "SUCCESS"
    LATENCY = "LATENCY"
    COST = "COST"
    RELIABILITY = "RELIABILITY"
    CONTEXT_FIT = "CONTEXT_FIT"
    TOOL_FIT = "TOOL_FIT"
    LOCALITY = "LOCALITY"


@dataclass(slots=True)
class MarketObservation:
    resource_id: str
    task_family: str
    council_id: str | None
    success: bool
    quality: float
    latency_ms: float | None = None
    cost_score: float = 0.0
    context_fit: float = 1.0
    tool_fit: float = 1.0
    local: bool = False
    evidence_ref: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ResourceScoreCard:
    resource_id: str
    task_family: str
    council_id: str | None
    samples: int
    success_rate: float
    mean_quality: float
    mean_latency_ms: float | None
    mean_cost_score: float
    reliability: float
    context_fit: float
    tool_fit: float
    local_ratio: float
    market_score: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MarketPolicy:
    quality_weight: float = 0.35
    success_weight: float = 0.25
    reliability_weight: float = 0.15
    latency_weight: float = 0.10
    cost_weight: float = 0.05
    context_weight: float = 0.05
    tool_weight: float = 0.03
    locality_weight: float = 0.02
    # Minimum observations before a resource is no longer considered
    # under-tested by bounded market exploration.
    min_samples_for_confidence: int = 3

    # Evidence required before MarketSelection confidence may reach 1.0.
    # Performance score and evidence confidence are intentionally separate.
    full_confidence_samples: int = 12
    full_confidence_scenarios: int = 6

    def total_weight(self) -> float:
        return (
            self.quality_weight
            + self.success_weight
            + self.reliability_weight
            + self.latency_weight
            + self.cost_weight
            + self.context_weight
            + self.tool_weight
            + self.locality_weight
        )


@dataclass(slots=True)
class MarketSelection:
    resource_id: str
    task_family: str
    council_id: str | None
    market_score: float
    confidence: float
    explored: bool
    rationale: dict[str, Any] = field(default_factory=dict)
