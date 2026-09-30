from __future__ import annotations
from dataclasses import dataclass

from maestro.autonomous.provider_adapters import ProviderRegistry, ProviderRequest
from maestro.providers.ollama import (
    OllamaClient, OllamaProviderAdapter, OllamaEmbeddingAdapter,
    OllamaDiscovery, OllamaHealthInspector, LocalModelPolicy, TaskClass,
)

@dataclass(slots=True)
class LocalIntelligence:
    client: OllamaClient
    provider: OllamaProviderAdapter
    embeddings: OllamaEmbeddingAdapter
    discovery: OllamaDiscovery
    health: OllamaHealthInspector
    policy: LocalModelPolicy

    @classmethod
    def ollama(cls, base_url: str = "http://localhost:11434") -> "LocalIntelligence":
        client = OllamaClient(base_url)
        return cls(
            client=client,
            provider=OllamaProviderAdapter(client),
            embeddings=OllamaEmbeddingAdapter(client),
            discovery=OllamaDiscovery(client),
            health=OllamaHealthInspector(client),
            policy=LocalModelPolicy(),
        )

    def generate(self, task_class: TaskClass, prompt: str) -> str:
        models = self.discovery.list_models()
        model = self.policy.select(task_class, models)
        response = self.provider.generate(
            ProviderRequest(task_class.value, model.name, prompt, {})
        )
        return response.output
