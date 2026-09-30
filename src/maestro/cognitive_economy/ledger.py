from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json

from .models import SpendObservation, EconomyTier


class CognitiveEconomyLedger:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else None
        self.rows: list[SpendObservation] = []

    def record(self, observation: SpendObservation) -> None:
        self.rows.append(observation)
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            d = asdict(observation)
            d["tier"] = observation.tier.value
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(d, ensure_ascii=False, sort_keys=True) + "\n")

    def by_task(self, task_family: str, council_id: str | None = None) -> list[SpendObservation]:
        return [
            x for x in self.rows
            if x.task_family == task_family
            and (council_id is None or x.council_id == council_id)
        ]

    def best_efficiency(self, task_family: str, council_id: str | None = None):
        rows = self.by_task(task_family, council_id)
        if not rows:
            return None

        def utility(x):
            spend = 1.0 + x.total_tokens / 10_000 + x.latency_ms / 60_000 + x.cost_score
            return (x.quality * (1.0 if x.success else 0.25)) / spend

        return max(rows, key=utility)
