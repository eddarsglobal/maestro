from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


GOVERNED_DURABLE_STATE_COMPATIBILITY_VERSION = 1


class GovernedDurableCompatibilityInvariantError(
    ValueError
):
    pass


class CompatibilityEvidenceState(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class DurableCompatibilityState(StrEnum):
    COMPATIBLE = "COMPATIBLE"
    MIGRATION_REQUIRED = "MIGRATION_REQUIRED"
    INCOMPATIBLE = "INCOMPATIBLE"
    UNKNOWN = "UNKNOWN"


class DirectionalCompatibilityState(StrEnum):
    COMPATIBLE = "COMPATIBLE"
    INCOMPATIBLE = "INCOMPATIBLE"
    UNKNOWN = "UNKNOWN"


def _required_text(
    value: str,
    name: str,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            f"{name} must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise GovernedDurableCompatibilityInvariantError(
            f"{name} must not be empty."
        )

    if "\x00" in normalized:
        raise GovernedDurableCompatibilityInvariantError(
            f"{name} must not contain NUL."
        )

    return normalized


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
    states: tuple[
        CompatibilityEvidenceState,
        ...,
    ],
) -> CompatibilityEvidenceState:
    if any(
        state
        is CompatibilityEvidenceState.FAIL
        for state in states
    ):
        return CompatibilityEvidenceState.FAIL

    if any(
        state
        is CompatibilityEvidenceState.UNKNOWN
        for state in states
    ):
        return CompatibilityEvidenceState.UNKNOWN

    return CompatibilityEvidenceState.PASS


def _directional_state(
    read_state: CompatibilityEvidenceState,
    write_state: CompatibilityEvidenceState,
) -> DirectionalCompatibilityState:
    aggregate = _aggregate(
        (
            read_state,
            write_state,
        )
    )

    if aggregate is CompatibilityEvidenceState.PASS:
        return (
            DirectionalCompatibilityState.COMPATIBLE
        )

    if aggregate is CompatibilityEvidenceState.FAIL:
        return (
            DirectionalCompatibilityState.INCOMPATIBLE
        )

    return DirectionalCompatibilityState.UNKNOWN


