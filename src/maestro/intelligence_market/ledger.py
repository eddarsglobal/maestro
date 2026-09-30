from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json

from .models import MarketObservation


class IntelligenceMarketLedger:
    """
    Append-only observation ledger.

    Learning from performance does not mutate provider/model authority.
    """

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else None
        self._observations: list[MarketObservation] = []

    def record(self, observation: MarketObservation) -> None:
        self._observations.append(observation)
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(observation), ensure_ascii=False, sort_keys=True) + "\n")

    def all(self) -> list[MarketObservation]:
        return list(self._observations)

    def load(self) -> None:
        if not self.path or not self.path.exists():
            return
        self._observations = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                self._observations.append(MarketObservation(**json.loads(line)))

    def query(
        self,
        *,
        resource_id: str | None = None,
        task_family: str | None = None,
        council_id: str | None = None,
    ) -> list[MarketObservation]:
        out = []
        for o in self._observations:
            if resource_id is not None and o.resource_id != resource_id:
                continue
            if task_family is not None and o.task_family != task_family:
                continue
            if council_id is not None and o.council_id != council_id:
                continue
            out.append(o)
        return out
