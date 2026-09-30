from __future__ import annotations

from maestro.providers.ollama.discovery import OllamaDiscovery
from maestro.providers.ollama.provider import OllamaProviderAdapter
from maestro.providers.ollama.sovereign_adapter import (
    OllamaSovereignResourceAdapter,
    descriptor_from_ollama,
)
from .registry import IntelligenceResourceRegistry


class SovereignDiscoveryBridge:
    """
    Imports provider-discovered models into MAESTRO's provider-neutral registry.

    This bridge is intentionally outside sovereign core initialization so that
    provider packages never become a dependency of MAESTRO's identity.
    """

    def import_ollama(
        self,
        registry: IntelligenceResourceRegistry,
        discovery: OllamaDiscovery,
        provider: OllamaProviderAdapter,
    ) -> list[str]:
        registered = []
        for model in discovery.list_models():
            descriptor = descriptor_from_ollama(model)
            if not descriptor.capabilities:
                continue
            adapter = OllamaSovereignResourceAdapter(model, provider)
            try:
                registry.register(descriptor, adapter)
                registered.append(descriptor.resource_id)
            except ValueError:
                pass
        return registered
