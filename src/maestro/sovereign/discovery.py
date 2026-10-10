from __future__ import annotations

from collections.abc import Iterable

from .contracts import (
    IntelligenceResourceAdapter,
    ResourceDescriptor,
)
from .registry import IntelligenceResourceRegistry


class SovereignDiscoveryBridge:
    """
    Provider-neutral compatibility bridge into the sovereign registry.

    Provider-specific discovery, descriptor projection and adapter
    construction belong outside this module. This bridge only accepts
    already constructed generic sovereign descriptor/adapter bindings.

    REGISTER != TRUST != ACTIVATE != EXECUTE.
    """

    def register_bindings(
        self,
        registry: IntelligenceResourceRegistry,
        bindings: Iterable[
            tuple[
                ResourceDescriptor,
                IntelligenceResourceAdapter,
            ]
        ],
    ) -> list[str]:
        if not isinstance(
            registry,
            IntelligenceResourceRegistry,
        ):
            raise TypeError(
                "registry must be IntelligenceResourceRegistry."
            )

        registered: list[str] = []

        for descriptor, adapter in bindings:
            if not isinstance(
                descriptor,
                ResourceDescriptor,
            ):
                raise TypeError(
                    "descriptor must be ResourceDescriptor."
                )

            if not descriptor.capabilities:
                continue

            try:
                registry.register(
                    descriptor,
                    adapter,
                )
            except ValueError:
                continue

            registered.append(
                descriptor.resource_id
            )

        return registered


__all__ = [
    "SovereignDiscoveryBridge",
]
