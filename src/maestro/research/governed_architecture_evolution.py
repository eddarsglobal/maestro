from __future__ import annotations

import hashlib
import json

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from .governed_capability_candidate import (
    GovernedCapabilityCandidate,
)


GOVERNED_ARCHITECTURE_EVOLUTION_VERSION = 1


class GovernedArchitectureEvolutionInvariantError(
    ValueError
):
    pass


class OntologySufficiencyState(StrEnum):
    UNKNOWN = "UNKNOWN"
    SUFFICIENT = "SUFFICIENT"
    INSUFFICIENT = "INSUFFICIENT"


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
        raise ValueError(
            f"{name} must not be empty."
        )

    if "\x00" in normalized:
        raise ValueError(
            f"{name} must not contain NUL."
        )

    return normalized


def _text_tuple(
    values: Iterable[str],
    name: str,
) -> tuple[str, ...]:
    if isinstance(
        values,
        (str, bytes),
    ):
        raise TypeError(
            f"{name} must be an iterable "
            "of strings."
        )

    return tuple(
        sorted({
            _required_text(
                item,
                name,
            )
            for item in values
        })
    )


def _digest_id(
    prefix: str,
    payload: dict[str, Any],
) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    digest = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()

    return f"{prefix}-{digest[:24]}"


def _assert_passive(
    *,
    proposal_approved: bool,
    schema_mutation_requested: bool,
    migration_requested: bool,
    registry_mutation_requested: bool,
    installation_requested: bool,
    activation_requested: bool,
    authorization_asserted: bool,
    execution_requested: bool,
    core_mutation_requested: bool,
    supply_chain_artifact_created: bool,
    system_truth_asserted: bool,
) -> None:
    flags = {
        "proposal_approved": (
            proposal_approved
        ),
        "schema_mutation_requested": (
            schema_mutation_requested
        ),
        "migration_requested": (
            migration_requested
        ),
        "registry_mutation_requested": (
            registry_mutation_requested
        ),
        "installation_requested": (
            installation_requested
        ),
        "activation_requested": (
            activation_requested
        ),
        "authorization_asserted": (
            authorization_asserted
        ),
        "execution_requested": (
            execution_requested
        ),
        "core_mutation_requested": (
            core_mutation_requested
        ),
        "supply_chain_artifact_created": (
            supply_chain_artifact_created
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
        raise (
            GovernedArchitectureEvolutionInvariantError(
                "Architecture-evolution boundary "
                "cannot assert downstream authority: "
                + ", ".join(asserted)
            )
        )


@dataclass(
    frozen=True,
    slots=True,
)
class CapabilityOntologyAssessment:
    """
    Explicit BMF-021 assessment of whether the current
    capability ontology can represent required concepts.

    This is not a check for provider availability,
    adapter availability, council availability, runtime
    availability, installation state, or execution state.
    """

    assessment_id: str

    state: OntologySufficiencyState

    capability_candidate_id: str
    landscape_change_id: str
    current_snapshot_id: str

    scope_id: str
    subject_id: str
    capability_term: str

    evidence_id: str
    source_ref: str
    landscape_evidence_ids: tuple[str, ...]

    ontology_id: str

    required_concepts: tuple[str, ...]
    represented_concepts: tuple[str, ...]
    missing_concepts: tuple[str, ...]

    ontology_complete: bool
    reason: str

    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )

    architecture_evolution_proposal_created: bool = False
    proposal_approved: bool = False
    schema_mutation_requested: bool = False
    migration_requested: bool = False
    registry_mutation_requested: bool = False
    installation_requested: bool = False
    activation_requested: bool = False
    authorization_asserted: bool = False
    execution_requested: bool = False
    core_mutation_requested: bool = False
    supply_chain_artifact_created: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.state,
            OntologySufficiencyState,
        ):
            raise TypeError(
                "state must be "
                "OntologySufficiencyState."
            )

        for name in (
            "assessment_id",
            "capability_candidate_id",
            "landscape_change_id",
            "current_snapshot_id",
            "scope_id",
            "subject_id",
            "capability_term",
            "evidence_id",
            "source_ref",
            "ontology_id",
            "reason",
            "verification_status",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(self, name),
                    name,
                ),
            )

        evidence_ids = _text_tuple(
            self.landscape_evidence_ids,
            "landscape_evidence_ids",
        )

        if self.evidence_id not in evidence_ids:
            raise (
                GovernedArchitectureEvolutionInvariantError(
                    "Ontology assessment evidence_id "
                    "must remain in landscape lineage."
                )
            )

        object.__setattr__(
            self,
            "landscape_evidence_ids",
            evidence_ids,
        )

        required = _text_tuple(
            self.required_concepts,
            "required_concepts",
        )

        represented = _text_tuple(
            self.represented_concepts,
            "represented_concepts",
        )

        missing = _text_tuple(
            self.missing_concepts,
            "missing_concepts",
        )

        if not required:
            raise (
                GovernedArchitectureEvolutionInvariantError(
                    "Ontology assessment requires at "
                    "least one explicit concept."
                )
            )

        object.__setattr__(
            self,
            "required_concepts",
            required,
        )

        object.__setattr__(
            self,
            "represented_concepts",
            represented,
        )

        object.__setattr__(
            self,
            "missing_concepts",
            missing,
        )

        if not isinstance(
            self.ontology_complete,
            bool,
        ):
            raise TypeError(
                "ontology_complete must be bool."
            )

        expected_missing = tuple(
            sorted(
                set(required)
                - set(represented)
            )
        )

        if not self.ontology_complete:
            if (
                self.state
                is not OntologySufficiencyState.UNKNOWN
            ):
                raise (
                    GovernedArchitectureEvolutionInvariantError(
                        "Incomplete ontology knowledge "
                        "must remain UNKNOWN."
                    )
                )

            if missing:
                raise (
                    GovernedArchitectureEvolutionInvariantError(
                        "UNKNOWN ontology assessment "
                        "cannot assert missing concepts."
                    )
                )

        else:
            if missing != expected_missing:
                raise (
                    GovernedArchitectureEvolutionInvariantError(
                        "missing_concepts does not match "
                        "the explicit ontology comparison."
                    )
                )

            expected_state = (
                OntologySufficiencyState.INSUFFICIENT
                if missing
                else OntologySufficiencyState.SUFFICIENT
            )

            if self.state is not expected_state:
                raise (
                    GovernedArchitectureEvolutionInvariantError(
                        "Ontology sufficiency state does "
                        "not match explicit concepts."
                    )
                )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                GovernedArchitectureEvolutionInvariantError(
                    "Architecture-evolution evidence "
                    "derived from external research "
                    "must remain UNVERIFIED_EXTERNAL."
                )
            )

        if (
            self.architecture_evolution_proposal_created
            is not False
        ):
            raise (
                GovernedArchitectureEvolutionInvariantError(
                    "Ontology assessment cannot silently "
                    "create an architecture proposal."
                )
            )

        _assert_passive(
            proposal_approved=(
                self.proposal_approved
            ),
            schema_mutation_requested=(
                self.schema_mutation_requested
            ),
            migration_requested=(
                self.migration_requested
            ),
            registry_mutation_requested=(
                self.registry_mutation_requested
            ),
            installation_requested=(
                self.installation_requested
            ),
            activation_requested=(
                self.activation_requested
            ),
            authorization_asserted=(
                self.authorization_asserted
            ),
            execution_requested=(
                self.execution_requested
            ),
            core_mutation_requested=(
                self.core_mutation_requested
            ),
            supply_chain_artifact_created=(
                self.supply_chain_artifact_created
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
                GOVERNED_ARCHITECTURE_EVOLUTION_VERSION
            ),
            "assessment_id": (
                self.assessment_id
            ),
            "state": self.state.value,
            "capability_candidate_id": (
                self.capability_candidate_id
            ),
            "landscape_change_id": (
                self.landscape_change_id
            ),
            "current_snapshot_id": (
                self.current_snapshot_id
            ),
            "scope_id": self.scope_id,
            "subject_id": self.subject_id,
            "capability_term": (
                self.capability_term
            ),
            "evidence_id": self.evidence_id,
            "source_ref": self.source_ref,
            "landscape_evidence_ids": list(
                self.landscape_evidence_ids
            ),
            "ontology_id": self.ontology_id,
            "required_concepts": list(
                self.required_concepts
            ),
            "represented_concepts": list(
                self.represented_concepts
            ),
            "missing_concepts": list(
                self.missing_concepts
            ),
            "ontology_complete": (
                self.ontology_complete
            ),
            "reason": self.reason,
            "verification_status": (
                self.verification_status
            ),
            "architecture_evolution_proposal_created": False,
            "proposal_approved": False,
            "schema_mutation_requested": False,
            "migration_requested": False,
            "registry_mutation_requested": False,
            "installation_requested": False,
            "activation_requested": False,
            "authorization_asserted": False,
            "execution_requested": False,
            "core_mutation_requested": False,
            "supply_chain_artifact_created": False,
            "system_truth_asserted": False,
        }


