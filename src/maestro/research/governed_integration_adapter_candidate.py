from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass
from typing import Any

from .governed_capability_candidate import (
    GovernedCapabilityCandidate,
)


GOVERNED_INTEGRATION_ADAPTER_CANDIDATE_VERSION = 1


class GovernedIntegrationAdapterCandidateInvariantError(
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


def _text_tuple(
    values: tuple[str, ...],
    name: str,
) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise TypeError(
            f"{name} must be a tuple."
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


def _proposal_id(
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
    registry_mutation_requested: bool,
    adapter_binding_created: bool,
    trust_asserted: bool,
    installation_requested: bool,
    activation_requested: bool,
    authorization_asserted: bool,
    execution_requested: bool,
    core_mutation_requested: bool,
    architecture_evolution_proposal_created: bool,
    system_truth_asserted: bool,
) -> None:
    flags = {
        "registry_mutation_requested": (
            registry_mutation_requested
        ),
        "adapter_binding_created": (
            adapter_binding_created
        ),
        "trust_asserted": trust_asserted,
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
        "architecture_evolution_proposal_created": (
            architecture_evolution_proposal_created
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
            GovernedIntegrationAdapterCandidateInvariantError(
                "BMF-020 proposal cannot assert "
                "downstream authority: "
                + ", ".join(asserted)
            )
        )


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedIntegrationCandidate:
    proposal_id: str

    capability_candidate_id: str
    landscape_change_id: str
    current_snapshot_id: str

    scope_id: str
    subject_id: str
    capability_term: str

    evidence_id: str
    source_ref: str
    landscape_evidence_ids: tuple[str, ...]

    interface_contract: str
    integration_requirements: tuple[str, ...] = ()

    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )

    registry_mutation_requested: bool = False
    adapter_binding_created: bool = False
    trust_asserted: bool = False
    installation_requested: bool = False
    activation_requested: bool = False
    authorization_asserted: bool = False
    execution_requested: bool = False
    core_mutation_requested: bool = False

    architecture_evolution_proposal_created: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "proposal_id",
            "capability_candidate_id",
            "landscape_change_id",
            "current_snapshot_id",
            "scope_id",
            "subject_id",
            "capability_term",
            "evidence_id",
            "source_ref",
            "interface_contract",
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
                GovernedIntegrationAdapterCandidateInvariantError(
                    "Integration proposal evidence_id "
                    "must remain in landscape lineage."
                )
            )

        object.__setattr__(
            self,
            "landscape_evidence_ids",
            evidence_ids,
        )

        object.__setattr__(
            self,
            "integration_requirements",
            _text_tuple(
                self.integration_requirements,
                "integration_requirements",
            ),
        )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                GovernedIntegrationAdapterCandidateInvariantError(
                    "Integration proposal derived from "
                    "external research must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        _assert_passive(
            registry_mutation_requested=(
                self.registry_mutation_requested
            ),
            adapter_binding_created=(
                self.adapter_binding_created
            ),
            trust_asserted=(
                self.trust_asserted
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
            architecture_evolution_proposal_created=(
                self
                .architecture_evolution_proposal_created
            ),
            system_truth_asserted=(
                self.system_truth_asserted
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "proposal_version": (
                GOVERNED_INTEGRATION_ADAPTER_CANDIDATE_VERSION
            ),
            "proposal_kind": "INTEGRATION",
            "proposal_id": self.proposal_id,
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
            "interface_contract": (
                self.interface_contract
            ),
            "integration_requirements": list(
                self.integration_requirements
            ),
            "verification_status": (
                self.verification_status
            ),
            "registry_mutation_requested": False,
            "adapter_binding_created": False,
            "trust_asserted": False,
            "installation_requested": False,
            "activation_requested": False,
            "authorization_asserted": False,
            "execution_requested": False,
            "core_mutation_requested": False,
            "architecture_evolution_proposal_created": False,
            "system_truth_asserted": False,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedAdapterCandidate:
    proposal_id: str

    integration_proposal_id: str
    capability_candidate_id: str

    landscape_change_id: str
    current_snapshot_id: str

    scope_id: str
    subject_id: str
    capability_term: str

    evidence_id: str
    source_ref: str
    landscape_evidence_ids: tuple[str, ...]

    interface_contract: str
    adapter_kind: str
    resource_contract: str

    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )

    registry_mutation_requested: bool = False
    adapter_binding_created: bool = False
    trust_asserted: bool = False
    installation_requested: bool = False
    activation_requested: bool = False
    authorization_asserted: bool = False
    execution_requested: bool = False
    core_mutation_requested: bool = False

    architecture_evolution_proposal_created: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "proposal_id",
            "integration_proposal_id",
            "capability_candidate_id",
            "landscape_change_id",
            "current_snapshot_id",
            "scope_id",
            "subject_id",
            "capability_term",
            "evidence_id",
            "source_ref",
            "interface_contract",
            "adapter_kind",
            "resource_contract",
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
                GovernedIntegrationAdapterCandidateInvariantError(
                    "Adapter proposal evidence_id "
                    "must remain in landscape lineage."
                )
            )

        object.__setattr__(
            self,
            "landscape_evidence_ids",
            evidence_ids,
        )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                GovernedIntegrationAdapterCandidateInvariantError(
                    "Adapter proposal derived from "
                    "external research must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        _assert_passive(
            registry_mutation_requested=(
                self.registry_mutation_requested
            ),
            adapter_binding_created=(
                self.adapter_binding_created
            ),
            trust_asserted=(
                self.trust_asserted
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
            architecture_evolution_proposal_created=(
                self
                .architecture_evolution_proposal_created
            ),
            system_truth_asserted=(
                self.system_truth_asserted
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "proposal_version": (
                GOVERNED_INTEGRATION_ADAPTER_CANDIDATE_VERSION
            ),
            "proposal_kind": "ADAPTER",
            "proposal_id": self.proposal_id,
            "integration_proposal_id": (
                self.integration_proposal_id
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
            "interface_contract": (
                self.interface_contract
            ),
            "adapter_kind": self.adapter_kind,
            "resource_contract": (
                self.resource_contract
            ),
            "verification_status": (
                self.verification_status
            ),
            "registry_mutation_requested": False,
            "adapter_binding_created": False,
            "trust_asserted": False,
            "installation_requested": False,
            "activation_requested": False,
            "authorization_asserted": False,
            "execution_requested": False,
            "core_mutation_requested": False,
            "architecture_evolution_proposal_created": False,
            "system_truth_asserted": False,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class IntegrationAdapterCandidateSet:
    integration_candidates: tuple[
        GovernedIntegrationCandidate,
        ...,
    ] = ()

    adapter_candidates: tuple[
        GovernedAdapterCandidate,
        ...,
    ] = ()

    def __post_init__(
        self,
    ) -> None:
        integrations = tuple(
            sorted(
                self.integration_candidates,
                key=lambda item: item.proposal_id,
            )
        )

        adapters = tuple(
            sorted(
                self.adapter_candidates,
                key=lambda item: item.proposal_id,
            )
        )

        for item in integrations:
            if not isinstance(
                item,
                GovernedIntegrationCandidate,
            ):
                raise TypeError(
                    "integration_candidates must "
                    "contain GovernedIntegrationCandidate."
                )

        for item in adapters:
            if not isinstance(
                item,
                GovernedAdapterCandidate,
            ):
                raise TypeError(
                    "adapter_candidates must contain "
                    "GovernedAdapterCandidate."
                )

        all_ids = [
            item.proposal_id
            for item in integrations + adapters
        ]

        if len(all_ids) != len(set(all_ids)):
            raise (
                GovernedIntegrationAdapterCandidateInvariantError(
                    "Proposal IDs must be unique."
                )
            )

        object.__setattr__(
            self,
            "integration_candidates",
            integrations,
        )

        object.__setattr__(
            self,
            "adapter_candidates",
            adapters,
        )

    @property
    def size(
        self,
    ) -> int:
        return (
            len(self.integration_candidates)
            + len(self.adapter_candidates)
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "proposal_version": (
                GOVERNED_INTEGRATION_ADAPTER_CANDIDATE_VERSION
            ),
            "integration_candidates": [
                item.to_dict()
                for item in self.integration_candidates
            ],
            "adapter_candidates": [
                item.to_dict()
                for item in self.adapter_candidates
            ],
        }


class GovernedIntegrationAdapterCandidateProposer:
    """
    Pure BMF-020 proposal boundary.

    No registry object, adapter object, platform binding,
    activation authority, execution authority, or
    architecture-evolution proposal is created here.
    """

    @classmethod
    def propose(
        cls,
        candidate: (
            GovernedCapabilityCandidate
            | None
        ),
        *,
        interface_contract: str | None = None,
        integration_requirements: tuple[str, ...] = (),
        adapter_kind: str | None = None,
        resource_contract: str | None = None,
    ) -> IntegrationAdapterCandidateSet:
        if candidate is None:
            return IntegrationAdapterCandidateSet()

        if not isinstance(
            candidate,
            GovernedCapabilityCandidate,
        ):
            raise TypeError(
                "candidate must be "
                "GovernedCapabilityCandidate or None."
            )

        interface = _required_text(
            interface_contract,
            "interface_contract",
        )

        requirements = _text_tuple(
            integration_requirements,
            "integration_requirements",
        )

        normalized_adapter_kind = _optional_text(
            adapter_kind,
            "adapter_kind",
        )

        normalized_resource_contract = _optional_text(
            resource_contract,
            "resource_contract",
        )

        if (
            normalized_adapter_kind is None
        ) != (
            normalized_resource_contract is None
        ):
            raise (
                GovernedIntegrationAdapterCandidateInvariantError(
                    "Adapter proposal requires both "
                    "adapter_kind and resource_contract."
                )
            )

        integration_payload = {
            "kind": "INTEGRATION",
            "capability_candidate_id": (
                candidate.candidate_id
            ),
            "landscape_change_id": (
                candidate.landscape_change_id
            ),
            "current_snapshot_id": (
                candidate.current_snapshot_id
            ),
            "scope_id": candidate.scope_id,
            "subject_id": candidate.subject_id,
            "capability_term": (
                candidate.capability_term
            ),
            "evidence_id": candidate.evidence_id,
            "interface_contract": interface,
            "integration_requirements": (
                requirements
            ),
        }

        integration_id = _proposal_id(
            "GIC",
            integration_payload,
        )

        integration = GovernedIntegrationCandidate(
            proposal_id=integration_id,
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
            evidence_id=candidate.evidence_id,
            source_ref=candidate.source_ref,
            landscape_evidence_ids=(
                candidate.landscape_evidence_ids
            ),
            interface_contract=interface,
            integration_requirements=(
                requirements
            ),
            verification_status=(
                candidate.verification_status
            ),
        )

        if normalized_adapter_kind is None:
            return IntegrationAdapterCandidateSet(
                integration_candidates=(
                    integration,
                ),
            )

        adapter_payload = {
            "kind": "ADAPTER",
            "integration_proposal_id": (
                integration_id
            ),
            "capability_candidate_id": (
                candidate.candidate_id
            ),
            "interface_contract": interface,
            "adapter_kind": (
                normalized_adapter_kind
            ),
            "resource_contract": (
                normalized_resource_contract
            ),
        }

        adapter = GovernedAdapterCandidate(
            proposal_id=_proposal_id(
                "GAC",
                adapter_payload,
            ),
            integration_proposal_id=(
                integration_id
            ),
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
            evidence_id=candidate.evidence_id,
            source_ref=candidate.source_ref,
            landscape_evidence_ids=(
                candidate.landscape_evidence_ids
            ),
            interface_contract=interface,
            adapter_kind=(
                normalized_adapter_kind
            ),
            resource_contract=(
                normalized_resource_contract
            ),
            verification_status=(
                candidate.verification_status
            ),
        )

        return IntegrationAdapterCandidateSet(
            integration_candidates=(
                integration,
            ),
            adapter_candidates=(
                adapter,
            ),
        )


__all__ = [
    "GOVERNED_INTEGRATION_ADAPTER_CANDIDATE_VERSION",
    "GovernedIntegrationAdapterCandidateInvariantError",
    "GovernedIntegrationCandidate",
    "GovernedAdapterCandidate",
    "IntegrationAdapterCandidateSet",
    "GovernedIntegrationAdapterCandidateProposer",
]
