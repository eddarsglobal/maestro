from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from maestro.models import Mission
from maestro.runtime.kernel import MaestroKernel


@dataclass(slots=True)
class CheckpointPolicy:
    every_events: int = 10
    on_states: frozenset[str] = frozenset({
        "PAUSED_FOR_AUDIT",
        "FAULT_RETURNED",
        "HUMAN_INPUT_REQUIRED",
        "STATE_COMMIT_PENDING",
    })


class AutomaticCheckpointManager:
    def __init__(self, kernel: MaestroKernel, directory: str | Path, policy: CheckpointPolicy | None = None):
        self.kernel = kernel
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.policy = policy or CheckpointPolicy()
        self._last_event_count: dict[str, int] = {}

    def should_checkpoint(self, mission: Mission, event_count: int) -> bool:
        if mission.state.value in self.policy.on_states:
            return True
        last = self._last_event_count.get(mission.task_id, 0)
        return event_count - last >= self.policy.every_events

    def maybe_checkpoint(self, mission: Mission, event_count: int) -> Path | None:
        if not self.should_checkpoint(mission, event_count):
            return None
        path = self.kernel.save_checkpoint(mission, self.directory)
        self._last_event_count[mission.task_id] = event_count
        return path
