from __future__ import annotations

import json
from pathlib import Path

from .models import AdaptationCandidate


class AdaptationCandidateLedger:
    "Append-only candidate snapshots with a latest-state logical view."

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else None
        self._rows: list[AdaptationCandidate] = []

    def _append_snapshot(self, candidate: AdaptationCandidate) -> None:
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(candidate.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")

    def record(self, candidate: AdaptationCandidate) -> str:
        if any(row.candidate_id == candidate.candidate_id for row in self._rows):
            return candidate.candidate_id
        self._rows.append(candidate)
        self._append_snapshot(candidate)
        return candidate.candidate_id

    def checkpoint(self, candidate: AdaptationCandidate) -> str:
        for index, row in enumerate(self._rows):
            if row.candidate_id == candidate.candidate_id:
                self._rows[index] = candidate
                self._append_snapshot(candidate)
                return candidate.candidate_id
        return self.record(candidate)

    def all(self) -> list[AdaptationCandidate]:
        return list(self._rows)

    def by_key(self, key: str) -> list[AdaptationCandidate]:
        return [row for row in self._rows if row.key == key]

    def history(self, candidate_id: str | None = None) -> list[AdaptationCandidate]:
        if not self.path or not self.path.exists():
            return []
        rows: list[AdaptationCandidate] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = AdaptationCandidate.from_dict(json.loads(line))
            if candidate_id is None or row.candidate_id == candidate_id:
                rows.append(row)
        return rows

    def load(self) -> None:
        if not self.path or not self.path.exists():
            return
        latest: dict[str, AdaptationCandidate] = {}
        order: list[str] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = AdaptationCandidate.from_dict(json.loads(line))
            if row.candidate_id not in latest:
                order.append(row.candidate_id)
            latest[row.candidate_id] = row
        self._rows = [latest[candidate_id] for candidate_id in order]
