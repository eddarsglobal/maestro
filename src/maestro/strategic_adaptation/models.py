from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import StrEnum
from typing import Any


class StrategyTrigger(StrEnum):
    META_DRIFT = "META_DRIFT"
    RETRY_LOOP = "RETRY_LOOP"
    EVIDENCE_GAP = "EVIDENCE_GAP"
    CONTRADICTION = "CONTRADICTION"
    CAPABILITY_GAP = "CAPABILITY_GAP"
    OVERSPEND = "OVERSPEND"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class StrategyStatus(StrEnum):
    CANDIDATE = "CANDIDATE"
    SHADOW = "SHADOW"
    ACTIVE = "ACTIVE"
    FAILED = "FAILED"
    RETIRED = "RETIRED"
    ROLLED_BACK = "ROLLED_BACK"


@dataclass(slots=True)
class StrategyCandidate:
    strategy_id: str
    family: str
    objective: str
    method: str
    required_capabilities: tuple[str, ...] = ()
    expected_quality: float = 0.5
    expected_evidence_gain: float = 0.5
    expected_cost: float = 0.5
    expected_latency: float = 0.5
    reversible: bool = True
    status: StrategyStatus = StrategyStatus.CANDIDATE
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StrategyEvaluation:
    strategy_id: str
    score: float
    confidence: float
    expected_quality: float
    expected_evidence_gain: float
    expected_cost: float
    expected_latency: float
    reversible: bool
    rationale: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StrategyDecision:
    selected_strategy_id: str
    previous_strategy_id: str | None
    trigger: StrategyTrigger
    switch_required: bool
    confidence: float
    rationale: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StrategyTransition:
    task_id: str
    from_strategy_id: str | None
    to_strategy_id: str
    trigger: StrategyTrigger
    authorized: bool
    reversible: bool
    outcome: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["trigger"] = self.trigger.value
        return d
