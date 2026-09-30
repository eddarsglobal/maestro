from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import StrEnum
from typing import Any


class MissionComplexity(StrEnum):
    TRIVIAL = "TRIVIAL"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EconomyTier(StrEnum):
    MINIMAL = "MINIMAL"
    STANDARD = "STANDARD"
    DEEP = "DEEP"
    MAX_GOVERNED = "MAX_GOVERNED"


@dataclass(slots=True)
class MissionEconomyProfile:
    task_id: str
    complexity: MissionComplexity
    risk_score: float
    uncertainty_score: float
    reversibility_score: float
    evidence_demand: float
    time_sensitivity: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CognitiveSpendPlan:
    task_id: str
    tier: EconomyTier
    max_stages: int
    max_resource_calls: int
    max_parallel_candidates: int
    max_tokens_per_call: int
    max_total_tokens: int
    max_latency_ms: int
    max_cost_score: float
    require_critic: bool
    require_verifier: bool
    allow_multi_resource: bool
    stop_on_sufficient_evidence: bool = True
    rationale: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["tier"] = self.tier.value
        return d


@dataclass(slots=True)
class SpendObservation:
    task_family: str
    council_id: str | None
    tier: EconomyTier
    success: bool
    quality: float
    total_tokens: int
    latency_ms: float
    cost_score: float
    stages_used: int
    resource_calls: int
    evidence_sufficient: bool


@dataclass(slots=True)
class MarginalUtilityDecision:
    continue_spending: bool
    expected_gain: float
    marginal_cost: float
    ratio: float
    reason: str
