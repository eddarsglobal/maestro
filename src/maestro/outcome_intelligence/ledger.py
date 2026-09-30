from __future__ import annotations

import json
from pathlib import Path

from .models import VerifiedOutcome


class OutcomeLedger:
    """Append-only ledger of AY-verified structured outcomes."""

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else None
        self._rows: list[VerifiedOutcome] = []

    def record(self, outcome: VerifiedOutcome) -> str:
        if not outcome.ay_verified:
            raise ValueError("Unverified outcomes cannot enter OutcomeLedger.")
        self._rows.append(outcome)
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(outcome.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
        return outcome.outcome_id

    def all(self) -> list[VerifiedOutcome]:
        return list(self._rows)

    def query(self, *, task_family: str | None = None, resource_id: str | None = None) -> list[VerifiedOutcome]:
        out = []
        for row in self._rows:
            if task_family is not None and row.task_family != task_family:
                continue
            if resource_id is not None and row.resource_id != resource_id:
                continue
            out.append(row)
        return out

    def load(self) -> None:
        if not self.path or not self.path.exists():
            return
        self._rows = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                self._rows.append(VerifiedOutcome.from_dict(json.loads(line)))
