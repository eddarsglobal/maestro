from __future__ import annotations

from dataclasses import MISSING, dataclass, fields
from typing import Any

from maestro.sovereign.discovery import (
    SovereignDiscoveryBridge,
)
from maestro.sovereign.generic_adapters import (
    GenericAdapterDescriptor,
)
from maestro.sovereign.generic_descriptors import (
    GenericResourceDescriptor,
)
from maestro.sovereign.generic_discovery import (
    CapabilityObservation,
    GenericDiscoveryProjection,
    GenericHostDiscoveryProjector,
    HostDiscoveryObservation,
    ResourceObservation,
)
from maestro.sovereign.platform_boundary import (
    GovernedPlatformBoundary,
    PlatformIdentity,
)
from maestro.sovereign.registry import (
    IntelligenceResourceRegistry,
)

from .discovery import OllamaDiscovery
from .provider import OllamaProviderAdapter
from .sovereign_adapter import (
    OllamaSovereignResourceAdapter,
    descriptor_from_ollama,
)


_PLATFORM_ID = "ollama-local-runtime"
_PLATFORM_KIND = "LOCAL_INTELLIGENCE_RUNTIME"
_HOST_ID = "ollama-local-host"


def _enum_value(value: Any) -> str:
    raw = getattr(value, "value", value)
    return str(raw)



def _construct_observation(
    cls: type,
    values: dict[str, Any],
):
    """Construct an existing GDR dataclass without inventing fields."""

    kwargs: dict[str, Any] = {}
    missing: list[str] = []

    for item in fields(cls):
        if item.name in values:
            kwargs[item.name] = values[item.name]
            continue

        if (
            item.default is MISSING
            and item.default_factory is MISSING
        ):
            missing.append(item.name)

    if missing:
        raise TypeError(
            f"Unsupported required {cls.__name__} "
            f"fields: {sorted(missing)}"
        )

    return cls(**kwargs)


@dataclass(frozen=True, slots=True)
class _OllamaGenericAdapterView:
    """Metadata-only GAR view; contains no execution method."""

    adapter_id: str
    resource_id: str
    capability_ids: frozenset[str]


