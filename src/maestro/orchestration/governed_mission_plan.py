from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Iterable

from maestro.intelligence_market.governed_capability_resource_market import (
    GovernedResourceSelection,
    MissionCapabilityGraph,
)
from maestro.orchestration.governed_mission_foundation import (
    GovernedCouncilGraph,
    MissionContract,
)


GOVERNED_MISSION_PLAN_VERSION = 1


class MissionPlanInvariantError(ValueError):
    pass


class MissionPlanIncompleteError(
    MissionPlanInvariantError
):
    pass


class ValidationEvidenceState(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class PlanValidationState(StrEnum):
    ELIGIBLE = "ELIGIBLE"
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
        raise MissionPlanInvariantError(
            f"{name} must not be empty."
        )

    if "\x00" in value:
        raise MissionPlanInvariantError(
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
        raise MissionPlanInvariantError(
            f"{name} must not be empty."
        )

    if len(rows) != len(set(rows)):
        raise MissionPlanInvariantError(
            f"{name} values must be unique."
        )

    return rows


def _nonnegative_int(
    value: int,
    name: str,
) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
    ):
        raise MissionPlanInvariantError(
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
class RetryPolicy:
    max_attempts: int
    backoff_profile: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.max_attempts, int)
            or isinstance(self.max_attempts, bool)
            or self.max_attempts < 1
        ):
            raise MissionPlanInvariantError(
                "max_attempts must be >= 1."
            )

        object.__setattr__(
            self,
            "backoff_profile",
            _required_text(
                self.backoff_profile,
                "backoff_profile",
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_attempts": self.max_attempts,
            "backoff_profile": (
                self.backoff_profile
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class EffectBudgetDeclaration:
    effects: tuple[str, ...]
    permissions: tuple[str, ...]

    max_tool_calls: int
    max_cost_units: int
    max_latency_ms: int

    sandbox_required: bool
    network_allowed: bool = False
    filesystem_write_allowed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "effects",
            _normalized_tuple(
                self.effects,
                "effect",
            ),
        )

        object.__setattr__(
            self,
            "permissions",
            _normalized_tuple(
                self.permissions,
                "permission",
            ),
        )

        for name in (
            "max_tool_calls",
            "max_cost_units",
            "max_latency_ms",
        ):
            object.__setattr__(
                self,
                name,
                _nonnegative_int(
                    getattr(self, name),
                    name,
                ),
            )

        for name in (
            "sandbox_required",
            "network_allowed",
            "filesystem_write_allowed",
        ):
            if not isinstance(
                getattr(self, name),
                bool,
            ):
                raise TypeError(
                    f"{name} must be bool."
                )

        if (
            self.network_allowed
            and "NETWORK"
            not in self.permissions
        ):
            raise MissionPlanInvariantError(
                "Network effect requires "
                "NETWORK permission declaration."
            )

        if (
            self.filesystem_write_allowed
            and "FILESYSTEM_WRITE"
            not in self.permissions
        ):
            raise MissionPlanInvariantError(
                "Filesystem write effect requires "
                "FILESYSTEM_WRITE permission declaration."
            )

        if (
            (
                self.network_allowed
                or self.filesystem_write_allowed
            )
            and not self.sandbox_required
        ):
            raise MissionPlanInvariantError(
                "External effects require "
                "an explicit sandbox boundary."
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "effects": list(self.effects),
            "permissions": list(
                self.permissions
            ),
            "max_tool_calls": (
                self.max_tool_calls
            ),
            "max_cost_units": (
                self.max_cost_units
            ),
            "max_latency_ms": (
                self.max_latency_ms
            ),
            "sandbox_required": (
                self.sandbox_required
            ),
            "network_allowed": (
                self.network_allowed
            ),
            "filesystem_write_allowed": (
                self.filesystem_write_allowed
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class RecoveryBoundary:
    failure_mode: str
    recovery_reference: str | None

    def __post_init__(self) -> None:
        mode = _required_text(
            self.failure_mode,
            "failure_mode",
        )

        object.__setattr__(
            self,
            "failure_mode",
            mode,
        )

        if self.recovery_reference is not None:
            object.__setattr__(
                self,
                "recovery_reference",
                _required_text(
                    self.recovery_reference,
                    "recovery_reference",
                ),
            )

        if (
            mode != "NONE"
            and self.recovery_reference is None
        ):
            raise MissionPlanInvariantError(
                "Non-NONE failure mode requires "
                "a recovery reference."
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "failure_mode": (
                self.failure_mode
            ),
            "recovery_reference": (
                self.recovery_reference
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class CapabilityPlanDirective:
    capability_id: str

    depends_on_capabilities: tuple[
        str,
        ...,
    ]

    acceptance_evidence: tuple[
        str,
        ...,
    ]

    retry_policy: RetryPolicy
    effects: EffectBudgetDeclaration
    recovery: RecoveryBoundary

    def __post_init__(self) -> None:
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
            "depends_on_capabilities",
            _normalized_tuple(
                self.depends_on_capabilities,
                "dependency_capability",
                require_nonempty=False,
            ),
        )

        object.__setattr__(
            self,
            "acceptance_evidence",
            _normalized_tuple(
                self.acceptance_evidence,
                "acceptance_evidence",
            ),
        )

        if not isinstance(
            self.retry_policy,
            RetryPolicy,
        ):
            raise TypeError(
                "retry_policy must be RetryPolicy."
            )

        if not isinstance(
            self.effects,
            EffectBudgetDeclaration,
        ):
            raise TypeError(
                "effects must be "
                "EffectBudgetDeclaration."
            )

        if not isinstance(
            self.recovery,
            RecoveryBoundary,
        ):
            raise TypeError(
                "recovery must be RecoveryBoundary."
            )


@dataclass(
    frozen=True,
    slots=True,
)
class MissionPlanNode:
    node_id: str
    capability_id: str
    council_id: str
    resource_id: str

    dependency_node_ids: tuple[
        str,
        ...,
    ]

    acceptance_evidence: tuple[
        str,
        ...,
    ]

    retry_policy: RetryPolicy
    effects: EffectBudgetDeclaration
    recovery: RecoveryBoundary

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "capability_id": (
                self.capability_id
            ),
            "council_id": self.council_id,
            "resource_id": self.resource_id,
            "dependency_node_ids": list(
                self.dependency_node_ids
            ),
            "acceptance_evidence": list(
                self.acceptance_evidence
            ),
            "retry_policy": (
                self.retry_policy.to_dict()
            ),
            "effects": self.effects.to_dict(),
            "recovery": (
                self.recovery.to_dict()
            ),
        }


def _assert_acyclic(
    nodes: tuple[
        MissionPlanNode,
        ...,
    ],
) -> None:
    graph = {
        node.node_id: set(
            node.dependency_node_ids
        )
        for node in nodes
    }

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visited:
            return

        if node_id in visiting:
            raise MissionPlanInvariantError(
                "Mission plan contains a cycle."
            )

        visiting.add(node_id)

        for dependency in sorted(
            graph[node_id]
        ):
            if dependency not in graph:
                raise MissionPlanInvariantError(
                    "Mission plan dependency "
                    "references unknown node."
                )

            visit(dependency)

        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in sorted(graph):
        visit(node_id)


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedMissionPlan:
    mission_contract_id: str
    council_graph_id: str
    capability_graph_id: str
    resource_selection_id: str

    mission_acceptance_criteria: tuple[
        str,
        ...,
    ]

    nodes: tuple[
        MissionPlanNode,
        ...,
    ]

    plan_id: str = field(
        init=False
    )

    execution_requested: bool = False
    execution_authorized: bool = False
    effects_authorized: bool = False
    network_authorized: bool = False
    filesystem_write_authorized: bool = False
    system_truth_asserted: bool = False

    def __post_init__(self) -> None:
        for name in (
            "mission_contract_id",
            "council_graph_id",
            "capability_graph_id",
            "resource_selection_id",
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
            "mission_acceptance_criteria",
            _normalized_tuple(
                self.mission_acceptance_criteria,
                "mission_acceptance_criterion",
            ),
        )

        raw = tuple(self.nodes)

        if not raw:
            raise MissionPlanIncompleteError(
                "Mission plan must not be empty."
            )

        if not all(
            isinstance(
                item,
                MissionPlanNode,
            )
            for item in raw
        ):
            raise TypeError(
                "nodes must contain "
                "MissionPlanNode only."
            )

        rows = tuple(
            sorted(
                raw,
                key=lambda item: (
                    item.capability_id
                ),
            )
        )

        capability_ids = [
            item.capability_id
            for item in rows
        ]

        node_ids = [
            item.node_id
            for item in rows
        ]

        if len(capability_ids) != len(
            set(capability_ids)
        ):
            raise MissionPlanInvariantError(
                "Mission plan must contain "
                "one node per capability."
            )

        if len(node_ids) != len(
            set(node_ids)
        ):
            raise MissionPlanInvariantError(
                "Mission plan node IDs "
                "must be unique."
            )

        _assert_acyclic(rows)

        object.__setattr__(
            self,
            "nodes",
            rows,
        )

        for name in (
            "execution_requested",
            "execution_authorized",
            "effects_authorized",
            "network_authorized",
            "filesystem_write_authorized",
            "system_truth_asserted",
        ):
            if getattr(self, name) is not False:
                raise MissionPlanInvariantError(
                    "Mission plan cannot "
                    f"assert {name}."
                )

        object.__setattr__(
            self,
            "plan_id",
            _stable_id(
                "GMP",
                {
                    "mission_contract_id": (
                        self.mission_contract_id
                    ),
                    "council_graph_id": (
                        self.council_graph_id
                    ),
                    "capability_graph_id": (
                        self.capability_graph_id
                    ),
                    "resource_selection_id": (
                        self.resource_selection_id
                    ),
                    "mission_acceptance_criteria": list(
                        self.mission_acceptance_criteria
                    ),
                    "nodes": [
                        item.to_dict()
                        for item in rows
                    ],
                },
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class CouncilPlanValidation:
    council_id: str
    state: ValidationEvidenceState
    evidence_ref: str

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
            ValidationEvidenceState,
        ):
            raise TypeError(
                "state must be "
                "ValidationEvidenceState."
            )

        object.__setattr__(
            self,
            "evidence_ref",
            _required_text(
                self.evidence_ref,
                "evidence_ref",
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class PlanValidationEvidence:
    plan_id: str

    ay_validation: ValidationEvidenceState
    plan_invariants: ValidationEvidenceState

    council_validations: tuple[
        CouncilPlanValidation,
        ...,
    ]

    acceptance_criteria_validated: tuple[
        str,
        ...,
    ]

    evidence_source_ref: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "plan_id",
            _required_text(
                self.plan_id,
                "plan_id",
            ),
        )

        for name in (
            "ay_validation",
            "plan_invariants",
        ):
            if not isinstance(
                getattr(self, name),
                ValidationEvidenceState,
            ):
                raise TypeError(
                    f"{name} must be "
                    "ValidationEvidenceState."
                )

        raw = tuple(
            self.council_validations
        )

        if not all(
            isinstance(
                item,
                CouncilPlanValidation,
            )
            for item in raw
        ):
            raise TypeError(
                "council_validations must "
                "contain CouncilPlanValidation."
            )

        rows = tuple(
            sorted(
                raw,
                key=lambda item: (
                    item.council_id
                ),
            )
        )

        ids = [
            item.council_id
            for item in rows
        ]

        if len(ids) != len(set(ids)):
            raise MissionPlanInvariantError(
                "Council validation evidence "
                "must be unique."
            )

        object.__setattr__(
            self,
            "council_validations",
            rows,
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

        object.__setattr__(
            self,
            "evidence_source_ref",
            _required_text(
                self.evidence_source_ref,
                "evidence_source_ref",
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedPlanValidation:
    plan: GovernedMissionPlan
    evidence: PlanValidationEvidence

    state: PlanValidationState = field(
        init=False
    )

    reasons: tuple[
        str,
        ...,
    ] = field(
        init=False
    )

    validation_id: str = field(
        init=False
    )

    execution_authorized: bool = False
    effects_authorized: bool = False
    network_authorized: bool = False
    filesystem_write_authorized: bool = False
    system_truth_asserted: bool = False

    def __post_init__(self) -> None:
        if not isinstance(
            self.plan,
            GovernedMissionPlan,
        ):
            raise TypeError(
                "plan must be GovernedMissionPlan."
            )

        if not isinstance(
            self.evidence,
            PlanValidationEvidence,
        ):
            raise TypeError(
                "evidence must be "
                "PlanValidationEvidence."
            )

        if (
            self.evidence.plan_id
            != self.plan.plan_id
        ):
            raise MissionPlanInvariantError(
                "Validation evidence is not "
                "bound to supplied plan."
            )

        required_councils = {
            node.council_id
            for node in self.plan.nodes
        }

        observed_councils = {
            item.council_id
            for item
            in self.evidence
            .council_validations
        }

        extras = (
            observed_councils
            - required_councils
        )

        if extras:
            raise MissionPlanInvariantError(
                "Validation evidence contains "
                "unrelated Councils."
            )

        expected_criteria = set(
            self.plan
            .mission_acceptance_criteria
        )

        observed_criteria = set(
            self.evidence
            .acceptance_criteria_validated
        )

        extra_criteria = (
            observed_criteria
            - expected_criteria
        )

        if extra_criteria:
            raise MissionPlanInvariantError(
                "Validation evidence contains "
                "unknown acceptance criteria."
            )

        reasons: list[str] = []

        states = [
            self.evidence.ay_validation,
            self.evidence.plan_invariants,
            *(
                item.state
                for item
                in self.evidence
                .council_validations
            ),
        ]

        if any(
            value
            is ValidationEvidenceState.FAIL
            for value in states
        ):
            state = (
                PlanValidationState.REJECTED
            )
            reasons.append(
                "Explicit plan validation "
                "failure observed."
            )

        elif (
            self.evidence.ay_validation
            is ValidationEvidenceState.UNKNOWN
            or self.evidence.plan_invariants
            is ValidationEvidenceState.UNKNOWN
            or any(
                value
                is ValidationEvidenceState.UNKNOWN
                for value in states
            )
            or observed_councils
            != required_councils
            or observed_criteria
            != expected_criteria
        ):
            state = PlanValidationState.UNKNOWN

            reasons.append(
                "Plan validation evidence "
                "is incomplete or unknown."
            )

        else:
            state = PlanValidationState.ELIGIBLE

            reasons.append(
                "AY, relevant Councils, "
                "plan invariants and acceptance "
                "criteria all passed."
            )

        object.__setattr__(
            self,
            "state",
            state,
        )

        object.__setattr__(
            self,
            "reasons",
            tuple(reasons),
        )

        for name in (
            "execution_authorized",
            "effects_authorized",
            "network_authorized",
            "filesystem_write_authorized",
            "system_truth_asserted",
        ):
            if getattr(self, name) is not False:
                raise MissionPlanInvariantError(
                    "Plan validation cannot "
                    f"assert {name}."
                )

        object.__setattr__(
            self,
            "validation_id",
            _stable_id(
                "GPV",
                {
                    "plan_id": (
                        self.plan.plan_id
                    ),
                    "state": state.value,
                    "reasons": reasons,
                    "evidence_source_ref": (
                        self.evidence
                        .evidence_source_ref
                    ),
                },
            ),
        )

    @property
    def execution_eligible(self) -> bool:
        return (
            self.state
            is PlanValidationState.ELIGIBLE
        )


class GovernedMissionPlanner:
    @staticmethod
    def synthesize(
        contract: MissionContract,
        council_graph: GovernedCouncilGraph,
        capability_graph: MissionCapabilityGraph,
        resource_selection: GovernedResourceSelection,
        directives: Iterable[
            CapabilityPlanDirective
        ],
    ) -> GovernedMissionPlan:
        if not isinstance(
            contract,
            MissionContract,
        ):
            raise TypeError(
                "contract must be MissionContract."
            )

        if not isinstance(
            council_graph,
            GovernedCouncilGraph,
        ):
            raise TypeError(
                "council_graph must be "
                "GovernedCouncilGraph."
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
            resource_selection,
            GovernedResourceSelection,
        ):
            raise TypeError(
                "resource_selection must be "
                "GovernedResourceSelection."
            )

        if (
            council_graph.contract_id
            != contract.contract_id
            or capability_graph
            .mission_contract_id
            != contract.contract_id
        ):
            raise MissionPlanInvariantError(
                "Mission planning lineage "
                "does not bind exact contract."
            )

        if (
            council_graph.demand_id
            != capability_graph.demand_id
        ):
            raise MissionPlanInvariantError(
                "Council/capability graphs "
                "bind different demand IDs."
            )

        if (
            resource_selection
            .capability_graph_id
            != capability_graph.graph_id
        ):
            raise MissionPlanInvariantError(
                "Resource selection is not "
                "bound to capability graph."
            )

        owners = dict(
            council_graph
            .capability_owners
        )

        selected = {
            item.capability_id: (
                item.resource_id
            )
            for item
            in resource_selection.bindings
        }

        required = set(
            capability_graph
            .capability_ids
        )

        if (
            set(owners)
            != required
            or set(selected)
            != required
        ):
            raise MissionPlanIncompleteError(
                "Council and resource coverage "
                "must exactly cover capability graph."
            )

        rows = tuple(
            directives
        )

        if not all(
            isinstance(
                item,
                CapabilityPlanDirective,
            )
            for item in rows
        ):
            raise TypeError(
                "directives must contain "
                "CapabilityPlanDirective only."
            )

        by_capability = {
            item.capability_id: item
            for item in rows
        }

        if len(by_capability) != len(rows):
            raise MissionPlanInvariantError(
                "Plan directives must be unique "
                "by capability."
            )

        if set(by_capability) != required:
            raise MissionPlanIncompleteError(
                "Plan directives must exactly "
                "cover capability graph."
            )

        node_ids = {
            capability: _stable_id(
                "MPN",
                {
                    "contract_id": (
                        contract.contract_id
                    ),
                    "capability_id": capability,
                    "council_id": (
                        owners[capability]
                    ),
                    "resource_id": (
                        selected[capability]
                    ),
                },
            )
            for capability in sorted(
                required
            )
        }

        nodes = []

        for capability in sorted(
            required
        ):
            directive = (
                by_capability[capability]
            )

            unknown_dependencies = (
                set(
                    directive
                    .depends_on_capabilities
                )
                - required
            )

            if unknown_dependencies:
                raise MissionPlanInvariantError(
                    "Plan directive references "
                    "unknown capability dependency."
                )

            if (
                capability
                in directive
                .depends_on_capabilities
            ):
                raise MissionPlanInvariantError(
                    "Capability cannot depend "
                    "on itself."
                )

            nodes.append(
                MissionPlanNode(
                    node_id=(
                        node_ids[capability]
                    ),
                    capability_id=capability,
                    council_id=(
                        owners[capability]
                    ),
                    resource_id=(
                        selected[capability]
                    ),
                    dependency_node_ids=tuple(
                        sorted(
                            node_ids[item]
                            for item
                            in directive
                            .depends_on_capabilities
                        )
                    ),
                    acceptance_evidence=(
                        directive
                        .acceptance_evidence
                    ),
                    retry_policy=(
                        directive.retry_policy
                    ),
                    effects=(
                        directive.effects
                    ),
                    recovery=(
                        directive.recovery
                    ),
                )
            )

        return GovernedMissionPlan(
            mission_contract_id=(
                contract.contract_id
            ),
            council_graph_id=(
                council_graph.graph_id
            ),
            capability_graph_id=(
                capability_graph.graph_id
            ),
            resource_selection_id=(
                resource_selection.selection_id
            ),
            mission_acceptance_criteria=(
                contract.acceptance_criteria
            ),
            nodes=tuple(nodes),
        )

    @staticmethod
    def validate(
        plan: GovernedMissionPlan,
        evidence: PlanValidationEvidence,
    ) -> GovernedPlanValidation:
        return GovernedPlanValidation(
            plan=plan,
            evidence=evidence,
        )


__all__ = [
    "GOVERNED_MISSION_PLAN_VERSION",
    "MissionPlanInvariantError",
    "MissionPlanIncompleteError",
    "ValidationEvidenceState",
    "PlanValidationState",
    "RetryPolicy",
    "EffectBudgetDeclaration",
    "RecoveryBoundary",
    "CapabilityPlanDirective",
    "MissionPlanNode",
    "GovernedMissionPlan",
    "CouncilPlanValidation",
    "PlanValidationEvidence",
    "GovernedPlanValidation",
    "GovernedMissionPlanner",
]
