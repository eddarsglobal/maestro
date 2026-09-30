from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class TraceEvent:
    task_id: str
    event: str
    actor: str
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)


@dataclass
class Tracer:
    events: list[TraceEvent] = field(default_factory=list)

    def emit(self, task_id: str, event: str, actor: str, **payload: Any) -> None:
        self.events.append(TraceEvent(task_id, event, actor, payload))

    def export(self) -> list[dict[str, Any]]:
        return [asdict(x) for x in self.events]
