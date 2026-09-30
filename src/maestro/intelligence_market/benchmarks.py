from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Any

from maestro.sovereign.contracts import IntelligenceRequest, IntelligenceResponse


@dataclass(slots=True)
class BenchmarkScenario:
    scenario_id: str
    task_family: str
    council_id: str | None
    request: IntelligenceRequest
    evaluator: Callable[[IntelligenceResponse], float]


@dataclass(slots=True)
class BenchmarkResult:
    scenario_id: str
    resource_id: str
    success: bool
    quality: float
    latency_ms: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class MarketBenchmark:
    """
    Runs the same scenario contract across eligible resources for Academy/Market.
    """

    def run(self, scenario: BenchmarkScenario, adapters: dict[str, Any]) -> list[BenchmarkResult]:
        out = []
        for rid, adapter in adapters.items():
            try:
                response = adapter.execute(scenario.request)
                quality = max(0.0, min(1.0, float(scenario.evaluator(response))))
                out.append(BenchmarkResult(
                    scenario.scenario_id,
                    rid,
                    response.success,
                    quality,
                    response.metadata.get("total_ms") if isinstance(response.metadata, dict) else None,
                    dict(response.metadata),
                ))
            except Exception as exc:
                out.append(BenchmarkResult(
                    scenario.scenario_id,
                    rid,
                    False,
                    0.0,
                    None,
                    {"error": str(exc)},
                ))
        return out
