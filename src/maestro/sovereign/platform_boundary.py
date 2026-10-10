from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from maestro.sovereign.generic_adapters import (
    AdapterBinding,
    DynamicAdapterRegistry,
    GenericAdapterDescriptor,
    GenericResourceAdapter,
)
from maestro.sovereign.generic_descriptors import (
    GenericResourceDescriptor,
)
from maestro.sovereign.generic_discovery import (
    GenericDiscoveryProjection,
)


PLATFORM_ABSTRACTION_BOUNDARY_VERSION = 1


class PlatformBoundaryInvariantError(ValueError):
    pass


def _required_text(value: str, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string.")

    normalized = value.strip()

    if not normalized:
        raise ValueError(f"{name} must not be empty.")

    return normalized


def _immutable_mapping(
    value: Mapping[str, Any],
    name: str,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping.")

    normalized: dict[str, Any] = {}

    for key, item in value.items():
        normalized[
            _required_text(key, f"{name} key")
        ] = item

    return MappingProxyType(normalized)


def _assert_passive_flags(
    *,
    selection_only: bool,
    trust_asserted: bool,
    installation_authorized: bool,
    activation_authorized: bool,
    execution_authorized: bool,
    network_authorized: bool,
    system_truth_asserted: bool,
) -> None:
    violations = {
        "selection_only": selection_only is not True,
        "trust_asserted": trust_asserted is not False,
        "installation_authorized": (
            installation_authorized is not False
        ),
        "activation_authorized": (
            activation_authorized is not False
        ),
        "execution_authorized": (
            execution_authorized is not False
        ),
        "network_authorized": (
            network_authorized is not False
        ),
        "system_truth_asserted": (
            system_truth_asserted is not False
        ),
    }

    bad = sorted(
        name
        for name, violated in violations.items()
        if violated
    )

    if bad:
        raise PlatformBoundaryInvariantError(
            "Platform boundary cannot assert downstream "
            "authority: " + ", ".join(bad)
        )


@dataclass(frozen=True, slots=True)
class PlatformIdentity:
    """Opaque adapter-edge identity, never a core technology identity."""

    platform_id: str
    platform_kind: str = "UNKNOWN"
    attributes: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "platform_id",
            _required_text(
                self.platform_id,
                "platform_id",
            ),
        )

        object.__setattr__(
            self,
            "platform_kind",
            _required_text(
                self.platform_kind,
                "platform_kind",
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
            "platform_id": self.platform_id,
            "platform_kind": self.platform_kind,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True, slots=True)
class PlatformDiscoveryBoundaryResult:
    """A platform discovery edge after generic projection."""

    platform: PlatformIdentity
    projection: GenericDiscoveryProjection
    selection_only: bool = True
    trust_asserted: bool = False
    installation_authorized: bool = False
    activation_authorized: bool = False
    execution_authorized: bool = False
    network_authorized: bool = False
    system_truth_asserted: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.platform, PlatformIdentity):
            raise TypeError(
                "platform must be PlatformIdentity."
            )

        if not isinstance(
            self.projection,
            GenericDiscoveryProjection,
        ):
            raise TypeError(
                "projection must be "
                "GenericDiscoveryProjection."
            )

        _assert_passive_flags(
            selection_only=self.selection_only,
            trust_asserted=self.trust_asserted,
            installation_authorized=(
                self.installation_authorized
            ),
            activation_authorized=(
                self.activation_authorized
            ),
            execution_authorized=(
                self.execution_authorized
            ),
            network_authorized=(
                self.network_authorized
            ),
            system_truth_asserted=(
                self.system_truth_asserted
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": PLATFORM_ABSTRACTION_BOUNDARY_VERSION,
            "platform": self.platform.to_dict(),
            "projection": self.projection.to_dict(),
            "selection_only": True,
            "trust_asserted": False,
            "installation_authorized": False,
            "activation_authorized": False,
            "execution_authorized": False,
            "network_authorized": False,
            "system_truth_asserted": False,
        }


@dataclass(frozen=True, slots=True)
class PlatformAdapterBoundaryResult:
    """A platform adapter validated only through GAR generic binding."""

    platform: PlatformIdentity
    binding: AdapterBinding
    selection_only: bool = True
    trust_asserted: bool = False
    installation_authorized: bool = False
    activation_authorized: bool = False
    execution_authorized: bool = False
    network_authorized: bool = False
    system_truth_asserted: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.platform, PlatformIdentity):
            raise TypeError(
                "platform must be PlatformIdentity."
            )

        if not isinstance(self.binding, AdapterBinding):
            raise TypeError(
                "binding must be AdapterBinding."
            )

        _assert_passive_flags(
            selection_only=self.selection_only,
            trust_asserted=self.trust_asserted,
            installation_authorized=(
                self.installation_authorized
            ),
            activation_authorized=(
                self.activation_authorized
            ),
            execution_authorized=(
                self.execution_authorized
            ),
            network_authorized=(
                self.network_authorized
            ),
            system_truth_asserted=(
                self.system_truth_asserted
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": PLATFORM_ABSTRACTION_BOUNDARY_VERSION,
            "platform": self.platform.to_dict(),
            "binding": self.binding.to_dict(),
            "selection_only": True,
            "trust_asserted": False,
            "installation_authorized": False,
            "activation_authorized": False,
            "execution_authorized": False,
            "network_authorized": False,
            "system_truth_asserted": False,
        }


@dataclass(frozen=True, slots=True)
class PlatformExecutionHandoff:
    """Execution intent metadata only. Never execution authorization."""

    platform_id: str
    platform_kind: str
    resource_id: str
    adapter_id: str
    adapter_kind: str
    capability_id: str
    handoff_only: bool = True
    execution_authorized: bool = False
    activation_authorized: bool = False
    network_authorized: bool = False
    system_truth_asserted: bool = False

    def __post_init__(self) -> None:
        for name in (
            "platform_id",
            "platform_kind",
            "resource_id",
            "adapter_id",
            "adapter_kind",
            "capability_id",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(self, name),
                    name,
                ),
            )

        if self.handoff_only is not True:
            raise PlatformBoundaryInvariantError(
                "Execution handoff must remain handoff-only."
            )

        if (
            self.execution_authorized
            or self.activation_authorized
            or self.network_authorized
            or self.system_truth_asserted
        ):
            raise PlatformBoundaryInvariantError(
                "Execution handoff cannot authorize execution, "
                "activation, network use, or system truth."
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": PLATFORM_ABSTRACTION_BOUNDARY_VERSION,
            "platform_id": self.platform_id,
            "platform_kind": self.platform_kind,
            "resource_id": self.resource_id,
            "adapter_id": self.adapter_id,
            "adapter_kind": self.adapter_kind,
            "capability_id": self.capability_id,
            "handoff_only": True,
            "execution_authorized": False,
            "activation_authorized": False,
            "network_authorized": False,
            "system_truth_asserted": False,
        }


class GovernedPlatformBoundary:
    """
    BMF-015 boundary for platform-specific discovery and execution edges.

    Platform discovery may cross into MAESTRO only after it has become a
    GenericDiscoveryProjection.

    Platform execution adapters may cross only after validation through
    GenericResourceDescriptor, GenericAdapterDescriptor and GAR binding.

    Execution handoff contains identity and capability metadata only.
    No adapter method is invoked here.
    """

    @staticmethod
    def accept_discovery(
        platform: PlatformIdentity,
        projection: GenericDiscoveryProjection,
    ) -> PlatformDiscoveryBoundaryResult:
        if not isinstance(platform, PlatformIdentity):
            raise TypeError(
                "platform must be PlatformIdentity."
            )

        if not isinstance(
            projection,
            GenericDiscoveryProjection,
        ):
            raise TypeError(
                "Platform discovery must cross the boundary "
                "as GenericDiscoveryProjection."
            )

        return PlatformDiscoveryBoundaryResult(
            platform=platform,
            projection=projection,
        )

    @staticmethod
    def validate_adapter(
        platform: PlatformIdentity,
        resource: GenericResourceDescriptor,
        descriptor: GenericAdapterDescriptor,
        adapter: GenericResourceAdapter,
    ) -> PlatformAdapterBoundaryResult:
        if not isinstance(platform, PlatformIdentity):
            raise TypeError(
                "platform must be PlatformIdentity."
            )

        if not isinstance(resource, GenericResourceDescriptor):
            raise TypeError(
                "resource must be GenericResourceDescriptor."
            )

        if not isinstance(descriptor, GenericAdapterDescriptor):
            raise TypeError(
                "descriptor must be GenericAdapterDescriptor."
            )

        registry = DynamicAdapterRegistry()
        binding = registry.register(
            resource,
            descriptor,
            adapter,
        )

        return PlatformAdapterBoundaryResult(
            platform=platform,
            binding=binding,
        )

    @staticmethod
    def build_execution_handoff(
        platform: PlatformIdentity,
        binding: AdapterBinding,
        capability_id: str,
    ) -> PlatformExecutionHandoff:
        if not isinstance(platform, PlatformIdentity):
            raise TypeError(
                "platform must be PlatformIdentity."
            )

        if not isinstance(binding, AdapterBinding):
            raise TypeError(
                "binding must be AdapterBinding."
            )

        normalized_capability = _required_text(
            capability_id,
            "capability_id",
        )

        if normalized_capability not in binding.resource.capability_ids:
            raise PlatformBoundaryInvariantError(
                "Requested capability is absent from generic resource."
            )

        if normalized_capability not in binding.descriptor.capability_ids:
            raise PlatformBoundaryInvariantError(
                "Requested capability is absent from generic adapter."
            )

        return PlatformExecutionHandoff(
            platform_id=platform.platform_id,
            platform_kind=platform.platform_kind,
            resource_id=binding.resource.resource_id,
            adapter_id=binding.descriptor.adapter_id,
            adapter_kind=binding.descriptor.adapter_kind,
            capability_id=normalized_capability,
        )


__all__ = [
    "PLATFORM_ABSTRACTION_BOUNDARY_VERSION",
    "PlatformBoundaryInvariantError",
    "PlatformIdentity",
    "PlatformDiscoveryBoundaryResult",
    "PlatformAdapterBoundaryResult",
    "PlatformExecutionHandoff",
    "GovernedPlatformBoundary",
]
