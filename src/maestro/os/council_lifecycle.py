from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class CouncilTemperature(StrEnum):
    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"
    ABSENT = "ABSENT"


@dataclass(slots=True)
class CouncilResidency:
    council_id: str
    temperature: CouncilTemperature = CouncilTemperature.COLD
    active_workers: int = 0
    last_used_at: str | None = None
    cached: bool = False


class CouncilLifecycleManager:
    """
    Keeps MAESTRO light by making Council residency explicit.
    """

    def __init__(self):
        self._state: dict[str, CouncilResidency] = {}

    def ensure(self, council_id: str) -> CouncilResidency:
        return self._state.setdefault(council_id, CouncilResidency(council_id))

    def activate(self, council_id: str) -> CouncilResidency:
        r = self.ensure(council_id)
        r.temperature = CouncilTemperature.HOT
        r.active_workers += 1
        r.last_used_at = utc_now()
        r.cached = True
        return r

    def release_worker(self, council_id: str) -> CouncilResidency:
        r = self.ensure(council_id)
        r.active_workers = max(0, r.active_workers - 1)
        r.last_used_at = utc_now()
        if r.active_workers == 0:
            r.temperature = CouncilTemperature.WARM
        return r

    def cool(self, council_id: str) -> CouncilResidency:
        r = self.ensure(council_id)
        if r.active_workers:
            raise RuntimeError("Cannot cool Council with active workers.")
        r.temperature = CouncilTemperature.COLD
        r.cached = False
        return r

    def mark_absent(self, council_id: str) -> CouncilResidency:
        r = self.ensure(council_id)
        if r.active_workers:
            raise RuntimeError("Cannot mark active Council absent.")
        r.temperature = CouncilTemperature.ABSENT
        r.cached = False
        return r

    def hot_count(self) -> int:
        return sum(1 for r in self._state.values() if r.temperature is CouncilTemperature.HOT)

    def warm_count(self) -> int:
        return sum(1 for r in self._state.values() if r.temperature is CouncilTemperature.WARM)

    def snapshot(self) -> dict[str, dict]:
        return {
            cid: {
                "temperature": r.temperature.value,
                "active_workers": r.active_workers,
                "last_used_at": r.last_used_at,
                "cached": r.cached,
            }
            for cid, r in self._state.items()
        }
