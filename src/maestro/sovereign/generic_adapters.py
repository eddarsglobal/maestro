from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from .generic_descriptors import GenericResourceDescriptor


GENERIC_ADAPTER_SCHEMA_VERSION = 1


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

    return frozenset(
        _required_text(item, name)
        for item in values
    )


def _immutable_mapping(
    value: Mapping[str, Any],
    name: str,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping.")

    return MappingProxyType(dict(value))


@dataclass(frozen=True, slots=True)
class GenericAdapterDescriptor:
    """Passive description of one replaceable resource adapter."""

    adapter_id: str
    resource_id: str
    adapter_kind: str = "UNKNOWN"
    capability_ids: frozenset[str] = frozenset()
    version: str | None = None
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "adapter_id",
            _required_text(self.adapter_id, "adapter_id"),
        )
        object.__setattr__(
            self,
            "resource_id",
            _required_text(self.resource_id, "resource_id"),
        )
        object.__setattr__(
            self,
            "adapter_kind",
            _required_text(self.adapter_kind, "adapter_kind"),
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
            "version",
            _optional_text(self.version, "version"),
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
            "schema_version": GENERIC_ADAPTER_SCHEMA_VERSION,
            "adapter_id": self.adapter_id,
            "resource_id": self.resource_id,
            "adapter_kind": self.adapter_kind,
            "capability_ids": sorted(self.capability_ids),
            "version": self.version,
            "attributes": dict(self.attributes),
        }


class GenericResourceAdapter(Protocol):
    """
    Structural registration contract for a future resource adapter.

    Registration metadata deliberately contains no provider/model
    requirement and grants no execution authority.
    """

    adapter_id: str
    resource_id: str
    capability_ids: frozenset[str]


@dataclass(frozen=True, slots=True)
class AdapterBinding:
    """Immutable registry binding; presence does not authorize use."""

    resource: GenericResourceDescriptor
    descriptor: GenericAdapterDescriptor
    adapter: GenericResourceAdapter

    def to_dict(self) -> dict[str, Any]:
        return {
            "resource": self.resource.to_dict(),
            "adapter": self.descriptor.to_dict(),
        }


