from __future__ import annotations

from .contracts import (
    IntelligenceCapability,
    IntelligenceResourceAdapter,
    ResourceDescriptor,
    ResourceStatus,
)


class IntelligenceResourceRegistry:
    """
    Model/provider resources are dynamically registered and replaceable.
    The registry itself owns no constitutional authority.
    """

    def __init__(self):
        self._descriptors: dict[str, ResourceDescriptor] = {}
        self._adapters: dict[str, IntelligenceResourceAdapter] = {}

    def register(self, descriptor: ResourceDescriptor, adapter: IntelligenceResourceAdapter) -> None:
        if descriptor.resource_id in self._descriptors:
            raise ValueError(f"Duplicate intelligence resource: {descriptor.resource_id}")
        if descriptor.resource_id != adapter.resource_id:
            raise ValueError("Descriptor/adapter resource_id mismatch.")
        self._descriptors[descriptor.resource_id] = descriptor
        self._adapters[descriptor.resource_id] = adapter

    def unregister(self, resource_id: str) -> None:
        self._descriptors.pop(resource_id, None)
        self._adapters.pop(resource_id, None)

    def descriptor(self, resource_id: str) -> ResourceDescriptor:
        return self._descriptors[resource_id]

    def adapter(self, resource_id: str) -> IntelligenceResourceAdapter:
        return self._adapters[resource_id]

    def set_status(self, resource_id: str, status: ResourceStatus) -> None:
        self._descriptors[resource_id].status = status

    def eligible(
        self,
        capability: IntelligenceCapability,
        *,
        requires_tools: bool = False,
        forbidden_resources: frozenset[str] = frozenset(),
    ) -> list[ResourceDescriptor]:
        out = []
        for d in self._descriptors.values():
            if d.resource_id in forbidden_resources:
                continue
            if d.status is ResourceStatus.UNAVAILABLE:
                continue
            if capability not in d.capabilities:
                continue
            if requires_tools and IntelligenceCapability.TOOL_USE not in d.capabilities:
                continue
            out.append(d)
        return out

    def all(self) -> list[ResourceDescriptor]:
        return list(self._descriptors.values())
