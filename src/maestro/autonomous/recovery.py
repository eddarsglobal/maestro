from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from maestro.runtime.checkpoint import CheckpointStore
from maestro.orchestration.dag import DagEngine
from maestro.orchestration.retry_ledger import RetryLedger
from maestro.models import Mission

from .event_store import EventStore, RuntimeEvent
from .mission_store import MissionStore


@dataclass(slots=True)
class RecoveryResult:
    mission: Mission
    recovered_from_checkpoint: bool
    event_count: int


class RecoveryManager:
    """
    Recover latest mission state after process crash.
    """

    def __init__(self, mission_store: MissionStore, event_store: EventStore):
        self.mission_store = mission_store
        self.event_store = event_store

    def recover(self, task_id: str, checkpoint_dir: str | Path | None = None) -> RecoveryResult:
        if checkpoint_dir is not None:
            try:
                bundle = CheckpointStore(checkpoint_dir).load(task_id)
                return RecoveryResult(
                    mission=bundle.mission,
                    recovered_from_checkpoint=True,
                    event_count=len(self.event_store.for_task(task_id)),
                )
            except Exception:
                pass

        mission = self.mission_store.load(task_id)
        return RecoveryResult(
            mission=mission,
            recovered_from_checkpoint=False,
            event_count=len(self.event_store.for_task(task_id)),
        )
