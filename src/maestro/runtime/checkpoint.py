from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import hashlib
import json

from maestro.enums import CouncilId, MissionState, VerdictScope, VerdictValue
from maestro.models import Mission, Verdict
from maestro.orchestration.dag import DagEngine
from maestro.orchestration.retry_ledger import RetryLedger


CHECKPOINT_SCHEMA = "maestro.checkpoint.v0.2"


class CheckpointError(RuntimeError):
    pass


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _checksum(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _mission_from_dict(raw: dict[str, Any]) -> Mission:
    mission = Mission(
        objective=raw["objective"],
        scope=raw.get("scope", ""),
        requested_output=raw.get("requested_output", ""),
        task_id=raw["task_id"],
        state=MissionState(raw["state"]),
        acceptance_criteria=list(raw.get("acceptance_criteria", [])),
        strike_team=[CouncilId(x) for x in raw.get("strike_team", [])],
        tx_commit_authorized=bool(raw.get("tx_commit_authorized", False)),
        tx_committed=bool(raw.get("tx_committed", False)),
        metadata=dict(raw.get("metadata", {})),
        created_at=raw["created_at"],
        updated_at=raw["updated_at"],
    )

    for item in raw.get("domain_verdicts", []):
        mission.domain_verdicts.append(
            Verdict(
                task_id=item["task_id"],
                council=CouncilId(item["council"]),
                value=VerdictValue(item["value"]),
                scope=VerdictScope(item["scope"]),
                findings=list(item.get("findings", [])),
                evidence_ids=list(item.get("evidence_ids", [])),
                created_at=item["created_at"],
            )
        )

    if raw.get("system_verdict"):
        item = raw["system_verdict"]
        mission.system_verdict = Verdict(
            task_id=item["task_id"],
            council=CouncilId(item["council"]),
            value=VerdictValue(item["value"]),
            scope=VerdictScope(item["scope"]),
            findings=list(item.get("findings", [])),
            evidence_ids=list(item.get("evidence_ids", [])),
            created_at=item["created_at"],
        )
    return mission


@dataclass(slots=True)
class CheckpointBundle:
    mission: Mission
    dag: DagEngine
    retry_ledger: RetryLedger
    metadata: dict[str, Any]


class CheckpointStore:
    def __init__(self, directory: str | Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        mission: Mission,
        dag: DagEngine,
        retry_ledger: RetryLedger,
        evidence_ids: list[str] | None = None,
        trace_count: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> Path:
        body = {
            "schema": CHECKPOINT_SCHEMA,
            "mission": mission.to_dict(),
            "dag": dag.snapshot(),
            "retry_ledger": retry_ledger.snapshot(),
            "evidence_ids": list(evidence_ids or []),
            "trace_count": int(trace_count),
            "metadata": dict(metadata or {}),
        }
        envelope = {"body": body, "sha256": _checksum(body)}
        path = self.directory / f"{mission.task_id}.checkpoint.json"
        path.write_text(
            json.dumps(envelope, indent=2, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )
        return path

    def load(self, task_id: str) -> CheckpointBundle:
        path = self.directory / f"{task_id}.checkpoint.json"
        if not path.exists():
            raise CheckpointError(f"Checkpoint not found: {task_id}")

        envelope = json.loads(path.read_text(encoding="utf-8"))
        body = envelope.get("body")
        if not isinstance(body, dict):
            raise CheckpointError("Malformed checkpoint body.")

        if body.get("schema") != CHECKPOINT_SCHEMA:
            raise CheckpointError(f"Unsupported checkpoint schema: {body.get('schema')}")

        expected = envelope.get("sha256")
        actual = _checksum(body)
        if expected != actual:
            raise CheckpointError("Checkpoint integrity check failed.")

        mission = _mission_from_dict(body["mission"])
        dag = DagEngine.from_snapshot(body["dag"])
        retry_ledger = RetryLedger.from_snapshot(body["retry_ledger"])
        return CheckpointBundle(
            mission=mission,
            dag=dag,
            retry_ledger=retry_ledger,
            metadata={
                **dict(body.get("metadata", {})),
                "evidence_ids": list(body.get("evidence_ids", [])),
                "trace_count": int(body.get("trace_count", 0)),
            },
        )
