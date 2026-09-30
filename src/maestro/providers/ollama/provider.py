from __future__ import annotations
from maestro.autonomous.provider_adapters import ProviderRequest, ProviderResponse
from .client import OllamaClient
from .models import OllamaGenerationResult

class OllamaProviderAdapter:
    provider_id = "ollama"

    def __init__(self, client: OllamaClient | None = None):
        self.client = client or OllamaClient()

    def generate_raw(self, request: ProviderRequest) -> OllamaGenerationResult:
        raw = self.client.generate(
            model=request.model_id,
            prompt=request.instructions,
            system=request.context.get("system") if isinstance(request.context, dict) else None,
            options=request.context.get("options") if isinstance(request.context, dict) else None,
            think=request.context.get("think") if isinstance(request.context, dict) else None,
        )
        return OllamaGenerationResult(
            model=raw.get("model", request.model_id),
            response=raw.get("response", ""),
            done=bool(raw.get("done", False)),
            done_reason=raw.get("done_reason"),
            total_duration_ns=raw.get("total_duration"),
            load_duration_ns=raw.get("load_duration"),
            prompt_eval_count=raw.get("prompt_eval_count"),
            eval_count=raw.get("eval_count"),
            eval_duration_ns=raw.get("eval_duration"),
        )

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        result = self.generate_raw(request)
        return ProviderResponse(
            provider=self.provider_id,
            model_id=result.model,
            output=result.response,
            metadata={
                "done": result.done,
                "done_reason": result.done_reason,
                "total_ms": result.total_ms,
                "load_ms": result.load_ms,
                "prompt_tokens": result.prompt_eval_count,
                "generated_tokens": result.eval_count,
                "tokens_per_second": result.tokens_per_second,
            },
        )