class DynamicAdapterRegistry:
    """
    Passive registry for replaceable adapters to generic resources.

    REGISTER != TRUST.
    REGISTER != INSTALL.
    REGISTER != ACTIVATE.
    REGISTER != EXECUTE.
    """

    def __init__(self) -> None:
        self._by_resource: dict[str, AdapterBinding] = {}
        self._adapter_to_resource: dict[str, str] = {}

    @staticmethod
    def _validate(
        resource: GenericResourceDescriptor,
        descriptor: GenericAdapterDescriptor,
        adapter: GenericResourceAdapter,
    ) -> AdapterBinding:
        if not isinstance(resource, GenericResourceDescriptor):
            raise TypeError(
                "resource must be a GenericResourceDescriptor."
            )

        if not isinstance(descriptor, GenericAdapterDescriptor):
            raise TypeError(
                "descriptor must be a GenericAdapterDescriptor."
            )

        if descriptor.resource_id != resource.resource_id:
            raise ValueError(
                "Adapter descriptor/resource resource_id mismatch."
            )

        adapter_id = _required_text(
            getattr(adapter, "adapter_id", None),
            "adapter.adapter_id",
        )
        resource_id = _required_text(
            getattr(adapter, "resource_id", None),
            "adapter.resource_id",
        )

        raw_capabilities = getattr(
            adapter,
            "capability_ids",
            None,
        )

        if not isinstance(raw_capabilities, frozenset):
            raise TypeError(
                "adapter.capability_ids must be a frozenset."
            )

        adapter_capabilities = _string_set(
            raw_capabilities,
            "adapter.capability_ids",
        )

        if adapter_id != descriptor.adapter_id:
            raise ValueError(
                "Adapter/descriptor adapter_id mismatch."
            )

        if resource_id != resource.resource_id:
            raise ValueError(
                "Adapter/resource resource_id mismatch."
            )

        if adapter_capabilities != descriptor.capability_ids:
            raise ValueError(
                "Adapter/descriptor capability mismatch."
            )

        if not descriptor.capability_ids.issubset(
            resource.capability_ids
        ):
            raise ValueError(
                "Adapter claims capability absent from resource."
            )

        return AdapterBinding(
            resource=resource,
            descriptor=descriptor,
            adapter=adapter,
        )

    def register(
        self,
        resource: GenericResourceDescriptor,
        descriptor: GenericAdapterDescriptor,
        adapter: GenericResourceAdapter,
    ) -> AdapterBinding:
        binding = self._validate(
            resource,
            descriptor,
            adapter,
        )

        if resource.resource_id in self._by_resource:
            raise ValueError(
                "Resource already has a registered adapter: "
                f"{resource.resource_id}"
            )

        if descriptor.adapter_id in self._adapter_to_resource:
            raise ValueError(
                "Duplicate adapter_id: "
                f"{descriptor.adapter_id}"
            )

        self._by_resource[resource.resource_id] = binding
        self._adapter_to_resource[
            descriptor.adapter_id
        ] = resource.resource_id

        return binding

    def unregister(
        self,
        resource_id: str,
    ) -> AdapterBinding | None:
        normalized = _required_text(
            resource_id,
            "resource_id",
        )

        binding = self._by_resource.pop(
            normalized,
            None,
        )

        if binding is not None:
            self._adapter_to_resource.pop(
                binding.descriptor.adapter_id,
                None,
            )

        return binding

    def replace(
        self,
        resource: GenericResourceDescriptor,
        descriptor: GenericAdapterDescriptor,
        adapter: GenericResourceAdapter,
    ) -> tuple[AdapterBinding, AdapterBinding]:
        replacement = self._validate(
            resource,
            descriptor,
            adapter,
        )

        current = self._by_resource.get(
            resource.resource_id
        )

        if current is None:
            raise KeyError(
                "Cannot replace unregistered resource: "
                f"{resource.resource_id}"
            )

        owner = self._adapter_to_resource.get(
            descriptor.adapter_id
        )

        if (
            owner is not None
            and owner != resource.resource_id
        ):
            raise ValueError(
                "Replacement adapter_id is bound to "
                f"another resource: {descriptor.adapter_id}"
            )

        old_adapter_id = current.descriptor.adapter_id

        self._by_resource[
            resource.resource_id
        ] = replacement

        if old_adapter_id != descriptor.adapter_id:
            self._adapter_to_resource.pop(
                old_adapter_id,
                None,
            )

        self._adapter_to_resource[
            descriptor.adapter_id
        ] = resource.resource_id

        return current, replacement

    def binding(
        self,
        resource_id: str,
    ) -> AdapterBinding:
        return self._by_resource[
            _required_text(resource_id, "resource_id")
        ]

    def descriptor(
        self,
        resource_id: str,
    ) -> GenericAdapterDescriptor:
        return self.binding(resource_id).descriptor

    def resource(
        self,
        resource_id: str,
    ) -> GenericResourceDescriptor:
        return self.binding(resource_id).resource

    def adapter(
        self,
        resource_id: str,
    ) -> GenericResourceAdapter:
        return self.binding(resource_id).adapter

    def all(self) -> tuple[AdapterBinding, ...]:
        return tuple(
            self._by_resource[resource_id]
            for resource_id in sorted(self._by_resource)
        )

    def inventory(self) -> tuple[dict[str, Any], ...]:
        return tuple(
            binding.to_dict()
            for binding in self.all()
        )

    def __len__(self) -> int:
        return len(self._by_resource)


__all__ = [
    "GENERIC_ADAPTER_SCHEMA_VERSION",
    "GenericAdapterDescriptor",
    "GenericResourceAdapter",
    "AdapterBinding",
    "DynamicAdapterRegistry",
]
