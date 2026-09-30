from __future__ import annotations
from .client import OllamaClient
from .models import OllamaEmbeddingResult

class OllamaEmbeddingAdapter:
    provider_id = "ollama"

    def __init__(self, client: OllamaClient | None = None):
        self.client = client or OllamaClient()

    def embed(self, model: str, text: str | list[str]) -> OllamaEmbeddingResult:
        raw = self.client.embed(model=model, input_text=text)
        return OllamaEmbeddingResult(
            model=raw.get("model", model),
            embeddings=raw.get("embeddings", []),
            total_duration_ns=raw.get("total_duration"),
            load_duration_ns=raw.get("load_duration"),
            prompt_eval_count=raw.get("prompt_eval_count"),
        )
