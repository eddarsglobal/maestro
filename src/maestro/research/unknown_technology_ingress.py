from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from maestro.sovereign.generic_descriptors import (
    CapabilityDescriptor,
    GenericResourceDescriptor,
    HostDescriptor,
)
from maestro.sovereign.generic_discovery import (
    GenericDiscoveryProjection,
)

from .provider_contracts import ResearchCapability


UNKNOWN_TECHNOLOGY_INGRESS_VERSION = 1


class UnknownTechnologyResearchIngressInvariantError(
    ValueError
):
    pass


def _required_text(value: str, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string.")

    normalized = value.strip()

    if not normalized:
        raise ValueError(f"{name} must not be empty.")

    return normalized


def _candidate_id(
    host: HostDescriptor,
    resource: GenericResourceDescriptor,
    capability: CapabilityDescriptor,
) -> str:
    canonical = json.dumps(
        {
            "host": host.to_dict(),
            "resource": resource.to_dict(),
            "capability": capability.to_dict(),
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    digest = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()

    return f"UTR-{digest[:24]}"


def _query(
    resource: GenericResourceDescriptor,
    capability: CapabilityDescriptor,
) -> str:
    return (
        "Research capability "
        f"{capability.capability_id!r} "
        "for generic resource "
        f"{resource.resource_id!r}. "
        "Determine capability semantics, "
        "compatibility constraints, security "
        "risks, integration requirements, and "
        "independent evidence. Do not assume "
        "trust, installation, activation, "
        "authorization, execution, or truth."
    )


@dataclass(frozen=True, slots=True)
class UnknownTechnologyResearchCandidate:
    """
    Passive RX/ADEL ingress candidate for an unknown technology.

    A candidate is NOT a ResearchRequest.
    It grants no network, trust, installation, activation,
    authorization, execution, promotion, or truth authority.
    """

    candidate_id: str
    host: HostDescriptor
    resource: GenericResourceDescriptor
    capability: CapabilityDescriptor
    research_capability: ResearchCapability
    query: str
    path: tuple[str, str] = ("RX", "ADEL")
    research_request_materialized: bool = False
    network_requested: bool = False
    trust_asserted: bool = False
    installation_requested: bool = False
    activation_requested: bool = False
    authorization_asserted: bool = False
    execution_requested: bool = False
    system_truth_asserted: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "candidate_id",
            _required_text(
                self.candidate_id,
                "candidate_id",
            ),
        )

        object.__setattr__(
            self,
            "query",
            _required_text(self.query, "query"),
        )

        if not isinstance(self.host, HostDescriptor):
            raise TypeError(
                "host must be a HostDescriptor."
            )

        if not isinstance(
            self.resource,
            GenericResourceDescriptor,
        ):
            raise TypeError(
                "resource must be a "
                "GenericResourceDescriptor."
            )

        if not isinstance(
            self.capability,
            CapabilityDescriptor,
        ):
            raise TypeError(
                "capability must be a "
                "CapabilityDescriptor."
            )

        if (
            self.research_capability
            is not ResearchCapability.SEARCH
        ):
            raise UnknownTechnologyResearchIngressInvariantError(
                "Unknown-technology ingress must "
                "remain a SEARCH research candidate."
            )

        if self.path != ("RX", "ADEL"):
            raise UnknownTechnologyResearchIngressInvariantError(
                "Unknown-technology ingress path must "
                "remain RX -> ADEL."
            )

        if self.resource.host_id != self.host.host_id:
            raise UnknownTechnologyResearchIngressInvariantError(
                "Resource host_id does not match "
                "HostDescriptor."
            )

        if (
            self.capability.capability_id
            not in self.host.capability_ids
        ):
            raise UnknownTechnologyResearchIngressInvariantError(
                "Capability is absent from host."
            )

        if (
            self.capability.capability_id
            not in self.resource.capability_ids
        ):
            raise UnknownTechnologyResearchIngressInvariantError(
                "Capability is absent from resource."
            )

        forbidden_assertions = {
            "research_request_materialized": (
                self.research_request_materialized
            ),
            "network_requested": self.network_requested,
            "trust_asserted": self.trust_asserted,
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
            "system_truth_asserted": (
                self.system_truth_asserted
            ),
        }

        asserted = sorted(
            name
            for name, value in forbidden_assertions.items()
            if value is not False
        )

        if asserted:
            raise UnknownTechnologyResearchIngressInvariantError(
                "Research ingress candidate cannot "
                "assert downstream authority: "
                + ", ".join(asserted)
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "ingress_version": (
                UNKNOWN_TECHNOLOGY_INGRESS_VERSION
            ),
            "candidate_id": self.candidate_id,
            "path": list(self.path),
            "research_capability": (
                self.research_capability.value
            ),
            "query": self.query,
            "host": self.host.to_dict(),
            "resource": self.resource.to_dict(),
            "capability": self.capability.to_dict(),
            "research_request_materialized": False,
            "network_requested": False,
            "trust_asserted": False,
            "installation_requested": False,
            "activation_requested": False,
            "authorization_asserted": False,
            "execution_requested": False,
            "system_truth_asserted": False,
        }


@dataclass(frozen=True, slots=True)
class UnknownTechnologyResearchIngressResult:
    candidates: tuple[
        UnknownTechnologyResearchCandidate,
        ...,
    ]

    def __post_init__(self) -> None:
        if not isinstance(self.candidates, tuple):
            raise TypeError(
                "candidates must be a tuple."
            )

        for candidate in self.candidates:
            if not isinstance(
                candidate,
                UnknownTechnologyResearchCandidate,
            ):
                raise TypeError(
                    "candidates must contain "
                    "UnknownTechnologyResearchCandidate "
                    "objects."
                )

        ids = [
            candidate.candidate_id
            for candidate in self.candidates
        ]

        if len(ids) != len(set(ids)):
            raise UnknownTechnologyResearchIngressInvariantError(
                "Research ingress requires unique "
                "candidate IDs."
            )

    @property
    def size(self) -> int:
        return len(self.candidates)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ingress_version": (
                UNKNOWN_TECHNOLOGY_INGRESS_VERSION
            ),
            "candidates": [
                candidate.to_dict()
                for candidate in self.candidates
            ],
        }


