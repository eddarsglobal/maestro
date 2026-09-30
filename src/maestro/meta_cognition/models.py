from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import StrEnum
from typing import Any


class EpistemicFlag(StrEnum):
    KNOWN = "KNOWN"
    UNKNOWN = "UNKNOWN"
    ASSUMED = "ASSUMED"
    INFERRED = "INFERRED"
    VERIFIED = "VERIFIED"
    BLOCKED = "BLOCKED"


class MetaSignalType(StrEnum):
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    CONTRADICTION = "CONTRADICTION"
    EVIDENCE_GAP = "EVIDENCE_GAP"
    STRATEGY_DRIFT = "STRATEGY_DRIFT"
    RETRY_LOOP = "RETRY_LOOP"
    OVERSPEND_RISK = "OVERSPEND_RISK"
    UNDERSPEND_RISK = "UNDERSPEND_RISK"
    STALE_ASSUMPTION = "STALE_ASSUMPTION"
    CAPABILITY_GAP = "CAPABILITY_GAP"
    HUMAN_AUTHORIZATION_REQUIRED = "HUMAN_AUTHORIZATION_REQUIRED"


class MetaAction(StrEnum):
    CONTINUE = "CONTINUE"
    REQUEST_MORE_EVIDENCE = "REQUEST_MORE_EVIDENCE"
    CHANGE_STRATEGY = "CHANGE_STRATEGY"
    DEEPEN_COGNITION = "DEEPEN_COGNITION"
    REDUCE_COGNITION = "REDUCE_COGNITION"
    REVALIDATE_ASSUMPTIONS = "REVALIDATE_ASSUMPTIONS"
    ESCALATE_AY = "ESCALATE_AY"
    ESCALATE_EX = "ESCALATE_EX"
    REQUEST_HUMAN_APPROVAL = "REQUEST_HUMAN_APPROVAL"
    BLOCK = "BLOCK"


@dataclass(slots=True)
class MetaSignal:
    signal_type: MetaSignalType
    severity: float
    confidence: float
    evidence_refs: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MetaAssessment:
    task_id: str
    confidence: float
    evidence_sufficiency: float
    contradiction_score: float
    strategy_drift_score: float
    signals: list[MetaSignal]
    recommended_actions: list[MetaAction]
    epistemic_status: EpistemicFlag
    safe_to_continue: bool
    rationale: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "confidence": self.confidence,
            "evidence_sufficiency": self.evidence_sufficiency,
            "contradiction_score": self.contradiction_score,
            "strategy_drift_score": self.strategy_drift_score,
            "signals": [
                {
                    "signal_type": s.signal_type.value,
                    "severity": s.severity,
                    "confidence": s.confidence,
                    "evidence_refs": list(s.evidence_refs),
                    "details": dict(s.details),
                }
                for s in self.signals
            ],
            "recommended_actions": [a.value for a in self.recommended_actions],
            "epistemic_status": self.epistemic_status.value,
            "safe_to_continue": self.safe_to_continue,
            "rationale": dict(self.rationale),
        }


@dataclass(slots=True)
class StrategyCheckpoint:
    task_id: str
    strategy_id: str
    objective: str
    progress_score: float
    evidence_score: float
    retries: int
    resource_calls: int
    cost_fraction: float
    latency_fraction: float
    assumptions: dict[str, EpistemicFlag] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
