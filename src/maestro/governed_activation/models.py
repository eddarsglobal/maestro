from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from collections.abc import Mapping
from typing import Any


def _deep_freeze_json(value):
    if isinstance(value, Mapping):
        return MappingProxyType({
            str(key): _deep_freeze_json(item)
            for key, item in value.items()
        })

    if isinstance(value, (list, tuple)):
        return tuple(
            _deep_freeze_json(item)
            for item in value
        )

    if value is None or isinstance(
        value,
        (str, int, float, bool),
    ):
        return value

    raise TypeError(
        "GPA immutable metadata accepts JSON-compatible values only."
    )


def _deep_thaw_json(value):
    if isinstance(value, Mapping):
        return {
            str(key): _deep_thaw_json(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            _deep_thaw_json(item)
            for item in value
        ]

    if value is None or isinstance(
        value,
        (str, int, float, bool),
    ):
        return value

    raise TypeError(
        "GPA immutable metadata contains unsupported value."
    )


def _canonical_json(value) -> str:
    return json.dumps(
        _deep_thaw_json(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


class ActivationState(str, Enum):
    PROPOSED = "PROPOSED"
    AY_VALIDATED = "AY_VALIDATED"
    EX_AUTHORIZED = "EX_AUTHORIZED"
    CANARY = "CANARY"
    CANARY_VERIFIED = "CANARY_VERIFIED"
    ACTIVE = "ACTIVE"
    ROLLED_BACK = "ROLLED_BACK"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class ActivationContract:
    candidate_id: str
    task_family: str
    policy_kind: str
    policy_ref: str
    baseline_ref: str
    rollback_ref: str
    canary_fraction: float = 0.10
    metadata: Mapping[str, Any] = field(default_factory=dict)
    contract_id: str = field(init=False)

    def __post_init__(self) -> None:
        if not self.candidate_id:
            raise ValueError("candidate_id is required")
        if not self.policy_kind:
            raise ValueError("policy_kind is required")
        if not self.policy_ref:
            raise ValueError("policy_ref is required")
        if not self.baseline_ref:
            raise ValueError("baseline_ref is required")
        if not self.rollback_ref:
            raise ValueError("rollback_ref is required")
        if not (0.0 < float(self.canary_fraction) <= 1.0):
            raise ValueError("canary_fraction must be in (0, 1]")

        frozen_metadata = _deep_freeze_json(
            dict(self.metadata or {})
        )
        object.__setattr__(self, "metadata", frozen_metadata)
        object.__setattr__(
            self,
            "contract_id",
            self._expected_contract_id(),
        )

    def _identity_payload(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "task_family": self.task_family,
            "policy_kind": self.policy_kind,
            "policy_ref": self.policy_ref,
            "baseline_ref": self.baseline_ref,
            "rollback_ref": self.rollback_ref,
            "canary_fraction": float(self.canary_fraction),
            "metadata": _deep_thaw_json(self.metadata),
        }

    def _expected_contract_id(self) -> str:
        raw = _canonical_json(self._identity_payload())
        digest = hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()[:12].upper()
        return f"GPA-{digest}"

    def assert_integrity(self) -> None:
        expected = self._expected_contract_id()
        if self.contract_id != expected:
            raise ValueError(
                "Activation contract integrity check failed"
            )

    def to_dict(self) -> dict[str, Any]:
        self.assert_integrity()
        return {
            **self._identity_payload(),
            "contract_id": self.contract_id,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "ActivationContract":
        contract = cls(
            candidate_id=str(data["candidate_id"]),
            task_family=str(data["task_family"]),
            policy_kind=str(data["policy_kind"]),
            policy_ref=str(data["policy_ref"]),
            baseline_ref=str(data["baseline_ref"]),
            rollback_ref=str(data["rollback_ref"]),
            canary_fraction=float(
                data.get("canary_fraction", 0.10)
            ),
            metadata=dict(data.get("metadata") or {}),
        )

        expected = data.get("contract_id")

        if expected and contract.contract_id != expected:
            raise ValueError(
                "Activation contract integrity check failed"
            )

        contract.assert_integrity()
        return contract


@dataclass(frozen=True)
class CanaryEvidence:
    success_rate: float
    regression_count: int
    observed_samples: int
    evidence_refs: tuple[str, ...]
    latency_budget_pass: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "evidence_refs",
            tuple(str(value) for value in self.evidence_refs),
        )
        object.__setattr__(
            self,
            "metadata",
            _deep_freeze_json(dict(self.metadata or {})),
        )

    def healthy(
        self,
        *,
        min_success_rate: float = 0.95,
        min_samples: int = 3,
    ) -> bool:
        return bool(
            self.observed_samples >= int(min_samples)
            and self.success_rate >= float(min_success_rate)
            and self.regression_count == 0
            and self.latency_budget_pass
            and len(self.evidence_refs) > 0
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "success_rate": float(self.success_rate),
            "regression_count": int(self.regression_count),
            "observed_samples": int(self.observed_samples),
            "evidence_refs": list(self.evidence_refs),
            "latency_budget_pass": bool(
                self.latency_budget_pass
            ),
            "metadata": _deep_thaw_json(self.metadata),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "CanaryEvidence":
        return cls(
            success_rate=float(data["success_rate"]),
            regression_count=int(data["regression_count"]),
            observed_samples=int(data["observed_samples"]),
            evidence_refs=tuple(
                str(value)
                for value in data.get("evidence_refs", ())
            ),
            latency_budget_pass=bool(
                data.get("latency_budget_pass", True)
            ),
            metadata=dict(data.get("metadata") or {}),
        )


@dataclass
class ActivationSnapshot:
    contract: ActivationContract
    state: ActivationState = ActivationState.PROPOSED
    ay_validated: bool = False
    ex_authorized: bool = False
    canary_evidence: CanaryEvidence | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def contract_id(self) -> str:
        return self.contract.contract_id

    @property
    def candidate_id(self) -> str:
        return self.contract.candidate_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract": self.contract.to_dict(),
            "state": self.state.value,
            "ay_validated": bool(self.ay_validated),
            "ex_authorized": bool(self.ex_authorized),
            "canary_evidence": (
                self.canary_evidence.to_dict()
                if self.canary_evidence is not None
                else None
            ),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ActivationSnapshot":
        evidence = data.get("canary_evidence")
        return cls(
            contract=ActivationContract.from_dict(dict(data["contract"])),
            state=ActivationState(str(data["state"])),
            ay_validated=bool(data.get("ay_validated", False)),
            ex_authorized=bool(data.get("ex_authorized", False)),
            canary_evidence=(
                CanaryEvidence.from_dict(dict(evidence))
                if evidence is not None
                else None
            ),
            metadata=dict(data.get("metadata") or {}),
        )
