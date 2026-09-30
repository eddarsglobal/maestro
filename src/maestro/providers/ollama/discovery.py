from __future__ import annotations
from .client import OllamaClient
from .models import OllamaModelInfo

class OllamaDiscovery:
    def __init__(self, client: OllamaClient):
        self.client = client

    def list_models(self) -> list[OllamaModelInfo]:
        raw = self.client.tags()
        models = [OllamaModelInfo.from_api(x) for x in raw.get("models", [])]
        return sorted(models, key=lambda m: m.name)

    def by_capability(self, capability: str) -> list[OllamaModelInfo]:
        return [m for m in self.list_models() if capability in m.capabilities]
