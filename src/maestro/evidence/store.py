from __future__ import annotations

from dataclasses import dataclass, field

from maestro.models import Evidence


@dataclass
class EvidenceStore:
    _items: dict[str, Evidence] = field(default_factory=dict)

    def add(self, evidence: Evidence) -> str:
        if evidence.evidence_id in self._items:
            raise ValueError(f"Duplicate evidence id: {evidence.evidence_id}")
        self._items[evidence.evidence_id] = evidence
        return evidence.evidence_id

    def get(self, evidence_id: str) -> Evidence:
        return self._items[evidence_id]

    def for_task(self, task_id: str) -> list[Evidence]:
        return [x for x in self._items.values() if x.task_id == task_id]
