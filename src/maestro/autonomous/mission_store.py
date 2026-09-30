from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from maestro.models import Mission
from maestro.runtime.checkpoint import _mission_from_dict


class MissionStore:
    """
    Durable mission state snapshots.

    EventStore records history; MissionStore records latest runtime snapshot.
    """

    def __init__(self, directory: str | Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, task_id: str) -> Path:
        return self.directory / f"{task_id}.mission.json"

    def save(self, mission: Mission) -> None:
        self._path(mission.task_id).write_text(
            json.dumps(mission.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def load(self, task_id: str) -> Mission:
        path = self._path(task_id)
        if not path.exists():
            raise KeyError(task_id)
        return _mission_from_dict(json.loads(path.read_text(encoding="utf-8")))

    def list_task_ids(self) -> list[str]:
        return sorted(p.name.replace(".mission.json", "") for p in self.directory.glob("*.mission.json"))
