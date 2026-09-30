from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class AcademyScenario:
    task_family: str
    objective: str
    required_councils: set[str]
    forbidden_councils: set[str] = field(default_factory=set)
    required_gates: set[str] = field(default_factory=set)
    difficulty: int = 1
    risk: int = 1
    tags: set[str] = field(default_factory=set)
    expected_human_approval: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    scenario_id: str = field(default_factory=lambda: f"SCN-{uuid4().hex[:12].upper()}")

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        for key in ("required_councils", "forbidden_councils", "required_gates", "tags"):
            d[key] = sorted(d[key])
        return d


@dataclass(slots=True)
class ScenarioResult:
    scenario_id: str
    policy_id: str
    success: bool
    selected_councils: set[str]
    gates_observed: set[str]
    human_approval_requested: bool
    retries: int = 0
    latency_ms: float = 0.0
    cost_units: float = 0.0
    evidence_score: float = 1.0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["selected_councils"] = sorted(self.selected_councils)
        d["gates_observed"] = sorted(self.gates_observed)
        return d


@dataclass(slots=True)
class PolicyVariant:
    policy_id: str
    version: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
    parent_policy_id: str | None = None


@dataclass(slots=True)
class Weakness:
    dimension: str
    key: str
    score: float
    sample_count: int
    severity: str
    evidence: list[str] = field(default_factory=list)


@dataclass(slots=True)
class CurriculumItem:
    focus: str
    task_family: str
    difficulty: int
    repetitions: int
    reason: str
    tags: set[str] = field(default_factory=set)
