from maestro.autonomous.provider_adapters import ProviderRequest
from maestro.providers.ollama import (
    OllamaProviderAdapter, OllamaEmbeddingAdapter,
    LocalModelPolicy, TaskClass, OllamaModelInfo, OllamaMetricsRecorder,
)

class FakeClient:
    def generate(self, **kwargs):
        return {
            "model": kwargs["model"],
            "response": "MAESTRO LOCAL OK",
            "done": True,
            "done_reason": "stop",
            "total_duration": 3_000_000_000,
            "load_duration": 1_000_000_000,
            "prompt_eval_count": 20,
            "eval_count": 100,
            "eval_duration": 2_000_000_000,
            "thinking": "transient-only",
            "context": [1,2,3],
        }
    def embed(self, **kwargs):
        return {
            "model": kwargs["model"],
            "embeddings": [[0.1,0.2,0.3,0.4]],
            "total_duration": 1_000_000_000,
            "load_duration": 500_000_000,
            "prompt_eval_count": 8,
        }

models = [
    OllamaModelInfo("qwen3:0.6b", 522_000_000, "a", capabilities=("completion","tools","thinking")),
    OllamaModelInfo("qwen3:8b", 5_200_000_000, "b", capabilities=("completion","tools","thinking")),
    OllamaModelInfo("qwen3-embedding:0.6b", 639_000_000, "c", capabilities=("embedding","tools","thinking")),
]

policy = LocalModelPolicy()
direct = policy.select(TaskClass.DIRECT, models)
embed_model = policy.select(TaskClass.EMBEDDING, models)

provider = OllamaProviderAdapter(FakeClient())
raw = provider.generate_raw(ProviderRequest("DIRECT", direct.name, "test", {}))
print("DIRECT MODEL:", direct.name)
print("RESPONSE:", raw.response)
print("TPS:", raw.tokens_per_second)

embedding = OllamaEmbeddingAdapter(FakeClient()).embed(embed_model.name, "MAESTRO")
print("EMBED MODEL:", embed_model.name)
print("EMBED DIM:", embedding.dimensions)

metrics = OllamaMetricsRecorder()
metrics.record_generation(task_class="DIRECT", result=raw)
print("METRICS:", metrics.summarize(direct.name, "DIRECT"))
