from __future__ import annotations

import hashlib
import json
import os
import tempfile

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Iterable, Mapping

from maestro.governance.governed_failure_containment_recovery import (
    EvidenceState as RecoveryEvidenceState,
    FailureState,
    RecoveryAssessmentState,
    RecoveryPlanAction,
)
from maestro.orchestration.governed_adaptive_mission_closure import (
    AdaptiveRoutingState,
    GovernedMissionVerdict,
    GovernedNodeClosure,
    MissionVerdictEvidence,
    NodeExecutionClosureEvidence,
)
from maestro.orchestration.governed_execution_routing import (
    GovernedExecutionRoutingPlan,
)
from maestro.orchestration.governed_mission_foundation import (
    MissionContract,
)
from maestro.orchestration.governed_mission_plan import (
    GovernedMissionPlan,
)


GOVERNED_DURABLE_MISSION_RECOVERY_VERSION = 1

DURABLE_MISSION_SCHEMA = (
    "maestro.phase2.durable-mission.v1"
)


class DurableMissionRecoveryInvariantError(
    ValueError
):
    pass


class DurableMissionIntegrityError(
    DurableMissionRecoveryInvariantError
):
    pass


class DurableMissionSchemaError(
    DurableMissionRecoveryInvariantError
):
    pass


class RecoveryDecisionState(StrEnum):
    HEALTHY = "HEALTHY"
    CONTAINMENT_PROPOSED = (
        "CONTAINMENT_PROPOSED"
    )
    ROLLBACK_PROPOSED = (
        "ROLLBACK_PROPOSED"
    )
    RESUME_PROPOSED = "RESUME_PROPOSED"
    REPLAN_PROPOSED = "REPLAN_PROPOSED"
    UNRECOVERABLE = "UNRECOVERABLE"
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
        raise DurableMissionRecoveryInvariantError(
            f"{name} must not be empty."
        )

    if "\x00" in value:
        raise DurableMissionRecoveryInvariantError(
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


def _nonnegative_int(
    value: int,
    name: str,
) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
    ):
        raise DurableMissionRecoveryInvariantError(
            f"{name} must be an integer >= 0."
        )

    return value


