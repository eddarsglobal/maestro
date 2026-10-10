from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


GOVERNED_FAILURE_CONTAINMENT_RECOVERY_VERSION = 1


class GovernedRecoveryInvariantError(
    ValueError
):
    pass


class EvidenceState(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class FailureState(StrEnum):
    DETECTED = "DETECTED"
    NOT_DETECTED = "NOT_DETECTED"
    UNKNOWN = "UNKNOWN"


class ContainmentState(StrEnum):
    CONTAINED = "CONTAINED"
    NOT_CONTAINED = "NOT_CONTAINED"
    UNKNOWN = "UNKNOWN"


class RecoveryAssessmentState(StrEnum):
    HEALTHY = "HEALTHY"
    CONTAINMENT_REQUIRED = "CONTAINMENT_REQUIRED"
    ROLLBACK_REQUIRED = "ROLLBACK_REQUIRED"
    RECOVERY_REQUIRED = "RECOVERY_REQUIRED"
    UNRECOVERABLE = "UNRECOVERABLE"
    UNKNOWN = "UNKNOWN"


class RecoveryPlanAction(StrEnum):
    CONTAINMENT = "CONTAINMENT"
    ROLLBACK = "ROLLBACK"
    RECOVERY = "RECOVERY"


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
        raise GovernedRecoveryInvariantError(
            f"{name} must not be empty."
        )

    if "\x00" in value:
        raise GovernedRecoveryInvariantError(
            f"{name} must not contain NUL."
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


def _aggregate(
    values: tuple[
        EvidenceState,
        ...,
    ],
) -> EvidenceState:
    if any(
        value is EvidenceState.FAIL
        for value in values
    ):
        return EvidenceState.FAIL

    if any(
        value is EvidenceState.UNKNOWN
        for value in values
    ):
        return EvidenceState.UNKNOWN

    return EvidenceState.PASS


def _assert_passive(
    *,
    containment_authorized: bool,
    containment_executed: bool,
    rollback_authorized: bool,
    rollback_executed: bool,
    recovery_authorized: bool,
    recovery_executed: bool,
    activation_authorized: bool,
    release_authorized: bool,
    source_state_mutation_requested: bool,
    source_state_deletion_requested: bool,
    system_truth_asserted: bool,
) -> None:
    flags = {
        "containment_authorized": containment_authorized,
        "containment_executed": containment_executed,
        "rollback_authorized": rollback_authorized,
        "rollback_executed": rollback_executed,
        "recovery_authorized": recovery_authorized,
        "recovery_executed": recovery_executed,
        "activation_authorized": activation_authorized,
        "release_authorized": release_authorized,
        "source_state_mutation_requested": (
            source_state_mutation_requested
        ),
        "source_state_deletion_requested": (
            source_state_deletion_requested
        ),
        "system_truth_asserted": (
            system_truth_asserted
        ),
    }

    asserted = sorted(
        name
        for name, value in flags.items()
        if value is not False
    )

    if asserted:
        raise GovernedRecoveryInvariantError(
            "FCR evidence and plans cannot assert "
            "containment, rollback, recovery, "
            "activation, release, mutation, deletion "
            "or truth authority: "
            + ", ".join(asserted)
        )


@dataclass(
    frozen=True,
    slots=True,
)
class UpdateRecoveryContext:
    subject_id: str
    update_generation_id: str
    current_state_id: str
    last_known_good_state_id: str

    preservation_requirements: tuple[
        str,
        ...,
    ]

    context_id: str = field(
        init=False
    )

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "subject_id",
            "update_generation_id",
            "current_state_id",
            "last_known_good_state_id",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(self, name),
                    name,
                ),
            )

        requirements = tuple(
            sorted(
                _required_text(
                    item,
                    "preservation_requirement",
                )
                for item
                in self.preservation_requirements
            )
        )

        if not requirements:
            raise GovernedRecoveryInvariantError(
                "Recovery context requires at least "
                "one preservation requirement."
            )

        if len(requirements) != len(
            set(requirements)
        ):
            raise GovernedRecoveryInvariantError(
                "Preservation requirements "
                "must be unique."
            )

        object.__setattr__(
            self,
            "preservation_requirements",
            requirements,
        )

        object.__setattr__(
            self,
            "context_id",
            _stable_id(
                "FRC",
                {
                    "version": (
                        GOVERNED_FAILURE_CONTAINMENT_RECOVERY_VERSION
                    ),
                    "subject_id": self.subject_id,
                    "update_generation_id": (
                        self.update_generation_id
                    ),
                    "current_state_id": (
                        self.current_state_id
                    ),
                    "last_known_good_state_id": (
                        self.last_known_good_state_id
                    ),
                    "preservation_requirements": list(
                        requirements
                    ),
                },
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "version": (
                GOVERNED_FAILURE_CONTAINMENT_RECOVERY_VERSION
            ),
            "context_id": self.context_id,
            "subject_id": self.subject_id,
            "update_generation_id": (
                self.update_generation_id
            ),
            "current_state_id": (
                self.current_state_id
            ),
            "last_known_good_state_id": (
                self.last_known_good_state_id
            ),
            "preservation_requirements": list(
                self.preservation_requirements
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class RecoveryPreservationEvidence:
    requirement_id: str
    rollback_state: EvidenceState
    recovery_state: EvidenceState

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "requirement_id",
            _required_text(
                self.requirement_id,
                "requirement_id",
            ),
        )

        if not isinstance(
            self.rollback_state,
            EvidenceState,
        ):
            raise TypeError(
                "rollback_state must be EvidenceState."
            )

        if not isinstance(
            self.recovery_state,
            EvidenceState,
        ):
            raise TypeError(
                "recovery_state must be EvidenceState."
            )

    def to_dict(
        self,
    ) -> dict[str, str]:
        return {
            "requirement_id": self.requirement_id,
            "rollback_state": (
                self.rollback_state.value
            ),
            "recovery_state": (
                self.recovery_state.value
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class FailureRecoveryEvidence:
    context_id: str

    failure_state: FailureState
    current_state_integrity: EvidenceState

    containment_capability: EvidenceState
    containment_state: ContainmentState

    rollback_path_available: EvidenceState
    recovery_path_available: EvidenceState

    preservation: tuple[
        RecoveryPreservationEvidence,
        ...,
    ]

    evidence_source_ref: str

    evidence_id: str = field(
        init=False
    )

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "context_id",
            _required_text(
                self.context_id,
                "context_id",
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

        if not isinstance(
            self.failure_state,
            FailureState,
        ):
            raise TypeError(
                "failure_state must be FailureState."
            )

        if not isinstance(
            self.current_state_integrity,
            EvidenceState,
        ):
            raise TypeError(
                "current_state_integrity must "
                "be EvidenceState."
            )

        if not isinstance(
            self.containment_capability,
            EvidenceState,
        ):
            raise TypeError(
                "containment_capability must "
                "be EvidenceState."
            )

        if not isinstance(
            self.containment_state,
            ContainmentState,
        ):
            raise TypeError(
                "containment_state must "
                "be ContainmentState."
            )

        if not isinstance(
            self.rollback_path_available,
            EvidenceState,
        ):
            raise TypeError(
                "rollback_path_available must "
                "be EvidenceState."
            )

        if not isinstance(
            self.recovery_path_available,
            EvidenceState,
        ):
            raise TypeError(
                "recovery_path_available must "
                "be EvidenceState."
            )

        if (
            self.containment_state
            is ContainmentState.CONTAINED
            and self.containment_capability
            is not EvidenceState.PASS
        ):
            raise GovernedRecoveryInvariantError(
                "CONTAINED requires explicit PASS "
                "containment capability evidence."
            )

        raw_rows = tuple(
            self.preservation
        )

        if not raw_rows:
            raise GovernedRecoveryInvariantError(
                "Recovery preservation evidence "
                "must not be empty."
            )

        if not all(
            isinstance(
                item,
                RecoveryPreservationEvidence,
            )
            for item in raw_rows
        ):
            raise TypeError(
                "preservation must contain "
                "RecoveryPreservationEvidence only."
            )

        rows = tuple(
            sorted(
                raw_rows,
                key=lambda item: (
                    item.requirement_id
                ),
            )
        )

        ids = [
            item.requirement_id
            for item in rows
        ]

        if len(ids) != len(set(ids)):
            raise GovernedRecoveryInvariantError(
                "Recovery preservation evidence "
                "requirements must be unique."
            )

        object.__setattr__(
            self,
            "preservation",
            rows,
        )

        object.__setattr__(
            self,
            "evidence_id",
            _stable_id(
                "FRE",
                {
                    "context_id": self.context_id,
                    "failure_state": (
                        self.failure_state.value
                    ),
                    "current_state_integrity": (
                        self.current_state_integrity.value
                    ),
                    "containment_capability": (
                        self.containment_capability.value
                    ),
                    "containment_state": (
                        self.containment_state.value
                    ),
                    "rollback_path_available": (
                        self.rollback_path_available.value
                    ),
                    "recovery_path_available": (
                        self.recovery_path_available.value
                    ),
                    "preservation": [
                        item.to_dict()
                        for item in rows
                    ],
                    "evidence_source_ref": (
                        self.evidence_source_ref
                    ),
                },
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "context_id": self.context_id,
            "failure_state": (
                self.failure_state.value
            ),
            "current_state_integrity": (
                self.current_state_integrity.value
            ),
            "containment_capability": (
                self.containment_capability.value
            ),
            "containment_state": (
                self.containment_state.value
            ),
            "rollback_path_available": (
                self.rollback_path_available.value
            ),
            "recovery_path_available": (
                self.recovery_path_available.value
            ),
            "preservation": [
                item.to_dict()
                for item in self.preservation
            ],
            "evidence_source_ref": (
                self.evidence_source_ref
            ),
        }


def _derive_recovery_route(
    *,
    path: EvidenceState,
    preservation: EvidenceState,
    reasons: list[str],
) -> RecoveryAssessmentState:
    if path is EvidenceState.UNKNOWN:
        reasons.append(
            "recovery path availability unknown"
        )
        return RecoveryAssessmentState.UNKNOWN

    if path is EvidenceState.FAIL:
        reasons.append(
            "recovery path unavailable"
        )
        return RecoveryAssessmentState.UNRECOVERABLE

    if preservation is EvidenceState.UNKNOWN:
        reasons.append(
            "recovery preservation unknown"
        )
        return RecoveryAssessmentState.UNKNOWN

    if preservation is EvidenceState.FAIL:
        reasons.append(
            "recovery preservation failed"
        )
        return RecoveryAssessmentState.UNRECOVERABLE

    reasons.append(
        "explicit preserving recovery path available"
    )
    return RecoveryAssessmentState.RECOVERY_REQUIRED


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedRecoveryAssessment:
    context: UpdateRecoveryContext
    evidence: FailureRecoveryEvidence

    assessment_id: str = field(
        init=False
    )

    state: RecoveryAssessmentState = field(
        init=False
    )

    reasons: tuple[
        str,
        ...,
    ] = field(
        init=False
    )

    containment_authorized: bool = False
    containment_executed: bool = False
    rollback_authorized: bool = False
    rollback_executed: bool = False
    recovery_authorized: bool = False
    recovery_executed: bool = False
    activation_authorized: bool = False
    release_authorized: bool = False
    source_state_mutation_requested: bool = False
    source_state_deletion_requested: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.context,
            UpdateRecoveryContext,
        ):
            raise TypeError(
                "context must be UpdateRecoveryContext."
            )

        if not isinstance(
            self.evidence,
            FailureRecoveryEvidence,
        ):
            raise TypeError(
                "evidence must be FailureRecoveryEvidence."
            )

        if (
            self.evidence.context_id
            != self.context.context_id
        ):
            raise GovernedRecoveryInvariantError(
                "Failure/recovery evidence is not "
                "bound to the supplied recovery context."
            )

        observed = tuple(
            item.requirement_id
            for item in self.evidence.preservation
        )

        if observed != (
            self.context.preservation_requirements
        ):
            raise GovernedRecoveryInvariantError(
                "Recovery preservation evidence "
                "must cover exactly the context "
                "preservation requirements."
            )

        rollback_preservation = _aggregate(
            tuple(
                item.rollback_state
                for item in self.evidence.preservation
            )
        )

        recovery_preservation = _aggregate(
            tuple(
                item.recovery_state
                for item in self.evidence.preservation
            )
        )

        reasons: list[str] = []

        failure = self.evidence.failure_state
        integrity = (
            self.evidence.current_state_integrity
        )

        if (
            failure is FailureState.UNKNOWN
            or integrity is EvidenceState.UNKNOWN
        ):
            if failure is FailureState.UNKNOWN:
                reasons.append(
                    "failure state unknown"
                )

            if integrity is EvidenceState.UNKNOWN:
                reasons.append(
                    "current state integrity unknown"
                )

            state = RecoveryAssessmentState.UNKNOWN

        elif failure is FailureState.NOT_DETECTED:
            if integrity is EvidenceState.PASS:
                state = RecoveryAssessmentState.HEALTHY
                reasons.append(
                    "no failure detected and "
                    "current state integrity passed"
                )
            else:
                state = RecoveryAssessmentState.UNKNOWN
                reasons.append(
                    "state integrity failure conflicts "
                    "with no detected failure"
                )

        else:
            containment_state = (
                self.evidence.containment_state
            )

            containment_capability = (
                self.evidence.containment_capability
            )

            if (
                containment_state
                is ContainmentState.UNKNOWN
            ):
                state = RecoveryAssessmentState.UNKNOWN
                reasons.append(
                    "containment state unknown"
                )

            elif (
                containment_state
                is ContainmentState.NOT_CONTAINED
            ):
                if (
                    containment_capability
                    is EvidenceState.PASS
                ):
                    state = (
                        RecoveryAssessmentState
                        .CONTAINMENT_REQUIRED
                    )
                    reasons.append(
                        "failure detected and "
                        "containment is available "
                        "but not yet confirmed"
                    )

                elif (
                    containment_capability
                    is EvidenceState.UNKNOWN
                ):
                    state = RecoveryAssessmentState.UNKNOWN
                    reasons.append(
                        "containment capability unknown"
                    )

                else:
                    state = (
                        RecoveryAssessmentState
                        .UNRECOVERABLE
                    )
                    reasons.append(
                        "failure cannot be contained"
                    )

            elif integrity is EvidenceState.FAIL:
                reasons.append(
                    "current state integrity failed"
                )

                state = _derive_recovery_route(
                    path=(
                        self.evidence
                        .recovery_path_available
                    ),
                    preservation=(
                        recovery_preservation
                    ),
                    reasons=reasons,
                )

            else:
                rollback_path = (
                    self.evidence
                    .rollback_path_available
                )

                if rollback_path is EvidenceState.UNKNOWN:
                    state = RecoveryAssessmentState.UNKNOWN
                    reasons.append(
                        "rollback path availability unknown"
                    )

                elif (
                    rollback_path is EvidenceState.PASS
                    and rollback_preservation
                    is EvidenceState.PASS
                ):
                    state = (
                        RecoveryAssessmentState
                        .ROLLBACK_REQUIRED
                    )
                    reasons.append(
                        "failure contained and preserving "
                        "rollback path available"
                    )

                elif (
                    rollback_path is EvidenceState.PASS
                    and rollback_preservation
                    is EvidenceState.UNKNOWN
                ):
                    state = RecoveryAssessmentState.UNKNOWN
                    reasons.append(
                        "rollback preservation unknown"
                    )

                else:
                    if (
                        rollback_path is EvidenceState.FAIL
                    ):
                        reasons.append(
                            "rollback path unavailable"
                        )

                    if (
                        rollback_preservation
                        is EvidenceState.FAIL
                    ):
                        reasons.append(
                            "rollback preservation failed"
                        )

                    state = _derive_recovery_route(
                        path=(
                            self.evidence
                            .recovery_path_available
                        ),
                        preservation=(
                            recovery_preservation
                        ),
                        reasons=reasons,
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

        object.__setattr__(
            self,
            "assessment_id",
            _stable_id(
                "FRA",
                {
                    "context_id": (
                        self.context.context_id
                    ),
                    "evidence_id": (
                        self.evidence.evidence_id
                    ),
                    "state": state.value,
                    "reasons": list(reasons),
                },
            ),
        )

        _assert_passive(
            containment_authorized=(
                self.containment_authorized
            ),
            containment_executed=(
                self.containment_executed
            ),
            rollback_authorized=(
                self.rollback_authorized
            ),
            rollback_executed=(
                self.rollback_executed
            ),
            recovery_authorized=(
                self.recovery_authorized
            ),
            recovery_executed=(
                self.recovery_executed
            ),
            activation_authorized=(
                self.activation_authorized
            ),
            release_authorized=(
                self.release_authorized
            ),
            source_state_mutation_requested=(
                self.source_state_mutation_requested
            ),
            source_state_deletion_requested=(
                self.source_state_deletion_requested
            ),
            system_truth_asserted=(
                self.system_truth_asserted
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "version": (
                GOVERNED_FAILURE_CONTAINMENT_RECOVERY_VERSION
            ),
            "assessment_id": (
                self.assessment_id
            ),
            "context": self.context.to_dict(),
            "evidence": self.evidence.to_dict(),
            "state": self.state.value,
            "reasons": list(self.reasons),
            "containment_authorized": False,
            "containment_executed": False,
            "rollback_authorized": False,
            "rollback_executed": False,
            "recovery_authorized": False,
            "recovery_executed": False,
            "activation_authorized": False,
            "release_authorized": False,
            "source_state_mutation_requested": False,
            "source_state_deletion_requested": False,
            "system_truth_asserted": False,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class RecoveryPlanStep:
    ordinal: int
    step_id: str
    description: str

    def __post_init__(
        self,
    ) -> None:
        if (
            not isinstance(self.ordinal, int)
            or isinstance(self.ordinal, bool)
            or self.ordinal < 1
        ):
            raise GovernedRecoveryInvariantError(
                "ordinal must be an integer >= 1."
            )

        object.__setattr__(
            self,
            "step_id",
            _required_text(
                self.step_id,
                "step_id",
            ),
        )

        object.__setattr__(
            self,
            "description",
            _required_text(
                self.description,
                "description",
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "ordinal": self.ordinal,
            "step_id": self.step_id,
            "description": self.description,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedRecoveryPlan:
    assessment: GovernedRecoveryAssessment
    action: RecoveryPlanAction

    steps: tuple[
        RecoveryPlanStep,
        ...,
    ]

    baseline_state_id: str | None = None

    plan_id: str = field(
        init=False
    )

    containment_authorized: bool = False
    containment_executed: bool = False
    rollback_authorized: bool = False
    rollback_executed: bool = False
    recovery_authorized: bool = False
    recovery_executed: bool = False
    activation_authorized: bool = False
    release_authorized: bool = False
    source_state_mutation_requested: bool = False
    source_state_deletion_requested: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.assessment,
            GovernedRecoveryAssessment,
        ):
            raise TypeError(
                "assessment must be "
                "GovernedRecoveryAssessment."
            )

        if not isinstance(
            self.action,
            RecoveryPlanAction,
        ):
            raise TypeError(
                "action must be RecoveryPlanAction."
            )

        expected_state = {
            RecoveryPlanAction.CONTAINMENT: (
                RecoveryAssessmentState
                .CONTAINMENT_REQUIRED
            ),
            RecoveryPlanAction.ROLLBACK: (
                RecoveryAssessmentState
                .ROLLBACK_REQUIRED
            ),
            RecoveryPlanAction.RECOVERY: (
                RecoveryAssessmentState
                .RECOVERY_REQUIRED
            ),
        }[
            self.action
        ]

        if (
            self.assessment.state
            is not expected_state
        ):
            raise GovernedRecoveryInvariantError(
                f"{self.action.value} plan requires "
                f"{expected_state.value} assessment."
            )

        rows = tuple(
            self.steps
        )

        if not rows:
            raise GovernedRecoveryInvariantError(
                "Recovery plan requires at least "
                "one passive step."
            )

        if not all(
            isinstance(
                item,
                RecoveryPlanStep,
            )
            for item in rows
        ):
            raise TypeError(
                "steps must contain "
                "RecoveryPlanStep only."
            )

        ordinals = tuple(
            item.ordinal
            for item in rows
        )

        expected_ordinals = tuple(
            range(
                1,
                len(rows) + 1,
            )
        )

        if ordinals != expected_ordinals:
            raise GovernedRecoveryInvariantError(
                "Recovery plan step ordinals must "
                "be contiguous from 1."
            )

        ids = [
            item.step_id
            for item in rows
        ]

        if len(ids) != len(set(ids)):
            raise GovernedRecoveryInvariantError(
                "Recovery plan step IDs "
                "must be unique."
            )

        object.__setattr__(
            self,
            "steps",
            rows,
        )

        if (
            self.action
            is RecoveryPlanAction.CONTAINMENT
        ):
            if self.baseline_state_id is not None:
                raise GovernedRecoveryInvariantError(
                    "Containment plan must not "
                    "claim a rollback/recovery baseline."
                )

        else:
            baseline = _required_text(
                self.baseline_state_id,
                "baseline_state_id",
            )

            if (
                baseline
                != self.assessment
                .context
                .last_known_good_state_id
            ):
                raise GovernedRecoveryInvariantError(
                    "Rollback/recovery plan baseline "
                    "must match the declared "
                    "last-known-good state."
                )

            object.__setattr__(
                self,
                "baseline_state_id",
                baseline,
            )

        object.__setattr__(
            self,
            "plan_id",
            _stable_id(
                "FRP",
                {
                    "assessment_id": (
                        self.assessment.assessment_id
                    ),
                    "context_id": (
                        self.assessment
                        .context
                        .context_id
                    ),
                    "action": self.action.value,
                    "steps": [
                        item.to_dict()
                        for item in rows
                    ],
                    "baseline_state_id": (
                        self.baseline_state_id
                    ),
                },
            ),
        )

        _assert_passive(
            containment_authorized=(
                self.containment_authorized
            ),
            containment_executed=(
                self.containment_executed
            ),
            rollback_authorized=(
                self.rollback_authorized
            ),
            rollback_executed=(
                self.rollback_executed
            ),
            recovery_authorized=(
                self.recovery_authorized
            ),
            recovery_executed=(
                self.recovery_executed
            ),
            activation_authorized=(
                self.activation_authorized
            ),
            release_authorized=(
                self.release_authorized
            ),
            source_state_mutation_requested=(
                self.source_state_mutation_requested
            ),
            source_state_deletion_requested=(
                self.source_state_deletion_requested
            ),
            system_truth_asserted=(
                self.system_truth_asserted
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "version": (
                GOVERNED_FAILURE_CONTAINMENT_RECOVERY_VERSION
            ),
            "plan_id": self.plan_id,
            "assessment_id": (
                self.assessment.assessment_id
            ),
            "action": self.action.value,
            "steps": [
                item.to_dict()
                for item in self.steps
            ],
            "baseline_state_id": (
                self.baseline_state_id
            ),
            "containment_authorized": False,
            "containment_executed": False,
            "rollback_authorized": False,
            "rollback_executed": False,
            "recovery_authorized": False,
            "recovery_executed": False,
            "activation_authorized": False,
            "release_authorized": False,
            "source_state_mutation_requested": False,
            "source_state_deletion_requested": False,
            "system_truth_asserted": False,
        }


class GovernedFailureContainment:
    @classmethod
    def assess(
        cls,
        context: UpdateRecoveryContext,
        evidence: FailureRecoveryEvidence,
    ) -> GovernedRecoveryAssessment:
        return GovernedRecoveryAssessment(
            context=context,
            evidence=evidence,
        )

    @classmethod
    def plan_containment(
        cls,
        assessment: GovernedRecoveryAssessment,
        steps: tuple[
            RecoveryPlanStep,
            ...,
        ],
    ) -> GovernedRecoveryPlan:
        return GovernedRecoveryPlan(
            assessment=assessment,
            action=RecoveryPlanAction.CONTAINMENT,
            steps=tuple(steps),
        )

    @classmethod
    def plan_rollback(
        cls,
        assessment: GovernedRecoveryAssessment,
        steps: tuple[
            RecoveryPlanStep,
            ...,
        ],
    ) -> GovernedRecoveryPlan:
        return GovernedRecoveryPlan(
            assessment=assessment,
            action=RecoveryPlanAction.ROLLBACK,
            steps=tuple(steps),
            baseline_state_id=(
                assessment
                .context
                .last_known_good_state_id
            ),
        )

    @classmethod
    def plan_recovery(
        cls,
        assessment: GovernedRecoveryAssessment,
        steps: tuple[
            RecoveryPlanStep,
            ...,
        ],
    ) -> GovernedRecoveryPlan:
        return GovernedRecoveryPlan(
            assessment=assessment,
            action=RecoveryPlanAction.RECOVERY,
            steps=tuple(steps),
            baseline_state_id=(
                assessment
                .context
                .last_known_good_state_id
            ),
        )


__all__ = [
    "GOVERNED_FAILURE_CONTAINMENT_RECOVERY_VERSION",
    "GovernedRecoveryInvariantError",
    "EvidenceState",
    "FailureState",
    "ContainmentState",
    "RecoveryAssessmentState",
    "RecoveryPlanAction",
    "UpdateRecoveryContext",
    "RecoveryPreservationEvidence",
    "FailureRecoveryEvidence",
    "GovernedRecoveryAssessment",
    "RecoveryPlanStep",
    "GovernedRecoveryPlan",
    "GovernedFailureContainment",
]
