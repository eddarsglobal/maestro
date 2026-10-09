from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


GENERIC_DESCRIPTOR_SCHEMA_VERSION = 1


def _required_text(value: str, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string.")

    normalized = value.strip()

    if not normalized:
        raise ValueError(f"{name} must not be empty.")

    return normalized


def _optional_text(
    value: str | None,
    name: str,
) -> str | None:
    if value is None:
        return None

    return _required_text(value, name)


def _string_set(
    values: frozenset[str],
    name: str,
) -> frozenset[str]:
    if not isinstance(values, frozenset):
        raise TypeError(f"{name} must be a frozenset.")

    normalized = frozenset(
        _required_text(value, name)
        for value in values
    )

    return normalized


def _immutable_mapping(
    value: Mapping[str, Any],
    name: str,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping.")

    return MappingProxyType(dict(value))


@dataclass(frozen=True, slots=True)
class CapabilityDescriptor:
    """
    Passive description of one capability.

    Capability identity is an extensible string rather than a closed
    technology-era enum. This object grants no execution authority.
    """

    capability_id: str
    domain: str = "generic"
    version: str | None = None
    description: str = ""
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "capability_id",
            _required_text(
                self.capability_id,
                "capability_id",
            ),
        )
        object.__setattr__(
            self,
            "domain",
            _required_text(self.domain, "domain"),
        )
        object.__setattr__(
            self,
            "version",
            _optional_text(self.version, "version"),
        )

        if not isinstance(self.description, str):
            raise TypeError("description must be a string.")

        object.__setattr__(
            self,
            "attributes",
            _immutable_mapping(
                self.attributes,
                "attributes",
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": GENERIC_DESCRIPTOR_SCHEMA_VERSION,
            "capability_id": self.capability_id,
            "domain": self.domain,
            "version": self.version,
            "description": self.description,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True, slots=True)
class HostDescriptor:
    """
    Passive description of a discovered or declared host boundary.

    A host is intentionally generic: it need not represent any one
    contemporary machine, runtime, cloud, accelerator or protocol.
    """

    host_id: str
    host_kind: str = "UNKNOWN"
    locality: str = "UNKNOWN"
    capability_ids: frozenset[str] = frozenset()
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "host_id",
            _required_text(self.host_id, "host_id"),
        )
        object.__setattr__(
            self,
            "host_kind",
            _required_text(self.host_kind, "host_kind"),
        )
        object.__setattr__(
            self,
            "locality",
            _required_text(self.locality, "locality"),
        )
        object.__setattr__(
            self,
            "capability_ids",
            _string_set(
                self.capability_ids,
                "capability_ids",
            ),
        )
        object.__setattr__(
            self,
            "attributes",
            _immutable_mapping(
                self.attributes,
                "attributes",
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": GENERIC_DESCRIPTOR_SCHEMA_VERSION,
            "host_id": self.host_id,
            "host_kind": self.host_kind,
            "locality": self.locality,
            "capability_ids": sorted(self.capability_ids),
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True, slots=True)
class GenericResourceDescriptor:
    """
    Passive description of a resource of any technological generation.

    The descriptor deliberately contains no required provider or model
    identity and performs no routing, discovery, installation or execution.
    """

    resource_id: str
    resource_kind: str = "UNKNOWN"
    host_id: str | None = None
    capability_ids: frozenset[str] = frozenset()
    status: str = "UNKNOWN"
    locality: str = "UNKNOWN"
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "resource_id",
            _required_text(
                self.resource_id,
                "resource_id",
            ),
        )
        object.__setattr__(
            self,
            "resource_kind",
            _required_text(
                self.resource_kind,
                "resource_kind",
            ),
        )
        object.__setattr__(
            self,
            "host_id",
            _optional_text(self.host_id, "host_id"),
        )
        object.__setattr__(
            self,
            "capability_ids",
            _string_set(
                self.capability_ids,
                "capability_ids",
            ),
        )
        object.__setattr__(
            self,
            "status",
            _required_text(self.status, "status"),
        )
        object.__setattr__(
            self,
            "locality",
            _required_text(self.locality, "locality"),
        )
        object.__setattr__(
            self,
            "attributes",
            _immutable_mapping(
                self.attributes,
                "attributes",
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": GENERIC_DESCRIPTOR_SCHEMA_VERSION,
            "resource_id": self.resource_id,
            "resource_kind": self.resource_kind,
            "host_id": self.host_id,
            "capability_ids": sorted(self.capability_ids),
            "status": self.status,
            "locality": self.locality,
            "attributes": dict(self.attributes),
        }


__all__ = [
    "GENERIC_DESCRIPTOR_SCHEMA_VERSION",
    "CapabilityDescriptor",
    "HostDescriptor",
    "GenericResourceDescriptor",
]
