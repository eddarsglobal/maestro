from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Iterable

from maestro.intelligence_market.governed_capability_resource_market import (
    GovernedCapabilityResourceMarket,
    IntelligenceResourceCandidate,
    MissionCapabilityGraph,
    ResourceSelectionIncompleteError,
    ResourceSelectionPolicy,
)
from maestro.orchestration.governed_execution_routing import (
    ExecutionRoute,
    GovernedExecutionRoutingPlan,
)
from maestro.orchestration.governed_mission_foundation import (
    MissionContract,
)
from maestro.orchestration.governed_mission_plan import (
    GovernedMissionPlan,
    MissionPlanNode,
)


GOVERNED_ADAPTIVE_MISSION_CLOSURE_VERSION = 1


class AdaptiveMissionClosureInvariantError(
    ValueError
):
    pass


class AdaptiveMissionClosureIncompleteError(
    AdaptiveMissionClosureInvariantError
):
    pass


class ClosureEvidenceState(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class RoutingFailureKind(StrEnum):
    RESOURCE_FAILURE = "RESOURCE_FAILURE"
    RESOURCE_DEGRADED = "RESOURCE_DEGRADED"
    CAPABILITY_LOSS = "CAPABILITY_LOSS"


class AdaptiveRoutingState(StrEnum):
    NO_CHANGE = "NO_CHANGE"
    REROUTE_PROPOSED = "REROUTE_PROPOSED"
    REPLAN_REQUIRED = "REPLAN_REQUIRED"
    UNKNOWN = "UNKNOWN"


class NodeClosureState(StrEnum):
    COMPLETE = "COMPLETE"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


class MissionVerdictState(StrEnum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
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
        raise AdaptiveMissionClosureInvariantError(
            f"{name} must not be empty."
        )

    if "\x00" in value:
        raise AdaptiveMissionClosureInvariantError(
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
        raise AdaptiveMissionClosureInvariantError(
            f"{name} must not be empty."
        )

    if len(rows) != len(set(rows)):
        raise AdaptiveMissionClosureInvariantError(
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


def _objective_fingerprint(
    contract: MissionContract,
) -> str:
    return _stable_id(
        "OBJ",
        {
            "contract_id": (
                contract.contract_id
            ),
            "objective": (
                contract.objective
            ),
        },
    )


@dataclass(
    frozen=True,
    slots=True,
)
class RouteFailureEvidence:
    routing_plan_id: str
    route_id: str
    node_id: str
    capability_id: str
    failed_resource_id: str

    failure_kind: RoutingFailureKind
    failure_detected: ClosureEvidenceState

    evidence_source_ref: str

    evidence_id: str = field(
        init=False
    )

    def __post_init__(self) -> None:
        for name in (
            "routing_plan_id",
            "route_id",
            "node_id",
            "capability_id",
            "failed_resource_id",
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

        if not isinstance(
            self.failure_kind,
            RoutingFailureKind,
        ):
            raise TypeError(
                "failure_kind must be "
                "RoutingFailureKind."
            )

        if not isinstance(
            self.failure_detected,
            ClosureEvidenceState,
        ):
            raise TypeError(
                "failure_detected must be "
                "ClosureEvidenceState."
            )

        object.__setattr__(
            self,
            "evidence_id",
            _stable_id(
                "RFE",
                {
                    "routing_plan_id": (
                        self.routing_plan_id
                    ),
                    "route_id": self.route_id,
                    "node_id": self.node_id,
                    "capability_id": (
                        self.capability_id
                    ),
                    "failed_resource_id": (
                        self.failed_resource_id
                    ),
                    "failure_kind": (
                        self.failure_kind.value
                    ),
                    "failure_detected": (
                        self.failure_detected.value
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
class GovernedAdaptiveRoutingDecision:
    mission_contract_id: str
    objective_fingerprint: str

    capability_graph_id: str
    routing_plan_id: str

    route_id: str
    node_id: str
    capability_id: str
    council_id: str

    previous_resource_id: str

    state: AdaptiveRoutingState

    replacement_resource_id: str | None
    replacement_candidate_id: str | None

    failure_evidence_id: str

    decision_id: str = field(
        init=False
    )

    objective_changed: bool = False
    council_changed: bool = False

    execution_requested: bool = False
    execution_authorized: bool = False
    effect_authorized: bool = False

    provider_authority_granted: bool = False
    model_authority_granted: bool = False
    resource_authority_granted: bool = False

    mission_state_transition_requested: bool = False
    system_truth_asserted: bool = False

    def __post_init__(self) -> None:
        for name in (
            "mission_contract_id",
            "objective_fingerprint",
            "capability_graph_id",
            "routing_plan_id",
            "route_id",
            "node_id",
            "capability_id",
            "council_id",
            "previous_resource_id",
            "failure_evidence_id",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(self, name),
                    name,
                ),
            )

        if not isinstance(
            self.state,
            AdaptiveRoutingState,
        ):
            raise TypeError(
                "state must be "
                "AdaptiveRoutingState."
            )

        for name in (
            "replacement_resource_id",
            "replacement_candidate_id",
        ):
            object.__setattr__(
                self,
                name,
                _optional_text(
                    getattr(self, name),
                    name,
                ),
            )

        if (
            self.state
            is AdaptiveRoutingState.REROUTE_PROPOSED
        ):
            if (
                self.replacement_resource_id
                is None
                or self.replacement_candidate_id
                is None
            ):
                raise AdaptiveMissionClosureInvariantError(
                    "REROUTE_PROPOSED requires "
                    "replacement resource evidence."
                )

            if (
                self.replacement_resource_id
                == self.previous_resource_id
            ):
                raise AdaptiveMissionClosureInvariantError(
                    "Reroute replacement cannot "
                    "reuse failed resource."
                )

        else:
            if (
                self.replacement_resource_id
                is not None
                or self.replacement_candidate_id
                is not None
            ):
                raise AdaptiveMissionClosureInvariantError(
                    "Replacement resource may "
                    "exist only for "
                    "REROUTE_PROPOSED."
                )

        for name in (
            "objective_changed",
            "council_changed",
            "execution_requested",
            "execution_authorized",
            "effect_authorized",
            "provider_authority_granted",
            "model_authority_granted",
            "resource_authority_granted",
            "mission_state_transition_requested",
            "system_truth_asserted",
        ):
            if getattr(self, name) is not False:
                raise AdaptiveMissionClosureInvariantError(
                    "Adaptive routing cannot "
                    f"assert {name}."
                )

        object.__setattr__(
            self,
            "decision_id",
            _stable_id(
                "ARD",
                {
                    "mission_contract_id": (
                        self.mission_contract_id
                    ),
                    "objective_fingerprint": (
                        self.objective_fingerprint
                    ),
                    "capability_graph_id": (
                        self.capability_graph_id
                    ),
                    "routing_plan_id": (
                        self.routing_plan_id
                    ),
                    "route_id": self.route_id,
                    "node_id": self.node_id,
                    "capability_id": (
                        self.capability_id
                    ),
                    "council_id": (
                        self.council_id
                    ),
                    "previous_resource_id": (
                        self.previous_resource_id
                    ),
                    "state": self.state.value,
                    "replacement_resource_id": (
                        self.replacement_resource_id
                    ),
                    "replacement_candidate_id": (
                        self.replacement_candidate_id
                    ),
                    "failure_evidence_id": (
                        self.failure_evidence_id
                    ),
                },
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class NodeExecutionClosureEvidence:
    plan_id: str
    routing_plan_id: str

    route_id: str
    node_id: str
    idempotency_key: str

    execution_state: ClosureEvidenceState

    output_ref: str | None

    provenance_refs: tuple[
        str,
        ...,
    ]

    execution_evidence_refs: tuple[
        str,
        ...,
    ]

    council_verdict_state: ClosureEvidenceState
    council_verdict_ref: str | None

    acceptance_evidence_keys: tuple[
        str,
        ...,
    ]

    evidence_source_ref: str

    evidence_id: str = field(
        init=False
    )

    def __post_init__(self) -> None:
        for name in (
            "plan_id",
            "routing_plan_id",
            "route_id",
            "node_id",
            "idempotency_key",
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

        if not isinstance(
            self.execution_state,
            ClosureEvidenceState,
        ):
            raise TypeError(
                "execution_state must be "
                "ClosureEvidenceState."
            )

        if not isinstance(
            self.council_verdict_state,
            ClosureEvidenceState,
        ):
            raise TypeError(
                "council_verdict_state must be "
                "ClosureEvidenceState."
            )

        object.__setattr__(
            self,
            "output_ref",
            _optional_text(
                self.output_ref,
                "output_ref",
            ),
        )

        object.__setattr__(
            self,
            "council_verdict_ref",
            _optional_text(
                self.council_verdict_ref,
                "council_verdict_ref",
            ),
        )

        for name in (
            "provenance_refs",
            "execution_evidence_refs",
            "acceptance_evidence_keys",
        ):
            object.__setattr__(
                self,
                name,
                _normalized_tuple(
                    getattr(self, name),
                    name,
                    require_nonempty=False,
                ),
            )

        object.__setattr__(
            self,
            "evidence_id",
            _stable_id(
                "NCE",
                {
                    "plan_id": self.plan_id,
                    "routing_plan_id": (
                        self.routing_plan_id
                    ),
                    "route_id": self.route_id,
                    "node_id": self.node_id,
                    "idempotency_key": (
                        self.idempotency_key
                    ),
                    "execution_state": (
                        self.execution_state.value
                    ),
                    "output_ref": self.output_ref,
                    "provenance_refs": list(
                        self.provenance_refs
                    ),
                    "execution_evidence_refs": list(
                        self.execution_evidence_refs
                    ),
                    "council_verdict_state": (
                        self
                        .council_verdict_state
                        .value
                    ),
                    "council_verdict_ref": (
                        self.council_verdict_ref
                    ),
                    "acceptance_evidence_keys": list(
                        self.acceptance_evidence_keys
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
class GovernedNodeClosure:
    plan_id: str
    routing_plan_id: str

    node_id: str
    route_id: str
    council_id: str
    capability_id: str
    resource_id: str

    evidence_id: str

    state: NodeClosureState
    reasons: tuple[str, ...]

    closure_id: str = field(
        init=False
    )

    downstream_completion_authorized: bool = False
    mission_close_authorized: bool = False
    learning_authorized: bool = False
    system_truth_asserted: bool = False

    def __post_init__(self) -> None:
        for name in (
            "plan_id",
            "routing_plan_id",
            "node_id",
            "route_id",
            "council_id",
            "capability_id",
            "resource_id",
            "evidence_id",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(self, name),
                    name,
                ),
            )

        if not isinstance(
            self.state,
            NodeClosureState,
        ):
            raise TypeError(
                "state must be "
                "NodeClosureState."
            )

        object.__setattr__(
            self,
            "reasons",
            _normalized_tuple(
                self.reasons,
                "reason",
            ),
        )

        for name in (
            "downstream_completion_authorized",
            "mission_close_authorized",
            "learning_authorized",
            "system_truth_asserted",
        ):
            if getattr(self, name) is not False:
                raise AdaptiveMissionClosureInvariantError(
                    "Node closure cannot "
                    f"assert {name}."
                )

        object.__setattr__(
            self,
            "closure_id",
            _stable_id(
                "GNC",
                {
                    "plan_id": self.plan_id,
                    "routing_plan_id": (
                        self.routing_plan_id
                    ),
                    "node_id": self.node_id,
                    "route_id": self.route_id,
                    "council_id": (
                        self.council_id
                    ),
                    "capability_id": (
                        self.capability_id
                    ),
                    "resource_id": (
                        self.resource_id
                    ),
                    "evidence_id": (
                        self.evidence_id
                    ),
                    "state": self.state.value,
                    "reasons": list(
                        self.reasons
                    ),
                },
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class CouncilMissionVerdictEvidence:
    council_id: str
    state: ClosureEvidenceState
    verdict_ref: str | None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "council_id",
            _required_text(
                self.council_id,
                "council_id",
            ),
        )

        if not isinstance(
            self.state,
            ClosureEvidenceState,
        ):
            raise TypeError(
                "state must be "
                "ClosureEvidenceState."
            )

        object.__setattr__(
            self,
            "verdict_ref",
            _optional_text(
                self.verdict_ref,
                "verdict_ref",
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class MissionVerdictEvidence:
    plan_id: str

    node_closures: tuple[
        GovernedNodeClosure,
        ...,
    ]

    acceptance_criteria_validated: tuple[
        str,
        ...,
    ]

    council_verdicts: tuple[
        CouncilMissionVerdictEvidence,
        ...,
    ]

    ay_system_verdict_state: ClosureEvidenceState
    ay_system_verdict_ref: str | None

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

        raw_closures = tuple(
            self.node_closures
        )

        if not all(
            isinstance(
                item,
                GovernedNodeClosure,
            )
            for item in raw_closures
        ):
            raise TypeError(
                "node_closures must contain "
                "GovernedNodeClosure only."
            )

        closures = tuple(
            sorted(
                raw_closures,
                key=lambda item: (
                    item.node_id
                ),
            )
        )

        node_ids = [
            item.node_id
            for item in closures
        ]

        if len(node_ids) != len(
            set(node_ids)
        ):
            raise AdaptiveMissionClosureInvariantError(
                "Mission verdict evidence "
                "contains duplicate node closures."
            )

        object.__setattr__(
            self,
            "node_closures",
            closures,
        )

        object.__setattr__(
            self,
            "acceptance_criteria_validated",
            _normalized_tuple(
                self.acceptance_criteria_validated,
                "acceptance_criterion",
                require_nonempty=False,
            ),
        )

        raw_verdicts = tuple(
            self.council_verdicts
        )

        if not all(
            isinstance(
                item,
                CouncilMissionVerdictEvidence,
            )
            for item in raw_verdicts
        ):
            raise TypeError(
                "council_verdicts must contain "
                "CouncilMissionVerdictEvidence only."
            )

        verdicts = tuple(
            sorted(
                raw_verdicts,
                key=lambda item: (
                    item.council_id
                ),
            )
        )

        council_ids = [
            item.council_id
            for item in verdicts
        ]

        if len(council_ids) != len(
            set(council_ids)
        ):
            raise AdaptiveMissionClosureInvariantError(
                "Council mission verdicts "
                "must be unique."
            )

        object.__setattr__(
            self,
            "council_verdicts",
            verdicts,
        )

        if not isinstance(
            self.ay_system_verdict_state,
            ClosureEvidenceState,
        ):
            raise TypeError(
                "ay_system_verdict_state must "
                "be ClosureEvidenceState."
            )

        object.__setattr__(
            self,
            "ay_system_verdict_ref",
            _optional_text(
                self.ay_system_verdict_ref,
                "ay_system_verdict_ref",
            ),
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
                "MVE",
                {
                    "plan_id": self.plan_id,
                    "node_closure_ids": [
                        item.closure_id
                        for item in closures
                    ],
                    "acceptance_criteria_validated": list(
                        self.acceptance_criteria_validated
                    ),
                    "council_verdicts": [
                        {
                            "council_id": (
                                item.council_id
                            ),
                            "state": (
                                item.state.value
                            ),
                            "verdict_ref": (
                                item.verdict_ref
                            ),
                        }
                        for item in verdicts
                    ],
                    "ay_system_verdict_state": (
                        self
                        .ay_system_verdict_state
                        .value
                    ),
                    "ay_system_verdict_ref": (
                        self.ay_system_verdict_ref
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
class GovernedMissionVerdict:
    plan_id: str
    evidence_id: str

    state: MissionVerdictState
    reasons: tuple[str, ...]

    verdict_id: str = field(
        init=False
    )

    mission_close_authorized: bool = False
    mission_state_transition_requested: bool = False
    durable_commit_authorized: bool = False
    learning_authorized: bool = False
    promotion_authorized: bool = False
    system_truth_asserted: bool = False

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
            "evidence_id",
            _required_text(
                self.evidence_id,
                "evidence_id",
            ),
        )

        if not isinstance(
            self.state,
            MissionVerdictState,
        ):
            raise TypeError(
                "state must be "
                "MissionVerdictState."
            )

        object.__setattr__(
            self,
            "reasons",
            _normalized_tuple(
                self.reasons,
                "reason",
            ),
        )

        for name in (
            "mission_close_authorized",
            "mission_state_transition_requested",
            "durable_commit_authorized",
            "learning_authorized",
            "promotion_authorized",
            "system_truth_asserted",
        ):
            if getattr(self, name) is not False:
                raise AdaptiveMissionClosureInvariantError(
                    "Mission verdict cannot "
                    f"assert {name}."
                )

        object.__setattr__(
            self,
            "verdict_id",
            _stable_id(
                "GMV",
                {
                    "plan_id": self.plan_id,
                    "evidence_id": (
                        self.evidence_id
                    ),
                    "state": self.state.value,
                    "reasons": list(
                        self.reasons
                    ),
                },
            ),
        )

    @property
    def accepted(self) -> bool:
        return (
            self.state
            is MissionVerdictState.ACCEPTED
        )


class GovernedAdaptiveMissionClosure:
    @staticmethod
    def assess_reroute(
        contract: MissionContract,
        capability_graph: MissionCapabilityGraph,
        routing_plan: GovernedExecutionRoutingPlan,
        failure: RouteFailureEvidence,
        candidates: Iterable[
            IntelligenceResourceCandidate
        ],
        policy: ResourceSelectionPolicy,
    ) -> GovernedAdaptiveRoutingDecision:
        if not isinstance(
            contract,
            MissionContract,
        ):
            raise TypeError(
                "contract must be MissionContract."
            )

        if not isinstance(
            capability_graph,
            MissionCapabilityGraph,
        ):
            raise TypeError(
                "capability_graph must be "
                "MissionCapabilityGraph."
            )

        if not isinstance(
            routing_plan,
            GovernedExecutionRoutingPlan,
        ):
            raise TypeError(
                "routing_plan must be "
                "GovernedExecutionRoutingPlan."
            )

        if not isinstance(
            failure,
            RouteFailureEvidence,
        ):
            raise TypeError(
                "failure must be "
                "RouteFailureEvidence."
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
            capability_graph
            .mission_contract_id
            != contract.contract_id
            or policy.mission_contract_id
            != contract.contract_id
        ):
            raise AdaptiveMissionClosureInvariantError(
                "Adaptive routing must bind "
                "the exact mission contract."
            )

        if (
            failure.routing_plan_id
            != routing_plan.routing_plan_id
        ):
            raise AdaptiveMissionClosureInvariantError(
                "Failure evidence is not "
                "bound to routing plan."
            )

        route = next(
            (
                item
                for item in routing_plan.routes
                if item.route_id
                == failure.route_id
            ),
            None,
        )

        if route is None:
            raise AdaptiveMissionClosureInvariantError(
                "Failure evidence references "
                "unknown route."
            )

        if (
            route.node_id
            != failure.node_id
            or route.capability_id
            != failure.capability_id
            or route.resource_id
            != failure.failed_resource_id
        ):
            raise AdaptiveMissionClosureInvariantError(
                "Failure evidence does not "
                "match routed node/resource."
            )

        objective = _objective_fingerprint(
            contract
        )

        if (
            failure.failure_detected
            is ClosureEvidenceState.FAIL
        ):
            return GovernedAdaptiveRoutingDecision(
                mission_contract_id=(
                    contract.contract_id
                ),
                objective_fingerprint=objective,
                capability_graph_id=(
                    capability_graph.graph_id
                ),
                routing_plan_id=(
                    routing_plan.routing_plan_id
                ),
                route_id=route.route_id,
                node_id=route.node_id,
                capability_id=(
                    route.capability_id
                ),
                council_id=(
                    route.council_id
                ),
                previous_resource_id=(
                    route.resource_id
                ),
                state=(
                    AdaptiveRoutingState
                    .NO_CHANGE
                ),
                replacement_resource_id=None,
                replacement_candidate_id=None,
                failure_evidence_id=(
                    failure.evidence_id
                ),
            )

        if (
            failure.failure_detected
            is ClosureEvidenceState.UNKNOWN
        ):
            return GovernedAdaptiveRoutingDecision(
                mission_contract_id=(
                    contract.contract_id
                ),
                objective_fingerprint=objective,
                capability_graph_id=(
                    capability_graph.graph_id
                ),
                routing_plan_id=(
                    routing_plan.routing_plan_id
                ),
                route_id=route.route_id,
                node_id=route.node_id,
                capability_id=(
                    route.capability_id
                ),
                council_id=(
                    route.council_id
                ),
                previous_resource_id=(
                    route.resource_id
                ),
                state=(
                    AdaptiveRoutingState
                    .UNKNOWN
                ),
                replacement_resource_id=None,
                replacement_candidate_id=None,
                failure_evidence_id=(
                    failure.evidence_id
                ),
            )

        capability_contract = next(
            (
                item
                for item
                in capability_graph.contracts
                if item.capability_id
                == route.capability_id
            ),
            None,
        )

        if capability_contract is None:
            raise AdaptiveMissionClosureInvariantError(
                "Routed capability does not "
                "exist in capability graph."
            )

        replacement_candidates = tuple(
            item
            for item in candidates
            if (
                item.resource_id
                != route.resource_id
            )
        )

        if not replacement_candidates:
            return GovernedAdaptiveRoutingDecision(
                mission_contract_id=(
                    contract.contract_id
                ),
                objective_fingerprint=objective,
                capability_graph_id=(
                    capability_graph.graph_id
                ),
                routing_plan_id=(
                    routing_plan.routing_plan_id
                ),
                route_id=route.route_id,
                node_id=route.node_id,
                capability_id=(
                    route.capability_id
                ),
                council_id=(
                    route.council_id
                ),
                previous_resource_id=(
                    route.resource_id
                ),
                state=(
                    AdaptiveRoutingState
                    .REPLAN_REQUIRED
                ),
                replacement_resource_id=None,
                replacement_candidate_id=None,
                failure_evidence_id=(
                    failure.evidence_id
                ),
            )

        single_capability_graph = (
            MissionCapabilityGraph(
                mission_contract_id=(
                    capability_graph
                    .mission_contract_id
                ),
                demand_id=(
                    capability_graph.demand_id
                ),
                contracts=(
                    capability_contract,
                ),
            )
        )

        try:
            replacement = (
                GovernedCapabilityResourceMarket
                .select(
                    single_capability_graph,
                    replacement_candidates,
                    policy,
                )
            )
        except ResourceSelectionIncompleteError:
            return GovernedAdaptiveRoutingDecision(
                mission_contract_id=(
                    contract.contract_id
                ),
                objective_fingerprint=objective,
                capability_graph_id=(
                    capability_graph.graph_id
                ),
                routing_plan_id=(
                    routing_plan.routing_plan_id
                ),
                route_id=route.route_id,
                node_id=route.node_id,
                capability_id=(
                    route.capability_id
                ),
                council_id=(
                    route.council_id
                ),
                previous_resource_id=(
                    route.resource_id
                ),
                state=(
                    AdaptiveRoutingState
                    .REPLAN_REQUIRED
                ),
                replacement_resource_id=None,
                replacement_candidate_id=None,
                failure_evidence_id=(
                    failure.evidence_id
                ),
            )

        binding = replacement.bindings[0]

        return GovernedAdaptiveRoutingDecision(
            mission_contract_id=(
                contract.contract_id
            ),
            objective_fingerprint=objective,
            capability_graph_id=(
                capability_graph.graph_id
            ),
            routing_plan_id=(
                routing_plan.routing_plan_id
            ),
            route_id=route.route_id,
            node_id=route.node_id,
            capability_id=(
                route.capability_id
            ),
            council_id=(
                route.council_id
            ),
            previous_resource_id=(
                route.resource_id
            ),
            state=(
                AdaptiveRoutingState
                .REROUTE_PROPOSED
            ),
            replacement_resource_id=(
                binding.resource_id
            ),
            replacement_candidate_id=(
                binding.candidate_id
            ),
            failure_evidence_id=(
                failure.evidence_id
            ),
        )

    @staticmethod
    def close_node(
        plan: GovernedMissionPlan,
        routing_plan: GovernedExecutionRoutingPlan,
        evidence: NodeExecutionClosureEvidence,
    ) -> GovernedNodeClosure:
        if not isinstance(
            plan,
            GovernedMissionPlan,
        ):
            raise TypeError(
                "plan must be "
                "GovernedMissionPlan."
            )

        if not isinstance(
            routing_plan,
            GovernedExecutionRoutingPlan,
        ):
            raise TypeError(
                "routing_plan must be "
                "GovernedExecutionRoutingPlan."
            )

        if not isinstance(
            evidence,
            NodeExecutionClosureEvidence,
        ):
            raise TypeError(
                "evidence must be "
                "NodeExecutionClosureEvidence."
            )

        if (
            evidence.plan_id
            != plan.plan_id
            or routing_plan.plan_id
            != plan.plan_id
            or evidence.routing_plan_id
            != routing_plan.routing_plan_id
        ):
            raise AdaptiveMissionClosureInvariantError(
                "Node closure lineage mismatch."
            )

        node = next(
            (
                item
                for item in plan.nodes
                if item.node_id
                == evidence.node_id
            ),
            None,
        )

        route = next(
            (
                item
                for item in routing_plan.routes
                if item.route_id
                == evidence.route_id
            ),
            None,
        )

        if node is None or route is None:
            raise AdaptiveMissionClosureInvariantError(
                "Node closure references "
                "unknown node or route."
            )

        if (
            route.node_id != node.node_id
            or route.capability_id
            != node.capability_id
            or route.council_id
            != node.council_id
            or route.resource_id
            != node.resource_id
            or route.idempotency_key
            != evidence.idempotency_key
        ):
            raise AdaptiveMissionClosureInvariantError(
                "Node closure evidence does "
                "not match execution route."
            )

        expected_acceptance = set(
            node.acceptance_evidence
        )

        observed_acceptance = set(
            evidence
            .acceptance_evidence_keys
        )

        extras = (
            observed_acceptance
            - expected_acceptance
        )

        if extras:
            raise AdaptiveMissionClosureInvariantError(
                "Node closure contains unknown "
                "acceptance evidence keys."
            )

        reasons: list[str] = []

        if (
            evidence.execution_state
            is ClosureEvidenceState.FAIL
            or evidence.council_verdict_state
            is ClosureEvidenceState.FAIL
        ):
            state = NodeClosureState.REJECTED

            reasons.append(
                "Explicit node execution or "
                "Council verdict failure."
            )

        elif (
            evidence.execution_state
            is ClosureEvidenceState.UNKNOWN
            or evidence.council_verdict_state
            is ClosureEvidenceState.UNKNOWN
            or evidence.output_ref is None
            or not evidence.provenance_refs
            or not evidence.execution_evidence_refs
            or evidence.council_verdict_ref
            is None
            or observed_acceptance
            != expected_acceptance
        ):
            state = NodeClosureState.UNKNOWN

            reasons.append(
                "Node evidence closure "
                "is incomplete or unknown."
            )

        else:
            state = NodeClosureState.COMPLETE

            reasons.append(
                "Output, provenance, execution "
                "evidence, Council verdict and "
                "acceptance evidence are complete."
            )

        return GovernedNodeClosure(
            plan_id=plan.plan_id,
            routing_plan_id=(
                routing_plan.routing_plan_id
            ),
            node_id=node.node_id,
            route_id=route.route_id,
            council_id=node.council_id,
            capability_id=(
                node.capability_id
            ),
            resource_id=(
                node.resource_id
            ),
            evidence_id=(
                evidence.evidence_id
            ),
            state=state,
            reasons=tuple(reasons),
        )

    @staticmethod
    def verdict(
        plan: GovernedMissionPlan,
        evidence: MissionVerdictEvidence,
    ) -> GovernedMissionVerdict:
        if not isinstance(
            plan,
            GovernedMissionPlan,
        ):
            raise TypeError(
                "plan must be "
                "GovernedMissionPlan."
            )

        if not isinstance(
            evidence,
            MissionVerdictEvidence,
        ):
            raise TypeError(
                "evidence must be "
                "MissionVerdictEvidence."
            )

        if evidence.plan_id != plan.plan_id:
            raise AdaptiveMissionClosureInvariantError(
                "Mission verdict evidence "
                "is not bound to plan."
            )

        required_nodes = {
            item.node_id
            for item in plan.nodes
        }

        observed_nodes = {
            item.node_id
            for item in evidence.node_closures
        }

        extra_nodes = (
            observed_nodes
            - required_nodes
        )

        if extra_nodes:
            raise AdaptiveMissionClosureInvariantError(
                "Mission verdict contains "
                "unrelated node closures."
            )

        for closure in evidence.node_closures:
            if closure.plan_id != plan.plan_id:
                raise AdaptiveMissionClosureInvariantError(
                    "Node closure belongs "
                    "to another plan."
                )

        required_criteria = set(
            plan.mission_acceptance_criteria
        )

        observed_criteria = set(
            evidence
            .acceptance_criteria_validated
        )

        extra_criteria = (
            observed_criteria
            - required_criteria
        )

        if extra_criteria:
            raise AdaptiveMissionClosureInvariantError(
                "Mission verdict contains "
                "unknown acceptance criteria."
            )

        required_councils = {
            item.council_id
            for item in plan.nodes
        }

        observed_councils = {
            item.council_id
            for item in evidence.council_verdicts
        }

        extra_councils = (
            observed_councils
            - required_councils
        )

        if extra_councils:
            raise AdaptiveMissionClosureInvariantError(
                "Mission verdict contains "
                "unrelated Council verdicts."
            )

        closure_states = [
            item.state
            for item in evidence.node_closures
        ]

        council_states = [
            item.state
            for item in evidence.council_verdicts
        ]

        reasons: list[str] = []

        if (
            any(
                value
                is NodeClosureState.REJECTED
                for value in closure_states
            )
            or evidence.ay_system_verdict_state
            is ClosureEvidenceState.FAIL
            or any(
                value
                is ClosureEvidenceState.FAIL
                for value in council_states
            )
        ):
            state = MissionVerdictState.REJECTED

            reasons.append(
                "Explicit node, Council or "
                "AY SYSTEM verdict failure."
            )

        elif (
            observed_nodes != required_nodes
            or any(
                value
                is not NodeClosureState.COMPLETE
                for value in closure_states
            )
            or observed_criteria
            != required_criteria
            or observed_councils
            != required_councils
            or any(
                value
                is not ClosureEvidenceState.PASS
                for value in council_states
            )
            or any(
                item.verdict_ref is None
                for item in evidence.council_verdicts
            )
            or evidence.ay_system_verdict_state
            is not ClosureEvidenceState.PASS
            or evidence.ay_system_verdict_ref
            is None
        ):
            state = MissionVerdictState.UNKNOWN

            reasons.append(
                "Mission acceptance evidence "
                "or governed verdict evidence "
                "is incomplete or unknown."
            )

        else:
            state = MissionVerdictState.ACCEPTED

            reasons.append(
                "All node closures, mission "
                "acceptance criteria, domain "
                "Council verdicts and AY SYSTEM "
                "verdict evidence passed."
            )

        return GovernedMissionVerdict(
            plan_id=plan.plan_id,
            evidence_id=evidence.evidence_id,
            state=state,
            reasons=tuple(reasons),
        )


__all__ = [
    "GOVERNED_ADAPTIVE_MISSION_CLOSURE_VERSION",
    "AdaptiveMissionClosureInvariantError",
    "AdaptiveMissionClosureIncompleteError",
    "ClosureEvidenceState",
    "RoutingFailureKind",
    "AdaptiveRoutingState",
    "NodeClosureState",
    "MissionVerdictState",
    "RouteFailureEvidence",
    "GovernedAdaptiveRoutingDecision",
    "NodeExecutionClosureEvidence",
    "GovernedNodeClosure",
    "CouncilMissionVerdictEvidence",
    "MissionVerdictEvidence",
    "GovernedMissionVerdict",
    "GovernedAdaptiveMissionClosure",
]
