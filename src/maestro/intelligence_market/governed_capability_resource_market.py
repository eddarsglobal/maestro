from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Iterable

from maestro.orchestration.governed_mission_foundation import (
    MissionCapabilityDemand,
)


GOVERNED_CAPABILITY_RESOURCE_MARKET_VERSION = 1


class CapabilityResourceMarketInvariantError(
    ValueError
):
    pass


class ResourceSelectionIncompleteError(
    CapabilityResourceMarketInvariantError
):
    pass


class ResourceEvidenceState(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class ResourceLocality(StrEnum):
    LOCAL = "LOCAL"
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    UNKNOWN = "UNKNOWN"


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
        raise CapabilityResourceMarketInvariantError(
            f"{name} must not be empty."
        )

    if "\x00" in value:
        raise CapabilityResourceMarketInvariantError(
            f"{name} must not contain NUL."
        )

    return value


def _optional_text(
    value: str | None,
    name: str,
) -> str | None:
    if value is None:
        return None

    return _required_text(
        value,
        name,
    )


def _normalized_tuple(
    values: Iterable[str],
    name: str,
    *,
    require_nonempty: bool = True,
) -> tuple[str, ...]:
    rows = tuple(
        sorted(
            _required_text(
                value,
                name,
            )
            for value in values
        )
    )

    if require_nonempty and not rows:
        raise CapabilityResourceMarketInvariantError(
            f"{name} must not be empty."
        )

    if len(rows) != len(set(rows)):
        raise CapabilityResourceMarketInvariantError(
            f"{name} values must be unique."
        )

    return rows


def _bounded_score(
    value: float,
    name: str,
) -> float:
    if (
        not isinstance(
            value,
            (int, float),
        )
        or isinstance(
            value,
            bool,
        )
    ):
        raise TypeError(
            f"{name} must be numeric."
        )

    value = float(value)

    if not 0.0 <= value <= 1.0:
        raise CapabilityResourceMarketInvariantError(
            f"{name} must be between 0 and 1."
        )

    return value


def _nonnegative_int(
    value: int,
    name: str,
) -> int:
    if (
        not isinstance(
            value,
            int,
        )
        or isinstance(
            value,
            bool,
        )
        or value < 0
    ):
        raise CapabilityResourceMarketInvariantError(
            f"{name} must be an integer >= 0."
        )

    return value


def _stable_id(
    prefix: str,
    payload: dict[str, Any],
) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )

    return (
        prefix
        + "-"
        + hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()[:24]
    )


