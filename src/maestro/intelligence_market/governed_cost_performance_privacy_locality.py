from __future__ import annotations

import hashlib
import json
import math

from dataclasses import dataclass, field
from typing import Any, Iterable

from maestro.intelligence_market.governed_capability_resource_market import (
    ResourceLocality,
)


GOVERNED_COST_PERFORMANCE_PRIVACY_LOCALITY_VERSION = 1


class CostPerformancePrivacyLocalityInvariantError(
    ValueError
):
    pass


class MissionConstraintUnsatisfiedError(
    CostPerformancePrivacyLocalityInvariantError
):
    pass


def _required_text(
    value: str,
    name: str,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            f"{name} must be a string."
        )

    value = value.strip()

    if not value:
        raise CostPerformancePrivacyLocalityInvariantError(
            f"{name} must not be empty."
        )

    if "\x00" in value:
        raise CostPerformancePrivacyLocalityInvariantError(
            f"{name} must not contain NUL."
        )

    return value


def _normalized_tuple(
    values: Iterable[str],
    name: str,
    *,
    require_nonempty: bool = True,
) -> tuple[str, ...]:
    rows = tuple(
        sorted(
            _required_text(
                item,
                name,
            )
            for item in values
        )
    )

    if require_nonempty and not rows:
        raise CostPerformancePrivacyLocalityInvariantError(
            f"{name} must not be empty."
        )

    if len(rows) != len(set(rows)):
        raise CostPerformancePrivacyLocalityInvariantError(
            f"{name} values must be unique."
        )

    return rows


def _score(
    value: float,
    name: str,
) -> float:
    if (
        not isinstance(
            value,
            (int, float),
        )
        or isinstance(value, bool)
    ):
        raise TypeError(
            f"{name} must be numeric."
        )

    value = float(value)

    if (
        not math.isfinite(value)
        or not 0.0 <= value <= 1.0
    ):
        raise CostPerformancePrivacyLocalityInvariantError(
            f"{name} must be between 0 and 1."
        )

    return value


def _nonnegative_int(
    value: int,
    name: str,
) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
    ):
        raise CostPerformancePrivacyLocalityInvariantError(
            f"{name} must be an integer >= 0."
        )

    return value


def _nonnegative_number(
    value: float,
    name: str,
) -> float:
    if (
        not isinstance(
            value,
            (int, float),
        )
        or isinstance(value, bool)
    ):
        raise TypeError(
            f"{name} must be numeric."
        )

    value = float(value)

    if (
        not math.isfinite(value)
        or value < 0.0
    ):
        raise CostPerformancePrivacyLocalityInvariantError(
            f"{name} must be finite and >= 0."
        )

    return value


def _required_bool(
    value: bool,
    name: str,
) -> bool:
    if not isinstance(value, bool):
        raise TypeError(
            f"{name} must be bool."
        )

    return value


def _canonical_json(
    value: Any,
) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _stable_id(
    prefix: str,
    payload: Any,
) -> str:
    return (
        prefix
        + "-"
        + hashlib.sha256(
            _canonical_json(
                payload
            ).encode("utf-8")
        ).hexdigest()[:24]
    )


