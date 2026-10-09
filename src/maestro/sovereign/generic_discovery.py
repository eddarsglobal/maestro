from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from .generic_descriptors import (
    CapabilityDescriptor,
    GenericResourceDescriptor,
    HostDescriptor,
)


def _freeze_mapping(
    value: Mapping[str, Any],
    name: str,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping.")

    return MappingProxyType(dict(value))


@dataclass(frozen=True, slots=True)
class CapabilityObservation:
    """Passive raw observation of one host capability."""

    capability_id: str
    domain: str = "generic"
    version: str | None = None
    description: str = ""
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        descriptor = CapabilityDescriptor(
            capability_id=self.capability_id,
            domain=self.domain,
            version=self.version,
            description=self.description,
            attributes=self.attributes,
        )

        object.__setattr__(
            self,
            "capability_id",
            descriptor.capability_id,
        )
        object.__setattr__(
            self,
            "domain",
            descriptor.domain,
        )
        object.__setattr__(
            self,
            "version",
            descriptor.version,
        )
        object.__setattr__(
            self,
            "description",
            descriptor.description,
        )
        object.__setattr__(
            self,
            "attributes",
            descriptor.attributes,
        )


@dataclass(frozen=True, slots=True)
class ResourceObservation:
    """Passive raw observation of one host resource."""

    resource_id: str
    resource_kind: str = "UNKNOWN"
    capability_ids: frozenset[str] = frozenset()
    status: str = "OBSERVED"
    locality: str = "UNKNOWN"
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        descriptor = GenericResourceDescriptor(
            resource_id=self.resource_id,
            resource_kind=self.resource_kind,
            host_id=None,
            capability_ids=self.capability_ids,
            status=self.status,
            locality=self.locality,
            attributes=self.attributes,
        )

        object.__setattr__(
            self,
            "resource_id",
            descriptor.resource_id,
        )
        object.__setattr__(
            self,
            "resource_kind",
            descriptor.resource_kind,
        )
        object.__setattr__(
            self,
            "capability_ids",
            descriptor.capability_ids,
        )
        object.__setattr__(
            self,
            "status",
            descriptor.status,
        )
        object.__setattr__(
            self,
            "locality",
            descriptor.locality,
        )
        object.__setattr__(
            self,
            "attributes",
            descriptor.attributes,
        )


@dataclass(frozen=True, slots=True)
class HostDiscoveryObservation:
    """
    Provider-neutral observation supplied by a host probe.

    This object performs no probing and owns no network authority.
    """

    host_id: str
    host_kind: str = "UNKNOWN"
    locality: str = "UNKNOWN"
    capabilities: tuple[CapabilityObservation, ...] = ()
    resources: tuple[ResourceObservation, ...] = ()
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.capabilities, tuple):
            raise TypeError("capabilities must be a tuple.")

        if not isinstance(self.resources, tuple):
            raise TypeError("resources must be a tuple.")

        for capability in self.capabilities:
            if not isinstance(
                capability,
                CapabilityObservation,
            ):
                raise TypeError(
                    "capabilities must contain "
                    "CapabilityObservation objects."
                )

        for resource in self.resources:
            if not isinstance(
                resource,
                ResourceObservation,
            ):
                raise TypeError(
                    "resources must contain "
                    "ResourceObservation objects."
                )

        normalized = HostDescriptor(
            host_id=self.host_id,
            host_kind=self.host_kind,
            locality=self.locality,
            capability_ids=frozenset(
                item.capability_id
                for item in self.capabilities
            ),
            attributes=self.attributes,
        )

        object.__setattr__(
            self,
            "host_id",
            normalized.host_id,
        )
        object.__setattr__(
            self,
            "host_kind",
            normalized.host_kind,
        )
        object.__setattr__(
            self,
            "locality",
            normalized.locality,
        )
        object.__setattr__(
            self,
            "attributes",
            _freeze_mapping(
                normalized.attributes,
                "attributes",
            ),
        )


@dataclass(frozen=True, slots=True)
class GenericDiscoveryProjection:
    """Passive descriptor projection produced from one host observation."""

    host: HostDescriptor
    capabilities: tuple[CapabilityDescriptor, ...]
    resources: tuple[GenericResourceDescriptor, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "host": self.host.to_dict(),
            "capabilities": [
                item.to_dict()
                for item in self.capabilities
            ],
            "resources": [
                item.to_dict()
                for item in self.resources
            ],
        }


class GenericHostDiscoveryProjector:
    """
    Converts passive host observations into generic descriptors.

    Projection is deterministic and performs no probing, routing,
    network access, installation, activation, or execution.
    """

    @staticmethod
    def project(
        observation: HostDiscoveryObservation,
    ) -> GenericDiscoveryProjection:
        if not isinstance(
            observation,
            HostDiscoveryObservation,
        ):
            raise TypeError(
                "observation must be a "
                "HostDiscoveryObservation."
            )

        capability_rows = {}

        for item in observation.capabilities:
            if item.capability_id in capability_rows:
                raise ValueError(
                    "Duplicate capability observation: "
                    f"{item.capability_id}"
                )

            capability_rows[item.capability_id] = item

        resource_rows = {}

        for item in observation.resources:
            if item.resource_id in resource_rows:
                raise ValueError(
                    "Duplicate resource observation: "
                    f"{item.resource_id}"
                )

            unknown = (
                item.capability_ids
                - capability_rows.keys()
            )

            if unknown:
                raise ValueError(
                    "Resource references undeclared "
                    "capabilities: "
                    + ", ".join(sorted(unknown))
                )

            resource_rows[item.resource_id] = item

        capabilities = tuple(
            CapabilityDescriptor(
                capability_id=item.capability_id,
                domain=item.domain,
                version=item.version,
                description=item.description,
                attributes=item.attributes,
            )
            for item in sorted(
                capability_rows.values(),
                key=lambda row: row.capability_id,
            )
        )

        resources = tuple(
            GenericResourceDescriptor(
                resource_id=item.resource_id,
                resource_kind=item.resource_kind,
                host_id=observation.host_id,
                capability_ids=item.capability_ids,
                status=item.status,
                locality=item.locality,
                attributes=item.attributes,
            )
            for item in sorted(
                resource_rows.values(),
                key=lambda row: row.resource_id,
            )
        )

        host = HostDescriptor(
            host_id=observation.host_id,
            host_kind=observation.host_kind,
            locality=observation.locality,
            capability_ids=frozenset(
                capability_rows
            ),
            attributes=observation.attributes,
        )

        return GenericDiscoveryProjection(
            host=host,
            capabilities=capabilities,
            resources=resources,
        )


__all__ = [
    "CapabilityObservation",
    "ResourceObservation",
    "HostDiscoveryObservation",
    "GenericDiscoveryProjection",
    "GenericHostDiscoveryProjector",
]