@dataclass(
    frozen=True,
    slots=True,
)
class GenericCapabilityContract:
    capability_id: str

    matched_rule_ids: tuple[
        str,
        ...,
    ]

    rationales: tuple[
        str,
        ...,
    ]

    capability_contract_id: str = field(
        init=False
    )

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "capability_id",
            _required_text(
                self.capability_id,
                "capability_id",
            ),
        )

        object.__setattr__(
            self,
            "matched_rule_ids",
            _normalized_tuple(
                self.matched_rule_ids,
                "matched_rule_id",
            ),
        )

        object.__setattr__(
            self,
            "rationales",
            _normalized_tuple(
                self.rationales,
                "rationale",
            ),
        )

        object.__setattr__(
            self,
            "capability_contract_id",
            _stable_id(
                "GCC",
                {
                    "capability_id": (
                        self.capability_id
                    ),
                    "matched_rule_ids": list(
                        self.matched_rule_ids
                    ),
                    "rationales": list(
                        self.rationales
                    ),
                },
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "capability_contract_id": (
                self.capability_contract_id
            ),
            "capability_id": (
                self.capability_id
            ),
            "matched_rule_ids": list(
                self.matched_rule_ids
            ),
            "rationales": list(
                self.rationales
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class MissionCapabilityGraph:
    mission_contract_id: str
    demand_id: str

    contracts: tuple[
        GenericCapabilityContract,
        ...,
    ]

    graph_id: str = field(
        init=False
    )

    provider_bound: bool = False
    model_bound: bool = False
    runtime_bound: bool = False
    resource_selected: bool = False
    execution_authorized: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
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
            "demand_id",
            _required_text(
                self.demand_id,
                "demand_id",
            ),
        )

        raw = tuple(
            self.contracts
        )

        if not raw:
            raise CapabilityResourceMarketInvariantError(
                "Capability graph "
                "must not be empty."
            )

        if not all(
            isinstance(
                item,
                GenericCapabilityContract,
            )
            for item in raw
        ):
            raise TypeError(
                "contracts must contain "
                "GenericCapabilityContract only."
            )

        rows = tuple(
            sorted(
                raw,
                key=lambda item: (
                    item.capability_id
                ),
            )
        )

        ids = [
            item.capability_id
            for item in rows
        ]

        if len(ids) != len(set(ids)):
            raise CapabilityResourceMarketInvariantError(
                "Capability graph contains "
                "duplicate capability IDs."
            )

        object.__setattr__(
            self,
            "contracts",
            rows,
        )

        for name in (
            "provider_bound",
            "model_bound",
            "runtime_bound",
            "resource_selected",
            "execution_authorized",
            "system_truth_asserted",
        ):
            if getattr(
                self,
                name,
            ) is not False:
                raise CapabilityResourceMarketInvariantError(
                    "Capability graph cannot "
                    f"assert {name}."
                )

        object.__setattr__(
            self,
            "graph_id",
            _stable_id(
                "MCAP",
                {
                    "mission_contract_id": (
                        self.mission_contract_id
                    ),
                    "demand_id": self.demand_id,
                    "contracts": [
                        item.to_dict()
                        for item in rows
                    ],
                },
            ),
        )

    @property
    def capability_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            item.capability_id
            for item in self.contracts
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "version": (
                GOVERNED_CAPABILITY_RESOURCE_MARKET_VERSION
            ),
            "graph_id": self.graph_id,
            "mission_contract_id": (
                self.mission_contract_id
            ),
            "demand_id": self.demand_id,
            "contracts": [
                item.to_dict()
                for item in self.contracts
            ],
            "provider_bound": False,
            "model_bound": False,
            "runtime_bound": False,
            "resource_selected": False,
            "execution_authorized": False,
            "system_truth_asserted": False,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class IntelligenceResourceCandidate:
    resource_id: str

    capabilities: tuple[
        str,
        ...,
    ]

    availability: ResourceEvidenceState

    evidence_quality: float
    reliability: float
    privacy_score: float

    cost_units: int
    latency_ms: int

    locality: ResourceLocality

    provider_ref: str | None = None
    model_ref: str | None = None
    runtime_ref: str | None = None

    candidate_id: str = field(
        init=False
    )

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "resource_id",
            _required_text(
                self.resource_id,
                "resource_id",
            ),
        )

        object.__setattr__(
            self,
            "capabilities",
            _normalized_tuple(
                self.capabilities,
                "capability",
            ),
        )

        if not isinstance(
            self.availability,
            ResourceEvidenceState,
        ):
            raise TypeError(
                "availability must be "
                "ResourceEvidenceState."
            )

        if not isinstance(
            self.locality,
            ResourceLocality,
        ):
            raise TypeError(
                "locality must be "
                "ResourceLocality."
            )

        for name in (
            "evidence_quality",
            "reliability",
            "privacy_score",
        ):
            object.__setattr__(
                self,
                name,
                _bounded_score(
                    getattr(
                        self,
                        name,
                    ),
                    name,
                ),
            )

        for name in (
            "cost_units",
            "latency_ms",
        ):
            object.__setattr__(
                self,
                name,
                _nonnegative_int(
                    getattr(
                        self,
                        name,
                    ),
                    name,
                ),
            )

        for name in (
            "provider_ref",
            "model_ref",
            "runtime_ref",
        ):
            object.__setattr__(
                self,
                name,
                _optional_text(
                    getattr(
                        self,
                        name,
                    ),
                    name,
                ),
            )

        object.__setattr__(
            self,
            "candidate_id",
            _stable_id(
                "IRC",
                {
                    "resource_id": (
                        self.resource_id
                    ),
                    "capabilities": list(
                        self.capabilities
                    ),
                    "availability": (
                        self.availability.value
                    ),
                    "evidence_quality": (
                        self.evidence_quality
                    ),
                    "reliability": (
                        self.reliability
                    ),
                    "privacy_score": (
                        self.privacy_score
                    ),
                    "cost_units": (
                        self.cost_units
                    ),
                    "latency_ms": (
                        self.latency_ms
                    ),
                    "locality": (
                        self.locality.value
                    ),
                    "provider_ref": (
                        self.provider_ref
                    ),
                    "model_ref": (
                        self.model_ref
                    ),
                    "runtime_ref": (
                        self.runtime_ref
                    ),
                },
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class ResourceSelectionPolicy:
    mission_contract_id: str

    constraint_refs: tuple[
        str,
        ...,
    ]

    min_evidence_quality: float
    min_reliability: float
    min_privacy_score: float

    max_cost_units: int
    max_latency_ms: int

    require_local: bool = False

    policy_id: str = field(
        init=False
    )

    def __post_init__(
        self,
    ) -> None:
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
            "min_evidence_quality",
            "min_reliability",
            "min_privacy_score",
        ):
            object.__setattr__(
                self,
                name,
                _bounded_score(
                    getattr(
                        self,
                        name,
                    ),
                    name,
                ),
            )

        for name in (
            "max_cost_units",
            "max_latency_ms",
        ):
            object.__setattr__(
                self,
                name,
                _nonnegative_int(
                    getattr(
                        self,
                        name,
                    ),
                    name,
                ),
            )

        if not isinstance(
            self.require_local,
            bool,
        ):
            raise TypeError(
                "require_local must be bool."
            )

        object.__setattr__(
            self,
            "policy_id",
            _stable_id(
                "RSP",
                {
                    "mission_contract_id": (
                        self.mission_contract_id
                    ),
                    "constraint_refs": list(
                        self.constraint_refs
                    ),
                    "min_evidence_quality": (
                        self.min_evidence_quality
                    ),
                    "min_reliability": (
                        self.min_reliability
                    ),
                    "min_privacy_score": (
                        self.min_privacy_score
                    ),
                    "max_cost_units": (
                        self.max_cost_units
                    ),
                    "max_latency_ms": (
                        self.max_latency_ms
                    ),
                    "require_local": (
                        self.require_local
                    ),
                },
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class CapabilityResourceBinding:
    capability_id: str
    resource_id: str
    candidate_id: str

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "capability_id",
            "resource_id",
            "candidate_id",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(
                        self,
                        name,
                    ),
                    name,
                ),
            )

    def to_dict(
        self,
    ) -> dict[str, str]:
        return {
            "capability_id": (
                self.capability_id
            ),
            "resource_id": (
                self.resource_id
            ),
            "candidate_id": (
                self.candidate_id
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedResourceSelection:
    capability_graph_id: str
    policy_id: str

    bindings: tuple[
        CapabilityResourceBinding,
        ...,
    ]

    selection_id: str = field(
        init=False
    )

    activation_authorized: bool = False
    execution_authorized: bool = False

    provider_authority_granted: bool = False
    model_authority_granted: bool = False
    runtime_authority_granted: bool = False

    mission_authority_transferred: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "capability_graph_id",
            _required_text(
                self.capability_graph_id,
                "capability_graph_id",
            ),
        )

        object.__setattr__(
            self,
            "policy_id",
            _required_text(
                self.policy_id,
                "policy_id",
            ),
        )

        raw = tuple(
            self.bindings
        )

        if not raw:
            raise ResourceSelectionIncompleteError(
                "Resource selection "
                "must not be empty."
            )

        if not all(
            isinstance(
                item,
                CapabilityResourceBinding,
            )
            for item in raw
        ):
            raise TypeError(
                "bindings must contain "
                "CapabilityResourceBinding only."
            )

        rows = tuple(
            sorted(
                raw,
                key=lambda item: (
                    item.capability_id
                ),
            )
        )

        capabilities = [
            item.capability_id
            for item in rows
        ]

        if len(capabilities) != len(
            set(capabilities)
        ):
            raise CapabilityResourceMarketInvariantError(
                "Resource selection "
                "must bind each capability once."
            )

        object.__setattr__(
            self,
            "bindings",
            rows,
        )

        for name in (
            "activation_authorized",
            "execution_authorized",
            "provider_authority_granted",
            "model_authority_granted",
            "runtime_authority_granted",
            "mission_authority_transferred",
            "system_truth_asserted",
        ):
            if getattr(
                self,
                name,
            ) is not False:
                raise CapabilityResourceMarketInvariantError(
                    "Resource selection cannot "
                    f"assert {name}."
                )

        object.__setattr__(
            self,
            "selection_id",
            _stable_id(
                "GRS",
                {
                    "capability_graph_id": (
                        self.capability_graph_id
                    ),
                    "policy_id": (
                        self.policy_id
                    ),
                    "bindings": [
                        item.to_dict()
                        for item in rows
                    ],
                },
            ),
        )

    @property
    def selected_resource_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    item.resource_id
                    for item in self.bindings
                }
            )
        )


