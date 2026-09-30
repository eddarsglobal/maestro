from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from heapq import heappush, heappop
from itertools import count
from typing import Any
from uuid import uuid4


class WorkStatus(StrEnum):
    QUEUED = "QUEUED"
    LEASED = "LEASED"
    DONE = "DONE"
    FAILED = "FAILED"


@dataclass(slots=True)
class WorkItem:
    task_id: str
    council: str
    action: str
    payload: dict[str, Any] = field(default_factory=dict)
    priority: int = 100
    work_id: str = field(default_factory=lambda: f"WRK-{uuid4().hex[:12].upper()}")
    status: WorkStatus = WorkStatus.QUEUED
    leased_by: str | None = None


class RuntimeScheduler:
    def __init__(self):
        self._counter = count()
        self._heap: list[tuple[int, int, str]] = []
        self._items: dict[str, WorkItem] = {}

    def enqueue(self, item: WorkItem) -> str:
        if item.work_id in self._items:
            raise ValueError("Duplicate work item.")
        self._items[item.work_id] = item
        heappush(self._heap, (item.priority, next(self._counter), item.work_id))
        return item.work_id

    def lease_next(self, worker_id: str, allowed_councils: set[str]) -> WorkItem | None:
        deferred = []
        chosen = None

        while self._heap:
            priority, seq, work_id = heappop(self._heap)
            item = self._items[work_id]
            if item.status is not WorkStatus.QUEUED:
                continue
            if item.council not in allowed_councils:
                deferred.append((priority, seq, work_id))
                continue
            item.status = WorkStatus.LEASED
            item.leased_by = worker_id
            chosen = item
            break

        for row in deferred:
            heappush(self._heap, row)
        return chosen

    def complete(self, work_id: str) -> None:
        item = self._items[work_id]
        if item.status is not WorkStatus.LEASED:
            raise RuntimeError("Work item must be LEASED before completion.")
        item.status = WorkStatus.DONE

    def fail(self, work_id: str) -> None:
        item = self._items[work_id]
        if item.status is not WorkStatus.LEASED:
            raise RuntimeError("Work item must be LEASED before failure.")
        item.status = WorkStatus.FAILED

    def requeue_failed(self, work_id: str) -> None:
        item = self._items[work_id]
        if item.status is not WorkStatus.FAILED:
            raise RuntimeError("Only FAILED work can be requeued.")
        item.status = WorkStatus.QUEUED
        item.leased_by = None
        heappush(self._heap, (item.priority, next(self._counter), item.work_id))

    def snapshot(self) -> dict[str, Any]:
        return {
            wid: {
                "task_id": x.task_id,
                "council": x.council,
                "action": x.action,
                "payload": x.payload,
                "priority": x.priority,
                "work_id": x.work_id,
                "status": x.status.value,
                "leased_by": x.leased_by,
            }
            for wid, x in self._items.items()
        }
