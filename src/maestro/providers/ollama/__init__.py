from .client import OllamaClient, OllamaHTTPError
from .models import (
    OllamaModelInfo,
    OllamaGenerationResult,
    OllamaEmbeddingResult,
    OllamaHealth,
    ModelBenchmarkSample,
)
from .provider import OllamaProviderAdapter
from .embeddings import OllamaEmbeddingAdapter
from .discovery import OllamaDiscovery
from .health import OllamaHealthInspector
from .metrics import OllamaMetricsRecorder
from .policy import LocalModelPolicy, TaskClass

__all__ = [
    "OllamaClient", "OllamaHTTPError",
    "OllamaModelInfo", "OllamaGenerationResult", "OllamaEmbeddingResult",
    "OllamaHealth", "ModelBenchmarkSample",
    "OllamaProviderAdapter", "OllamaEmbeddingAdapter",
    "OllamaDiscovery", "OllamaHealthInspector", "OllamaMetricsRecorder",
    "LocalModelPolicy", "TaskClass",
]

from .sovereign_adapter import OllamaSovereignResourceAdapter, descriptor_from_ollama
