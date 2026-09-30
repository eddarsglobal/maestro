from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .enums import (
    CouncilId,
    MissionState,
    VerdictScope,
    VerdictValue,
    EvidenceKind,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class Evidence:
    task_id: str
    council: CouncilId
    kind: EvidenceKind
    claim: str
    payload: Any
    source_ref: str | None = None
    created_at: str = field(default_factory=utc_now)
    evidence_id: str = field(default_factory=lambda: f"EVD-{uuid4().hex[:12].upper()}")

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["council"] = self.council.value
        d["kind"] = self.kind.value
        return d


@dataclass(slots=True)
class Verdict:
    task_id: str
    council: CouncilId
    value: VerdictValue
    scope: VerdictScope
    findings: list[dict[str, Any]] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["council"] = self.council.value
        d["value"] = self.value.value
        d["scope"] = self.scope.value
        return d


@dataclass(slots=True)
class RoutingRequest:
    task_id: str
    requested_by: CouncilId
    targets: list[CouncilId]
    action: str
    reason: str
    via: CouncilId = CouncilId.EX

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "requested_by": self.requested_by.value,
            "targets": [x.value for x in self.targets],
            "action": self.action,
            "reason": self.reason,
            "via": self.via.value,
        }


@dataclass(slots=True)
class Mission:
    objective: str
    scope: str = ""
    requested_output: str = ""
    task_id: str = field(default_factory=lambda: f"TASK-{uuid4().hex[:12].upper()}")
    state: MissionState = MissionState.RECEIVED
    acceptance_criteria: list[str] = field(default_factory=list)
    strike_team: list[CouncilId] = field(default_factory=list)
    domain_verdicts: list[Verdict] = field(default_factory=list)
    system_verdict: Verdict | None = None
    tx_commit_authorized: bool = False
    tx_committed: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def touch(self) -> None:
        self.updated_at = utc_now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "objective": self.objective,
            "scope": self.scope,
            "requested_output": self.requested_output,
            "state": self.state.value,
            "acceptance_criteria": list(self.acceptance_criteria),
            "strike_team": [x.value for x in self.strike_team],
            "domain_verdicts": [x.to_dict() for x in self.domain_verdicts],
            "system_verdict": self.system_verdict.to_dict() if self.system_verdict else None,
            "tx_commit_authorized": self.tx_commit_authorized,
            "tx_committed": self.tx_committed,
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