class GovernedCapabilityResourceMarket:
    @staticmethod
    def synthesize_capability_graph(
        demand: MissionCapabilityDemand,
    ) -> MissionCapabilityGraph:
        if not isinstance(
            demand,
            MissionCapabilityDemand,
        ):
            raise TypeError(
                "demand must be "
                "MissionCapabilityDemand."
            )

        contracts = tuple(
            GenericCapabilityContract(
                capability_id=(
                    item.capability_id
                ),
                matched_rule_ids=(
                    item.matched_rule_ids
                ),
                rationales=(
                    item.rationales
                ),
            )
            for item in demand.demands
        )

        return MissionCapabilityGraph(
            mission_contract_id=(
                demand.contract_id
            ),
            demand_id=demand.demand_id,
            contracts=contracts,
        )

    @staticmethod
    def select(
        graph: MissionCapabilityGraph,
        candidates: Iterable[
            IntelligenceResourceCandidate
        ],
        policy: ResourceSelectionPolicy,
    ) -> GovernedResourceSelection:
        if not isinstance(
            graph,
            MissionCapabilityGraph,
        ):
            raise TypeError(
                "graph must be "
                "MissionCapabilityGraph."
            )

        if not isinstance(
            policy,
            ResourceSelectionPolicy,
        ):
            raise TypeError(
                "policy must be "
                "ResourceSelectionPolicy."
            )

        if (
            policy.mission_contract_id
            != graph.mission_contract_id
        ):
            raise CapabilityResourceMarketInvariantError(
                "Selection policy is not "
                "bound to the capability "
                "graph mission contract."
            )

        rows = tuple(
            candidates
        )

        if not rows:
            raise ResourceSelectionIncompleteError(
                "Resource selection requires "
                "resource candidates."
            )

        if not all(
            isinstance(
                item,
                IntelligenceResourceCandidate,
            )
            for item in rows
        ):
            raise TypeError(
                "candidates must contain "
                "IntelligenceResourceCandidate only."
            )

        resource_ids = [
            item.resource_id
            for item in rows
        ]

        if len(resource_ids) != len(
            set(resource_ids)
        ):
            raise CapabilityResourceMarketInvariantError(
                "Resource candidate IDs "
                "must be unique."
            )

        bindings = []

        for capability in graph.capability_ids:
            eligible = [
                item
                for item in rows
                if (
                    capability
                    in item.capabilities
                    and item.availability
                    is ResourceEvidenceState.PASS
                    and item.evidence_quality
                    >= policy.min_evidence_quality
                    and item.reliability
                    >= policy.min_reliability
                    and item.privacy_score
                    >= policy.min_privacy_score
                    and item.cost_units
                    <= policy.max_cost_units
                    and item.latency_ms
                    <= policy.max_latency_ms
                    and (
                        not policy.require_local
                        or item.locality
                        is ResourceLocality.LOCAL
                    )
                )
            ]

            if not eligible:
                raise ResourceSelectionIncompleteError(
                    "No eligible intelligence "
                    "resource for capability: "
                    + capability
                )

            eligible.sort(
                key=lambda item: (
                    -item.evidence_quality,
                    -item.reliability,
                    -item.privacy_score,
                    item.cost_units,
                    item.latency_ms,
                    item.resource_id,
                    item.candidate_id,
                )
            )

            selected = eligible[0]

            bindings.append(
                CapabilityResourceBinding(
                    capability_id=capability,
                    resource_id=(
                        selected.resource_id
                    ),
                    candidate_id=(
                        selected.candidate_id
                    ),
                )
            )

        return GovernedResourceSelection(
            capability_graph_id=(
                graph.graph_id
            ),
            policy_id=(
                policy.policy_id
            ),
            bindings=tuple(
                bindings
            ),
        )


__all__ = [
    "GOVERNED_CAPABILITY_RESOURCE_MARKET_VERSION",
    "CapabilityResourceMarketInvariantError",
    "ResourceSelectionIncompleteError",
    "ResourceEvidenceState",
    "ResourceLocality",
    "GenericCapabilityContract",
    "MissionCapabilityGraph",
    "IntelligenceResourceCandidate",
    "ResourceSelectionPolicy",
    "CapabilityResourceBinding",
    "GovernedResourceSelection",
    "GovernedCapabilityResourceMarket",
]