def _positive_int(
    value: int,
    name: str,
) -> int:
    value = _nonnegative_int(
        value,
        name,
    )

    if value < 1:
        raise DurableMissionRecoveryInvariantError(
            f"{name} must be >= 1."
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
        raise DurableMissionRecoveryInvariantError(
            f"{name} must not be empty."
        )

    if len(rows) != len(set(rows)):
        raise DurableMissionRecoveryInvariantError(
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


def _sha256_text(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def _stable_id(
    prefix: str,
    payload: Mapping[str, Any],
) -> str:
    return (
        prefix
        + "-"
        + _sha256_text(
            _canonical_json(payload)
        )[:24]
    )


def _require_sha256(
    value: str,
    name: str,
) -> str:
    value = _required_text(
        value,
        name,
    ).lower()

    if (
        len(value) != 64
        or any(
            char not in "0123456789abcdef"
            for char in value
        )
    ):
        raise DurableMissionRecoveryInvariantError(
            f"{name} must be a SHA-256 hex digest."
        )

    return value


def _objective_fingerprint(
    contract: MissionContract,
) -> str:
    return _stable_id(
        "OBJ",
        {
            "contract_id": contract.contract_id,
            "objective": contract.objective,
        },
    )


def _validate_canonical_mission(
    value: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(
            "canonical_mission must be a mapping."
        )

    raw = dict(value)

    for key in (
        "task_id",
        "objective",
        "state",
    ):
        if key not in raw:
            raise DurableMissionRecoveryInvariantError(
                "Canonical mission snapshot "
                f"requires {key}."
            )

        _required_text(
            str(raw[key]),
            f"canonical_mission.{key}",
        )

    _canonical_json(raw)

    return raw


def _plan_payload(
    plan: GovernedMissionPlan,
) -> dict[str, Any]:
    return {
        "plan_id": plan.plan_id,
        "mission_contract_id": (
            plan.mission_contract_id
        ),
        "council_graph_id": (
            plan.council_graph_id
        ),
        "capability_graph_id": (
            plan.capability_graph_id
        ),
        "resource_selection_id": (
            plan.resource_selection_id
        ),
        "mission_acceptance_criteria": list(
            plan.mission_acceptance_criteria
        ),
        "nodes": [
            {
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
                "dependency_node_ids": list(
                    node.dependency_node_ids
                ),
                "acceptance_evidence": list(
                    node.acceptance_evidence
                ),
                "retry_policy": (
                    node.retry_policy.to_dict()
                ),
                "effects": (
                    node.effects.to_dict()
                ),
                "recovery": (
                    node.recovery.to_dict()
                ),
            }
            for node in plan.nodes
        ],
    }


def _dag_payload(
    plan: GovernedMissionPlan,
) -> dict[str, Any]:
    return {
        "plan_id": plan.plan_id,
        "nodes": [
            {
                "node_id": node.node_id,
                "dependency_node_ids": list(
                    node.dependency_node_ids
                ),
            }
            for node in plan.nodes
        ],
    }


def _routing_payload(
    routing: GovernedExecutionRoutingPlan,
) -> dict[str, Any]:
    return {
        "routing_plan_id": (
            routing.routing_plan_id
        ),
        "plan_id": routing.plan_id,
        "validation_id": (
            routing.validation_id
        ),
        "authorization_evidence_id": (
            routing.authorization_evidence_id
        ),
        "routes": [
            route.to_dict()
            for route in routing.routes
        ],
        "waves": [
            {
                "wave_index": (
                    wave.wave_index
                ),
                "route_ids": list(
                    wave.route_ids
                ),
                "node_ids": list(
                    wave.node_ids
                ),
            }
            for wave in routing.waves
        ],
        "placements": [
            placement.to_dict()
            for placement in routing.placements
        ],
    }


def _node_execution_evidence_payload(
    evidence: NodeExecutionClosureEvidence,
) -> dict[str, Any]:
    return {
        "evidence_id": evidence.evidence_id,
        "plan_id": evidence.plan_id,
        "routing_plan_id": (
            evidence.routing_plan_id
        ),
        "route_id": evidence.route_id,
        "node_id": evidence.node_id,
        "idempotency_key": (
            evidence.idempotency_key
        ),
        "execution_state": (
            evidence.execution_state.value
        ),
        "output_ref": evidence.output_ref,
        "provenance_refs": list(
            evidence.provenance_refs
        ),
        "execution_evidence_refs": list(
            evidence.execution_evidence_refs
        ),
        "council_verdict_state": (
            evidence
            .council_verdict_state
            .value
        ),
        "council_verdict_ref": (
            evidence.council_verdict_ref
        ),
        "acceptance_evidence_keys": list(
            evidence.acceptance_evidence_keys
        ),
        "evidence_source_ref": (
            evidence.evidence_source_ref
        ),
    }


def _node_closure_payload(
    closure: GovernedNodeClosure,
) -> dict[str, Any]:
    return {
        "closure_id": closure.closure_id,
        "plan_id": closure.plan_id,
        "routing_plan_id": (
            closure.routing_plan_id
        ),
        "node_id": closure.node_id,
        "route_id": closure.route_id,
        "council_id": closure.council_id,
        "capability_id": (
            closure.capability_id
        ),
        "resource_id": closure.resource_id,
        "evidence_id": closure.evidence_id,
        "state": closure.state.value,
        "reasons": list(closure.reasons),
    }


def _mission_verdict_evidence_payload(
    evidence: MissionVerdictEvidence,
) -> dict[str, Any]:
    return {
        "evidence_id": evidence.evidence_id,
        "plan_id": evidence.plan_id,
        "node_closure_ids": [
            item.closure_id
            for item in evidence.node_closures
        ],
        "acceptance_criteria_validated": list(
            evidence.acceptance_criteria_validated
        ),
        "council_verdicts": [
            {
                "council_id": (
                    item.council_id
                ),
                "state": item.state.value,
                "verdict_ref": (
                    item.verdict_ref
                ),
            }
            for item in evidence.council_verdicts
        ],
        "ay_system_verdict_state": (
            evidence
            .ay_system_verdict_state
            .value
        ),
        "ay_system_verdict_ref": (
            evidence.ay_system_verdict_ref
        ),
        "evidence_source_ref": (
            evidence.evidence_source_ref
        ),
    }


def _mission_verdict_payload(
    verdict: GovernedMissionVerdict,
) -> dict[str, Any]:
    return {
        "verdict_id": verdict.verdict_id,
        "plan_id": verdict.plan_id,
        "evidence_id": verdict.evidence_id,
        "state": verdict.state.value,
        "reasons": list(verdict.reasons),
    }


@dataclass(
    frozen=True,
    slots=True,
)
class DurableRetryRecord:
    node_id: str
    attempts_used: int
    max_attempts: int
    last_failure_ref: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "node_id",
            _required_text(
                self.node_id,
                "node_id",
            ),
        )

        object.__setattr__(
            self,
            "attempts_used",
            _nonnegative_int(
                self.attempts_used,
                "attempts_used",
            ),
        )

        object.__setattr__(
            self,
            "max_attempts",
            _positive_int(
                self.max_attempts,
                "max_attempts",
            ),
        )

        if self.attempts_used > self.max_attempts:
            raise DurableMissionRecoveryInvariantError(
                "attempts_used exceeds max_attempts."
            )

        object.__setattr__(
            self,
            "last_failure_ref",
            _optional_text(
                self.last_failure_ref,
                "last_failure_ref",
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "attempts_used": (
                self.attempts_used
            ),
            "max_attempts": (
                self.max_attempts
            ),
            "last_failure_ref": (
                self.last_failure_ref
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class DurableCouncilState:
    council_id: str
    runtime_state: str
    state_ref: str
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "council_id",
            _required_text(
                self.council_id,
                "council_id",
            ),
        )

        object.__setattr__(
            self,
            "runtime_state",
            _required_text(
                self.runtime_state,
                "runtime_state",
            ),
        )

        object.__setattr__(
            self,
            "state_ref",
            _required_text(
                self.state_ref,
                "state_ref",
            ),
        )

        object.__setattr__(
            self,
            "evidence_refs",
            _normalized_tuple(
                self.evidence_refs,
                "evidence_ref",
                require_nonempty=False,
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "council_id": self.council_id,
            "runtime_state": (
                self.runtime_state
            ),
            "state_ref": self.state_ref,
            "evidence_refs": list(
                self.evidence_refs
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class DurableRecoveryInformation:
    last_stable_checkpoint_ref: str
    last_stable_generation: int

    rollback_checkpoint_ref: str | None
    recovery_checkpoint_ref: str | None

    recovery_evidence_refs: tuple[
        str,
        ...,
    ]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "last_stable_checkpoint_ref",
            _required_text(
                self.last_stable_checkpoint_ref,
                "last_stable_checkpoint_ref",
            ),
        )

        object.__setattr__(
            self,
            "last_stable_generation",
            _positive_int(
                self.last_stable_generation,
                "last_stable_generation",
            ),
        )

        for name in (
            "rollback_checkpoint_ref",
            "recovery_checkpoint_ref",
        ):
            object.__setattr__(
                self,
                name,
                _optional_text(
                    getattr(self, name),
                    name,
                ),
            )

        object.__setattr__(
            self,
            "recovery_evidence_refs",
            _normalized_tuple(
                self.recovery_evidence_refs,
                "recovery_evidence_ref",
                require_nonempty=False,
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "last_stable_checkpoint_ref": (
                self.last_stable_checkpoint_ref
            ),
            "last_stable_generation": (
                self.last_stable_generation
            ),
            "rollback_checkpoint_ref": (
                self.rollback_checkpoint_ref
            ),
            "recovery_checkpoint_ref": (
                self.recovery_checkpoint_ref
            ),
            "recovery_evidence_refs": list(
                self.recovery_evidence_refs
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedDurableMissionCheckpoint:
    schema: str
    generation: int

    runtime_checkpoint_schema: str
    runtime_checkpoint_sha256: str

    mission_contract_id: str
    objective_fingerprint: str
    plan_id: str
    routing_plan_id: str

    payload_json: str
    payload_sha256: str

    checkpoint_id: str = field(
        init=False
    )

    durable_commit_authorized: bool = False
    mission_state_transition_requested: bool = False
    execution_authorized: bool = False
    learning_authorized: bool = False
    system_truth_asserted: bool = False

    def __post_init__(self) -> None:
        if self.schema != DURABLE_MISSION_SCHEMA:
            raise DurableMissionSchemaError(
                "Unsupported durable mission schema."
            )

        object.__setattr__(
            self,
            "generation",
            _positive_int(
                self.generation,
                "generation",
            ),
        )

        for name in (
            "runtime_checkpoint_schema",
            "mission_contract_id",
            "objective_fingerprint",
            "plan_id",
            "routing_plan_id",
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
            "runtime_checkpoint_sha256",
            _require_sha256(
                self.runtime_checkpoint_sha256,
                "runtime_checkpoint_sha256",
            ),
        )

        object.__setattr__(
            self,
            "payload_sha256",
            _require_sha256(
                self.payload_sha256,
                "payload_sha256",
            ),
        )

        try:
            payload = json.loads(
                self.payload_json
            )
        except json.JSONDecodeError as exc:
            raise DurableMissionIntegrityError(
                "Durable mission payload "
                "is not valid JSON."
            ) from exc

        canonical = _canonical_json(
            payload
        )

        if canonical != self.payload_json:
            raise DurableMissionIntegrityError(
                "Durable mission payload is "
                "not canonical JSON."
            )

        calculated = _sha256_text(
            canonical
        )

        if calculated != self.payload_sha256:
            raise DurableMissionIntegrityError(
                "Durable mission payload "
                "checksum mismatch."
            )

        required = {
            "schema",
            "generation",
            "runtime_checkpoint",
            "mission",
            "mission_contract",
            "mission_plan",
            "dag_state",
            "routing",
            "node_execution_evidence",
            "node_closures",
            "mission_verdict_evidence",
            "mission_verdict",
            "retry_state",
            "council_state",
            "recovery_information",
        }

        if set(payload) != required:
            raise DurableMissionSchemaError(
                "Durable mission payload "
                "surface mismatch."
            )

        if payload["schema"] != self.schema:
            raise DurableMissionSchemaError(
                "Payload schema mismatch."
            )

        if payload["generation"] != self.generation:
            raise DurableMissionIntegrityError(
                "Generation mismatch."
            )

        runtime = payload[
            "runtime_checkpoint"
        ]

        if (
            runtime.get("schema")
            != self.runtime_checkpoint_schema
            or runtime.get("sha256")
            != self.runtime_checkpoint_sha256
        ):
            raise DurableMissionIntegrityError(
                "Runtime checkpoint binding "
                "mismatch."
            )

        contract = payload[
            "mission_contract"
        ]

        plan = payload[
            "mission_plan"
        ]

        routing = payload[
            "routing"
        ]

        if (
            contract.get("contract_id")
            != self.mission_contract_id
            or contract.get(
                "objective_fingerprint"
            )
            != self.objective_fingerprint
            or plan.get("plan_id")
            != self.plan_id
            or routing.get(
                "routing_plan_id"
            )
            != self.routing_plan_id
        ):
            raise DurableMissionIntegrityError(
                "Durable mission identity "
                "binding mismatch."
            )

        if (
            plan.get(
                "mission_contract_id"
            )
            != self.mission_contract_id
            or routing.get("plan_id")
            != self.plan_id
        ):
            raise DurableMissionIntegrityError(
                "Durable mission lineage "
                "mismatch."
            )

        for name in (
            "durable_commit_authorized",
            "mission_state_transition_requested",
            "execution_authorized",
            "learning_authorized",
            "system_truth_asserted",
        ):
            if getattr(self, name) is not False:
                raise DurableMissionRecoveryInvariantError(
                    "Durable checkpoint cannot "
                    f"assert {name}."
                )

        object.__setattr__(
            self,
            "checkpoint_id",
            _stable_id(
                "DMC",
                {
                    "schema": self.schema,
                    "generation": (
                        self.generation
                    ),
                    "payload_sha256": (
                        self.payload_sha256
                    ),
                    "runtime_checkpoint_sha256": (
                        self
                        .runtime_checkpoint_sha256
                    ),
                },
            ),
        )

    @property
    def payload(self) -> dict[str, Any]:
        return json.loads(
            self.payload_json
        )

    def to_envelope(self) -> dict[str, Any]:
        body = {
            "schema": self.schema,
            "generation": self.generation,
            "runtime_checkpoint_schema": (
                self.runtime_checkpoint_schema
            ),
            "runtime_checkpoint_sha256": (
                self.runtime_checkpoint_sha256
            ),
            "mission_contract_id": (
                self.mission_contract_id
            ),
            "objective_fingerprint": (
                self.objective_fingerprint
            ),
            "plan_id": self.plan_id,
            "routing_plan_id": (
                self.routing_plan_id
            ),
            "payload": self.payload,
            "payload_sha256": (
                self.payload_sha256
            ),
        }

        return {
            "body": body,
            "sha256": _sha256_text(
                _canonical_json(body)
            ),
        }

    @classmethod
    def from_envelope(
        cls,
        envelope: Mapping[str, Any],
    ) -> GovernedDurableMissionCheckpoint:
        if not isinstance(
            envelope,
            Mapping,
        ):
            raise TypeError(
                "envelope must be a mapping."
            )

        body = envelope.get("body")
        digest = envelope.get("sha256")

        if not isinstance(body, Mapping):
            raise DurableMissionIntegrityError(
                "Durable mission envelope "
                "body missing."
            )

        if not isinstance(digest, str):
            raise DurableMissionIntegrityError(
                "Durable mission envelope "
                "checksum missing."
            )

        body_dict = dict(body)

        if (
            _sha256_text(
                _canonical_json(
                    body_dict
                )
            )
            != digest
        ):
            raise DurableMissionIntegrityError(
                "Durable mission envelope "
                "checksum mismatch."
            )

        payload = body_dict.get(
            "payload"
        )

        if not isinstance(
            payload,
            Mapping,
        ):
            raise DurableMissionIntegrityError(
                "Durable mission payload missing."
            )

        return cls(
            schema=body_dict["schema"],
            generation=body_dict[
                "generation"
            ],
            runtime_checkpoint_schema=(
                body_dict[
                    "runtime_checkpoint_schema"
                ]
            ),
            runtime_checkpoint_sha256=(
                body_dict[
                    "runtime_checkpoint_sha256"
                ]
            ),
            mission_contract_id=(
                body_dict[
                    "mission_contract_id"
                ]
            ),
            objective_fingerprint=(
                body_dict[
                    "objective_fingerprint"
                ]
            ),
            plan_id=body_dict[
                "plan_id"
            ],
            routing_plan_id=(
                body_dict[
                    "routing_plan_id"
                ]
            ),
            payload_json=_canonical_json(
                dict(payload)
            ),
            payload_sha256=body_dict[
                "payload_sha256"
            ],
        )


@dataclass(
    frozen=True,
    slots=True,
)
class MissionRecoveryEvidence:
    checkpoint_id: str
    checkpoint_payload_sha256: str
    objective_fingerprint: str

    checkpoint_integrity: RecoveryEvidenceState
    failure_state: FailureState

    fcr_assessment_state: RecoveryAssessmentState
    fcr_action: RecoveryPlanAction | None
    fcr_plan_id: str | None

    adaptive_state: AdaptiveRoutingState
    adaptive_decision_id: str | None

    target_generation: int

    evidence_source_ref: str

    evidence_id: str = field(
        init=False
    )

    def __post_init__(self) -> None:
        for name in (
            "checkpoint_id",
            "objective_fingerprint",
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
            "checkpoint_payload_sha256",
            _require_sha256(
                self.checkpoint_payload_sha256,
                "checkpoint_payload_sha256",
            ),
        )

        if not isinstance(
            self.checkpoint_integrity,
            RecoveryEvidenceState,
        ):
            raise TypeError(
                "checkpoint_integrity must be "
                "RecoveryEvidenceState."
            )

        if not isinstance(
            self.failure_state,
            FailureState,
        ):
            raise TypeError(
                "failure_state must be "
                "FailureState."
            )

        if not isinstance(
            self.fcr_assessment_state,
            RecoveryAssessmentState,
        ):
            raise TypeError(
                "fcr_assessment_state must be "
                "RecoveryAssessmentState."
            )

        if (
            self.fcr_action is not None
            and not isinstance(
                self.fcr_action,
                RecoveryPlanAction,
            )
        ):
            raise TypeError(
                "fcr_action must be "
                "RecoveryPlanAction or None."
            )

        object.__setattr__(
            self,
            "fcr_plan_id",
            _optional_text(
                self.fcr_plan_id,
                "fcr_plan_id",
            ),
        )

        if not isinstance(
            self.adaptive_state,
            AdaptiveRoutingState,
        ):
            raise TypeError(
                "adaptive_state must be "
                "AdaptiveRoutingState."
            )

        object.__setattr__(
            self,
            "adaptive_decision_id",
            _optional_text(
                self.adaptive_decision_id,
                "adaptive_decision_id",
            ),
        )

        object.__setattr__(
            self,
            "target_generation",
            _positive_int(
                self.target_generation,
                "target_generation",
            ),
        )

        if (
            self.fcr_action is None
            and self.fcr_plan_id is not None
        ):
            raise DurableMissionRecoveryInvariantError(
                "fcr_plan_id requires fcr_action."
            )

        if (
            self.fcr_action is not None
            and self.fcr_plan_id is None
        ):
            raise DurableMissionRecoveryInvariantError(
                "fcr_action requires fcr_plan_id."
            )

        if (
            self.adaptive_state
            is AdaptiveRoutingState.REPLAN_REQUIRED
            and self.adaptive_decision_id is None
        ):
            raise DurableMissionRecoveryInvariantError(
                "REPLAN_REQUIRED requires "
                "adaptive_decision_id."
            )

        object.__setattr__(
            self,
            "evidence_id",
            _stable_id(
                "MRE",
                {
                    "checkpoint_id": (
                        self.checkpoint_id
                    ),
                    "checkpoint_payload_sha256": (
                        self
                        .checkpoint_payload_sha256
                    ),
                    "objective_fingerprint": (
                        self.objective_fingerprint
                    ),
                    "checkpoint_integrity": (
                        self
                        .checkpoint_integrity
                        .value
                    ),
                    "failure_state": (
                        self.failure_state.value
                    ),
                    "fcr_assessment_state": (
                        self
                        .fcr_assessment_state
                        .value
                    ),
                    "fcr_action": (
                        self.fcr_action.value
                        if self.fcr_action
                        is not None
                        else None
                    ),
                    "fcr_plan_id": (
                        self.fcr_plan_id
                    ),
                    "adaptive_state": (
                        self.adaptive_state.value
                    ),
                    "adaptive_decision_id": (
                        self.adaptive_decision_id
                    ),
                    "target_generation": (
                        self.target_generation
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
class GovernedMissionRecoveryDecision:
    checkpoint_id: str
    evidence_id: str

    objective_fingerprint: str

    state: RecoveryDecisionState

    target_generation: int

    fcr_plan_id: str | None
    adaptive_decision_id: str | None

    reasons: tuple[str, ...]

    decision_id: str = field(
        init=False
    )

    ay_revalidation_required: bool = True
    ex_reauthorization_required: bool = True

    recovery_executed: bool = False
    rollback_executed: bool = False
    replanning_executed: bool = False
    mission_state_transition_requested: bool = False

    execution_authorized: bool = False
    effect_authorized: bool = False
    durable_commit_authorized: bool = False
    learning_authorized: bool = False
    system_truth_asserted: bool = False

    def __post_init__(self) -> None:
        for name in (
            "checkpoint_id",
            "evidence_id",
            "objective_fingerprint",
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
            RecoveryDecisionState,
        ):
            raise TypeError(
                "state must be "
                "RecoveryDecisionState."
            )

        object.__setattr__(
            self,
            "target_generation",
            _positive_int(
                self.target_generation,
                "target_generation",
            ),
        )

        for name in (
            "fcr_plan_id",
            "adaptive_decision_id",
        ):
            object.__setattr__(
                self,
                name,
                _optional_text(
                    getattr(self, name),
                    name,
                ),
            )

        object.__setattr__(
            self,
            "reasons",
            _normalized_tuple(
                self.reasons,
                "reason",
            ),
        )

        if self.ay_revalidation_required is not True:
            raise DurableMissionRecoveryInvariantError(
                "Recovery must require AY "
                "revalidation."
            )

        if self.ex_reauthorization_required is not True:
            raise DurableMissionRecoveryInvariantError(
                "Recovery must require EX "
                "reauthorization."
            )

        for name in (
            "recovery_executed",
            "rollback_executed",
            "replanning_executed",
            "mission_state_transition_requested",
            "execution_authorized",
            "effect_authorized",
            "durable_commit_authorized",
            "learning_authorized",
            "system_truth_asserted",
        ):
            if getattr(self, name) is not False:
                raise DurableMissionRecoveryInvariantError(
                    "Recovery decision cannot "
                    f"assert {name}."
                )

        object.__setattr__(
            self,
            "decision_id",
            _stable_id(
                "GMR",
                {
                    "checkpoint_id": (
                        self.checkpoint_id
                    ),
                    "evidence_id": (
                        self.evidence_id
                    ),
                    "objective_fingerprint": (
                        self.objective_fingerprint
                    ),
                    "state": self.state.value,
                    "target_generation": (
                        self.target_generation
                    ),
                    "fcr_plan_id": (
                        self.fcr_plan_id
                    ),
                    "adaptive_decision_id": (
                        self.adaptive_decision_id
                    ),
                    "reasons": list(
                        self.reasons
                    ),
                    "ay_revalidation_required": True,
                    "ex_reauthorization_required": True,
                },
            ),
        )


class GovernedDurableMission:
    @staticmethod
    def checkpoint(
        *,
        canonical_mission: Mapping[
            str,
            Any,
        ],
        contract: MissionContract,
        plan: GovernedMissionPlan,
        routing: GovernedExecutionRoutingPlan,
        node_execution_evidence: Iterable[
            NodeExecutionClosureEvidence
        ],
        node_closures: Iterable[
            GovernedNodeClosure
        ],
        mission_verdict_evidence: (
            MissionVerdictEvidence | None
        ),
        mission_verdict: (
            GovernedMissionVerdict | None
        ),
        retries: Iterable[
            DurableRetryRecord
        ],
        councils: Iterable[
            DurableCouncilState
        ],
        recovery: DurableRecoveryInformation,
        runtime_checkpoint_schema: str,
        runtime_checkpoint_sha256: str,
        generation: int,
    ) -> GovernedDurableMissionCheckpoint:
        if not isinstance(
            contract,
            MissionContract,
        ):
            raise TypeError(
                "contract must be "
                "MissionContract."
            )

        if not isinstance(
            plan,
            GovernedMissionPlan,
        ):
            raise TypeError(
                "plan must be "
                "GovernedMissionPlan."
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
            recovery,
            DurableRecoveryInformation,
        ):
            raise TypeError(
                "recovery must be "
                "DurableRecoveryInformation."
            )

        mission = _validate_canonical_mission(
            canonical_mission
        )

        generation = _positive_int(
            generation,
            "generation",
        )

        runtime_checkpoint_schema = (
            _required_text(
                runtime_checkpoint_schema,
                "runtime_checkpoint_schema",
            )
        )

        runtime_checkpoint_sha256 = (
            _require_sha256(
                runtime_checkpoint_sha256,
                "runtime_checkpoint_sha256",
            )
        )

        if (
            plan.mission_contract_id
            != contract.contract_id
        ):
            raise DurableMissionRecoveryInvariantError(
                "Plan does not bind supplied "
                "mission contract."
            )

        if routing.plan_id != plan.plan_id:
            raise DurableMissionRecoveryInvariantError(
                "Routing does not bind supplied plan."
            )

        if (
            str(
                mission["objective"]
            ).strip()
            != contract.objective
        ):
            raise DurableMissionRecoveryInvariantError(
                "Canonical mission objective "
                "does not match contract."
            )

        execution_rows = tuple(
            node_execution_evidence
        )

        closure_rows = tuple(
            node_closures
        )

        retry_rows = tuple(
            retries
        )

        council_rows = tuple(
            councils
        )

        if not all(
            isinstance(
                item,
                NodeExecutionClosureEvidence,
            )
            for item in execution_rows
        ):
            raise TypeError(
                "node_execution_evidence must "
                "contain "
                "NodeExecutionClosureEvidence."
            )

        if not all(
            isinstance(
                item,
                GovernedNodeClosure,
            )
            for item in closure_rows
        ):
            raise TypeError(
                "node_closures must contain "
                "GovernedNodeClosure."
            )

        if not all(
            isinstance(
                item,
                DurableRetryRecord,
            )
            for item in retry_rows
        ):
            raise TypeError(
                "retries must contain "
                "DurableRetryRecord."
            )

        if not all(
            isinstance(
                item,
                DurableCouncilState,
            )
            for item in council_rows
        ):
            raise TypeError(
                "councils must contain "
                "DurableCouncilState."
            )

        planned_node_ids = {
            node.node_id
            for node in plan.nodes
        }

        route_node_ids = {
            route.node_id
            for route in routing.routes
        }

        if route_node_ids != planned_node_ids:
            raise DurableMissionRecoveryInvariantError(
                "Routing must exactly cover "
                "planned nodes."
            )

        execution_node_ids = [
            item.node_id
            for item in execution_rows
        ]

        closure_node_ids = [
            item.node_id
            for item in closure_rows
        ]

        retry_node_ids = [
            item.node_id
            for item in retry_rows
        ]

        if (
            len(execution_node_ids)
            != len(set(execution_node_ids))
            or len(closure_node_ids)
            != len(set(closure_node_ids))
            or len(retry_node_ids)
            != len(set(retry_node_ids))
        ):
            raise DurableMissionRecoveryInvariantError(
                "Durable node state must be unique."
            )

        for node_id in (
            set(execution_node_ids)
            | set(closure_node_ids)
            | set(retry_node_ids)
        ):
            if node_id not in planned_node_ids:
                raise DurableMissionRecoveryInvariantError(
                    "Durable node state contains "
                    "unknown plan node."
                )

        council_ids = [
            item.council_id
            for item in council_rows
        ]

        if len(council_ids) != len(
            set(council_ids)
        ):
            raise DurableMissionRecoveryInvariantError(
                "Council durable state "
                "must be unique."
            )

        required_councils = {
            node.council_id
            for node in plan.nodes
        }

        if (
            set(council_ids)
            != required_councils
        ):
            raise DurableMissionRecoveryInvariantError(
                "Council durable state must "
                "exactly cover plan Councils."
            )

        if mission_verdict_evidence is not None:
            if not isinstance(
                mission_verdict_evidence,
                MissionVerdictEvidence,
            ):
                raise TypeError(
                    "mission_verdict_evidence "
                    "must be "
                    "MissionVerdictEvidence "
                    "or None."
                )

            if (
                mission_verdict_evidence.plan_id
                != plan.plan_id
            ):
                raise DurableMissionRecoveryInvariantError(
                    "Mission verdict evidence "
                    "belongs to another plan."
                )

        if mission_verdict is not None:
            if not isinstance(
                mission_verdict,
                GovernedMissionVerdict,
            ):
                raise TypeError(
                    "mission_verdict must be "
                    "GovernedMissionVerdict "
                    "or None."
                )

            if (
                mission_verdict.plan_id
                != plan.plan_id
            ):
                raise DurableMissionRecoveryInvariantError(
                    "Mission verdict belongs "
                    "to another plan."
                )

        objective = _objective_fingerprint(
            contract
        )

        payload = {
            "schema": (
                DURABLE_MISSION_SCHEMA
            ),
            "generation": generation,
            "runtime_checkpoint": {
                "schema": (
                    runtime_checkpoint_schema
                ),
                "sha256": (
                    runtime_checkpoint_sha256
                ),
            },
            "mission": mission,
            "mission_contract": {
                "contract_id": (
                    contract.contract_id
                ),
                "objective": contract.objective,
                "objective_fingerprint": (
                    objective
                ),
                "scope": contract.scope,
                "requested_output": (
                    contract.requested_output
                ),
                "constraints": list(
                    contract.constraints
                ),
                "acceptance_criteria": list(
                    contract.acceptance_criteria
                ),
                "authority_requirements": list(
                    contract.authority_requirements
                ),
                "evidence_obligations": list(
                    contract.evidence_obligations
                ),
            },
            "mission_plan": (
                _plan_payload(plan)
            ),
            "dag_state": (
                _dag_payload(plan)
            ),
            "routing": (
                _routing_payload(routing)
            ),
            "node_execution_evidence": [
                _node_execution_evidence_payload(
                    item
                )
                for item in sorted(
                    execution_rows,
                    key=lambda item: (
                        item.node_id
                    ),
                )
            ],
            "node_closures": [
                _node_closure_payload(
                    item
                )
                for item in sorted(
                    closure_rows,
                    key=lambda item: (
                        item.node_id
                    ),
                )
            ],
            "mission_verdict_evidence": (
                _mission_verdict_evidence_payload(
                    mission_verdict_evidence
                )
                if mission_verdict_evidence
                is not None
                else None
            ),
            "mission_verdict": (
                _mission_verdict_payload(
                    mission_verdict
                )
                if mission_verdict
                is not None
                else None
            ),
            "retry_state": [
                item.to_dict()
                for item in sorted(
                    retry_rows,
                    key=lambda item: (
                        item.node_id
                    ),
                )
            ],
            "council_state": [
                item.to_dict()
                for item in sorted(
                    council_rows,
                    key=lambda item: (
                        item.council_id
                    ),
                )
            ],
            "recovery_information": (
                recovery.to_dict()
            ),
        }

        payload_json = _canonical_json(
            payload
        )

        return GovernedDurableMissionCheckpoint(
            schema=DURABLE_MISSION_SCHEMA,
            generation=generation,
            runtime_checkpoint_schema=(
                runtime_checkpoint_schema
            ),
            runtime_checkpoint_sha256=(
                runtime_checkpoint_sha256
            ),
            mission_contract_id=(
                contract.contract_id
            ),
            objective_fingerprint=(
                objective
            ),
            plan_id=plan.plan_id,
            routing_plan_id=(
                routing.routing_plan_id
            ),
            payload_json=payload_json,
            payload_sha256=(
                _sha256_text(
                    payload_json
                )
            ),
        )


class GovernedDurableMissionStore:
    @staticmethod
    def save(
        checkpoint: GovernedDurableMissionCheckpoint,
        path: str | Path,
    ) -> Path:
        if not isinstance(
            checkpoint,
            GovernedDurableMissionCheckpoint,
        ):
            raise TypeError(
                "checkpoint must be "
                "GovernedDurableMissionCheckpoint."
            )

        target = Path(path)

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        envelope_json = (
            _canonical_json(
                checkpoint.to_envelope()
            )
        )

        fd, temporary = tempfile.mkstemp(
            prefix=(
                "."
                + target.name
                + "."
            ),
            suffix=".tmp",
            dir=str(target.parent),
            text=True,
        )

        try:
            with os.fdopen(
                fd,
                "w",
                encoding="utf-8",
            ) as handle:
                handle.write(
                    envelope_json
                )
                handle.flush()
                os.fsync(
                    handle.fileno()
                )

            os.replace(
                temporary,
                target,
            )

        except Exception:
            try:
                os.unlink(
                    temporary
                )
            except FileNotFoundError:
                pass
            raise

        return target

    @staticmethod
    def load(
        path: str | Path,
    ) -> GovernedDurableMissionCheckpoint:
        target = Path(path)

        try:
            envelope = json.loads(
                target.read_text(
                    encoding="utf-8"
                )
            )
        except (
            OSError,
            json.JSONDecodeError,
        ) as exc:
            raise DurableMissionIntegrityError(
                "Cannot load durable mission "
                "checkpoint."
            ) from exc

        return (
            GovernedDurableMissionCheckpoint
            .from_envelope(
                envelope
            )
        )


class GovernedAutonomousMissionRecovery:
    @staticmethod
    def compose(
        checkpoint: GovernedDurableMissionCheckpoint,
        evidence: MissionRecoveryEvidence,
    ) -> GovernedMissionRecoveryDecision:
        if not isinstance(
            checkpoint,
            GovernedDurableMissionCheckpoint,
        ):
            raise TypeError(
                "checkpoint must be "
                "GovernedDurableMissionCheckpoint."
            )

        if not isinstance(
            evidence,
            MissionRecoveryEvidence,
        ):
            raise TypeError(
                "evidence must be "
                "MissionRecoveryEvidence."
            )

        if (
            evidence.checkpoint_id
            != checkpoint.checkpoint_id
            or evidence.checkpoint_payload_sha256
            != checkpoint.payload_sha256
        ):
            raise DurableMissionRecoveryInvariantError(
                "Recovery evidence is not "
                "bound to exact checkpoint."
            )

        if (
            evidence.objective_fingerprint
            != checkpoint.objective_fingerprint
        ):
            raise DurableMissionRecoveryInvariantError(
                "Recovery cannot change "
                "mission objective."
            )

        if (
            evidence.target_generation
            > checkpoint.generation
        ):
            raise DurableMissionRecoveryInvariantError(
                "Recovery cannot target a "
                "future checkpoint generation."
            )

        reasons: list[str] = []

        if (
            evidence.checkpoint_integrity
            is RecoveryEvidenceState.FAIL
        ):
            state = (
                RecoveryDecisionState
                .UNRECOVERABLE
            )

            reasons.append(
                "Checkpoint integrity failed."
            )

        elif (
            evidence.checkpoint_integrity
            is RecoveryEvidenceState.UNKNOWN
            or evidence.failure_state
            is FailureState.UNKNOWN
            or evidence.fcr_assessment_state
            is RecoveryAssessmentState.UNKNOWN
            or evidence.adaptive_state
            is AdaptiveRoutingState.UNKNOWN
        ):
            state = RecoveryDecisionState.UNKNOWN

            reasons.append(
                "Recovery evidence is unknown "
                "or incomplete."
            )

        elif (
            evidence.failure_state
            is FailureState.NOT_DETECTED
        ):
            if (
                evidence.fcr_assessment_state
                is not RecoveryAssessmentState.HEALTHY
            ):
                raise DurableMissionRecoveryInvariantError(
                    "No-failure evidence must "
                    "compose HEALTHY FCR state."
                )

            if evidence.fcr_action is not None:
                raise DurableMissionRecoveryInvariantError(
                    "Healthy recovery state "
                    "cannot include FCR action."
                )

            state = RecoveryDecisionState.HEALTHY

            reasons.append(
                "No mission-level failure "
                "was detected."
            )

        elif (
            evidence.failure_state
            is FailureState.DETECTED
        ):
            if (
                evidence.adaptive_state
                is AdaptiveRoutingState
                .REPLAN_REQUIRED
            ):
                state = (
                    RecoveryDecisionState
                    .REPLAN_PROPOSED
                )

                reasons.append(
                    "Adaptive routing requires "
                    "mission replanning."
                )

            elif (
                evidence.fcr_assessment_state
                is RecoveryAssessmentState
                .CONTAINMENT_REQUIRED
            ):
                if (
                    evidence.fcr_action
                    is not RecoveryPlanAction
                    .CONTAINMENT
                ):
                    raise DurableMissionRecoveryInvariantError(
                        "Containment-required "
                        "state requires FCR "
                        "containment plan."
                    )

                state = (
                    RecoveryDecisionState
                    .CONTAINMENT_PROPOSED
                )

                reasons.append(
                    "Existing FCR evidence "
                    "requires containment."
                )

            elif (
                evidence.fcr_assessment_state
                is RecoveryAssessmentState
                .ROLLBACK_REQUIRED
            ):
                if (
                    evidence.fcr_action
                    is not RecoveryPlanAction
                    .ROLLBACK
                ):
                    raise DurableMissionRecoveryInvariantError(
                        "Rollback-required state "
                        "requires FCR rollback plan."
                    )

                state = (
                    RecoveryDecisionState
                    .ROLLBACK_PROPOSED
                )

                reasons.append(
                    "Existing FCR evidence "
                    "requires rollback."
                )

            elif (
                evidence.fcr_assessment_state
                is RecoveryAssessmentState
                .RECOVERY_REQUIRED
            ):
                if (
                    evidence.fcr_action
                    is not RecoveryPlanAction
                    .RECOVERY
                ):
                    raise DurableMissionRecoveryInvariantError(
                        "Recovery-required state "
                        "requires FCR recovery plan."
                    )

                state = (
                    RecoveryDecisionState
                    .RESUME_PROPOSED
                )

                reasons.append(
                    "Existing FCR evidence "
                    "supports governed recovery "
                    "from durable mission state."
                )

            elif (
                evidence.fcr_assessment_state
                is RecoveryAssessmentState
                .UNRECOVERABLE
            ):
                if evidence.fcr_action is not None:
                    raise DurableMissionRecoveryInvariantError(
                        "UNRECOVERABLE cannot "
                        "include executable "
                        "recovery plan."
                    )

                state = (
                    RecoveryDecisionState
                    .UNRECOVERABLE
                )

                reasons.append(
                    "Existing FCR assessment "
                    "declares recovery unsafe."
                )

            else:
                raise DurableMissionRecoveryInvariantError(
                    "Detected failure and FCR "
                    "state are inconsistent."
                )

        else:
            raise DurableMissionRecoveryInvariantError(
                "Unsupported failure state."
            )

        return GovernedMissionRecoveryDecision(
            checkpoint_id=(
                checkpoint.checkpoint_id
            ),
            evidence_id=evidence.evidence_id,
            objective_fingerprint=(
                checkpoint.objective_fingerprint
            ),
            state=state,
            target_generation=(
                evidence.target_generation
            ),
            fcr_plan_id=(
                evidence.fcr_plan_id
            ),
            adaptive_decision_id=(
                evidence.adaptive_decision_id
            ),
            reasons=tuple(reasons),
        )


__all__ = [
    "GOVERNED_DURABLE_MISSION_RECOVERY_VERSION",
    "DURABLE_MISSION_SCHEMA",
    "DurableMissionRecoveryInvariantError",
    "DurableMissionIntegrityError",
    "DurableMissionSchemaError",
    "RecoveryDecisionState",
    "DurableRetryRecord",
    "DurableCouncilState",
    "DurableRecoveryInformation",
    "GovernedDurableMissionCheckpoint",
    "MissionRecoveryEvidence",
    "GovernedMissionRecoveryDecision",
    "GovernedDurableMission",
    "GovernedDurableMissionStore",
    "GovernedAutonomousMissionRecovery",
]