class OllamaSovereignDiscoveryBridge:
    """
    Ollama compatibility edge admitted through BMF-015 generic contracts.

    Provider discovery occurs at the provider edge.
    Observations are projected through GDR and accepted by PAB.
    Adapter metadata is validated through GAR/PAB.
    Only after every generic validation succeeds may the historical
    sovereign compatibility registry receive executable adapters.

    DISCOVERY != TRUST.
    BINDING != EXECUTION.
    HANDOFF != AUTHORIZATION.
    """

    @staticmethod
    def _platform() -> PlatformIdentity:
        return PlatformIdentity(
            platform_id=_PLATFORM_ID,
            platform_kind=_PLATFORM_KIND,
            attributes={
                "provider_family": "ollama",
                "boundary_role": "provider-edge",
            },
        )

    @staticmethod
    def _generic_projection(
        legacy_descriptors: tuple[Any, ...],
    ) -> GenericDiscoveryProjection:
        capability_ids = sorted({
            _enum_value(capability)
            for descriptor in legacy_descriptors
            for capability in descriptor.capabilities
        })

        capability_observations = tuple(
            _construct_observation(
                CapabilityObservation,
                {
                    "capability_id": capability_id,
                    "capability_kind": "INTELLIGENCE",
                    "description": (
                        "Provider-edge capability observation."
                    ),
                    "attributes": {
                        "boundary": "BMF-015",
                    },
                },
            )
            for capability_id in capability_ids
        )

        resource_observations = []

        for descriptor in legacy_descriptors:
            generic_capabilities = frozenset(
                _enum_value(capability)
                for capability in descriptor.capabilities
            )

            resource_observations.append(
                _construct_observation(
                    ResourceObservation,
                    {
                        "resource_id": descriptor.resource_id,
                        "resource_kind": "INTELLIGENCE_RESOURCE",
                        "host_id": _HOST_ID,
                        "capability_ids": generic_capabilities,
                        "status": _enum_value(descriptor.status),
                        "locality": (
                            "LOCAL"
                            if descriptor.local
                            else "REMOTE"
                        ),
                        "attributes": {
                            "edge_platform_id": _PLATFORM_ID,
                            "legacy_provider_id": descriptor.provider_id,
                            "legacy_model_id": descriptor.model_id,
                        },
                    },
                )
            )

        observation = _construct_observation(
            HostDiscoveryObservation,
            {
                "host_id": _HOST_ID,
                "host_kind": "INTELLIGENCE_HOST",
                "locality": "LOCAL",
                "attributes": {
                    "edge_platform_id": _PLATFORM_ID,
                },
                "capabilities": capability_observations,
                "resources": tuple(resource_observations),
            },
        )

        projection = GenericHostDiscoveryProjector.project(
            observation
        )

        if not isinstance(
            projection,
            GenericDiscoveryProjection,
        ):
            raise TypeError(
                "GDR projector returned invalid projection."
            )

        return projection

    @staticmethod
    def _validate_generic_adapter(
        platform: PlatformIdentity,
        resource: GenericResourceDescriptor,
    ) -> None:
        capability_ids = frozenset(
            resource.capability_ids
        )

        adapter_id = (
            f"ollama-adapter::{resource.resource_id}"
        )

        descriptor = GenericAdapterDescriptor(
            adapter_id=adapter_id,
            resource_id=resource.resource_id,
            adapter_kind="INTELLIGENCE_RESOURCE_ADAPTER",
            capability_ids=capability_ids,
            attributes={
                "edge_platform_id": platform.platform_id,
            },
        )

        adapter_view = _OllamaGenericAdapterView(
            adapter_id=adapter_id,
            resource_id=resource.resource_id,
            capability_ids=capability_ids,
        )

        result = GovernedPlatformBoundary.validate_adapter(
            platform,
            resource,
            descriptor,
            adapter_view,
        )

        for capability_id in sorted(capability_ids):
            handoff = (
                GovernedPlatformBoundary
                .build_execution_handoff(
                    platform,
                    result.binding,
                    capability_id,
                )
            )

            if handoff.execution_authorized:
                raise RuntimeError(
                    "PAB handoff unexpectedly authorized execution."
                )

    def import_ollama(
        self,
        registry: IntelligenceResourceRegistry,
        discovery: OllamaDiscovery,
        provider: OllamaProviderAdapter,
    ) -> list[str]:
        models = tuple(discovery.list_models())

        prepared = []

        for model in models:
            descriptor = descriptor_from_ollama(model)

            if not descriptor.capabilities:
                continue

            adapter = OllamaSovereignResourceAdapter(
                model,
                provider,
            )

            prepared.append(
                (
                    descriptor,
                    adapter,
                )
            )

        legacy_descriptors = tuple(
            descriptor
            for descriptor, _ in prepared
        )

        platform = self._platform()

        projection = self._generic_projection(
            legacy_descriptors
        )

        GovernedPlatformBoundary.accept_discovery(
            platform,
            projection,
        )

        resources = {
            resource.resource_id: resource
            for resource in projection.resources
        }

        for descriptor, _ in prepared:
            resource = resources.get(
                descriptor.resource_id
            )

            if resource is None:
                raise RuntimeError(
                    "GDR projection lost provider-edge resource: "
                    f"{descriptor.resource_id}"
                )

            self._validate_generic_adapter(
                platform,
                resource,
            )

        # Compatibility registration is deliberately last.
        # No executable adapter enters the legacy registry until every
        # discovery and adapter metadata boundary has passed.
        return (
            SovereignDiscoveryBridge()
            .register_bindings(
                registry,
                prepared,
            )
        )


__all__ = [
    "OllamaSovereignDiscoveryBridge",
]
