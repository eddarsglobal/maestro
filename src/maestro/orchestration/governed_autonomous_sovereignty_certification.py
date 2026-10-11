from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass, field
from typing import Any, Iterable

from maestro.intelligence_market.governed_capability_resource_market import (
    GovernedResourceSelection,
    MissionCapabilityGraph,
)
from maestro.learning.governed_experience_learning_promotion import (
    ImmutableExperienceEvidence,
)
from maestro.orchestration.governed_adaptive_mission_closure import (
    GovernedMissionVerdict,
    GovernedNodeClosure,
    MissionVerdictState,
    NodeExecutionClosureEvidence,
)
from maestro.orchestration.governed_durable_mission_recovery import (
    GovernedDurableMissionCheckpoint,
)
from maestro.orchestration.governed_execution_routing import (
    GovernedExecutionRoutingPlan,
)
from maestro.orchestration.governed_mission_foundation import (
    GovernedCouncilGraph,
    MissionContract,
)
from maestro.orchestration.governed_mission_plan import (
    GovernedMissionPlan,
    GovernedPlanValidation,
)


GOVERNED_AUTONOMOUS_SOVEREIGNTY_CERTIFICATION_VERSION = 1


class AutonomousSovereigntyCertificationError(
    ValueError
):
    pass


def _required_text(
    value: str,
    name: str,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise TypeError(
            f"{name} must be a string."
        )

    value = value.strip()

    if not value:
        raise AutonomousSovereigntyCertificationError(
            f"{name} must not be empty."
        )

    if "\x00" in value:
        raise AutonomousSovereigntyCertificationError(
            f"{name} must not contain NUL."
        )

    return value


def _normalized_tuple(
    values: Iterable[str],
    name: str,
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

    if not rows:
        raise AutonomousSovereigntyCertificationError(
            f"{name} must not be empty."
        )

    if len(rows) != len(
        set(rows)
    ):
        raise AutonomousSovereigntyCertificationError(
            f"{name} values must be unique."
        )

    return rows


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
    digest = hashlib.sha256(
        _canonical_json(
            payload
        ).encode("utf-8")
    ).hexdigest()

    return (
        prefix
        + "-"
        + digest[:24]
    )


def _require_false(
    obj: object,
    fields: Iterable[str],
) -> None:
    for name in fields:
        if not hasattr(
            obj,
            name,
        ):
            raise AutonomousSovereigntyCertificationError(
                "Missing sovereignty field: "
                + name
            )

        if getattr(
            obj,
            name,
        ) is not False:
            raise AutonomousSovereigntyCertificationError(
                "Sovereignty violation: "
                + name
            )


@dataclass(
    frozen=True,
    slots=True,
)
class CouncilExecutionWitness:
    task_id: str
    route_id: str
    node_id: str
    council_id: str
    ex_authorization_ref: str
    success: bool
    output_ref: str
    evidence_refs: tuple[str, ...]

    witness_id: str = field(
        init=False
    )

    provider_authority_granted: bool = False
    model_authority_granted: bool = False
    worker_authority_granted: bool = False
    mission_authority_transferred: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "task_id",
            "route_id",
            "node_id",
            "council_id",
            "ex_authorization_ref",
            "output_ref",
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

        if self.success is not True:
            raise AutonomousSovereigntyCertificationError(
                "Execution witness must represent "
                "successful governed execution."
            )

        object.__setattr__(
            self,
            "evidence_refs",
            _normalized_tuple(
                self.evidence_refs,
                "evidence_ref",
            ),
        )

        _require_false(
            self,
            (
                "provider_authority_granted",
                "model_authority_granted",
                "worker_authority_granted",
                "mission_authority_transferred",
                "system_truth_asserted",
            ),
        )

        object.__setattr__(
            self,
            "witness_id",
            _stable_id(
                "CEW",
                {
                    "task_id": (
                        self.task_id
                    ),
                    "route_id": (
                        self.route_id
                    ),
                    "node_id": (
                        self.node_id
                    ),
                    "council_id": (
                        self.council_id
                    ),
                    "ex_authorization_ref": (
                        self
                        .ex_authorization_ref
                    ),
                    "success": (
                        self.success
                    ),
                    "output_ref": (
                        self.output_ref
                    ),
                    "evidence_refs": list(
                        self.evidence_refs
                    ),
                },
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class AutonomousSovereigntyCertificate:
    mission_contract_id: str
    council_graph_id: str
    capability_graph_id: str
    resource_selection_id: str
    plan_id: str
    validation_id: str
    routing_plan_id: str

    execution_witness_ids: tuple[str, ...]
    node_closure_ids: tuple[str, ...]

    mission_verdict_id: str
    checkpoint_id: str
    experience_id: str

    certification_id: str = field(
        init=False
    )

    autonomous_loop_complete: bool = True
    provider_independent: bool = True
    model_independent: bool = True
    runtime_independent: bool = True
    council_governed: bool = True
    evidence_bound: bool = True
    fail_closed: bool = True
    recoverable: bool = True
    zero_model_compatible: bool = True

    authority_expanded: bool = False
    system_truth_asserted: bool = False
    production_release_authorized: bool = False

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "mission_contract_id",
            "council_graph_id",
            "capability_graph_id",
            "resource_selection_id",
            "plan_id",
            "validation_id",
            "routing_plan_id",
            "mission_verdict_id",
            "checkpoint_id",
            "experience_id",
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

        for name in (
            "execution_witness_ids",
            "node_closure_ids",
        ):
            object.__setattr__(
                self,
                name,
                _normalized_tuple(
                    getattr(
                        self,
                        name,
                    ),
                    name,
                ),
            )

        for name in (
            "autonomous_loop_complete",
            "provider_independent",
            "model_independent",
            "runtime_independent",
            "council_governed",
            "evidence_bound",
            "fail_closed",
            "recoverable",
            "zero_model_compatible",
        ):
            if getattr(
                self,
                name,
            ) is not True:
                raise AutonomousSovereigntyCertificationError(
                    "Certification requires "
                    + name
                )

        for name in (
            "authority_expanded",
            "system_truth_asserted",
            "production_release_authorized",
        ):
            if getattr(
                self,
                name,
            ) is not False:
                raise AutonomousSovereigntyCertificationError(
                    "Certification cannot assert "
                    + name
                )

        object.__setattr__(
            self,
            "certification_id",
            _stable_id(
                "ASC",
                {
                    "mission_contract_id": (
                        self
                        .mission_contract_id
                    ),
                    "council_graph_id": (
                        self
                        .council_graph_id
                    ),
                    "capability_graph_id": (
                        self
                        .capability_graph_id
                    ),
                    "resource_selection_id": (
                        self
                        .resource_selection_id
                    ),
                    "plan_id": (
                        self.plan_id
                    ),
                    "validation_id": (
                        self.validation_id
                    ),
                    "routing_plan_id": (
                        self.routing_plan_id
                    ),
                    "execution_witness_ids": list(
                        self
                        .execution_witness_ids
                    ),
                    "node_closure_ids": list(
                        self.node_closure_ids
                    ),
                    "mission_verdict_id": (
                        self
                        .mission_verdict_id
                    ),
                    "checkpoint_id": (
                        self.checkpoint_id
                    ),
                    "experience_id": (
                        self.experience_id
                    ),
                },
            ),
        )


class GovernedAutonomousSovereigntyCertification:
    @staticmethod
    def certify(
        *,
        contract: MissionContract,
        council_graph: GovernedCouncilGraph,
        capability_graph: MissionCapabilityGraph,
        resource_selection: GovernedResourceSelection,
        plan: GovernedMissionPlan,
        validation: GovernedPlanValidation,
        routing: GovernedExecutionRoutingPlan,
        execution_witnesses: Iterable[
            CouncilExecutionWitness
        ],
        node_execution_evidence: Iterable[
            NodeExecutionClosureEvidence
        ],
        node_closures: Iterable[
            GovernedNodeClosure
        ],
        verdict: GovernedMissionVerdict,
        checkpoint: GovernedDurableMissionCheckpoint,
        experience: ImmutableExperienceEvidence,
        zero_model_core_certified: bool,
    ) -> AutonomousSovereigntyCertificate:
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
            routing,
            GovernedExecutionRoutingPlan,
        ):
            raise TypeError(
                "routing must be "
                "GovernedExecutionRoutingPlan."
            )

        if not isinstance(
            verdict,
            GovernedMissionVerdict,
        ):
            raise TypeError(
                "verdict must be "
                "GovernedMissionVerdict."
            )

        if not isinstance(
            checkpoint,
            GovernedDurableMissionCheckpoint,
        ):
            raise TypeError(
                "checkpoint must be "
                "GovernedDurableMissionCheckpoint."
            )

        if not isinstance(
            experience,
            ImmutableExperienceEvidence,
        ):
            raise TypeError(
                "experience must be "
                "ImmutableExperienceEvidence."
            )

        if zero_model_core_certified is not True:
            raise AutonomousSovereigntyCertificationError(
                "Zero-model Core sovereignty "
                "must be certified."
            )

        if (
            council_graph.contract_id
            != contract.contract_id
        ):
            raise AutonomousSovereigntyCertificationError(
                "Council graph contract lineage mismatch."
            )

        if (
            capability_graph
            .mission_contract_id
            != contract.contract_id
        ):
            raise AutonomousSovereigntyCertificationError(
                "Capability graph contract lineage mismatch."
            )

        if (
            capability_graph.demand_id
            != council_graph.demand_id
        ):
            raise AutonomousSovereigntyCertificationError(
                "Council/capability demand lineage mismatch."
            )

        if (
            resource_selection
            .capability_graph_id
            != capability_graph.graph_id
        ):
            raise AutonomousSovereigntyCertificationError(
                "Resource selection capability "
                "graph lineage mismatch."
            )

        if (
            plan.mission_contract_id
            != contract.contract_id
        ):
            raise AutonomousSovereigntyCertificationError(
                "Plan mission contract lineage mismatch."
            )

        if (
            plan.council_graph_id
            != council_graph.graph_id
        ):
            raise AutonomousSovereigntyCertificationError(
                "Plan Council graph lineage mismatch."
            )

        if (
            plan.capability_graph_id
            != capability_graph.graph_id
        ):
            raise AutonomousSovereigntyCertificationError(
                "Plan capability graph lineage mismatch."
            )

        if (
            plan.resource_selection_id
            != resource_selection.selection_id
        ):
            raise AutonomousSovereigntyCertificationError(
                "Plan resource selection lineage mismatch."
            )

        if (
            validation.plan.plan_id
            != plan.plan_id
        ):
            raise AutonomousSovereigntyCertificationError(
                "Validation plan lineage mismatch."
            )

        if not getattr(
            validation,
            "execution_eligible",
            False,
        ):
            raise AutonomousSovereigntyCertificationError(
                "Plan is not execution-eligible."
            )

        if (
            routing.plan_id
            != plan.plan_id
        ):
            raise AutonomousSovereigntyCertificationError(
                "Routing plan lineage mismatch."
            )

        if (
            routing.validation_id
            != validation.validation_id
        ):
            raise AutonomousSovereigntyCertificationError(
                "Routing validation lineage mismatch."
            )

        if (
            routing.ex_authority_observed
            is not True
        ):
            raise AutonomousSovereigntyCertificationError(
                "Routing lacks EX authority evidence."
            )

        routes = tuple(
            routing.routes
        )

        if not routes:
            raise AutonomousSovereigntyCertificationError(
                "Autonomous mission requires routes."
            )

        route_by_id = {
            route.route_id: route
            for route in routes
        }

        route_ids = set(
            route_by_id
        )

        witnesses = tuple(
            execution_witnesses
        )

        if not witnesses:
            raise AutonomousSovereigntyCertificationError(
                "Council execution witnesses are required."
            )

        if {
            witness.route_id
            for witness in witnesses
        } != route_ids:
            raise AutonomousSovereigntyCertificationError(
                "Execution witness route coverage mismatch."
            )

        for witness in witnesses:
            route = route_by_id[
                witness.route_id
            ]

            if (
                witness.node_id
                != route.node_id
            ):
                raise AutonomousSovereigntyCertificationError(
                    "Execution witness node mismatch."
                )

            if (
                witness.council_id
                != route.council_id
            ):
                raise AutonomousSovereigntyCertificationError(
                    "Execution witness Council mismatch."
                )

        execution_rows = tuple(
            node_execution_evidence
        )

        if {
            item.route_id
            for item in execution_rows
        } != route_ids:
            raise AutonomousSovereigntyCertificationError(
                "Execution evidence route coverage mismatch."
            )

        for item in execution_rows:
            if (
                item.plan_id
                != plan.plan_id
            ):
                raise AutonomousSovereigntyCertificationError(
                    "Execution evidence plan mismatch."
                )

            if (
                item.routing_plan_id
                != routing.routing_plan_id
            ):
                raise AutonomousSovereigntyCertificationError(
                    "Execution evidence routing mismatch."
                )

        closures = tuple(
            node_closures
        )

        if {
            item.route_id
            for item in closures
        } != route_ids:
            raise AutonomousSovereigntyCertificationError(
                "Node closure route coverage mismatch."
            )

        for closure in closures:
            route = route_by_id[
                closure.route_id
            ]

            if (
                closure.plan_id
                != plan.plan_id
            ):
                raise AutonomousSovereigntyCertificationError(
                    "Node closure plan mismatch."
                )

            if (
                closure.routing_plan_id
                != routing.routing_plan_id
            ):
                raise AutonomousSovereigntyCertificationError(
                    "Node closure routing mismatch."
                )

            if (
                closure.node_id
                != route.node_id
                or closure.council_id
                != route.council_id
                or closure.capability_id
                != route.capability_id
                or closure.resource_id
                != route.resource_id
            ):
                raise AutonomousSovereigntyCertificationError(
                    "Node closure route identity mismatch."
                )

        if (
            verdict.plan_id
            != plan.plan_id
        ):
            raise AutonomousSovereigntyCertificationError(
                "Mission verdict plan mismatch."
            )

        if (
            verdict.state
            is not MissionVerdictState.ACCEPTED
        ):
            raise AutonomousSovereigntyCertificationError(
                "Final successful loop requires "
                "ACCEPTED mission verdict."
            )

        if (
            checkpoint.mission_contract_id
            != contract.contract_id
        ):
            raise AutonomousSovereigntyCertificationError(
                "Checkpoint contract lineage mismatch."
            )

        if (
            checkpoint.plan_id
            != plan.plan_id
        ):
            raise AutonomousSovereigntyCertificationError(
                "Checkpoint plan lineage mismatch."
            )

        if (
            checkpoint.routing_plan_id
            != routing.routing_plan_id
        ):
            raise AutonomousSovereigntyCertificationError(
                "Checkpoint routing lineage mismatch."
            )

        try:
            payload = json.loads(
                checkpoint.payload_json
            )
        except (
            TypeError,
            json.JSONDecodeError,
        ) as exc:
            raise AutonomousSovereigntyCertificationError(
                "Checkpoint payload is invalid."
            ) from exc

        recovery_information = payload.get(
            "recovery_information"
        )

        if (
            not isinstance(
                recovery_information,
                dict,
            )
            or not recovery_information
        ):
            raise AutonomousSovereigntyCertificationError(
                "Durable recovery information missing."
            )

        if (
            experience.checkpoint_id
            != checkpoint.checkpoint_id
        ):
            raise AutonomousSovereigntyCertificationError(
                "Experience checkpoint lineage mismatch."
            )

        if (
            experience
            .checkpoint_payload_sha256
            != checkpoint.payload_sha256
        ):
            raise AutonomousSovereigntyCertificationError(
                "Experience checkpoint digest mismatch."
            )

        if (
            experience.mission_contract_id
            != contract.contract_id
        ):
            raise AutonomousSovereigntyCertificationError(
                "Experience contract lineage mismatch."
            )

        if (
            experience.plan_id
            != plan.plan_id
        ):
            raise AutonomousSovereigntyCertificationError(
                "Experience plan lineage mismatch."
            )

        if (
            experience.routing_plan_id
            != routing.routing_plan_id
        ):
            raise AutonomousSovereigntyCertificationError(
                "Experience routing lineage mismatch."
            )

        if (
            experience.mission_verdict_id
            != verdict.verdict_id
        ):
            raise AutonomousSovereigntyCertificationError(
                "Experience verdict lineage mismatch."
            )

        _require_false(
            capability_graph,
            (
                "provider_bound",
                "model_bound",
                "runtime_bound",
                "execution_authorized",
                "system_truth_asserted",
            ),
        )

        _require_false(
            resource_selection,
            (
                "activation_authorized",
                "execution_authorized",
                "provider_authority_granted",
                "model_authority_granted",
                "runtime_authority_granted",
                "mission_authority_transferred",
                "system_truth_asserted",
            ),
        )

        _require_false(
            plan,
            (
                "execution_requested",
                "execution_authorized",
                "effects_authorized",
                "network_authorized",
                "filesystem_write_authorized",
                "system_truth_asserted",
            ),
        )

        _require_false(
            validation,
            (
                "execution_authorized",
                "effects_authorized",
                "network_authorized",
                "filesystem_write_authorized",
                "system_truth_asserted",
            ),
        )

        _require_false(
            routing,
            (
                "adapter_authority_granted",
                "provider_authority_granted",
                "model_authority_granted",
                "worker_authority_granted",
                "mission_authority_transferred",
                "system_truth_asserted",
                "execution_performed",
            ),
        )

        for witness in witnesses:
            _require_false(
                witness,
                (
                    "provider_authority_granted",
                    "model_authority_granted",
                    "worker_authority_granted",
                    "mission_authority_transferred",
                    "system_truth_asserted",
                ),
            )

        for closure in closures:
            _require_false(
                closure,
                (
                    "downstream_completion_authorized",
                    "mission_close_authorized",
                    "learning_authorized",
                    "system_truth_asserted",
                ),
            )

        _require_false(
            verdict,
            (
                "mission_close_authorized",
                "mission_state_transition_requested",
                "durable_commit_authorized",
                "learning_authorized",
                "promotion_authorized",
                "system_truth_asserted",
            ),
        )

        _require_false(
            checkpoint,
            (
                "durable_commit_authorized",
                "mission_state_transition_requested",
                "execution_authorized",
                "learning_authorized",
                "system_truth_asserted",
            ),
        )

        _require_false(
            experience,
            (
                "learning_authorized",
                "policy_mutation_authorized",
                "memory_authority_granted",
                "routing_authority_granted",
                "council_authority_granted",
                "core_mutation_authorized",
                "promotion_authorized",
            ),
        )

        return AutonomousSovereigntyCertificate(
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
            plan_id=(
                plan.plan_id
            ),
            validation_id=(
                validation.validation_id
            ),
            routing_plan_id=(
                routing.routing_plan_id
            ),
            execution_witness_ids=tuple(
                witness.witness_id
                for witness in witnesses
            ),
            node_closure_ids=tuple(
                closure.closure_id
                for closure in closures
            ),
            mission_verdict_id=(
                verdict.verdict_id
            ),
            checkpoint_id=(
                checkpoint.checkpoint_id
            ),
            experience_id=(
                experience.experience_id
            ),
        )


__all__ = [
    "GOVERNED_AUTONOMOUS_SOVEREIGNTY_CERTIFICATION_VERSION",
    "AutonomousSovereigntyCertificationError",
    "CouncilExecutionWitness",
    "AutonomousSovereigntyCertificate",
    "GovernedAutonomousSovereigntyCertification",
]
