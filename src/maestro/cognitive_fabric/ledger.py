from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json


class CognitiveFabricLedger:
    """
    Compact append-only execution ledger.
    Raw model thinking is never required here.
    """

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else None
        self.rows: list[dict] = []

    def record_artifact(self, task_id: str, artifact) -> None:
        row = {
            "task_id": task_id,
            "stage_id": artifact.stage_id,
            "role": artifact.role.value,
            "resource_id": artifact.resource_id,
            "provider_id": artifact.provider_id,
            "model_id": artifact.model_id,
            "success": artifact.success,
            "quality": artifact.quality,
            "output_chars": len(artifact.output),
            "evidence_refs": list(artifact.evidence_refs),
            "metadata": dict(artifact.metadata),
        }
        self.rows.append(row)
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
