from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import hashlib
from typing import Any

from maestro.enums import CouncilId, LoopRisk


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sig(value: str) -> str:
    normalized = " ".join(value.lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


@dataclass(slots=True)
class RetryAttempt:
    task_id: str
    worker: CouncilId
    criterion_id: str
    failure_mode: str
    strategy: str
    new_evidence: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_utc_now)
    failure_signature: str = ""
    strategy_signature: str = ""

    def __post_init__(self) -> None:
        if not self.failure_signature:
            self.failure_signature = _sig(f"{self.criterion_id}|{self.failure_mode}")
        if not self.strategy_signature:
            self.strategy_signature = _sig(self.strategy)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["worker"] = self.worker.value
        return d


@dataclass(slots=True)
class RetryAssessment:
    same_failure_same_strategy_count: int
    risk: LoopRisk
    breakout_recommended: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "same_failure_same_strategy_count": self.same_failure_same_strategy_count,
            "risk": self.risk.value,
            "breakout_recommended": self.breakout_recommended,
            "reason": self.reason,
        }


@dataclass
class RetryLedger:
    breakout_threshold: int = 3
    attempts: list[RetryAttempt] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.breakout_threshold < 2:
            raise ValueError("breakout_threshold must be at least 2.")

    def record(self, actor: CouncilId, attempt: RetryAttempt) -> RetryAssessment:
        if actor is not CouncilId.OP:
            raise PermissionError("Only OP may write the canonical retry ledger.")
        self.attempts.append(attempt)
        return self.assess(attempt)

    def assess(self, attempt: RetryAttempt) -> RetryAssessment:
        matches = [
            x for x in self.attempts
            if x.task_id == attempt.task_id
            and x.worker == attempt.worker
            and x.failure_signature == attempt.failure_signature
            and x.strategy_signature == attempt.strategy_signature
        ]
        count = len(matches)

        if count >= self.breakout_threshold:
            return RetryAssessment(
                count,
                LoopRisk.BREAKOUT_CANDIDATE,
                True,
                "Repeated materially equivalent failure with materially equivalent strategy.",
            )
        if count == self.breakout_threshold - 1:
            return RetryAssessment(
                count,
                LoopRisk.HIGH,
                False,
                "Repeated failure pattern; change strategy before another blind retry.",
            )
        if count == 1:
            return RetryAssessment(count, LoopRisk.LOW, False, "First recorded occurrence.")
        return RetryAssessment(count, LoopRisk.ELEVATED, False, "Failure pattern is recurring.")

    def new_strategy_resets_pattern(self, previous: RetryAttempt, current: RetryAttempt) -> bool:
        return previous.strategy_signature != current.strategy_signature

    def snapshot(self) -> dict[str, Any]:
        return {
            "breakout_threshold": self.breakout_threshold,
            "attempts": [x.to_dict() for x in self.attempts],
        }

    @classmethod
    def from_snapshot(cls, snapshot: dict[str, Any]) -> "RetryLedger":
        ledger = cls(breakout_threshold=int(snapshot.get("breakout_threshold", 3)))
        for raw in snapshot.get("attempts", []):
            ledger.attempts.append(
                RetryAttempt(
                    task_id=raw["task_id"],
                    worker=CouncilId(raw["worker"]),
                    criterion_id=raw["criterion_id"],
                    failure_mode=raw["failure_mode"],
                    strategy=raw["strategy"],
                    new_evidence=list(raw.get("new_evidence", [])),
                    created_at=raw["created_at"],
                    failure_signature=raw["failure_signature"],
                    strategy_signature=raw["strategy_signature"],
                )
            )
        return ledger
