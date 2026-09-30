from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from collections.abc import Mapping
from typing import Any
from uuid import uuid4

from maestro.adaptive import PersistentAdaptivePolicyManager, PolicyKind

from .models import ActivationSnapshot, ActivationState


def _freeze_transaction_json(value):
    if isinstance(value, Mapping):
        return MappingProxyType({
            str(key): _freeze_transaction_json(item)
            for key, item in value.items()
        })

    if isinstance(value, (list, tuple)):
        return tuple(
            _freeze_transaction_json(item)
            for item in value
        )

    if value is None or isinstance(
        value,
        (str, int, float, bool),
    ):
        return value

    raise TypeError(
        "Runtime transaction governance must be JSON-compatible."
    )


def _thaw_transaction_json(value):
    if isinstance(value, Mapping):
        return {
            str(key): _thaw_transaction_json(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            _thaw_transaction_json(item)
            for item in value
        ]

    if value is None or isinstance(
        value,
        (str, int, float, bool),
    ):
        return value

    raise TypeError(
        "Runtime transaction governance contains unsupported data."
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RuntimeCommitOperation(str, Enum):
    ACTIVATE = "ACTIVATE"
    ROLLBACK = "ROLLBACK"


class RuntimeCommitState(str, Enum):
    PREPARED = "PREPARED"
    MANAGER_COMMITTED = "MANAGER_COMMITTED"
    GPA_COMMITTED = "GPA_COMMITTED"
    ABORTED = "ABORTED"
    BLOCKED = "BLOCKED"


TERMINAL_STATES = {
    RuntimeCommitState.GPA_COMMITTED,
    RuntimeCommitState.ABORTED,
    RuntimeCommitState.BLOCKED,
}


@dataclass(frozen=True)
class RuntimeCommitRecord:
    contract_id: str
    operation: RuntimeCommitOperation
    kind: str
    before_active_policy_id: str | None
    after_active_policy_id: str | None
    gpa_before_state: str
    gpa_after_state: str
    reason: str | None = None
    evidence_ref: str | None = None
    governance: Mapping[str, Any] = field(default_factory=dict)
    state: RuntimeCommitState = RuntimeCommitState.PREPARED
    transaction_id: str = field(
        default_factory=lambda: f"RTX-{uuid4().hex[:16].upper()}"
    )
    created_at: str = field(default_factory=_utc_now)
    previous_event_id: str | None = None
    event_id: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "governance",
            _freeze_transaction_json(
                dict(self.governance or {})
            ),
        )
        object.__setattr__(
            self,
            "event_id",
            self._expected_event_id(),
        )

    def _event_payload(self) -> dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "operation": self.operation.value,
            "kind": self.kind,
            "before_active_policy_id": self.before_active_policy_id,
            "after_active_policy_id": self.after_active_policy_id,
            "gpa_before_state": self.gpa_before_state,
            "gpa_after_state": self.gpa_after_state,
            "reason": self.reason,
            "evidence_ref": self.evidence_ref,
            "governance": _thaw_transaction_json(
                self.governance
            ),
            "state": self.state.value,
            "transaction_id": self.transaction_id,
            "created_at": self.created_at,
            "previous_event_id": self.previous_event_id,
        }

    def _expected_event_id(self) -> str:
        raw = json.dumps(
            self._event_payload(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        digest = hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()[:20].upper()
        return f"RTE-{digest}"

    def assert_integrity(self) -> None:
        if self.event_id != self._expected_event_id():
            raise ValueError(
                "Runtime transaction event integrity check failed."
            )

    def to_dict(self) -> dict[str, Any]:
        self.assert_integrity()
        return {
            **self._event_payload(),
            "event_id": self.event_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RuntimeCommitRecord":
        row = cls(
            contract_id=str(data["contract_id"]),
            operation=RuntimeCommitOperation(
                str(data["operation"])
            ),
            kind=str(data["kind"]),
            before_active_policy_id=(
                str(data["before_active_policy_id"])
                if data.get("before_active_policy_id") is not None
                else None
            ),
            after_active_policy_id=(
                str(data["after_active_policy_id"])
                if data.get("after_active_policy_id") is not None
                else None
            ),
            gpa_before_state=str(data["gpa_before_state"]),
            gpa_after_state=str(data["gpa_after_state"]),
            reason=(
                str(data["reason"])
                if data.get("reason") is not None
                else None
            ),
            evidence_ref=(
                str(data["evidence_ref"])
                if data.get("evidence_ref") is not None
                else None
            ),
            governance=dict(data.get("governance") or {}),
            state=RuntimeCommitState(str(data["state"])),
            transaction_id=str(data["transaction_id"]),
            created_at=str(data["created_at"]),
            previous_event_id=(
                str(data["previous_event_id"])
                if data.get("previous_event_id") is not None
                else None
            ),
        )

        expected = data.get("event_id")

        if expected is None:
            raise ValueError(
                "Runtime transaction event lacks integrity ID."
            )

        if row.event_id != str(expected):
            raise ValueError(
                "Runtime transaction event integrity check failed."
            )

        return row

    def advanced(
        self,
        state: RuntimeCommitState,
        *,
        reason: str | None = None,
    ) -> "RuntimeCommitRecord":
        return replace(
            self,
            state=state,
            reason=self.reason if reason is None else str(reason),
            previous_event_id=None,
        )


class RuntimeCommitJournal:
    """Append-only durable transaction journal with latest-state projection."""

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path is not None else None
        self._events: list[RuntimeCommitRecord] = []

        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.load()

    @staticmethod
    def _clone(row: RuntimeCommitRecord) -> RuntimeCommitRecord:
        return RuntimeCommitRecord.from_dict(row.to_dict())

    def append(
        self,
        row: RuntimeCommitRecord,
    ) -> RuntimeCommitRecord:
        previous_event_id = (
            self._events[-1].event_id
            if self._events
            else None
        )

        chained = replace(
            row,
            previous_event_id=previous_event_id,
        )
        chained.assert_integrity()
        self._events.append(chained)

        if self.path is not None:
            raw = (
                json.dumps(
                    chained.to_dict(),
                    sort_keys=True,
                    ensure_ascii=False,
                    allow_nan=False,
                )
                + "\n"
            )

            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())

        return self._clone(chained)

    def load(self) -> None:
        self._events = []

        if self.path is None or not self.path.exists():
            return

        expected_previous = None

        with self.path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(
                handle,
                start=1,
            ):
                line = line.strip()
                if not line:
                    continue

                row = RuntimeCommitRecord.from_dict(
                    json.loads(line)
                )

                if row.previous_event_id != expected_previous:
                    raise ValueError(
                        "Runtime transaction journal chain "
                        f"break at line {line_number}."
                    )

                self._events.append(row)
                expected_previous = row.event_id

    def history(
        self,
        transaction_id: str,
    ) -> list[RuntimeCommitRecord]:
        return [
            self._clone(row)
            for row in self._events
            if row.transaction_id == transaction_id
        ]

    def latest(
        self,
        transaction_id: str,
    ) -> RuntimeCommitRecord | None:
        for row in reversed(self._events):
            if row.transaction_id == transaction_id:
                return self._clone(row)
        return None

    def pending(self) -> list[RuntimeCommitRecord]:
        latest: dict[str, RuntimeCommitRecord] = {}

        for row in self._events:
            latest[row.transaction_id] = row

        return [
            self._clone(row)
            for row in latest.values()
            if row.state not in TERMINAL_STATES
        ]

    def blocked(self) -> list[RuntimeCommitRecord]:
        latest: dict[str, RuntimeCommitRecord] = {}

        for row in self._events:
            latest[row.transaction_id] = row

        return [
            self._clone(row)
            for row in latest.values()
            if row.state is RuntimeCommitState.BLOCKED
        ]


class RuntimeCommitCoordinator:
    """
    Coordinates the persistent adaptive manager and GPA lifecycle ledger.
    """

    def __init__(self, journal: RuntimeCommitJournal):
        self.journal = journal

    @staticmethod
    def _require_persistent_manager(manager) -> None:
        if not isinstance(
            manager,
            PersistentAdaptivePolicyManager,
        ):
            raise PermissionError(
                "Production GPA runtime commit requires "
                "PersistentAdaptivePolicyManager."
            )

    @staticmethod
    def _active_id(manager, kind: PolicyKind) -> str | None:
        active = manager.active(kind)
        return active.policy_id if active is not None else None

    def activate(
        self,
        engine,
        snapshot: ActivationSnapshot,
        manager,
        *,
        evidence,
    ):
        self._require_persistent_manager(manager)
        engine.runtime_bridge.assert_activation_ready(
            snapshot,
            evidence,
        )

        kind = PolicyKind(snapshot.contract.policy_kind)
        before_id = self._active_id(manager, kind)
        after_id = snapshot.contract.policy_ref

        if before_id == after_id:
            raise RuntimeError(
                "Activation transaction target is already active."
            )

        txn = RuntimeCommitRecord(
            contract_id=snapshot.contract_id,
            operation=RuntimeCommitOperation.ACTIVATE,
            kind=kind.value,
            before_active_policy_id=before_id,
            after_active_policy_id=after_id,
            gpa_before_state=snapshot.state.value,
            gpa_after_state=ActivationState.ACTIVE.value,
        )
        self.journal.append(txn)

        record = engine.runtime_bridge.activate(
            snapshot,
            manager,
            evidence=evidence,
        )

        if self._active_id(manager, kind) != after_id:
            blocked = txn.advanced(
                RuntimeCommitState.BLOCKED,
                reason=(
                    "manager activation did not produce "
                    "expected active policy"
                ),
            )
            self.journal.append(blocked)
            raise RuntimeError(blocked.reason)

        txn = txn.advanced(
            RuntimeCommitState.MANAGER_COMMITTED
        )
        self.journal.append(txn)

        engine.activation.activate(snapshot)
        snapshot.metadata["adaptive_runtime_policy_id"] = after_id
        snapshot.metadata["runtime_commit_transaction_id"] = (
            txn.transaction_id
        )
        engine.ledger.checkpoint(snapshot)

        txn = txn.advanced(
            RuntimeCommitState.GPA_COMMITTED
        )
        self.journal.append(txn)

        return record

    def rollback(
        self,
        engine,
        snapshot: ActivationSnapshot,
        manager,
        *,
        kind,
        reason: str,
        evidence_ref: str,
        ay_attestation,
        ex_attestation,
    ):
        self._require_persistent_manager(manager)

        policy_kind = (
            kind
            if isinstance(kind, PolicyKind)
            else PolicyKind(str(kind))
        )

        before_id = self._active_id(
            manager,
            policy_kind,
        )
        after_id = snapshot.contract.rollback_ref

        txn = RuntimeCommitRecord(
            contract_id=snapshot.contract_id,
            operation=RuntimeCommitOperation.ROLLBACK,
            kind=policy_kind.value,
            before_active_policy_id=before_id,
            after_active_policy_id=after_id,
            gpa_before_state=snapshot.state.value,
            gpa_after_state=ActivationState.ROLLED_BACK.value,
            reason=str(reason),
            evidence_ref=str(evidence_ref),
            governance={
                "ay_attestation": ay_attestation.to_dict(),
                "ex_attestation": ex_attestation.to_dict(),
            },
        )
        self.journal.append(txn)

        record = engine.runtime_bridge.rollback(
            snapshot,
            manager,
            kind=policy_kind,
            ex_authorized=True,
            ay_acknowledged=True,
            reason=reason,
        )

        if self._active_id(manager, policy_kind) != after_id:
            blocked = txn.advanced(
                RuntimeCommitState.BLOCKED,
                reason=(
                    "manager rollback did not restore "
                    "expected policy"
                ),
            )
            self.journal.append(blocked)
            raise RuntimeError(blocked.reason)

        txn = txn.advanced(
            RuntimeCommitState.MANAGER_COMMITTED
        )
        self.journal.append(txn)

        self._commit_rollback_gpa(
            engine,
            snapshot,
            txn,
        )

        txn = txn.advanced(
            RuntimeCommitState.GPA_COMMITTED
        )
        self.journal.append(txn)

        return record

    @staticmethod
    def _commit_rollback_gpa(
        engine,
        snapshot: ActivationSnapshot,
        txn: RuntimeCommitRecord,
    ) -> None:
        engine.rollback_engine.rollback(
            snapshot,
            reason=str(txn.reason),
            evidence_ref=str(txn.evidence_ref),
        )

        ay = dict(
            txn.governance.get("ay_attestation") or {}
        )
        ex = dict(
            txn.governance.get("ex_attestation") or {}
        )

        snapshot.metadata["rollback_ex_authority_ref"] = (
            ex.get("authority_ref")
        )
        snapshot.metadata["rollback_ay_ack_ref"] = (
            ay.get("attestation_id")
        )
        snapshot.metadata["rollback_ay_attestation_id"] = (
            ay.get("attestation_id")
        )
        snapshot.metadata["rollback_ex_attestation_id"] = (
            ex.get("attestation_id")
        )
        snapshot.metadata["rollback_ay_attestation"] = ay
        snapshot.metadata["rollback_ex_attestation"] = ex
        snapshot.metadata[
            "adaptive_runtime_restored_policy_id"
        ] = txn.after_active_policy_id
        snapshot.metadata["runtime_commit_transaction_id"] = (
            txn.transaction_id
        )

        engine.ledger.checkpoint(snapshot)

    def recover(
        self,
        engine,
        manager,
    ) -> list[RuntimeCommitRecord]:
        self._require_persistent_manager(manager)
        results: list[RuntimeCommitRecord] = []

        for pending in self.journal.pending():
            row = pending
            snapshot = engine.ledger.latest(
                row.contract_id
            )

            if snapshot is None:
                blocked = row.advanced(
                    RuntimeCommitState.BLOCKED,
                    reason="GPA snapshot missing during recovery",
                )
                self.journal.append(blocked)
                results.append(blocked)
                continue

            kind = PolicyKind(row.kind)
            active_id = self._active_id(
                manager,
                kind,
            )

            if row.state is RuntimeCommitState.PREPARED:
                if active_id == row.before_active_policy_id:
                    aborted = row.advanced(
                        RuntimeCommitState.ABORTED,
                        reason=(
                            "manager commit not observed "
                            "after restart"
                        ),
                    )
                    self.journal.append(aborted)
                    results.append(aborted)
                    continue

                if active_id == row.after_active_policy_id:
                    row = row.advanced(
                        RuntimeCommitState.MANAGER_COMMITTED
                    )
                    self.journal.append(row)
                else:
                    blocked = row.advanced(
                        RuntimeCommitState.BLOCKED,
                        reason=(
                            "manager active pointer matches neither "
                            "transaction before nor after state"
                        ),
                    )
                    self.journal.append(blocked)
                    results.append(blocked)
                    continue

            if row.state is RuntimeCommitState.MANAGER_COMMITTED:
                if active_id != row.after_active_policy_id:
                    blocked = row.advanced(
                        RuntimeCommitState.BLOCKED,
                        reason=(
                            "manager commit lost or contradicted"
                        ),
                    )
                    self.journal.append(blocked)
                    results.append(blocked)
                    continue

                expected_before = ActivationState(
                    row.gpa_before_state
                )
                expected_after = ActivationState(
                    row.gpa_after_state
                )

                if snapshot.state is expected_after:
                    committed = row.advanced(
                        RuntimeCommitState.GPA_COMMITTED
                    )
                    self.journal.append(committed)
                    results.append(committed)
                    continue

                if snapshot.state is not expected_before:
                    blocked = row.advanced(
                        RuntimeCommitState.BLOCKED,
                        reason=(
                            "GPA state matches neither transaction "
                            "before nor after state"
                        ),
                    )
                    self.journal.append(blocked)
                    results.append(blocked)
                    continue

                if (
                    row.operation
                    is RuntimeCommitOperation.ACTIVATE
                ):
                    engine.activation.activate(snapshot)
                    snapshot.metadata[
                        "adaptive_runtime_policy_id"
                    ] = row.after_active_policy_id
                    snapshot.metadata[
                        "runtime_commit_transaction_id"
                    ] = row.transaction_id
                    engine.ledger.checkpoint(snapshot)
                else:
                    self._commit_rollback_gpa(
                        engine,
                        snapshot,
                        row,
                    )

                committed = row.advanced(
                    RuntimeCommitState.GPA_COMMITTED
                )
                self.journal.append(committed)
                results.append(committed)

        return results
