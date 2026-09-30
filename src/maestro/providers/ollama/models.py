from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass(slots=True)
class OllamaModelInfo:
    name: str
    size: int
    digest: str
    family: str | None = None
    parameter_size: str | None = None
    quantization_level: str | None = None
    context_length: int | None = None
    embedding_length: int | None = None
    capabilities: tuple[str, ...] = ()

    @classmethod
    def from_api(cls, raw: dict[str, Any]) -> "OllamaModelInfo":
        details = raw.get("details") or {}
        return cls(
            name=raw.get("name") or raw.get("model") or "",
            size=int(raw.get("size") or 0),
            digest=raw.get("digest") or "",
            family=details.get("family"),
            parameter_size=details.get("parameter_size"),
            quantization_level=details.get("quantization_level"),
            context_length=details.get("context_length"),
            embedding_length=details.get("embedding_length"),
            capabilities=tuple(raw.get("capabilities") or ()),
        )

@dataclass(slots=True)
class OllamaGenerationResult:
    model: str
    response: str
    done: bool
    done_reason: str | None
    total_duration_ns: int | None
    load_duration_ns: int | None
    prompt_eval_count: int | None
    eval_count: int | None
    eval_duration_ns: int | None

    @property
    def total_ms(self) -> float | None:
        return None if self.total_duration_ns is None else self.total_duration_ns / 1_000_000

    @property
    def load_ms(self) -> float | None:
        return None if self.load_duration_ns is None else self.load_duration_ns / 1_000_000

    @property
    def tokens_per_second(self) -> float | None:
        if not self.eval_count or not self.eval_duration_ns:
            return None
        seconds = self.eval_duration_ns / 1_000_000_000
        return self.eval_count / seconds if seconds > 0 else None

@dataclass(slots=True)
class OllamaEmbeddingResult:
    model: str
    embeddings: list[list[float]]
    total_duration_ns: int | None = None
    load_duration_ns: int | None = None
    prompt_eval_count: int | None = None

    @property
    def dimensions(self) -> int:
        return len(self.embeddings[0]) if self.embeddings else 0

@dataclass(slots=True)
class OllamaHealth:
    reachable: bool
    model_count: int
    error: str | None = None

@dataclass(slots=True)
class ModelBenchmarkSample:
    model: str
    task_class: str
    success: bool
    latency_ms: float | None
    load_ms: float | None
    tokens_per_second: float | None
    output_length: int
    metadata: dict[str, Any] = field(default_factory=dict)
