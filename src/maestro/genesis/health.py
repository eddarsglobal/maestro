from __future__ import annotations

from pathlib import Path
from typing import Any

from maestro.genesis.models import HealthReport, HealthStatus


class HealthInspector:
    def inspect(
        self,
        *,
        runtime_dir: str | Path,
        queue_depth: int = 0,
        stale_workers: int = 0,
        failed_work: int = 0,
        active_locks: int = 0,
        prepared_effects: int = 0,
    ) -> HealthReport:
        runtime_dir = Path(runtime_dir)
        runtime_dir.mkdir(parents=True, exist_ok=True)

        components: dict[str, dict[str, Any]] = {
            "runtime_dir": {"ok": runtime_dir.exists(), "path": str(runtime_dir)},
            "queue": {"ok": queue_depth < 10000, "depth": queue_depth},
            "workers": {"ok": stale_workers == 0, "stale": stale_workers},
            "work_failures": {"ok": failed_work < 100, "failed": failed_work},
            "locks": {"ok": True, "active": active_locks},
            "effects": {"ok": prepared_effects < 100, "prepared": prepared_effects},
        }

        hard_fail = not components["runtime_dir"]["ok"]
        degraded = (
            not components["queue"]["ok"]
            or not components["workers"]["ok"]
            or not components["work_failures"]["ok"]
            or not components["effects"]["ok"]
        )

        if hard_fail:
            status = HealthStatus.UNHEALTHY
        elif degraded:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.HEALTHY

        return HealthReport(status=status, components=components)
