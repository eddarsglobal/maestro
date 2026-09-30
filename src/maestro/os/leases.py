from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class LeaseState(StrEnum):
    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"
    EXPIRED = "EXPIRED"


@dataclass(slots=True)
class LeaseRecord:
    work_id: str
    worker_id: str
    lease_seconds: int
    lease_id: str = field(default_factory=lambda: f"LSE-{uuid4().hex[:12].upper()}")
    state: LeaseState = LeaseState.ACTIVE
    acquired_at: datetime = field(default_factory=utc_now)
    heartbeat_at: datetime = field(default_factory=utc_now)

    @property
    def expires_at(self) -> datetime:
        return self.heartbeat_at + timedelta(seconds=self.lease_seconds)

    def expired(self, now: datetime | None = None) -> bool:
        now = now or utc_now()
        return self.state is LeaseState.ACTIVE and now >= self.expires_at


class LeaseManager:
    def __init__(self):
        self._leases: dict[str, LeaseRecord] = {}

    def acquire(self, work_id: str, worker_id: str, *, lease_seconds: int = 30) -> LeaseRecord:
        existing = self._leases.get(work_id)
        if existing and existing.state is LeaseState.ACTIVE and not existing.expired():
            raise RuntimeError("Work item already has an active lease.")

        lease = LeaseRecord(work_id=work_id, worker_id=worker_id, lease_seconds=lease_seconds)
        self._leases[work_id] = lease
        return lease

    def heartbeat(self, work_id: str, worker_id: str) -> LeaseRecord:
        lease = self._leases[work_id]
        if lease.worker_id != worker_id:
            raise PermissionError("Heartbeat worker does not own lease.")
        if lease.state is not LeaseState.ACTIVE:
            raise RuntimeError("Lease is not active.")
        if lease.expired():
            lease.state = LeaseState.EXPIRED
            raise RuntimeError("Lease already expired.")
        lease.heartbeat_at = utc_now()
        return lease

    def release(self, work_id: str, worker_id: str) -> None:
        lease = self._leases[work_id]
        if lease.worker_id != worker_id:
            raise PermissionError("Worker does not own lease.")
        lease.state = LeaseState.RELEASED

    def expire_stale(self, now: datetime | None = None) -> list[LeaseRecord]:
        expired = []
        for lease in self._leases.values():
            if lease.expired(now):
                lease.state = LeaseState.EXPIRED
                expired.append(lease)
        return expired

    def get(self, work_id: str) -> LeaseRecord | None:
        return self._leases.get(work_id)
