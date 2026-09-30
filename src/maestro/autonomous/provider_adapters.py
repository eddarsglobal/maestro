from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class ProviderRequest:
    purpose: str
    model_id: str
    instructions: str
    context: dict[str, Any]


@dataclass(slots=True)
class ProviderResponse:
    provider: str
    model_id: str
    output: str
    metadata: dict[str, Any] = field(default_factory=dict)


class ProviderAdapter(Protocol):
    provider_id: str

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        ...


class ProviderRegistry:
    """
    Model providers remain replaceable runtime resources.
    """

    def __init__(self):
        self._providers: dict[str, ProviderAdapter] = {}

    def register(self, adapter: ProviderAdapter) -> None:
        if adapter.provider_id in self._providers:
            raise ValueError("Duplicate provider adapter.")
        self._providers[adapter.provider_id] = adapter

    def get(self, provider_id: str) -> ProviderAdapter:
        return self._providers[provider_id]

    def generate(self, provider_id: str, request: ProviderRequest) -> ProviderResponse:
        return self.get(provider_id).generate(request)
