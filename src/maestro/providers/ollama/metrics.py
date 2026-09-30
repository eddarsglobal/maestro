from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
import json

from .models import ModelBenchmarkSample, OllamaGenerationResult

class OllamaMetricsRecorder:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else None
        self.samples: list[ModelBenchmarkSample] = []

    def record_generation(self, *, task_class: str, result: OllamaGenerationResult, success: bool = True):
        sample = ModelBenchmarkSample(
            model=result.model,
            task_class=task_class,
            success=success,
            latency_ms=result.total_ms,
            load_ms=result.load_ms,
            tokens_per_second=result.tokens_per_second,
            output_length=len(result.response),
        )
        self.samples.append(sample)
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(sample), ensure_ascii=False) + "\n")
        return sample

    def summarize(self, model: str, task_class: str | None = None) -> dict:
        rows = [
            s for s in self.samples
            if s.model == model and (task_class is None or s.task_class == task_class)
        ]
        if not rows:
            return {"samples": 0}
        lat = [s.latency_ms for s in rows if s.latency_ms is not None]
        tps = [s.tokens_per_second for s in rows if s.tokens_per_second is not None]
        return {
            "samples": len(rows),
            "success_rate": sum(1 for s in rows if s.success) / len(rows),
            "mean_latency_ms": (sum(lat) / len(lat)) if lat else None,
            "mean_tokens_per_second": (sum(tps) / len(tps)) if tps else None,
        }
