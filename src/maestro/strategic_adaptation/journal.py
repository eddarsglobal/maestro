from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json


class StrategyTransitionJournal:
    """
    Append-only journal for strategy changes and outcomes.
    """

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else None
        self.rows = []

    def record(self, transition) -> None:
        row = transition.to_dict()
        self.rows.append(row)
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def last_for_task(self, task_id: str):
        for row in reversed(self.rows):
            if row["task_id"] == task_id:
                return row
        return None
