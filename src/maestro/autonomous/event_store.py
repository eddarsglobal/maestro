from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class RuntimeEvent:
    task_id: str
    event_type: str
    actor: str
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EventStore:
    """
    Append-only JSONL event store.

    v0.6 uses JSONL deliberately for inspectability. Heavy payloads should be
    stored by reference in the MAESTRO Binary Object Store.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: RuntimeEvent) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")

    def all(self) -> list[RuntimeEvent]:
        if not self.path.exists():
            return []
        out = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            raw = json.loads(line)
            out.append(RuntimeEvent(**raw))
        return out

    def for_task(self, task_id: str) -> list[RuntimeEvent]:
        return [e for e in self.all() if e.task_id == task_id]
