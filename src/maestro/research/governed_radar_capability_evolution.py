from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Iterable


GOVERNED_RADAR_CAPABILITY_EVOLUTION_VERSION = 1


class RadarCapabilityEvolutionInvariantError(
    ValueError
):
    pass


class ResearchEvidenceIncompleteError(
    RadarCapabilityEvolutionInvariantError
):
    pass


class CapabilityGapAbsentError(
    RadarCapabilityEvolutionInvariantError
):
    pass


class ObservationSourceKind(StrEnum):
    HUMAN_DISCOVERY = "HUMAN_DISCOVERY"
    TECHNOLOGY_RADAR = "TECHNOLOGY_RADAR"
    RESEARCH_RETURN = "RESEARCH_RETURN"


class ResearchVerificationState(StrEnum):
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


class EvolutionProposalKind(StrEnum):
    ADAPTER = "ADAPTER"
    INTEGRATION = "INTEGRATION"
    ARCHITECTURE = "ARCHITECTURE"


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
        raise RadarCapabilityEvolutionInvariantError(
            f"{name} must not be empty."
        )

    if "\x00" in value:
        raise RadarCapabilityEvolutionInvariantError(
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
        raise RadarCapabilityEvolutionInvariantError(
            f"{name} must not be empty."
        )

    if len(rows) != len(set(rows)):
        raise RadarCapabilityEvolutionInvariantError(
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
    return (
        prefix
        + "-"
        + hashlib.sha256(
            _canonical_json(
                payload
            ).encode("utf-8")
        ).hexdigest()[:24]
    )


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedTechnologyObservation:
    subject: str
    source_kind: ObservationSourceKind
    source_ref: str

    claims: tuple[str, ...]
    capability_terms: tuple[str, ...]

    observation_id: str = field(
        init=False
    )

    trust_asserted: bool = False
    installation_requested: bool = False
    installation_authorized: bool = False
    activation_requested: bool = False
    activation_authorized: bool = False
    execution_requested: bool = False
    execution_authorized: bool = False
    learning_authorized: bool = False
    promotion_authorized: bool = False
    constitutional_dependency: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "subject",
            _required_text(
                self.subject,
                "subject",
            ),
        )

        if not isinstance(
            self.source_kind,
            ObservationSourceKind,
        ):
            raise TypeError(
                "source_kind must be "
                "ObservationSourceKind."
            )

        object.__setattr__(
            self,
            "source_ref",
            _required_text(
                self.source_ref,
                "source_ref",
            ),
        )

        object.__setattr__(
            self,
            "claims",
            _normalized_tuple(
                self.claims,
                "claim",
            ),
        )

        object.__setattr__(
            self,
            "capability_terms",
            _normalized_tuple(
                self.capability_terms,
                "capability_term",
            ),
        )

        for name in (
            "trust_asserted",
            "installation_requested",
            "installation_authorized",
            "activation_requested",
            "activation_authorized",
            "execution_requested",
            "execution_authorized",
            "learning_authorized",
            "promotion_authorized",
            "constitutional_dependency",
        ):
            if getattr(self, name) is not False:
                raise RadarCapabilityEvolutionInvariantError(
                    "Technology observation "
                    f"cannot assert {name}."
                )

        object.__setattr__(
            self,
            "observation_id",
            _stable_id(
                "RCO",
                {
                    "subject": self.subject,
                    "source_kind": (
                        self.source_kind.value
                    ),
                    "source_ref": (
                        self.source_ref
                    ),
                    "claims": list(
                        self.claims
                    ),
                    "capability_terms": list(
                        self.capability_terms
                    ),
                },
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedResearchEvidence:
    observation_id: str
    subject: str

    verification_state: ResearchVerificationState

    findings: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    capability_terms: tuple[str, ...]

    research_evidence_id: str = field(
        init=False
    )

    truth_asserted: bool = False
    trust_asserted: bool = False
    installation_authorized: bool = False
    activation_authorized: bool = False
    execution_authorized: bool = False

    def __post_init__(self) -> None:
        for name in (
            "observation_id",
            "subject",
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
            self.verification_state,
            ResearchVerificationState,
        ):
            raise TypeError(
                "verification_state must be "
                "ResearchVerificationState."
            )

        object.__setattr__(
            self,
            "findings",
            _normalized_tuple(
                self.findings,
                "finding",
            ),
        )

        object.__setattr__(
            self,
            "evidence_refs",
            _normalized_tuple(
                self.evidence_refs,
                "evidence_ref",
            ),
        )

        object.__setattr__(
            self,
            "capability_terms",
            _normalized_tuple(
                self.capability_terms,
                "capability_term",
            ),
        )

        for name in (
            "truth_asserted",
            "trust_asserted",
            "installation_authorized",
            "activation_authorized",
            "execution_authorized",
        ):
            if getattr(self, name) is not False:
                raise RadarCapabilityEvolutionInvariantError(
                    "Research evidence cannot "
                    f"assert {name}."
                )

        object.__setattr__(
            self,
            "research_evidence_id",
            _stable_id(
                "RRE",
                {
                    "observation_id": (
                        self.observation_id
                    ),
                    "subject": self.subject,
                    "verification_state": (
                        self
                        .verification_state
                        .value
                    ),
                    "findings": list(
                        self.findings
                    ),
                    "evidence_refs": list(
                        self.evidence_refs
                    ),
                    "capability_terms": list(
                        self.capability_terms
                    ),
                },
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedCapabilityEvolutionCandidate:
    research_evidence_id: str
    subject: str

    capability_terms: tuple[str, ...]
    existing_capabilities: tuple[str, ...]
    missing_capabilities: tuple[str, ...]

    candidate_id: str = field(
        init=False
    )

    trusted: bool = False
    installation_requested: bool = False
    activation_requested: bool = False
    authorization_asserted: bool = False
    execution_requested: bool = False
    ontology_mutation_requested: bool = False
    constitutional_identity_change_requested: bool = False
    core_mutation_requested: bool = False

    def __post_init__(self) -> None:
        for name in (
            "research_evidence_id",
            "subject",
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
            "capability_terms",
            "existing_capabilities",
            "missing_capabilities",
        ):
            object.__setattr__(
                self,
                name,
                _normalized_tuple(
                    getattr(self, name),
                    name,
                    require_nonempty=(
                        name
                        != "existing_capabilities"
                    ),
                ),
            )

        terms = set(
            self.capability_terms
        )

        existing = set(
            self.existing_capabilities
        )

        missing = set(
            self.missing_capabilities
        )

        if missing != (
            terms - existing
        ):
            raise RadarCapabilityEvolutionInvariantError(
                "Missing capabilities must "
                "exactly equal capability terms "
                "minus existing capabilities."
            )

        if not missing:
            raise CapabilityGapAbsentError(
                "Capability evolution candidate "
                "requires an actual capability gap."
            )

        for name in (
            "trusted",
            "installation_requested",
            "activation_requested",
            "authorization_asserted",
            "execution_requested",
            "ontology_mutation_requested",
            "constitutional_identity_change_requested",
            "core_mutation_requested",
        ):
            if getattr(self, name) is not False:
                raise RadarCapabilityEvolutionInvariantError(
                    "Capability candidate cannot "
                    f"assert {name}."
                )

        object.__setattr__(
            self,
            "candidate_id",
            _stable_id(
                "GCC2",
                {
                    "research_evidence_id": (
                        self
                        .research_evidence_id
                    ),
                    "subject": self.subject,
                    "capability_terms": list(
                        self.capability_terms
                    ),
                    "existing_capabilities": list(
                        self
                        .existing_capabilities
                    ),
                    "missing_capabilities": list(
                        self
                        .missing_capabilities
                    ),
                },
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedCapabilityEvolutionProposal:
    candidate_id: str
    subject: str
    kind: EvolutionProposalKind

    missing_capabilities: tuple[str, ...]

    requirements: tuple[str, ...]
    evidence_refs: tuple[str, ...]

    proposal_id: str = field(
        init=False
    )

    trust_granted: bool = False
    installation_requested: bool = False
    installation_authorized: bool = False
    activation_requested: bool = False
    activation_authorized: bool = False
    authorization_asserted: bool = False
    execution_requested: bool = False
    execution_authorized: bool = False

    ontology_mutation_requested: bool = False
    constitutional_identity_change_requested: bool = False
    core_mutation_requested: bool = False

    def __post_init__(self) -> None:
        for name in (
            "candidate_id",
            "subject",
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
            self.kind,
            EvolutionProposalKind,
        ):
            raise TypeError(
                "kind must be "
                "EvolutionProposalKind."
            )

        for name in (
            "missing_capabilities",
            "requirements",
            "evidence_refs",
        ):
            object.__setattr__(
                self,
                name,
                _normalized_tuple(
                    getattr(self, name),
                    name,
                ),
            )

        for name in (
            "trust_granted",
            "installation_requested",
            "installation_authorized",
            "activation_requested",
            "activation_authorized",
            "authorization_asserted",
            "execution_requested",
            "execution_authorized",
            "ontology_mutation_requested",
            "constitutional_identity_change_requested",
            "core_mutation_requested",
        ):
            if getattr(self, name) is not False:
                raise RadarCapabilityEvolutionInvariantError(
                    "Evolution proposal cannot "
                    f"assert {name}."
                )

        object.__setattr__(
            self,
            "proposal_id",
            _stable_id(
                "CEP",
                {
                    "candidate_id": (
                        self.candidate_id
                    ),
                    "subject": self.subject,
                    "kind": self.kind.value,
                    "missing_capabilities": list(
                        self.missing_capabilities
                    ),
                    "requirements": list(
                        self.requirements
                    ),
                    "evidence_refs": list(
                        self.evidence_refs
                    ),
                },
            ),
        )


class GovernedRadarCapabilityEvolution:
    @staticmethod
    def record_observation(
        *,
        subject: str,
        source_kind: ObservationSourceKind,
        source_ref: str,
        claims: Iterable[str],
        capability_terms: Iterable[str],
    ) -> GovernedTechnologyObservation:
        return GovernedTechnologyObservation(
            subject=subject,
            source_kind=source_kind,
            source_ref=source_ref,
            claims=tuple(claims),
            capability_terms=tuple(
                capability_terms
            ),
        )

    @staticmethod
    def admit_research(
        observation: GovernedTechnologyObservation,
        *,
        verification_state: ResearchVerificationState,
        findings: Iterable[str],
        evidence_refs: Iterable[str],
        capability_terms: Iterable[str] | None = None,
    ) -> GovernedResearchEvidence:
        if not isinstance(
            observation,
            GovernedTechnologyObservation,
        ):
            raise TypeError(
                "observation must be "
                "GovernedTechnologyObservation."
            )

        terms = (
            observation.capability_terms
            if capability_terms is None
            else tuple(capability_terms)
        )

        terms = _normalized_tuple(
            terms,
            "capability_term",
        )

        if not set(terms).issubset(
            set(
                observation
                .capability_terms
            )
        ):
            raise RadarCapabilityEvolutionInvariantError(
                "Research cannot silently "
                "introduce capabilities absent "
                "from the originating observation."
            )

        return GovernedResearchEvidence(
            observation_id=(
                observation.observation_id
            ),
            subject=observation.subject,
            verification_state=(
                verification_state
            ),
            findings=tuple(findings),
            evidence_refs=tuple(
                evidence_refs
            ),
            capability_terms=terms,
        )

    @staticmethod
    def derive_candidate(
        evidence: GovernedResearchEvidence,
        *,
        existing_capabilities: Iterable[str],
    ) -> GovernedCapabilityEvolutionCandidate:
        if not isinstance(
            evidence,
            GovernedResearchEvidence,
        ):
            raise TypeError(
                "evidence must be "
                "GovernedResearchEvidence."
            )

        if (
            evidence.verification_state
            is not ResearchVerificationState
            .VERIFIED
        ):
            raise ResearchEvidenceIncompleteError(
                "Only VERIFIED research "
                "evidence may produce a "
                "capability candidate."
            )

        existing = _normalized_tuple(
            existing_capabilities,
            "existing_capability",
            require_nonempty=False,
        )

        missing = tuple(
            sorted(
                set(
                    evidence
                    .capability_terms
                )
                - set(existing)
            )
        )

        if not missing:
            raise CapabilityGapAbsentError(
                "Research reveals no missing "
                "capability."
            )

        return (
            GovernedCapabilityEvolutionCandidate(
                research_evidence_id=(
                    evidence
                    .research_evidence_id
                ),
                subject=evidence.subject,
                capability_terms=(
                    evidence
                    .capability_terms
                ),
                existing_capabilities=(
                    existing
                ),
                missing_capabilities=(
                    missing
                ),
            )
        )

    @staticmethod
    def propose_evolution(
        candidate: GovernedCapabilityEvolutionCandidate,
        *,
        kind: EvolutionProposalKind,
        requirements: Iterable[str],
        evidence_refs: Iterable[str],
    ) -> GovernedCapabilityEvolutionProposal:
        if not isinstance(
            candidate,
            GovernedCapabilityEvolutionCandidate,
        ):
            raise TypeError(
                "candidate must be "
                "GovernedCapabilityEvolutionCandidate."
            )

        return GovernedCapabilityEvolutionProposal(
            candidate_id=(
                candidate.candidate_id
            ),
            subject=candidate.subject,
            kind=kind,
            missing_capabilities=(
                candidate
                .missing_capabilities
            ),
            requirements=tuple(
                requirements
            ),
            evidence_refs=tuple(
                evidence_refs
            ),
        )


__all__ = [
    "GOVERNED_RADAR_CAPABILITY_EVOLUTION_VERSION",
    "RadarCapabilityEvolutionInvariantError",
    "ResearchEvidenceIncompleteError",
    "CapabilityGapAbsentError",
    "ObservationSourceKind",
    "ResearchVerificationState",
    "EvolutionProposalKind",
    "GovernedTechnologyObservation",
    "GovernedResearchEvidence",
    "GovernedCapabilityEvolutionCandidate",
    "GovernedCapabilityEvolutionProposal",
    "GovernedRadarCapabilityEvolution",
]