def _assert_passive(
    *,
    migration_authorized: bool,
    migration_executed: bool,
    activation_authorized: bool,
    rollback_authorized: bool,
    source_state_mutation_requested: bool,
    source_state_deletion_requested: bool,
    core_mutation_requested: bool,
    state_loss_accepted: bool,
    system_truth_asserted: bool,
) -> None:
    flags = {
        "migration_authorized": (
            migration_authorized
        ),
        "migration_executed": (
            migration_executed
        ),
        "activation_authorized": (
            activation_authorized
        ),
        "rollback_authorized": (
            rollback_authorized
        ),
        "source_state_mutation_requested": (
            source_state_mutation_requested
        ),
        "source_state_deletion_requested": (
            source_state_deletion_requested
        ),
        "core_mutation_requested": (
            core_mutation_requested
        ),
        "state_loss_accepted": (
            state_loss_accepted
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
        raise GovernedDurableCompatibilityInvariantError(
            "Durable compatibility evidence "
            "cannot assert migration, activation, "
            "rollback, deletion, mutation, state-loss "
            "or truth authority: "
            + ", ".join(asserted)
        )


@dataclass(
    frozen=True,
    slots=True,
)
class DurableStateDescriptor:
    durable_state_id: str
    state_type: str

    generation_id: str
    application_version: str

    schema_id: str
    schema_version: str

    format_id: str
    format_version: str

    preservation_requirements: tuple[
        str,
        ...,
    ]

    descriptor_id: str = field(
        init=False
    )

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "durable_state_id",
            "state_type",
            "generation_id",
            "application_version",
            "schema_id",
            "schema_version",
            "format_id",
            "format_version",
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
            raise GovernedDurableCompatibilityInvariantError(
                "Durable state requires at least "
                "one preservation requirement."
            )

        if len(requirements) != len(
            set(requirements)
        ):
            raise GovernedDurableCompatibilityInvariantError(
                "Preservation requirements "
                "must be unique."
            )

        object.__setattr__(
            self,
            "preservation_requirements",
            requirements,
        )

        payload = {
            "version": (
                GOVERNED_DURABLE_STATE_COMPATIBILITY_VERSION
            ),
            "durable_state_id": (
                self.durable_state_id
            ),
            "state_type": self.state_type,
            "generation_id": (
                self.generation_id
            ),
            "application_version": (
                self.application_version
            ),
            "schema_id": self.schema_id,
            "schema_version": (
                self.schema_version
            ),
            "format_id": self.format_id,
            "format_version": (
                self.format_version
            ),
            "preservation_requirements": list(
                requirements
            ),
        }

        object.__setattr__(
            self,
            "descriptor_id",
            _stable_id(
                "DSD",
                payload,
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "version": (
                GOVERNED_DURABLE_STATE_COMPATIBILITY_VERSION
            ),
            "descriptor_id": (
                self.descriptor_id
            ),
            "durable_state_id": (
                self.durable_state_id
            ),
            "state_type": self.state_type,
            "generation_id": (
                self.generation_id
            ),
            "application_version": (
                self.application_version
            ),
            "schema_id": self.schema_id,
            "schema_version": (
                self.schema_version
            ),
            "format_id": self.format_id,
            "format_version": (
                self.format_version
            ),
            "preservation_requirements": list(
                self.preservation_requirements
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class PreservationEvidence:
    requirement_id: str

    direct_state: CompatibilityEvidenceState
    migration_state: CompatibilityEvidenceState

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
            self.direct_state,
            CompatibilityEvidenceState,
        ):
            raise TypeError(
                "direct_state must be "
                "CompatibilityEvidenceState."
            )

        if not isinstance(
            self.migration_state,
            CompatibilityEvidenceState,
        ):
            raise TypeError(
                "migration_state must be "
                "CompatibilityEvidenceState."
            )

    def to_dict(
        self,
    ) -> dict[str, str]:
        return {
            "requirement_id": (
                self.requirement_id
            ),
            "direct_state": (
                self.direct_state.value
            ),
            "migration_state": (
                self.migration_state.value
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class DurableCompatibilityEvidence:
    source_descriptor_id: str
    target_descriptor_id: str

    target_reads_source: CompatibilityEvidenceState
    target_writes_source: CompatibilityEvidenceState

    source_reads_target: CompatibilityEvidenceState
    source_writes_target: CompatibilityEvidenceState

    migration_path_available: CompatibilityEvidenceState
    rollback_path_available: CompatibilityEvidenceState

    preservation: tuple[
        PreservationEvidence,
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
            "source_descriptor_id",
            _required_text(
                self.source_descriptor_id,
                "source_descriptor_id",
            ),
        )

        object.__setattr__(
            self,
            "target_descriptor_id",
            _required_text(
                self.target_descriptor_id,
                "target_descriptor_id",
            ),
        )

        for name in (
            "target_reads_source",
            "target_writes_source",
            "source_reads_target",
            "source_writes_target",
            "migration_path_available",
            "rollback_path_available",
        ):
            if not isinstance(
                getattr(self, name),
                CompatibilityEvidenceState,
            ):
                raise TypeError(
                    f"{name} must be "
                    "CompatibilityEvidenceState."
                )

        object.__setattr__(
            self,
            "evidence_source_ref",
            _required_text(
                self.evidence_source_ref,
                "evidence_source_ref",
            ),
        )

        raw_rows = tuple(
            self.preservation
        )

        if not raw_rows:
            raise GovernedDurableCompatibilityInvariantError(
                "Preservation evidence "
                "must not be empty."
            )

        if not all(
            isinstance(
                item,
                PreservationEvidence,
            )
            for item in raw_rows
        ):
            raise TypeError(
                "preservation must contain "
                "PreservationEvidence only."
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
            raise GovernedDurableCompatibilityInvariantError(
                "Preservation evidence "
                "requirements must be unique."
            )

        object.__setattr__(
            self,
            "preservation",
            rows,
        )

        payload = {
            "source_descriptor_id": (
                self.source_descriptor_id
            ),
            "target_descriptor_id": (
                self.target_descriptor_id
            ),
            "target_reads_source": (
                self.target_reads_source.value
            ),
            "target_writes_source": (
                self.target_writes_source.value
            ),
            "source_reads_target": (
                self.source_reads_target.value
            ),
            "source_writes_target": (
                self.source_writes_target.value
            ),
            "migration_path_available": (
                self.migration_path_available.value
            ),
            "rollback_path_available": (
                self.rollback_path_available.value
            ),
            "preservation": [
                item.to_dict()
                for item in rows
            ],
            "evidence_source_ref": (
                self.evidence_source_ref
            ),
        }

        object.__setattr__(
            self,
            "evidence_id",
            _stable_id(
                "DCE",
                payload,
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "source_descriptor_id": (
                self.source_descriptor_id
            ),
            "target_descriptor_id": (
                self.target_descriptor_id
            ),
            "target_reads_source": (
                self.target_reads_source.value
            ),
            "target_writes_source": (
                self.target_writes_source.value
            ),
            "source_reads_target": (
                self.source_reads_target.value
            ),
            "source_writes_target": (
                self.source_writes_target.value
            ),
            "migration_path_available": (
                self.migration_path_available.value
            ),
            "rollback_path_available": (
                self.rollback_path_available.value
            ),
            "preservation": [
                item.to_dict()
                for item in self.preservation
            ],
            "evidence_source_ref": (
                self.evidence_source_ref
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedCompatibilityAssessment:
    source: DurableStateDescriptor
    target: DurableStateDescriptor
    evidence: DurableCompatibilityEvidence

    assessment_id: str = field(
        init=False
    )

    state: DurableCompatibilityState = field(
        init=False
    )

    backward_state: DirectionalCompatibilityState = field(
        init=False
    )

    forward_state: DirectionalCompatibilityState = field(
        init=False
    )

    reasons: tuple[
        str,
        ...,
    ] = field(
        init=False
    )

    migration_authorized: bool = False
    migration_executed: bool = False
    activation_authorized: bool = False
    rollback_authorized: bool = False
    source_state_mutation_requested: bool = False
    source_state_deletion_requested: bool = False
    core_mutation_requested: bool = False
    state_loss_accepted: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.source,
            DurableStateDescriptor,
        ):
            raise TypeError(
                "source must be "
                "DurableStateDescriptor."
            )

        if not isinstance(
            self.target,
            DurableStateDescriptor,
        ):
            raise TypeError(
                "target must be "
                "DurableStateDescriptor."
            )

        if not isinstance(
            self.evidence,
            DurableCompatibilityEvidence,
        ):
            raise TypeError(
                "evidence must be "
                "DurableCompatibilityEvidence."
            )

        if (
            self.evidence.source_descriptor_id
            != self.source.descriptor_id
        ):
            raise GovernedDurableCompatibilityInvariantError(
                "Compatibility evidence is not "
                "bound to the supplied source "
                "state descriptor."
            )

        if (
            self.evidence.target_descriptor_id
            != self.target.descriptor_id
        ):
            raise GovernedDurableCompatibilityInvariantError(
                "Compatibility evidence is not "
                "bound to the supplied target "
                "state descriptor."
            )

        if (
            self.source.durable_state_id
            != self.target.durable_state_id
        ):
            raise GovernedDurableCompatibilityInvariantError(
                "Source and target must describe "
                "the same durable state identity."
            )

        if (
            self.source.state_type
            != self.target.state_type
        ):
            raise GovernedDurableCompatibilityInvariantError(
                "Source and target must describe "
                "the same durable state type."
            )

        required = tuple(
            sorted(
                set(
                    self.source
                    .preservation_requirements
                )
                | set(
                    self.target
                    .preservation_requirements
                )
            )
        )

        observed = tuple(
            item.requirement_id
            for item
            in self.evidence.preservation
        )

        if observed != required:
            raise GovernedDurableCompatibilityInvariantError(
                "Preservation evidence must "
                "cover exactly the union of "
                "source and target requirements."
            )

        backward = _directional_state(
            self.evidence.target_reads_source,
            self.evidence.target_writes_source,
        )

        forward = _directional_state(
            self.evidence.source_reads_target,
            self.evidence.source_writes_target,
        )

        direct_preservation = _aggregate(
            tuple(
                item.direct_state
                for item
                in self.evidence.preservation
            )
        )

        migration_preservation = _aggregate(
            tuple(
                item.migration_state
                for item
                in self.evidence.preservation
            )
        )

        direct = _aggregate(
            (
                self.evidence.target_reads_source,
                self.evidence.target_writes_source,
                direct_preservation,
            )
        )

        reasons: list[str] = []

        if (
            self.evidence.target_reads_source
            is CompatibilityEvidenceState.FAIL
        ):
            reasons.append(
                "target cannot read source state"
            )

        elif (
            self.evidence.target_reads_source
            is CompatibilityEvidenceState.UNKNOWN
        ):
            reasons.append(
                "target read compatibility unknown"
            )

        if (
            self.evidence.target_writes_source
            is CompatibilityEvidenceState.FAIL
        ):
            reasons.append(
                "target cannot safely write source state"
            )

        elif (
            self.evidence.target_writes_source
            is CompatibilityEvidenceState.UNKNOWN
        ):
            reasons.append(
                "target write compatibility unknown"
            )

        if (
            direct_preservation
            is CompatibilityEvidenceState.FAIL
        ):
            reasons.append(
                "direct state preservation failed"
            )

        elif (
            direct_preservation
            is CompatibilityEvidenceState.UNKNOWN
        ):
            reasons.append(
                "direct state preservation unknown"
            )

        if (
            direct
            is CompatibilityEvidenceState.PASS
        ):
            state = DurableCompatibilityState.COMPATIBLE

        elif (
            direct
            is CompatibilityEvidenceState.UNKNOWN
        ):
            state = DurableCompatibilityState.UNKNOWN

        else:
            migration = (
                self.evidence
                .migration_path_available
            )

            if (
                migration
                is CompatibilityEvidenceState.FAIL
            ):
                reasons.append(
                    "migration path unavailable"
                )

                state = (
                    DurableCompatibilityState
                    .INCOMPATIBLE
                )

            elif (
                migration
                is CompatibilityEvidenceState.UNKNOWN
            ):
                reasons.append(
                    "migration path availability unknown"
                )

                state = (
                    DurableCompatibilityState.UNKNOWN
                )

            elif (
                migration_preservation
                is CompatibilityEvidenceState.FAIL
            ):
                reasons.append(
                    "migration preservation failed"
                )

                state = (
                    DurableCompatibilityState
                    .INCOMPATIBLE
                )

            elif (
                migration_preservation
                is CompatibilityEvidenceState.UNKNOWN
            ):
                reasons.append(
                    "migration preservation unknown"
                )

                state = (
                    DurableCompatibilityState.UNKNOWN
                )

            else:
                state = (
                    DurableCompatibilityState
                    .MIGRATION_REQUIRED
                )

                reasons.append(
                    "direct compatibility failed; "
                    "preserving migration path available"
                )

        object.__setattr__(
            self,
            "state",
            state,
        )

        object.__setattr__(
            self,
            "backward_state",
            backward,
        )

        object.__setattr__(
            self,
            "forward_state",
            forward,
        )

        object.__setattr__(
            self,
            "reasons",
            tuple(reasons),
        )

        payload = {
            "source_descriptor_id": (
                self.source.descriptor_id
            ),
            "target_descriptor_id": (
                self.target.descriptor_id
            ),
            "evidence_id": (
                self.evidence.evidence_id
            ),
            "state": state.value,
            "backward_state": backward.value,
            "forward_state": forward.value,
            "reasons": list(reasons),
        }

        object.__setattr__(
            self,
            "assessment_id",
            _stable_id(
                "DCA",
                payload,
            ),
        )

        _assert_passive(
            migration_authorized=(
                self.migration_authorized
            ),
            migration_executed=(
                self.migration_executed
            ),
            activation_authorized=(
                self.activation_authorized
            ),
            rollback_authorized=(
                self.rollback_authorized
            ),
            source_state_mutation_requested=(
                self.source_state_mutation_requested
            ),
            source_state_deletion_requested=(
                self.source_state_deletion_requested
            ),
            core_mutation_requested=(
                self.core_mutation_requested
            ),
            state_loss_accepted=(
                self.state_loss_accepted
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
                GOVERNED_DURABLE_STATE_COMPATIBILITY_VERSION
            ),
            "assessment_id": (
                self.assessment_id
            ),
            "source": self.source.to_dict(),
            "target": self.target.to_dict(),
            "evidence": self.evidence.to_dict(),
            "state": self.state.value,
            "backward_state": (
                self.backward_state.value
            ),
            "forward_state": (
                self.forward_state.value
            ),
            "reasons": list(
                self.reasons
            ),
            "migration_authorized": False,
            "migration_executed": False,
            "activation_authorized": False,
            "rollback_authorized": False,
            "source_state_mutation_requested": False,
            "source_state_deletion_requested": False,
            "core_mutation_requested": False,
            "state_loss_accepted": False,
            "system_truth_asserted": False,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class MigrationPlanStep:
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
            raise GovernedDurableCompatibilityInvariantError(
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
class GovernedMigrationPlan:
    assessment: GovernedCompatibilityAssessment

    steps: tuple[
        MigrationPlanStep,
        ...,
    ]

    rollback_reference: str | None = None

    plan_id: str = field(
        init=False
    )

    migration_authorized: bool = False
    migration_executed: bool = False
    activation_authorized: bool = False
    rollback_authorized: bool = False
    source_state_mutation_requested: bool = False
    source_state_deletion_requested: bool = False
    core_mutation_requested: bool = False
    state_loss_accepted: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.assessment,
            GovernedCompatibilityAssessment,
        ):
            raise TypeError(
                "assessment must be "
                "GovernedCompatibilityAssessment."
            )

        if (
            self.assessment.state
            is not
            DurableCompatibilityState.MIGRATION_REQUIRED
        ):
            raise GovernedDurableCompatibilityInvariantError(
                "Migration plans require a "
                "MIGRATION_REQUIRED assessment."
            )

        rows = tuple(self.steps)

        if not rows:
            raise GovernedDurableCompatibilityInvariantError(
                "Migration plan requires "
                "at least one passive step."
            )

        if not all(
            isinstance(
                item,
                MigrationPlanStep,
            )
            for item in rows
        ):
            raise TypeError(
                "steps must contain "
                "MigrationPlanStep only."
            )

        ordinals = tuple(
            item.ordinal
            for item in rows
        )

        expected = tuple(
            range(
                1,
                len(rows) + 1,
            )
        )

        if ordinals != expected:
            raise GovernedDurableCompatibilityInvariantError(
                "Migration step ordinals must be "
                "contiguous and explicitly ordered "
                "from 1."
            )

        step_ids = [
            item.step_id
            for item in rows
        ]

        if len(step_ids) != len(set(step_ids)):
            raise GovernedDurableCompatibilityInvariantError(
                "Migration step IDs "
                "must be unique."
            )

        object.__setattr__(
            self,
            "steps",
            rows,
        )

        if self.rollback_reference is not None:
            object.__setattr__(
                self,
                "rollback_reference",
                _required_text(
                    self.rollback_reference,
                    "rollback_reference",
                ),
            )

        payload = {
            "assessment_id": (
                self.assessment.assessment_id
            ),
            "source_descriptor_id": (
                self.assessment
                .source
                .descriptor_id
            ),
            "target_descriptor_id": (
                self.assessment
                .target
                .descriptor_id
            ),
            "steps": [
                item.to_dict()
                for item in rows
            ],
            "rollback_reference": (
                self.rollback_reference
            ),
        }

        object.__setattr__(
            self,
            "plan_id",
            _stable_id(
                "DMP",
                payload,
            ),
        )

        _assert_passive(
            migration_authorized=(
                self.migration_authorized
            ),
            migration_executed=(
                self.migration_executed
            ),
            activation_authorized=(
                self.activation_authorized
            ),
            rollback_authorized=(
                self.rollback_authorized
            ),
            source_state_mutation_requested=(
                self.source_state_mutation_requested
            ),
            source_state_deletion_requested=(
                self.source_state_deletion_requested
            ),
            core_mutation_requested=(
                self.core_mutation_requested
            ),
            state_loss_accepted=(
                self.state_loss_accepted
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
                GOVERNED_DURABLE_STATE_COMPATIBILITY_VERSION
            ),
            "plan_id": self.plan_id,
            "assessment_id": (
                self.assessment.assessment_id
            ),
            "source_descriptor_id": (
                self.assessment
                .source
                .descriptor_id
            ),
            "target_descriptor_id": (
                self.assessment
                .target
                .descriptor_id
            ),
            "steps": [
                item.to_dict()
                for item in self.steps
            ],
            "rollback_reference": (
                self.rollback_reference
            ),
            "migration_authorized": False,
            "migration_executed": False,
            "activation_authorized": False,
            "rollback_authorized": False,
            "source_state_mutation_requested": False,
            "source_state_deletion_requested": False,
            "core_mutation_requested": False,
            "state_loss_accepted": False,
            "system_truth_asserted": False,
        }


class GovernedDurableStateCompatibility:
    @classmethod
    def assess(
        cls,
        source: DurableStateDescriptor,
        target: DurableStateDescriptor,
        evidence: DurableCompatibilityEvidence,
    ) -> GovernedCompatibilityAssessment:
        return GovernedCompatibilityAssessment(
            source=source,
            target=target,
            evidence=evidence,
        )

    @classmethod
    def plan(
        cls,
        assessment: GovernedCompatibilityAssessment,
        steps: tuple[
            MigrationPlanStep,
            ...,
        ],
        *,
        rollback_reference: str | None = None,
    ) -> GovernedMigrationPlan:
        return GovernedMigrationPlan(
            assessment=assessment,
            steps=tuple(steps),
            rollback_reference=rollback_reference,
        )


__all__ = [
    "GOVERNED_DURABLE_STATE_COMPATIBILITY_VERSION",
    "GovernedDurableCompatibilityInvariantError",
    "CompatibilityEvidenceState",
    "DurableCompatibilityState",
    "DirectionalCompatibilityState",
    "DurableStateDescriptor",
    "PreservationEvidence",
    "DurableCompatibilityEvidence",
    "GovernedCompatibilityAssessment",
    "MigrationPlanStep",
    "GovernedMigrationPlan",
    "GovernedDurableStateCompatibility",
]
