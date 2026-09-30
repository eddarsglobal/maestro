from __future__ import annotations

import json
import os
from pathlib import Path

from .models import ActivationSnapshot


class ActivationLedger:
    """Append-only activation lifecycle ledger with latest-state projection."""

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path is not None else None
        self._events: list[ActivationSnapshot] = []

        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.load()

    @staticmethod
    def _clone(snapshot: ActivationSnapshot) -> ActivationSnapshot:
        return ActivationSnapshot.from_dict(snapshot.to_dict())

    def checkpoint(self, snapshot: ActivationSnapshot) -> ActivationSnapshot:
        row = self._clone(snapshot)
        self._events.append(row)

        if self.path is not None:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row.to_dict(), sort_keys=True) + "\n")
                f.flush()
                os.fsync(f.fileno())

        return self._clone(row)

    record = checkpoint

    def load(self) -> None:
        self._events = []

        if self.path is None or not self.path.exists():
            return

        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                self._events.append(
                    ActivationSnapshot.from_dict(json.loads(line))
                )

    def events(self) -> list[ActivationSnapshot]:
        return [self._clone(row) for row in self._events]

    def all(self) -> list[ActivationSnapshot]:
        latest: dict[str, ActivationSnapshot] = {}

        for row in self._events:
            latest[row.contract_id] = row

        return [
            self._clone(latest[key])
            for key in sorted(latest)
        ]

    def latest(self, contract_id: str) -> ActivationSnapshot | None:
        for row in reversed(self._events):
            if row.contract_id == contract_id:
                return self._clone(row)
        return None

    def by_candidate(
        self,
        candidate_id: str,
    ) -> list[ActivationSnapshot]:
        candidate_id = str(candidate_id)

        return [
            row
            for row in self.all()
            if row.candidate_id == candidate_id
        ]

    def history(self, contract_id: str) -> list[ActivationSnapshot]:
        return [
            self._clone(row)
            for row in self._events
            if row.contract_id == contract_id
        ]
