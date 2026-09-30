from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

from maestro.autonomous.event_store import EventStore, RuntimeEvent


@dataclass(slots=True)
class MissionProjection:
    task_id: str
    event_count: int
    last_event_type: str | None
    last_actor: str | None
    state: str | None
    completed_work: int
    failed_work: int
    metadata: dict[str, Any]


class EventSourcedMissionStore:
    """
    Rebuilds compact runtime projections from the append-only event log.

    Event history is authoritative for runtime history; mission snapshots remain
    acceleration/checkpoint artifacts.
    """

    def __init__(self, event_store: EventStore):
        self.events = event_store

    def project(self, task_id: str) -> MissionProjection:
        events = self.events.for_task(task_id)
        state = None
        completed = 0
        failed = 0
        metadata: dict[str, Any] = {}

        for event in events:
            if event.event_type == "STATE_TRANSITION":
                state = event.payload.get("new_state")
            elif event.event_type == "WORK_SUCCEEDED":
                completed += 1
            elif event.event_type == "WORK_FAILED":
                failed += 1
            elif event.event_type == "MISSION_CREATED":
                metadata["objective"] = event.payload.get("objective")

        last = events[-1] if events else None
        return MissionProjection(
            task_id=task_id,
            event_count=len(events),
            last_event_type=last.event_type if last else None,
            last_actor=last.actor if last else None,
            state=state,
            completed_work=completed,
            failed_work=failed,
            metadata=metadata,
        )

    def replay(self, task_id: str) -> list[RuntimeEvent]:
        return self.events.for_task(task_id)