@dataclass(
    frozen=True,
    slots=True,
)
class MissionResourcePerformanceEvidence:
    mission_contract_id: str
    resource_id: str
    capability_id: str

    cost_units: int
    latency_ms: int
    energy_millijoules: float

    locality: ResourceLocality

    reliability: float
    outcome_score: float
    privacy_score: float

    offline_capable: bool
    private_execution: bool

    cost_evidence_ref: str
    latency_evidence_ref: str
    energy_evidence_ref: str
    locality_evidence_ref: str
    reliability_evidence_ref: str
    outcome_evidence_ref: str
    privacy_evidence_ref: str

    evidence_id: str = field(
        init=False
    )

    optimization_authority_granted: bool = False
    trust_granted: bool = False
    activation_authorized: bool = False
    execution_authorized: bool = False
    effect_authorized: bool = False
    network_authorized: bool = False
    mission_authority_transferred: bool = False
    system_truth_asserted: bool = False

    def __post_init__(self) -> None:
        for name in (
            "mission_contract_id",
            "resource_id",
            "capability_id",
            "cost_evidence_ref",
            "latency_evidence_ref",
            "energy_evidence_ref",
            "locality_evidence_ref",
            "reliability_evidence_ref",
            "outcome_evidence_ref",
            "privacy_evidence_ref",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(self, name),
                    name,
                ),
            )

        object.__setattr__(
            self,
            "cost_units",
            _nonnegative_int(
                self.cost_units,
                "cost_units",
            ),
        )

        object.__setattr__(
            self,
            "latency_ms",
            _nonnegative_int(
                self.latency_ms,
                "latency_ms",
            ),
        )

        object.__setattr__(
            self,
            "energy_millijoules",
            _nonnegative_number(
                self.energy_millijoules,
                "energy_millijoules",
            ),
        )

        if not isinstance(
            self.locality,
            ResourceLocality,
        ):
            raise TypeError(
                "locality must be ResourceLocality."
            )

        for name in (
            "reliability",
            "outcome_score",
            "privacy_score",
        ):
            object.__setattr__(
                self,
                name,
                _score(
                    getattr(self, name),
                    name,
                ),
            )

        for name in (
            "offline_capable",
            "private_execution",
        ):
            object.__setattr__(
                self,
                name,
                _required_bool(
                    getattr(self, name),
                    name,
                ),
            )

        for name in (
            "optimization_authority_granted",
            "trust_granted",
            "activation_authorized",
            "execution_authorized",
            "effect_authorized",
            "network_authorized",
            "mission_authority_transferred",
            "system_truth_asserted",
        ):
            if getattr(self, name) is not False:
                raise CostPerformancePrivacyLocalityInvariantError(
                    "Performance evidence cannot "
                    f"assert {name}."
                )

        object.__setattr__(
            self,
            "evidence_id",
            _stable_id(
                "MRP",
                self.to_payload(),
            ),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "mission_contract_id": (
                self.mission_contract_id
            ),
            "resource_id": self.resource_id,
            "capability_id": self.capability_id,
            "cost_units": self.cost_units,
            "latency_ms": self.latency_ms,
            "energy_millijoules": (
                self.energy_millijoules
            ),
            "locality": self.locality.value,
            "reliability": self.reliability,
            "outcome_score": self.outcome_score,
            "privacy_score": self.privacy_score,
            "offline_capable": (
                self.offline_capable
            ),
            "private_execution": (
                self.private_execution
            ),
            "cost_evidence_ref": (
                self.cost_evidence_ref
            ),
            "latency_evidence_ref": (
                self.latency_evidence_ref
            ),
            "energy_evidence_ref": (
                self.energy_evidence_ref
            ),
            "locality_evidence_ref": (
                self.locality_evidence_ref
            ),
            "reliability_evidence_ref": (
                self.reliability_evidence_ref
            ),
            "outcome_evidence_ref": (
                self.outcome_evidence_ref
            ),
            "privacy_evidence_ref": (
                self.privacy_evidence_ref
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class MissionExecutionOptimizationPolicy:
    mission_contract_id: str
    constraint_refs: tuple[str, ...]

    prefer_local: bool
    prefer_offline: bool
    prefer_private: bool

    require_local: bool
    require_offline: bool
    require_private: bool

    min_privacy_score: float
    min_reliability: float

    max_cost_units: int
    max_latency_ms: int
    max_energy_millijoules: float

    policy_id: str = field(
        init=False
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "mission_contract_id",
            _required_text(
                self.mission_contract_id,
                "mission_contract_id",
            ),
        )

        object.__setattr__(
            self,
            "constraint_refs",
            _normalized_tuple(
                self.constraint_refs,
                "constraint_ref",
            ),
        )

        for name in (
            "prefer_local",
            "prefer_offline",
            "prefer_private",
            "require_local",
            "require_offline",
            "require_private",
        ):
            object.__setattr__(
                self,
                name,
                _required_bool(
                    getattr(self, name),
                    name,
                ),
            )

        for name in (
            "min_privacy_score",
            "min_reliability",
        ):
            object.__setattr__(
                self,
                name,
                _score(
                    getattr(self, name),
                    name,
                ),
            )

        object.__setattr__(
            self,
            "max_cost_units",
            _nonnegative_int(
                self.max_cost_units,
                "max_cost_units",
            ),
        )

        object.__setattr__(
            self,
            "max_latency_ms",
            _nonnegative_int(
                self.max_latency_ms,
                "max_latency_ms",
            ),
        )

        object.__setattr__(
            self,
            "max_energy_millijoules",
            _nonnegative_number(
                self.max_energy_millijoules,
                "max_energy_millijoules",
            ),
        )

        object.__setattr__(
            self,
            "policy_id",
            _stable_id(
                "MEP",
                {
                    "mission_contract_id": (
                        self.mission_contract_id
                    ),
                    "constraint_refs": list(
                        self.constraint_refs
                    ),
                    "prefer_local": (
                        self.prefer_local
                    ),
                    "prefer_offline": (
                        self.prefer_offline
                    ),
                    "prefer_private": (
                        self.prefer_private
                    ),
                    "require_local": (
                        self.require_local
                    ),
                    "require_offline": (
                        self.require_offline
                    ),
                    "require_private": (
                        self.require_private
                    ),
                    "min_privacy_score": (
                        self.min_privacy_score
                    ),
                    "min_reliability": (
                        self.min_reliability
                    ),
                    "max_cost_units": (
                        self.max_cost_units
                    ),
                    "max_latency_ms": (
                        self.max_latency_ms
                    ),
                    "max_energy_millijoules": (
                        self.max_energy_millijoules
                    ),
                },
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedResourceOptimizationSelection:
    mission_contract_id: str
    capability_id: str
    policy_id: str

    selected_resource_id: str
    selected_evidence_id: str

    eligible_resource_ids: tuple[str, ...]
    eligible_evidence_ids: tuple[str, ...]

    selection_id: str = field(
        init=False
    )

    optimization_authority_granted: bool = False
    trust_granted: bool = False
    activation_authorized: bool = False
    execution_authorized: bool = False
    effect_authorized: bool = False
    network_authorized: bool = False
    mission_authority_transferred: bool = False
    system_truth_asserted: bool = False

    def __post_init__(self) -> None:
        for name in (
            "mission_contract_id",
            "capability_id",
            "policy_id",
            "selected_resource_id",
            "selected_evidence_id",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(self, name),
                    name,
                ),
            )

        object.__setattr__(
            self,
            "eligible_resource_ids",
            _normalized_tuple(
                self.eligible_resource_ids,
                "eligible_resource_id",
            ),
        )

        object.__setattr__(
            self,
            "eligible_evidence_ids",
            _normalized_tuple(
                self.eligible_evidence_ids,
                "eligible_evidence_id",
            ),
        )

        if (
            self.selected_resource_id
            not in self.eligible_resource_ids
        ):
            raise CostPerformancePrivacyLocalityInvariantError(
                "Selected resource must be eligible."
            )

        if (
            self.selected_evidence_id
            not in self.eligible_evidence_ids
        ):
            raise CostPerformancePrivacyLocalityInvariantError(
                "Selected evidence must be eligible."
            )

        for name in (
            "optimization_authority_granted",
            "trust_granted",
            "activation_authorized",
            "execution_authorized",
            "effect_authorized",
            "network_authorized",
            "mission_authority_transferred",
            "system_truth_asserted",
        ):
            if getattr(self, name) is not False:
                raise CostPerformancePrivacyLocalityInvariantError(
                    "Optimization selection cannot "
                    f"assert {name}."
                )

        object.__setattr__(
            self,
            "selection_id",
            _stable_id(
                "CPL",
                {
                    "mission_contract_id": (
                        self.mission_contract_id
                    ),
                    "capability_id": (
                        self.capability_id
                    ),
                    "policy_id": self.policy_id,
                    "selected_resource_id": (
                        self.selected_resource_id
                    ),
                    "selected_evidence_id": (
                        self.selected_evidence_id
                    ),
                    "eligible_resource_ids": list(
                        self.eligible_resource_ids
                    ),
                    "eligible_evidence_ids": list(
                        self.eligible_evidence_ids
                    ),
                },
            ),
        )


class GovernedCostPerformancePrivacyLocality:
    @staticmethod
    def select(
        *,
        capability_id: str,
        policy: MissionExecutionOptimizationPolicy,
        evidence: Iterable[
            MissionResourcePerformanceEvidence
        ],
    ) -> GovernedResourceOptimizationSelection:
        capability_id = _required_text(
            capability_id,
            "capability_id",
        )

        if not isinstance(
            policy,
            MissionExecutionOptimizationPolicy,
        ):
            raise TypeError(
                "policy must be "
                "MissionExecutionOptimizationPolicy."
            )

        rows = tuple(
            evidence
        )

        if not rows:
            raise MissionConstraintUnsatisfiedError(
                "No resource performance evidence."
            )

        if not all(
            isinstance(
                item,
                MissionResourcePerformanceEvidence,
            )
            for item in rows
        ):
            raise TypeError(
                "evidence must contain "
                "MissionResourcePerformanceEvidence."
            )

        resource_ids = [
            item.resource_id
            for item in rows
        ]

        if len(resource_ids) != len(
            set(resource_ids)
        ):
            raise CostPerformancePrivacyLocalityInvariantError(
                "Resource performance evidence "
                "must contain unique resource IDs."
            )

        for item in rows:
            if (
                item.mission_contract_id
                != policy.mission_contract_id
            ):
                raise CostPerformancePrivacyLocalityInvariantError(
                    "Performance evidence belongs "
                    "to another mission contract."
                )

        candidates = tuple(
            item
            for item in rows
            if (
                item.capability_id
                == capability_id
                and item.privacy_score
                >= policy.min_privacy_score
                and item.reliability
                >= policy.min_reliability
                and item.cost_units
                <= policy.max_cost_units
                and item.latency_ms
                <= policy.max_latency_ms
                and item.energy_millijoules
                <= policy.max_energy_millijoules
                and (
                    not policy.require_local
                    or item.locality
                    is ResourceLocality.LOCAL
                )
                and (
                    not policy.require_offline
                    or item.offline_capable
                )
                and (
                    not policy.require_private
                    or item.private_execution
                )
            )
        )

        if not candidates:
            raise MissionConstraintUnsatisfiedError(
                "No resource satisfies mission "
                "cost/performance/privacy/locality "
                "constraints."
            )

        def ranking_key(
            item: MissionResourcePerformanceEvidence,
        ) -> tuple[Any, ...]:
            local_penalty = int(
                policy.prefer_local
                and item.locality
                is not ResourceLocality.LOCAL
            )

            offline_penalty = int(
                policy.prefer_offline
                and not item.offline_capable
            )

            private_penalty = int(
                policy.prefer_private
                and not item.private_execution
            )

            return (
                (
                    local_penalty
                    + offline_penalty
                    + private_penalty
                ),
                local_penalty,
                offline_penalty,
                private_penalty,
                -item.outcome_score,
                -item.reliability,
                -item.privacy_score,
                item.energy_millijoules,
                item.cost_units,
                item.latency_ms,
                item.resource_id,
                item.evidence_id,
            )

        ordered = tuple(
            sorted(
                candidates,
                key=ranking_key,
            )
        )

        selected = ordered[0]

        return GovernedResourceOptimizationSelection(
            mission_contract_id=(
                policy.mission_contract_id
            ),
            capability_id=capability_id,
            policy_id=policy.policy_id,
            selected_resource_id=(
                selected.resource_id
            ),
            selected_evidence_id=(
                selected.evidence_id
            ),
            eligible_resource_ids=tuple(
                item.resource_id
                for item in ordered
            ),
            eligible_evidence_ids=tuple(
                item.evidence_id
                for item in ordered
            ),
        )


__all__ = [
    "GOVERNED_COST_PERFORMANCE_PRIVACY_LOCALITY_VERSION",
    "CostPerformancePrivacyLocalityInvariantError",
    "MissionConstraintUnsatisfiedError",
    "MissionResourcePerformanceEvidence",
    "MissionExecutionOptimizationPolicy",
    "GovernedResourceOptimizationSelection",
    "GovernedCostPerformancePrivacyLocality",
]
