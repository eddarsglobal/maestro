from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class WorkerState(StrEnum):
    IDLE = "IDLE"
    BUSY = "BUSY"
    OFFLINE = "OFFLINE"


@dataclass(slots=True)
class WorkerSpec:
    worker_id: str
    allowed_councils: set[str]
    capabilities: set[str] = field(default_factory=set)
    state: WorkerState = WorkerState.IDLE


class WorkerRegistry:
    def __init__(self):
        self._workers: dict[str, WorkerSpec] = {}

    def register(self, worker: WorkerSpec) -> None:
        if worker.worker_id in self._workers:
            raise ValueError("Duplicate worker.")
        self._workers[worker.worker_id] = worker

    def get(self, worker_id: str) -> WorkerSpec:
        return self._workers[worker_id]

    def available_for(self, council: str) -> list[WorkerSpec]:
        return [
            w for w in self._workers.values()
            if w.state is WorkerState.IDLE and council in w.allowed_councils
        ]