class GovernedUnknownTechnologyResearchIngress:
    """
    Pure bridge from generic discovery into RX/ADEL candidacy.

    This layer materializes no ResearchRequest and performs no
    network access, routing, execution, installation, activation,
    trust decision, authorization, verification, or truth assertion.
    """

    @classmethod
    def build(
        cls,
        projection: GenericDiscoveryProjection,
    ) -> UnknownTechnologyResearchIngressResult:
        if not isinstance(
            projection,
            GenericDiscoveryProjection,
        ):
            raise TypeError(
                "projection must be a "
                "GenericDiscoveryProjection."
            )

        capability_by_id = {
            capability.capability_id: capability
            for capability in projection.capabilities
        }

        if len(capability_by_id) != len(
            projection.capabilities
        ):
            raise UnknownTechnologyResearchIngressInvariantError(
                "Projection contains duplicate "
                "capability IDs."
            )

        candidates = []

        for resource in sorted(
            projection.resources,
            key=lambda item: item.resource_id,
        ):
            if resource.host_id != projection.host.host_id:
                raise UnknownTechnologyResearchIngressInvariantError(
                    "Resource host_id does not match "
                    "projection host."
                )

            for capability_id in sorted(
                resource.capability_ids
            ):
                capability = capability_by_id.get(
                    capability_id
                )

                if capability is None:
                    raise UnknownTechnologyResearchIngressInvariantError(
                        "Resource references an undeclared "
                        f"capability: {capability_id}"
                    )

                candidates.append(
                    UnknownTechnologyResearchCandidate(
                        candidate_id=_candidate_id(
                            projection.host,
                            resource,
                            capability,
                        ),
                        host=projection.host,
                        resource=resource,
                        capability=capability,
                        research_capability=(
                            ResearchCapability.SEARCH
                        ),
                        query=_query(
                            resource,
                            capability,
                        ),
                    )
                )

        ordered = tuple(
            sorted(
                candidates,
                key=lambda item: (
                    item.capability.capability_id,
                    item.resource.resource_id,
                    item.candidate_id,
                ),
            )
        )

        return UnknownTechnologyResearchIngressResult(
            candidates=ordered
        )


__all__ = [
    "UNKNOWN_TECHNOLOGY_INGRESS_VERSION",
    "UnknownTechnologyResearchIngressInvariantError",
    "UnknownTechnologyResearchCandidate",
    "UnknownTechnologyResearchIngressResult",
    "GovernedUnknownTechnologyResearchIngress",
]
