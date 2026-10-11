from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Iterable

from maestro.orchestration.governed_mission_plan import (
    GovernedMissionPlan,
    GovernedPlanValidation,
    MissionPlanNode,
    PlanValidationState,
)


GOVERNED_EXECUTION_ROUTING_VERSION = 1


class ExecutionRoutingInvariantError(
    ValueError
):
    pass


class ExecutionRoutingIncompleteError(
    ExecutionRoutingInvariantError
):
    pass


class RoutingEvidenceState(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class WorkerLocality(StrEnum):
    LOCAL = "LOCAL"
    DISTRIBUTED = "DISTRIBUTED"


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
        raise ExecutionRoutingInvariantError(
            f"{name} must not be empty."
        )

    if "\x00" in value:
        raise ExecutionRoutingInvariantError(
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
        raise ExecutionRoutingInvariantError(
            f"{name} must not be empty."
        )

    if len(rows) != len(set(rows)):
        raise ExecutionRoutingInvariantError(
            f"{name} values must be unique."
        )

    return rows


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


def _idempotency_key(
    plan_id: str,
    node: MissionPlanNode,
) -> str:
    return _stable_id(
        "EXE",
        {
            "plan_id": plan_id,
            "node_id": node.node_id,
            "capability_id": (
                node.capability_id
            ),
            "council_id": (
                node.council_id
            ),
            "resource_id": (
                node.resource_id
            ),
        },
    )


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionAuthorizationEvidence:
    plan_id: str
    validation_id: str

    ex_authorization: RoutingEvidenceState
    effect_authorization: RoutingEvidenceState

    evidence_source_ref: str

    evidence_id: str = field(
        init=False
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "plan_id",
            _required_text(
                self.plan_id,
                "plan_id",
            ),
        )

        object.__setattr__(
            self,
            "validation_id",
            _required_text(
                self.validation_id,
                "validation_id",
            ),
        )

        for name in (
            "ex_authorization",
            "effect_authorization",
        ):
            if not isinstance(
                getattr(self, name),
                RoutingEvidenceState,
            ):
                raise TypeError(
                    f"{name} must be "
                    "RoutingEvidenceState."
                )

        object.__setattr__(
            self,
            "evidence_source_ref",
            _required_text(
                self.evidence_source_ref,
                "evidence_source_ref",
            ),
        )

        object.__setattr__(
            self,
            "evidence_id",
            _stable_id(
                "EAE",
                {
                    "plan_id": self.plan_id,
                    "validation_id": (
                        self.validation_id
                    ),
                    "ex_authorization": (
                        self.ex_authorization.value
                    ),
                    "effect_authorization": (
                        self.effect_authorization.value
                    ),
                    "evidence_source_ref": (
                        self.evidence_source_ref
                    ),
                },
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionRoute:
    node_id: str
    capability_id: str
    council_id: str
    resource_id: str
    idempotency_key: str

    route_id: str = field(
        init=False
    )

    adapter_authority_granted: bool = False
    provider_authority_granted: bool = False
    model_authority_granted: bool = False
    worker_authority_granted: bool = False
    mission_authority_transferred: bool = False

    def __post_init__(self) -> None:
        for name in (
            "node_id",
            "capability_id",
            "council_id",
            "resource_id",
            "idempotency_key",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(self, name),
                    name,
                ),
            )

        for name in (
            "adapter_authority_granted",
            "provider_authority_granted",
            "model_authority_granted",
            "worker_authority_granted",
            "mission_authority_transferred",
        ):
            if getattr(self, name) is not False:
                raise ExecutionRoutingInvariantError(
                    "Execution route cannot "
                    f"assert {name}."
                )

        object.__setattr__(
            self,
            "route_id",
            _stable_id(
                "EXR",
                {
                    "node_id": self.node_id,
                    "capability_id": (
                        self.capability_id
                    ),
                    "council_id": (
                        self.council_id
                    ),
                    "resource_id": (
                        self.resource_id
                    ),
                    "idempotency_key": (
                        self.idempotency_key
                    ),
                },
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "route_id": self.route_id,
            "node_id": self.node_id,
            "capability_id": (
                self.capability_id
            ),
            "council_id": self.council_id,
            "resource_id": self.resource_id,
            "idempotency_key": (
                self.idempotency_key
            ),
            "adapter_authority_granted": False,
            "provider_authority_granted": False,
            "model_authority_granted": False,
            "worker_authority_granted": False,
            "mission_authority_transferred": False,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionWave:
    wave_index: int
    route_ids: tuple[str, ...]
    node_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            not isinstance(
                self.wave_index,
                int,
            )
            or isinstance(
                self.wave_index,
                bool,
            )
            or self.wave_index < 1
        ):
            raise ExecutionRoutingInvariantError(
                "wave_index must be >= 1."
            )

        object.__setattr__(
            self,
            "route_ids",
            _normalized_tuple(
                self.route_ids,
                "route_id",
            ),
        )

        object.__setattr__(
            self,
            "node_ids",
            _normalized_tuple(
                self.node_ids,
                "node_id",
            ),
        )

        if (
            len(self.route_ids)
            != len(self.node_ids)
        ):
            raise ExecutionRoutingInvariantError(
                "Execution wave route/node "
                "cardinality mismatch."
            )


@dataclass(
    frozen=True,
    slots=True,
)
class DistributedWorkerEvidence:
    worker_id: str
    node_id: str

    councils: tuple[str, ...]
    capabilities: tuple[str, ...]

    locality: WorkerLocality

    online: RoutingEvidenceState
    lease_valid: RoutingEvidenceState
    duplicate_guard: RoutingEvidenceState
    recovery_ready: RoutingEvidenceState

    leased_plan_id: str
    leased_node_ids: tuple[str, ...]

    load_milli: int
    max_active_routes: int
    current_active_routes: int

    evidence_source_ref: str

    worker_evidence_id: str = field(
        init=False
    )

    def __post_init__(self) -> None:
        for name in (
            "worker_id",
            "node_id",
            "leased_plan_id",
            "evidence_source_ref",
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
            "councils",
            _normalized_tuple(
                self.councils,
                "council",
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

        object.__setattr__(
            self,
            "leased_node_ids",
            _normalized_tuple(
                self.leased_node_ids,
                "leased_node_id",
            ),
        )

        if not isinstance(
            self.locality,
            WorkerLocality,
        ):
            raise TypeError(
                "locality must be "
                "WorkerLocality."
            )

        for name in (
            "online",
            "lease_valid",
            "duplicate_guard",
            "recovery_ready",
        ):
            if not isinstance(
                getattr(self, name),
                RoutingEvidenceState,
            ):
                raise TypeError(
                    f"{name} must be "
                    "RoutingEvidenceState."
                )

        for name in (
            "load_milli",
            "max_active_routes",
            "current_active_routes",
        ):
            value = getattr(
                self,
                name,
            )

            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
            ):
                raise ExecutionRoutingInvariantError(
                    f"{name} must be >= 0."
                )

        if self.load_milli > 1000:
            raise ExecutionRoutingInvariantError(
                "load_milli must be <= 1000."
            )

        if self.max_active_routes < 1:
            raise ExecutionRoutingInvariantError(
                "max_active_routes must be >= 1."
            )

        if (
            self.current_active_routes
            > self.max_active_routes
        ):
            raise ExecutionRoutingInvariantError(
                "current_active_routes exceeds "
                "worker capacity."
            )

        object.__setattr__(
            self,
            "worker_evidence_id",
            _stable_id(
                "DWE",
                {
                    "worker_id": (
                        self.worker_id
                    ),
                    "node_id": self.node_id,
                    "councils": list(
                        self.councils
                    ),
                    "capabilities": list(
                        self.capabilities
                    ),
                    "locality": (
                        self.locality.value
                    ),
                    "online": (
                        self.online.value
                    ),
                    "lease_valid": (
                        self.lease_valid.value
                    ),
                    "duplicate_guard": (
                        self.duplicate_guard.value
                    ),
                    "recovery_ready": (
                        self.recovery_ready.value
                    ),
                    "leased_plan_id": (
                        self.leased_plan_id
                    ),
                    "leased_node_ids": list(
                        self.leased_node_ids
                    ),
                    "load_milli": (
                        self.load_milli
                    ),
                    "max_active_routes": (
                        self.max_active_routes
                    ),
                    "current_active_routes": (
                        self.current_active_routes
                    ),
                    "evidence_source_ref": (
                        self.evidence_source_ref
                    ),
                },
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class WorkerPlacement:
    route_id: str
    node_id: str
    worker_id: str
    worker_node_id: str
    locality: WorkerLocality
    worker_evidence_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "route_id": self.route_id,
            "node_id": self.node_id,
            "worker_id": self.worker_id,
            "worker_node_id": (
                self.worker_node_id
            ),
            "locality": self.locality.value,
            "worker_evidence_id": (
                self.worker_evidence_id
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedExecutionRoutingPlan:
    plan_id: str
    validation_id: str
    authorization_evidence_id: str

    routes: tuple[
        ExecutionRoute,
        ...,
    ]

    waves: tuple[
        ExecutionWave,
        ...,
    ]

    placements: tuple[
        WorkerPlacement,
        ...,
    ]

    routing_plan_id: str = field(
        init=False
    )

    ex_authority_observed: bool = True

    adapter_authority_granted: bool = False
    provider_authority_granted: bool = False
    model_authority_granted: bool = False
    worker_authority_granted: bool = False
    mission_authority_transferred: bool = False
    system_truth_asserted: bool = False

    execution_performed: bool = False

    def __post_init__(self) -> None:
        for name in (
            "plan_id",
            "validation_id",
            "authorization_evidence_id",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(self, name),
                    name,
                ),
            )

        routes = tuple(
            sorted(
                self.routes,
                key=lambda item: (
                    item.node_id
                ),
            )
        )

        if not routes:
            raise ExecutionRoutingIncompleteError(
                "Execution routing plan "
                "must contain routes."
            )

        route_ids = [
            item.route_id
            for item in routes
        ]

        node_ids = [
            item.node_id
            for item in routes
        ]

        if len(route_ids) != len(
            set(route_ids)
        ):
            raise ExecutionRoutingInvariantError(
                "Route IDs must be unique."
            )

        if len(node_ids) != len(
            set(node_ids)
        ):
            raise ExecutionRoutingInvariantError(
                "Each plan node must route once."
            )

        waves = tuple(
            sorted(
                self.waves,
                key=lambda item: (
                    item.wave_index
                ),
            )
        )

        if not waves:
            raise ExecutionRoutingIncompleteError(
                "Execution routing plan "
                "must contain waves."
            )

        if tuple(
            item.wave_index
            for item in waves
        ) != tuple(
            range(
                1,
                len(waves) + 1,
            )
        ):
            raise ExecutionRoutingInvariantError(
                "Execution waves must be "
                "contiguous from 1."
            )

        waved_nodes = tuple(
            node
            for wave in waves
            for node in wave.node_ids
        )

        if (
            set(waved_nodes)
            != set(node_ids)
            or len(waved_nodes)
            != len(node_ids)
        ):
            raise ExecutionRoutingInvariantError(
                "Execution waves must cover "
                "each routed node exactly once."
            )

        placements = tuple(
            sorted(
                self.placements,
                key=lambda item: (
                    item.node_id
                ),
            )
        )

        placed_nodes = [
            item.node_id
            for item in placements
        ]

        if (
            set(placed_nodes)
            != set(node_ids)
            or len(placed_nodes)
            != len(node_ids)
        ):
            raise ExecutionRoutingInvariantError(
                "Worker placement must cover "
                "each routed node exactly once."
            )

        if self.ex_authority_observed is not True:
            raise ExecutionRoutingInvariantError(
                "Execution routing requires "
                "observed EX authority."
            )

        for name in (
            "adapter_authority_granted",
            "provider_authority_granted",
            "model_authority_granted",
            "worker_authority_granted",
            "mission_authority_transferred",
            "system_truth_asserted",
            "execution_performed",
        ):
            if getattr(self, name) is not False:
                raise ExecutionRoutingInvariantError(
                    "Routing plan cannot "
                    f"assert {name}."
                )

        object.__setattr__(
            self,
            "routes",
            routes,
        )

        object.__setattr__(
            self,
            "waves",
            waves,
        )

        object.__setattr__(
            self,
            "placements",
            placements,
        )

        object.__setattr__(
            self,
            "routing_plan_id",
            _stable_id(
                "GER",
                {
                    "plan_id": self.plan_id,
                    "validation_id": (
                        self.validation_id
                    ),
                    "authorization_evidence_id": (
                        self
                        .authorization_evidence_id
                    ),
                    "routes": [
                        item.to_dict()
                        for item in routes
                    ],
                    "waves": [
                        {
                            "wave_index": (
                                item.wave_index
                            ),
                            "route_ids": list(
                                item.route_ids
                            ),
                            "node_ids": list(
                                item.node_ids
                            ),
                        }
                        for item in waves
                    ],
                    "placements": [
                        item.to_dict()
                        for item in placements
                    ],
                },
            ),
        )


class GovernedExecutionRouter:
    @staticmethod
    def idempotency_key(
        plan: GovernedMissionPlan,
        node: MissionPlanNode,
    ) -> str:
        if not isinstance(
            plan,
            GovernedMissionPlan,
        ):
            raise TypeError(
                "plan must be GovernedMissionPlan."
            )

        if not isinstance(
            node,
            MissionPlanNode,
        ):
            raise TypeError(
                "node must be MissionPlanNode."
            )

        return _idempotency_key(
            plan.plan_id,
            node,
        )

    @staticmethod
    def build(
        plan: GovernedMissionPlan,
        validation: GovernedPlanValidation,
        authorization: ExecutionAuthorizationEvidence,
        workers: Iterable[
            DistributedWorkerEvidence
        ],
        *,
        max_parallelism: int,
    ) -> GovernedExecutionRoutingPlan:
        if not isinstance(
            plan,
            GovernedMissionPlan,
        ):
            raise TypeError(
                "plan must be GovernedMissionPlan."
            )

        if not isinstance(
            validation,
            GovernedPlanValidation,
        ):
            raise TypeError(
                "validation must be "
                "GovernedPlanValidation."
            )

        if not isinstance(
            authorization,
            ExecutionAuthorizationEvidence,
        ):
            raise TypeError(
                "authorization must be "
                "ExecutionAuthorizationEvidence."
            )

        if (
            not isinstance(
                max_parallelism,
                int,
            )
            or isinstance(
                max_parallelism,
                bool,
            )
            or max_parallelism < 1
        ):
            raise ExecutionRoutingInvariantError(
                "max_parallelism must be >= 1."
            )

        if (
            validation.plan.plan_id
            != plan.plan_id
            or validation.state
            is not PlanValidationState.ELIGIBLE
            or not validation.execution_eligible
        ):
            raise ExecutionRoutingIncompleteError(
                "Execution routing requires "
                "an execution-eligible "
                "validation bound to plan."
            )

        if (
            authorization.plan_id
            != plan.plan_id
            or authorization.validation_id
            != validation.validation_id
        ):
            raise ExecutionRoutingInvariantError(
                "Execution authorization "
                "evidence lineage mismatch."
            )

        if (
            authorization.ex_authorization
            is RoutingEvidenceState.FAIL
            or authorization.effect_authorization
            is RoutingEvidenceState.FAIL
        ):
            raise PermissionError(
                "Explicit execution/effect "
                "authorization failure."
            )

        if (
            authorization.ex_authorization
            is not RoutingEvidenceState.PASS
            or authorization.effect_authorization
            is not RoutingEvidenceState.PASS
        ):
            raise ExecutionRoutingIncompleteError(
                "Execution/effect authorization "
                "evidence is incomplete."
            )

        worker_rows = tuple(
            workers
        )

        if not worker_rows:
            raise ExecutionRoutingIncompleteError(
                "Execution routing requires "
                "worker evidence."
            )

        if not all(
            isinstance(
                item,
                DistributedWorkerEvidence,
            )
            for item in worker_rows
        ):
            raise TypeError(
                "workers must contain "
                "DistributedWorkerEvidence only."
            )

        worker_ids = [
            item.worker_id
            for item in worker_rows
        ]

        if len(worker_ids) != len(
            set(worker_ids)
        ):
            raise ExecutionRoutingInvariantError(
                "Worker IDs must be unique."
            )

        routes = tuple(
            ExecutionRoute(
                node_id=node.node_id,
                capability_id=(
                    node.capability_id
                ),
                council_id=(
                    node.council_id
                ),
                resource_id=(
                    node.resource_id
                ),
                idempotency_key=(
                    _idempotency_key(
                        plan.plan_id,
                        node,
                    )
                ),
            )
            for node in plan.nodes
        )

        route_by_node = {
            item.node_id: item
            for item in routes
        }

        node_by_id = {
            item.node_id: item
            for item in plan.nodes
        }

        remaining = set(
            node_by_id
        )

        completed: set[str] = set()
        waves: list[ExecutionWave] = []
        wave_index = 1

        while remaining:
            ready = tuple(
                sorted(
                    node_id
                    for node_id in remaining
                    if set(
                        node_by_id[
                            node_id
                        ].dependency_node_ids
                    ).issubset(
                        completed
                    )
                )
            )

            if not ready:
                raise ExecutionRoutingInvariantError(
                    "No dependency-safe "
                    "execution route available."
                )

            for start in range(
                0,
                len(ready),
                max_parallelism,
            ):
                chunk = ready[
                    start:
                    start + max_parallelism
                ]

                waves.append(
                    ExecutionWave(
                        wave_index=(
                            wave_index
                        ),
                        route_ids=tuple(
                            route_by_node[
                                node_id
                            ].route_id
                            for node_id
                            in chunk
                        ),
                        node_ids=chunk,
                    )
                )

                wave_index += 1

            completed.update(
                ready
            )
            remaining.difference_update(
                ready
            )

        placements = []

        for node in plan.nodes:
            eligible = []

            for worker in worker_rows:
                if (
                    worker.online
                    is not RoutingEvidenceState.PASS
                    or worker.lease_valid
                    is not RoutingEvidenceState.PASS
                    or worker.duplicate_guard
                    is not RoutingEvidenceState.PASS
                    or worker.recovery_ready
                    is not RoutingEvidenceState.PASS
                ):
                    continue

                if (
                    worker.leased_plan_id
                    != plan.plan_id
                    or node.node_id
                    not in worker.leased_node_ids
                ):
                    continue

                if (
                    node.council_id
                    not in worker.councils
                    or node.capability_id
                    not in worker.capabilities
                ):
                    continue

                if (
                    worker.current_active_routes
                    >= worker.max_active_routes
                ):
                    continue

                eligible.append(
                    worker
                )

            if not eligible:
                raise ExecutionRoutingIncompleteError(
                    "No lease-valid, "
                    "duplicate-guarded, "
                    "recovery-ready worker "
                    "for node: "
                    + node.node_id
                )

            eligible.sort(
                key=lambda item: (
                    item.load_milli,
                    item.locality.value,
                    item.node_id,
                    item.worker_id,
                )
            )

            selected = eligible[0]

            placements.append(
                WorkerPlacement(
                    route_id=(
                        route_by_node[
                            node.node_id
                        ].route_id
                    ),
                    node_id=node.node_id,
                    worker_id=(
                        selected.worker_id
                    ),
                    worker_node_id=(
                        selected.node_id
                    ),
                    locality=(
                        selected.locality
                    ),
                    worker_evidence_id=(
                        selected
                        .worker_evidence_id
                    ),
                )
            )

        return GovernedExecutionRoutingPlan(
            plan_id=plan.plan_id,
            validation_id=(
                validation.validation_id
            ),
            authorization_evidence_id=(
                authorization.evidence_id
            ),
            routes=routes,
            waves=tuple(waves),
            placements=tuple(
                placements
            ),
        )


__all__ = [
    "GOVERNED_EXECUTION_ROUTING_VERSION",
    "ExecutionRoutingInvariantError",
    "ExecutionRoutingIncompleteError",
    "RoutingEvidenceState",
    "WorkerLocality",
    "ExecutionAuthorizationEvidence",
    "ExecutionRoute",
    "ExecutionWave",
    "DistributedWorkerEvidence",
    "WorkerPlacement",
    "GovernedExecutionRoutingPlan",
    "GovernedExecutionRouter",
]
