from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Iterable

from maestro.councils.capsules import (
    CapsuleStatus,
    CouncilCapsuleManifest,
)
from maestro.councils.registry import COUNCILS
from maestro.orchestration.governed_mission_foundation import (
    MissionCapabilityDemand,
)


GOVERNED_COUNCIL_EXPANSION_VERSION = 1


class CouncilExpansionInvariantError(
    ValueError
):
    pass


class CouncilGapAbsentError(
    CouncilExpansionInvariantError
):
    pass


class CouncilLifecycleEvidenceState(
    StrEnum
):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class CouncilLifecycleState(
    StrEnum
):
    SHADOW_REQUIRED = "SHADOW_REQUIRED"
    EVALUATION_REQUIRED = "EVALUATION_REQUIRED"
    AY_REQUIRED = "AY_REQUIRED"
    EX_REQUIRED = "EX_REQUIRED"
    HUMAN_APPROVAL_REQUIRED = (
        "HUMAN_APPROVAL_REQUIRED"
    )
    INSTALL_ELIGIBLE = "INSTALL_ELIGIBLE"
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
        raise CouncilExpansionInvariantError(
            f"{name} must not be empty."
        )

    if "\x00" in value:
        raise CouncilExpansionInvariantError(
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
        raise CouncilExpansionInvariantError(
            f"{name} must not be empty."
        )

    if len(rows) != len(set(rows)):
        raise CouncilExpansionInvariantError(
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


@dataclass(
    frozen=True,
    slots=True,
)
class CouncilGapAssessment:
    demand_id: str

    required_capabilities: tuple[
        str,
        ...,
    ]

    covered_capabilities: tuple[
        str,
        ...,
    ]

    missing_capabilities: tuple[
        str,
        ...,
    ] = field(
        init=False
    )

    gap_id: str = field(
        init=False
    )

    council_installation_authorized: bool = False
    council_activation_authorized: bool = False
    execution_authorized: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "demand_id",
            _required_text(
                self.demand_id,
                "demand_id",
            ),
        )

        required = _normalized_tuple(
            self.required_capabilities,
            "required_capability",
        )

        covered = _normalized_tuple(
            self.covered_capabilities,
            "covered_capability",
            require_nonempty=False,
        )

        extras = (
            set(covered)
            - set(required)
        )

        if extras:
            raise CouncilExpansionInvariantError(
                "Covered capability evidence "
                "contains capabilities outside "
                "the mission demand."
            )

        missing = tuple(
            sorted(
                set(required)
                - set(covered)
            )
        )

        object.__setattr__(
            self,
            "required_capabilities",
            required,
        )

        object.__setattr__(
            self,
            "covered_capabilities",
            covered,
        )

        object.__setattr__(
            self,
            "missing_capabilities",
            missing,
        )

        for name in (
            "council_installation_authorized",
            "council_activation_authorized",
            "execution_authorized",
            "system_truth_asserted",
        ):
            if getattr(
                self,
                name,
            ) is not False:
                raise CouncilExpansionInvariantError(
                    "Council-gap assessment "
                    f"cannot assert {name}."
                )

        object.__setattr__(
            self,
            "gap_id",
            _stable_id(
                "CGA",
                {
                    "version": (
                        GOVERNED_COUNCIL_EXPANSION_VERSION
                    ),
                    "demand_id": (
                        self.demand_id
                    ),
                    "required_capabilities": list(
                        required
                    ),
                    "covered_capabilities": list(
                        covered
                    ),
                    "missing_capabilities": list(
                        missing
                    ),
                },
            ),
        )

    @property
    def gap_present(
        self,
    ) -> bool:
        return bool(
            self.missing_capabilities
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "version": (
                GOVERNED_COUNCIL_EXPANSION_VERSION
            ),
            "gap_id": self.gap_id,
            "demand_id": self.demand_id,
            "required_capabilities": list(
                self.required_capabilities
            ),
            "covered_capabilities": list(
                self.covered_capabilities
            ),
            "missing_capabilities": list(
                self.missing_capabilities
            ),
            "gap_present": self.gap_present,
            "council_installation_authorized": False,
            "council_activation_authorized": False,
            "execution_authorized": False,
            "system_truth_asserted": False,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedCouncilProposal:
    gap_id: str
    demand_id: str

    council_id: str
    name: str
    primary_authority: str

    capabilities: tuple[
        str,
        ...,
    ]

    triggers: tuple[
        str,
        ...,
    ]

    cannot_own: tuple[
        str,
        ...,
    ]

    proposal_id: str = field(
        init=False
    )

    approved: bool = False
    installed: bool = False
    activated: bool = False
    execution_authorized: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "gap_id",
            "demand_id",
            "council_id",
            "name",
            "primary_authority",
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

        genesis_ids = {
            council.value
            for council in COUNCILS
        }

        if (
            self.council_id
            in genesis_ids
        ):
            raise CouncilExpansionInvariantError(
                "Dynamic Council proposal "
                "cannot replace a Genesis Council."
            )

        for name in (
            "capabilities",
            "triggers",
            "cannot_own",
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
            "approved",
            "installed",
            "activated",
            "execution_authorized",
            "system_truth_asserted",
        ):
            if getattr(
                self,
                name,
            ) is not False:
                raise CouncilExpansionInvariantError(
                    "Council proposal cannot "
                    f"assert {name}."
                )

        object.__setattr__(
            self,
            "proposal_id",
            _stable_id(
                "GCP",
                {
                    "gap_id": self.gap_id,
                    "demand_id": (
                        self.demand_id
                    ),
                    "council_id": (
                        self.council_id
                    ),
                    "name": self.name,
                    "primary_authority": (
                        self.primary_authority
                    ),
                    "capabilities": list(
                        self.capabilities
                    ),
                    "triggers": list(
                        self.triggers
                    ),
                    "cannot_own": list(
                        self.cannot_own
                    ),
                },
            ),
        )

    def to_manifest(
        self,
        *,
        status: CapsuleStatus = (
            CapsuleStatus.PROPOSED
        ),
    ) -> CouncilCapsuleManifest:
        if not isinstance(
            status,
            CapsuleStatus,
        ):
            raise TypeError(
                "status must be CapsuleStatus."
            )

        manifest = CouncilCapsuleManifest(
            council_id=self.council_id,
            name=self.name,
            system_variable=(
                "$conseil-"
                + self.council_id.lower()
            ),
            primary_authority=(
                self.primary_authority
            ),
            capabilities=list(
                self.capabilities
            ),
            triggers=list(
                self.triggers
            ),
            cannot_own=list(
                self.cannot_own
            ),
            status=status,
            genesis=False,
            metadata={
                "proposal_id": (
                    self.proposal_id
                ),
                "gap_id": self.gap_id,
                "demand_id": (
                    self.demand_id
                ),
            },
        )

        manifest.validate()

        return manifest

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "version": (
                GOVERNED_COUNCIL_EXPANSION_VERSION
            ),
            "proposal_id": (
                self.proposal_id
            ),
            "gap_id": self.gap_id,
            "demand_id": self.demand_id,
            "council_id": (
                self.council_id
            ),
            "name": self.name,
            "primary_authority": (
                self.primary_authority
            ),
            "capabilities": list(
                self.capabilities
            ),
            "triggers": list(
                self.triggers
            ),
            "cannot_own": list(
                self.cannot_own
            ),
            "approved": False,
            "installed": False,
            "activated": False,
            "execution_authorized": False,
            "system_truth_asserted": False,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class CouncilLifecycleEvidence:
    proposal_id: str

    capsule_status: CapsuleStatus

    evaluation: CouncilLifecycleEvidenceState
    ay_validation: CouncilLifecycleEvidenceState
    ex_authorization: CouncilLifecycleEvidenceState
    human_approval: CouncilLifecycleEvidenceState

    evidence_source_ref: str

    evidence_id: str = field(
        init=False
    )

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "proposal_id",
            _required_text(
                self.proposal_id,
                "proposal_id",
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
            self.capsule_status,
            CapsuleStatus,
        ):
            raise TypeError(
                "capsule_status must "
                "be CapsuleStatus."
            )

        for name in (
            "evaluation",
            "ay_validation",
            "ex_authorization",
            "human_approval",
        ):
            if not isinstance(
                getattr(
                    self,
                    name,
                ),
                CouncilLifecycleEvidenceState,
            ):
                raise TypeError(
                    f"{name} must be "
                    "CouncilLifecycleEvidenceState."
                )

        object.__setattr__(
            self,
            "evidence_id",
            _stable_id(
                "CLE",
                {
                    "proposal_id": (
                        self.proposal_id
                    ),
                    "capsule_status": (
                        self.capsule_status.value
                    ),
                    "evaluation": (
                        self.evaluation.value
                    ),
                    "ay_validation": (
                        self.ay_validation.value
                    ),
                    "ex_authorization": (
                        self.ex_authorization.value
                    ),
                    "human_approval": (
                        self.human_approval.value
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
class GovernedCouncilLifecycleAssessment:
    proposal: GovernedCouncilProposal
    evidence: CouncilLifecycleEvidence

    state: CouncilLifecycleState = field(
        init=False
    )

    reasons: tuple[
        str,
        ...,
    ] = field(
        init=False
    )

    assessment_id: str = field(
        init=False
    )

    installation_authorized: bool = False
    installation_executed: bool = False
    activation_authorized: bool = False
    activation_executed: bool = False
    execution_authorized: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.proposal,
            GovernedCouncilProposal,
        ):
            raise TypeError(
                "proposal must be "
                "GovernedCouncilProposal."
            )

        if not isinstance(
            self.evidence,
            CouncilLifecycleEvidence,
        ):
            raise TypeError(
                "evidence must be "
                "CouncilLifecycleEvidence."
            )

        if (
            self.evidence.proposal_id
            != self.proposal.proposal_id
        ):
            raise CouncilExpansionInvariantError(
                "Lifecycle evidence is not "
                "bound to the supplied "
                "Council proposal."
            )

        reasons: list[str] = []

        if (
            self.evidence.capsule_status
            is CapsuleStatus.PROPOSED
        ):
            state = (
                CouncilLifecycleState
                .SHADOW_REQUIRED
            )

            reasons.append(
                "Council proposal requires "
                "shadow lifecycle state."
            )

        elif self.evidence.evaluation is (
            CouncilLifecycleEvidenceState.FAIL
        ):
            state = (
                CouncilLifecycleState.REJECTED
            )

            reasons.append(
                "Council evaluation failed."
            )

        elif self.evidence.evaluation is (
            CouncilLifecycleEvidenceState.UNKNOWN
        ):
            state = (
                CouncilLifecycleState.UNKNOWN
            )

            reasons.append(
                "Council evaluation unknown."
            )

        elif self.evidence.ay_validation is (
            CouncilLifecycleEvidenceState.FAIL
        ):
            state = (
                CouncilLifecycleState.REJECTED
            )

            reasons.append(
                "AY validation failed."
            )

        elif self.evidence.ay_validation is (
            CouncilLifecycleEvidenceState.UNKNOWN
        ):
            state = (
                CouncilLifecycleState.AY_REQUIRED
            )

            reasons.append(
                "AY validation required."
            )

        elif self.evidence.ex_authorization is (
            CouncilLifecycleEvidenceState.FAIL
        ):
            state = (
                CouncilLifecycleState.REJECTED
            )

            reasons.append(
                "EX authorization failed."
            )

        elif self.evidence.ex_authorization is (
            CouncilLifecycleEvidenceState.UNKNOWN
        ):
            state = (
                CouncilLifecycleState.EX_REQUIRED
            )

            reasons.append(
                "EX authorization required."
            )

        elif self.evidence.human_approval is (
            CouncilLifecycleEvidenceState.FAIL
        ):
            state = (
                CouncilLifecycleState.REJECTED
            )

            reasons.append(
                "Human governance approval failed."
            )

        elif self.evidence.human_approval is (
            CouncilLifecycleEvidenceState.UNKNOWN
        ):
            state = (
                CouncilLifecycleState
                .HUMAN_APPROVAL_REQUIRED
            )

            reasons.append(
                "Human governance approval required."
            )

        else:
            state = (
                CouncilLifecycleState
                .INSTALL_ELIGIBLE
            )

            reasons.append(
                "Shadow/evaluation/AY/EX/"
                "human evidence is complete."
            )

        object.__setattr__(
            self,
            "state",
            state,
        )

        object.__setattr__(
            self,
            "reasons",
            tuple(
                reasons
            ),
        )

        for name in (
            "installation_authorized",
            "installation_executed",
            "activation_authorized",
            "activation_executed",
            "execution_authorized",
            "system_truth_asserted",
        ):
            if getattr(
                self,
                name,
            ) is not False:
                raise CouncilExpansionInvariantError(
                    "Lifecycle assessment "
                    f"cannot assert {name}."
                )

        object.__setattr__(
            self,
            "assessment_id",
            _stable_id(
                "CLA",
                {
                    "proposal_id": (
                        self.proposal
                        .proposal_id
                    ),
                    "evidence_id": (
                        self.evidence
                        .evidence_id
                    ),
                    "state": (
                        state.value
                    ),
                    "reasons": reasons,
                },
            ),
        )

    @property
    def install_eligible(
        self,
    ) -> bool:
        return (
            self.state
            is CouncilLifecycleState
            .INSTALL_ELIGIBLE
        )


class GovernedCouncilExpansion:
    @staticmethod
    def assess_gap(
        demand: MissionCapabilityDemand,
        covered_capabilities: Iterable[str],
    ) -> CouncilGapAssessment:
        if not isinstance(
            demand,
            MissionCapabilityDemand,
        ):
            raise TypeError(
                "demand must be "
                "MissionCapabilityDemand."
            )

        required = tuple(
            item.capability_id
            for item in demand.demands
        )

        return CouncilGapAssessment(
            demand_id=demand.demand_id,
            required_capabilities=required,
            covered_capabilities=tuple(
                covered_capabilities
            ),
        )

    @staticmethod
    def propose(
        gap: CouncilGapAssessment,
        *,
        council_id: str,
        name: str,
        primary_authority: str,
        triggers: Iterable[str],
        cannot_own: Iterable[str],
    ) -> GovernedCouncilProposal:
        if not isinstance(
            gap,
            CouncilGapAssessment,
        ):
            raise TypeError(
                "gap must be "
                "CouncilGapAssessment."
            )

        if not gap.gap_present:
            raise CouncilGapAbsentError(
                "Dynamic Council proposal "
                "requires an explicit "
                "Council capability gap."
            )

        return GovernedCouncilProposal(
            gap_id=gap.gap_id,
            demand_id=gap.demand_id,
            council_id=council_id,
            name=name,
            primary_authority=(
                primary_authority
            ),
            capabilities=(
                gap.missing_capabilities
            ),
            triggers=tuple(
                triggers
            ),
            cannot_own=tuple(
                cannot_own
            ),
        )

    @staticmethod
    def assess_lifecycle(
        proposal: GovernedCouncilProposal,
        evidence: CouncilLifecycleEvidence,
    ) -> GovernedCouncilLifecycleAssessment:
        return GovernedCouncilLifecycleAssessment(
            proposal=proposal,
            evidence=evidence,
        )


__all__ = [
    "GOVERNED_COUNCIL_EXPANSION_VERSION",
    "CouncilExpansionInvariantError",
    "CouncilGapAbsentError",
    "CouncilLifecycleEvidenceState",
    "CouncilLifecycleState",
    "CouncilGapAssessment",
    "GovernedCouncilProposal",
    "CouncilLifecycleEvidence",
    "GovernedCouncilLifecycleAssessment",
    "GovernedCouncilExpansion",
]
