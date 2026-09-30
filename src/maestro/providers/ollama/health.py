from __future__ import annotations
from .client import OllamaClient
from .models import OllamaHealth

class OllamaHealthInspector:
    def __init__(self, client: OllamaClient):
        self.client = client

    def inspect(self) -> OllamaHealth:
        try:
            raw = self.client.tags()
            return OllamaHealth(True, len(raw.get("models", [])))
        except Exception as exc:
            return OllamaHealth(False, 0, str(exc))