class GovernedCapabilityOntologyAssessor:
    """
    Pure BMF-021 ontology-sufficiency assessment.

    Missing runtime/provider/adapter availability is outside
    this assessment and cannot by itself establish ontology
    insufficiency.
    """

    @classmethod
    def assess(
        cls,
        candidate: GovernedCapabilityCandidate,
        *,
        ontology_id: str,
        required_concepts: Iterable[str],
        represented_concepts: Iterable[str],
        ontology_complete: bool,
    ) -> CapabilityOntologyAssessment:
        if not isinstance(
            candidate,
            GovernedCapabilityCandidate,
        ):
            raise TypeError(
                "candidate must be "
                "GovernedCapabilityCandidate."
            )

        normalized_ontology_id = (
            _required_text(
                ontology_id,
                "ontology_id",
            )
        )

        required = _text_tuple(
            required_concepts,
            "required_concepts",
        )

        represented = _text_tuple(
            represented_concepts,
            "represented_concepts",
        )

        if not required:
            raise (
                GovernedArchitectureEvolutionInvariantError(
                    "At least one required ontology "
                    "concept must be explicit."
                )
            )

        if not isinstance(
            ontology_complete,
            bool,
        ):
            raise TypeError(
                "ontology_complete must be bool."
            )

        if ontology_complete:
            missing = tuple(
                sorted(
                    set(required)
                    - set(represented)
                )
            )

            state = (
                OntologySufficiencyState.INSUFFICIENT
                if missing
                else OntologySufficiencyState.SUFFICIENT
            )

            reason = (
                "ONTOLOGY_MISSING_REQUIRED_CONCEPTS"
                if missing
                else "ONTOLOGY_REPRESENTS_REQUIRED_CONCEPTS"
            )

        else:
            missing = ()
            state = (
                OntologySufficiencyState.UNKNOWN
            )
            reason = (
                "ONTOLOGY_COMPLETENESS_UNKNOWN"
            )

        payload = {
            "capability_candidate_id": (
                candidate.candidate_id
            ),
            "ontology_id": (
                normalized_ontology_id
            ),
            "required_concepts": required,
            "represented_concepts": represented,
            "ontology_complete": ontology_complete,
            "state": state.value,
        }

        return CapabilityOntologyAssessment(
            assessment_id=_digest_id(
                "COA",
                payload,
            ),
            state=state,
            capability_candidate_id=(
                candidate.candidate_id
            ),
            landscape_change_id=(
                candidate.landscape_change_id
            ),
            current_snapshot_id=(
                candidate.current_snapshot_id
            ),
            scope_id=candidate.scope_id,
            subject_id=candidate.subject_id,
            capability_term=(
                candidate.capability_term
            ),
            evidence_id=(
                candidate.evidence_id
            ),
            source_ref=(
                candidate.source_ref
            ),
            landscape_evidence_ids=(
                candidate.landscape_evidence_ids
            ),
            ontology_id=(
                normalized_ontology_id
            ),
            required_concepts=required,
            represented_concepts=represented,
            missing_concepts=missing,
            ontology_complete=ontology_complete,
            reason=reason,
            verification_status=(
                candidate.verification_status
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedArchitectureEvolutionProposal:
    """
    Passive proposal describing a conceptual extension.

    It grants no authority to change schemas, migrate state,
    mutate Core, install, activate, authorize, or execute.
    """

    proposal_id: str
    assessment_id: str

    capability_candidate_id: str
    landscape_change_id: str
    current_snapshot_id: str

    scope_id: str
    subject_id: str
    capability_term: str

    evidence_id: str
    source_ref: str
    landscape_evidence_ids: tuple[str, ...]

    ontology_id: str
    missing_concepts: tuple[str, ...]
    proposed_concepts: tuple[str, ...]

    rationale: str

    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )

    proposal_approved: bool = False
    schema_mutation_requested: bool = False
    migration_requested: bool = False
    registry_mutation_requested: bool = False
    installation_requested: bool = False
    activation_requested: bool = False
    authorization_asserted: bool = False
    execution_requested: bool = False
    core_mutation_requested: bool = False
    supply_chain_artifact_created: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "proposal_id",
            "assessment_id",
            "capability_candidate_id",
            "landscape_change_id",
            "current_snapshot_id",
            "scope_id",
            "subject_id",
            "capability_term",
            "evidence_id",
            "source_ref",
            "ontology_id",
            "rationale",
            "verification_status",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(self, name),
                    name,
                ),
            )

        lineage = _text_tuple(
            self.landscape_evidence_ids,
            "landscape_evidence_ids",
        )

        if self.evidence_id not in lineage:
            raise (
                GovernedArchitectureEvolutionInvariantError(
                    "Architecture proposal evidence_id "
                    "must remain in landscape lineage."
                )
            )

        object.__setattr__(
            self,
            "landscape_evidence_ids",
            lineage,
        )

        missing = _text_tuple(
            self.missing_concepts,
            "missing_concepts",
        )

        proposed = _text_tuple(
            self.proposed_concepts,
            "proposed_concepts",
        )

        if not missing:
            raise (
                GovernedArchitectureEvolutionInvariantError(
                    "Architecture proposal requires "
                    "an explicit ontology gap."
                )
            )

        if not proposed:
            raise (
                GovernedArchitectureEvolutionInvariantError(
                    "Architecture proposal requires "
                    "explicit conceptual extensions."
                )
            )

        if not set(missing).issubset(
            set(proposed)
        ):
            raise (
                GovernedArchitectureEvolutionInvariantError(
                    "Proposed concepts must cover every "
                    "missing ontology concept."
                )
            )

        object.__setattr__(
            self,
            "missing_concepts",
            missing,
        )

        object.__setattr__(
            self,
            "proposed_concepts",
            proposed,
        )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                GovernedArchitectureEvolutionInvariantError(
                    "Architecture proposal derived from "
                    "external research must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        _assert_passive(
            proposal_approved=(
                self.proposal_approved
            ),
            schema_mutation_requested=(
                self.schema_mutation_requested
            ),
            migration_requested=(
                self.migration_requested
            ),
            registry_mutation_requested=(
                self.registry_mutation_requested
            ),
            installation_requested=(
                self.installation_requested
            ),
            activation_requested=(
                self.activation_requested
            ),
            authorization_asserted=(
                self.authorization_asserted
            ),
            execution_requested=(
                self.execution_requested
            ),
            core_mutation_requested=(
                self.core_mutation_requested
            ),
            supply_chain_artifact_created=(
                self.supply_chain_artifact_created
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
                GOVERNED_ARCHITECTURE_EVOLUTION_VERSION
            ),
            "proposal_id": self.proposal_id,
            "assessment_id": (
                self.assessment_id
            ),
            "capability_candidate_id": (
                self.capability_candidate_id
            ),
            "landscape_change_id": (
                self.landscape_change_id
            ),
            "current_snapshot_id": (
                self.current_snapshot_id
            ),
            "scope_id": self.scope_id,
            "subject_id": self.subject_id,
            "capability_term": (
                self.capability_term
            ),
            "evidence_id": self.evidence_id,
            "source_ref": self.source_ref,
            "landscape_evidence_ids": list(
                self.landscape_evidence_ids
            ),
            "ontology_id": self.ontology_id,
            "missing_concepts": list(
                self.missing_concepts
            ),
            "proposed_concepts": list(
                self.proposed_concepts
            ),
            "rationale": self.rationale,
            "verification_status": (
                self.verification_status
            ),
            "proposal_approved": False,
            "schema_mutation_requested": False,
            "migration_requested": False,
            "registry_mutation_requested": False,
            "installation_requested": False,
            "activation_requested": False,
            "authorization_asserted": False,
            "execution_requested": False,
            "core_mutation_requested": False,
            "supply_chain_artifact_created": False,
            "system_truth_asserted": False,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class ArchitectureEvolutionProposalSet:
    proposals: tuple[
        GovernedArchitectureEvolutionProposal,
        ...,
    ] = ()

    def __post_init__(
        self,
    ) -> None:
        supplied = tuple(
            self.proposals
        )

        for proposal in supplied:
            if not isinstance(
                proposal,
                GovernedArchitectureEvolutionProposal,
            ):
                raise TypeError(
                    "proposals must contain "
                    "GovernedArchitectureEvolutionProposal."
                )

        ordered = tuple(
            sorted(
                supplied,
                key=lambda item: (
                    item.ontology_id,
                    item.proposal_id,
                ),
            )
        )

        ids = [
            item.proposal_id
            for item in ordered
        ]

        if len(ids) != len(set(ids)):
            raise (
                GovernedArchitectureEvolutionInvariantError(
                    "Architecture proposal IDs "
                    "must be unique."
                )
            )

        object.__setattr__(
            self,
            "proposals",
            ordered,
        )

    @property
    def size(
        self,
    ) -> int:
        return len(
            self.proposals
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "version": (
                GOVERNED_ARCHITECTURE_EVOLUTION_VERSION
            ),
            "proposals": [
                proposal.to_dict()
                for proposal in self.proposals
            ],
        }


class GovernedArchitectureEvolutionProposer:
    """
    Pure BMF-021 proposal boundary.

    UNKNOWN and SUFFICIENT assessments produce no proposal.

    INSUFFICIENT assessment may produce a passive conceptual
    architecture-evolution proposal only.

    No schema mutation, migration, registry mutation,
    supply-chain artifact, installation, activation,
    authorization, execution, or Core mutation occurs here.
    """

    @classmethod
    def propose(
        cls,
        assessment: CapabilityOntologyAssessment,
        *,
        proposed_concepts: Iterable[str] = (),
        rationale: str,
    ) -> ArchitectureEvolutionProposalSet:
        if not isinstance(
            assessment,
            CapabilityOntologyAssessment,
        ):
            raise TypeError(
                "assessment must be "
                "CapabilityOntologyAssessment."
            )

        if (
            assessment.state
            is not OntologySufficiencyState.INSUFFICIENT
        ):
            return ArchitectureEvolutionProposalSet()

        concepts = _text_tuple(
            proposed_concepts,
            "proposed_concepts",
        )

        normalized_rationale = (
            _required_text(
                rationale,
                "rationale",
            )
        )

        if not concepts:
            raise (
                GovernedArchitectureEvolutionInvariantError(
                    "INSUFFICIENT ontology requires "
                    "explicit proposed concepts."
                )
            )

        if not set(
            assessment.missing_concepts
        ).issubset(
            set(concepts)
        ):
            raise (
                GovernedArchitectureEvolutionInvariantError(
                    "Proposed concepts must cover the "
                    "explicit ontology gap."
                )
            )

        payload = {
            "assessment_id": (
                assessment.assessment_id
            ),
            "ontology_id": (
                assessment.ontology_id
            ),
            "missing_concepts": (
                assessment.missing_concepts
            ),
            "proposed_concepts": concepts,
            "rationale": normalized_rationale,
        }

        proposal = (
            GovernedArchitectureEvolutionProposal(
                proposal_id=_digest_id(
                    "AEP",
                    payload,
                ),
                assessment_id=(
                    assessment.assessment_id
                ),
                capability_candidate_id=(
                    assessment.capability_candidate_id
                ),
                landscape_change_id=(
                    assessment.landscape_change_id
                ),
                current_snapshot_id=(
                    assessment.current_snapshot_id
                ),
                scope_id=(
                    assessment.scope_id
                ),
                subject_id=(
                    assessment.subject_id
                ),
                capability_term=(
                    assessment.capability_term
                ),
                evidence_id=(
                    assessment.evidence_id
                ),
                source_ref=(
                    assessment.source_ref
                ),
                landscape_evidence_ids=(
                    assessment.landscape_evidence_ids
                ),
                ontology_id=(
                    assessment.ontology_id
                ),
                missing_concepts=(
                    assessment.missing_concepts
                ),
                proposed_concepts=concepts,
                rationale=(
                    normalized_rationale
                ),
                verification_status=(
                    assessment.verification_status
                ),
            )
        )

        return ArchitectureEvolutionProposalSet(
            proposals=(
                proposal,
            )
        )


__all__ = [
    "GOVERNED_ARCHITECTURE_EVOLUTION_VERSION",
    "GovernedArchitectureEvolutionInvariantError",
    "OntologySufficiencyState",
    "CapabilityOntologyAssessment",
    "GovernedCapabilityOntologyAssessor",
    "GovernedArchitectureEvolutionProposal",
    "ArchitectureEvolutionProposalSet",
    "GovernedArchitectureEvolutionProposer",
]
