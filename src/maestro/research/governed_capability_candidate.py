from __future__ import annotations

import hashlib
import json

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from .capability_integration import (
    CapabilityIntegrationEvaluation,
)
from .technology_landscape_change import (
    LandscapeChangeState,
    TechnologyLandscapeChange,
    TechnologyLandscapeObservation,
    TechnologyLandscapeSnapshot,
)


GOVERNED_CAPABILITY_CANDIDATE_VERSION = 1


class GovernedCapabilityCandidateInvariantError(
    ValueError
):
    pass


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


def _candidate_id(
    *,
    landscape_change_id: str,
    current_snapshot_id: str,
    subject_id: str,
    capability_term: str,
    evidence_id: str,
) -> str:
    canonical = json.dumps(
        {
            "landscape_change_id": (
                landscape_change_id
            ),
            "current_snapshot_id": (
                current_snapshot_id
            ),
            "subject_id": subject_id,
            "capability_term": capability_term,
            "evidence_id": evidence_id,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    digest = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()

    return f"GCC-{digest[:24]}"


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedCapabilityCandidate:
    """
    Passive BMF-019 capability candidate derived from
    governed research evidence and explicit landscape change.

    A candidate is evidence-linked possibility only.
    It is not an integration candidate, adapter candidate,
    trust decision, installation, activation, authorization,
    execution request, Core mutation, or system truth.
    """

    candidate_id: str
    landscape_change_id: str
    current_snapshot_id: str
    scope_id: str
    subject_id: str
    capability_term: str
    evidence_id: str
    source_ref: str
    landscape_evidence_ids: tuple[str, ...]

    expected_capability_gain: float | None = None

    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )

    trust_asserted: bool = False
    integration_candidate_created: bool = False
    adapter_candidate_created: bool = False
    installation_requested: bool = False
    activation_requested: bool = False
    authorization_asserted: bool = False
    execution_requested: bool = False
    core_mutation_requested: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "candidate_id",
            "landscape_change_id",
            "current_snapshot_id",
            "scope_id",
            "subject_id",
            "capability_term",
            "evidence_id",
            "source_ref",
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

        evidence_ids = tuple(
            sorted({
                _required_text(
                    item,
                    "landscape_evidence_id",
                )
                for item in self.landscape_evidence_ids
            })
        )

        if self.evidence_id not in evidence_ids:
            raise GovernedCapabilityCandidateInvariantError(
                "Candidate evidence_id must belong "
                "to landscape evidence lineage."
            )

        object.__setattr__(
            self,
            "landscape_evidence_ids",
            evidence_ids,
        )

        if (
            self.expected_capability_gain
            is not None
        ):
            if isinstance(
                self.expected_capability_gain,
                bool,
            ) or not isinstance(
                self.expected_capability_gain,
                (int, float),
            ):
                raise TypeError(
                    "expected_capability_gain "
                    "must be numeric or None."
                )

            gain = float(
                self.expected_capability_gain
            )

            if not 0.0 <= gain <= 1.0:
                raise ValueError(
                    "expected_capability_gain "
                    "must be in [0, 1]."
                )

            object.__setattr__(
                self,
                "expected_capability_gain",
                gain,
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise GovernedCapabilityCandidateInvariantError(
                "Capability candidates derived from "
                "external research must remain "
                "UNVERIFIED_EXTERNAL."
            )

        forbidden = {
            "trust_asserted": (
                self.trust_asserted
            ),
            "integration_candidate_created": (
                self.integration_candidate_created
            ),
            "adapter_candidate_created": (
                self.adapter_candidate_created
            ),
            "installation_requested": (
                self.installation_requested
            ),
            "activation_requested": (
                self.activation_requested
            ),
            "authorization_asserted": (
                self.authorization_asserted
            ),
            "execution_requested": (
                self.execution_requested
            ),
            "core_mutation_requested": (
                self.core_mutation_requested
            ),
            "system_truth_asserted": (
                self.system_truth_asserted
            ),
        }

        asserted = sorted(
            name
            for name, value
            in forbidden.items()
            if value is not False
        )

        if asserted:
            raise GovernedCapabilityCandidateInvariantError(
                "Capability candidate cannot assert "
                "downstream authority: "
                + ", ".join(asserted)
            )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "candidate_version": (
                GOVERNED_CAPABILITY_CANDIDATE_VERSION
            ),
            "candidate_id": self.candidate_id,
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
            "expected_capability_gain": (
                self.expected_capability_gain
            ),
            "verification_status": (
                self.verification_status
            ),
            "trust_asserted": False,
            "integration_candidate_created": False,
            "adapter_candidate_created": False,
            "installation_requested": False,
            "activation_requested": False,
            "authorization_asserted": False,
            "execution_requested": False,
            "core_mutation_requested": False,
            "system_truth_asserted": False,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class CapabilityCandidateSet:
    candidates: tuple[
        GovernedCapabilityCandidate,
        ...,
    ]

    def __post_init__(
        self,
    ) -> None:
        supplied = tuple(
            self.candidates
        )

        for candidate in supplied:
            if not isinstance(
                candidate,
                GovernedCapabilityCandidate,
            ):
                raise TypeError(
                    "candidates must contain "
                    "GovernedCapabilityCandidate "
                    "objects only."
                )

        ordered = tuple(
            sorted(
                supplied,
                key=lambda item: (
                    item.subject_id,
                    item.capability_term,
                    item.evidence_id,
                    item.candidate_id,
                ),
            )
        )

        ids = [
            candidate.candidate_id
            for candidate in ordered
        ]

        if len(ids) != len(set(ids)):
            raise GovernedCapabilityCandidateInvariantError(
                "Capability candidate IDs "
                "must be unique."
            )

        object.__setattr__(
            self,
            "candidates",
            ordered,
        )

    @property
    def size(
        self,
    ) -> int:
        return len(
            self.candidates
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "candidate_version": (
                GOVERNED_CAPABILITY_CANDIDATE_VERSION
            ),
            "candidates": [
                candidate.to_dict()
                for candidate
                in self.candidates
            ],
        }


class GovernedCapabilityCandidateDeriver:
    """
    Pure BMF-019 derivation boundary.

    It consumes explicit CHANGED landscape evidence,
    the corresponding current snapshot, and existing
    capability-integration evaluations.

    It creates passive capability candidates only for
    added or modified current subjects whose research
    evidence explicitly supports novel capability terms.

    It performs no research, network access, routing,
    integration proposal, adapter proposal, trust decision,
    installation, activation, authorization, execution,
    learning, promotion, persistence, or Core mutation.
    """

    @staticmethod
    def _evidence_map(
        snapshot: TechnologyLandscapeSnapshot,
    ) -> dict[
        str,
        TechnologyLandscapeObservation | None,
    ]:
        rows: dict[
            str,
            TechnologyLandscapeObservation | None,
        ] = {}

        for observation in snapshot.observations:
            evidence_id = (
                observation.evidence_id
            )

            if evidence_id in rows:
                rows[evidence_id] = None
            else:
                rows[evidence_id] = (
                    observation
                )

        return rows

    @classmethod
    def derive(
        cls,
        change: TechnologyLandscapeChange,
        *,
        current_snapshot: (
            TechnologyLandscapeSnapshot
            | None
        ),
        evaluations: Iterable[
            CapabilityIntegrationEvaluation
        ] = (),
    ) -> CapabilityCandidateSet:
        if not isinstance(
            change,
            TechnologyLandscapeChange,
        ):
            raise TypeError(
                "change must be "
                "TechnologyLandscapeChange."
            )

        if (
            change.state
            is not LandscapeChangeState.CHANGED
        ):
            return CapabilityCandidateSet(
                candidates=()
            )

        if current_snapshot is None:
            raise GovernedCapabilityCandidateInvariantError(
                "CHANGED landscape evidence requires "
                "its current snapshot."
            )

        if not isinstance(
            current_snapshot,
            TechnologyLandscapeSnapshot,
        ):
            raise TypeError(
                "current_snapshot must be "
                "TechnologyLandscapeSnapshot "
                "or None."
            )

        if (
            change.current_snapshot_id
            != current_snapshot.snapshot_id
        ):
            raise GovernedCapabilityCandidateInvariantError(
                "Current snapshot identity does not "
                "match landscape change evidence."
            )

        if (
            change.scope_id
            != current_snapshot.scope_id
        ):
            raise GovernedCapabilityCandidateInvariantError(
                "Current snapshot scope does not "
                "match landscape change evidence."
            )

        changed_current_subjects = frozenset(
            change.added_subject_ids
            + change.modified_subject_ids
        )

        evidence_map = cls._evidence_map(
            current_snapshot
        )

        supplied = tuple(
            evaluations
        )

        for evaluation in supplied:
            if not isinstance(
                evaluation,
                CapabilityIntegrationEvaluation,
            ):
                raise TypeError(
                    "evaluations must contain "
                    "CapabilityIntegrationEvaluation "
                    "objects only."
                )

        candidates = []

        for evaluation in sorted(
            supplied,
            key=lambda item: (
                item.evidence_id
            ),
        ):
            if (
                evaluation.evidence_id
                not in change.evidence_ids
            ):
                raise GovernedCapabilityCandidateInvariantError(
                    "Capability evaluation evidence "
                    "is absent from landscape-change "
                    "evidence lineage."
                )

            if (
                evaluation.evidence_id
                not in evidence_map
            ):
                raise GovernedCapabilityCandidateInvariantError(
                    "Capability evaluation evidence "
                    "is absent from current landscape "
                    "snapshot."
                )

            observation = evidence_map[
                evaluation.evidence_id
            ]

            if observation is None:
                raise GovernedCapabilityCandidateInvariantError(
                    "Capability evaluation evidence "
                    "maps ambiguously to multiple "
                    "current subjects."
                )

            if (
                observation.subject_id
                not in changed_current_subjects
            ):
                continue

            if (
                evaluation.verification_status
                != "UNVERIFIED_EXTERNAL"
            ):
                raise GovernedCapabilityCandidateInvariantError(
                    "Capability evaluation must remain "
                    "UNVERIFIED_EXTERNAL."
                )

            if (
                evaluation.system_truth_asserted
                is not False
            ):
                raise GovernedCapabilityCandidateInvariantError(
                    "Capability evaluation cannot "
                    "assert system truth."
                )

            for capability_term in sorted(
                evaluation
                .matched_novel_capability_terms
            ):
                term = _required_text(
                    capability_term,
                    "capability_term",
                )

                candidates.append(
                    GovernedCapabilityCandidate(
                        candidate_id=_candidate_id(
                            landscape_change_id=(
                                change.change_id
                            ),
                            current_snapshot_id=(
                                current_snapshot
                                .snapshot_id
                            ),
                            subject_id=(
                                observation.subject_id
                            ),
                            capability_term=term,
                            evidence_id=(
                                evaluation.evidence_id
                            ),
                        ),
                        landscape_change_id=(
                            change.change_id
                        ),
                        current_snapshot_id=(
                            current_snapshot.snapshot_id
                        ),
                        scope_id=(
                            current_snapshot.scope_id
                        ),
                        subject_id=(
                            observation.subject_id
                        ),
                        capability_term=term,
                        evidence_id=(
                            evaluation.evidence_id
                        ),
                        source_ref=(
                            observation.source_ref
                        ),
                        landscape_evidence_ids=(
                            change.evidence_ids
                        ),
                        expected_capability_gain=(
                            evaluation
                            .expected_capability_gain
                        ),
                        verification_status=(
                            evaluation
                            .verification_status
                        ),
                    )
                )

        return CapabilityCandidateSet(
            candidates=tuple(
                candidates
            )
        )


__all__ = [
    "GOVERNED_CAPABILITY_CANDIDATE_VERSION",
    "GovernedCapabilityCandidateInvariantError",
    "GovernedCapabilityCandidate",
    "CapabilityCandidateSet",
    "GovernedCapabilityCandidateDeriver",
]
