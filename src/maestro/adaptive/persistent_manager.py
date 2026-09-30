from __future__ import annotations

import json
import os
from pathlib import Path

from .models import (
    ActivationRecord,
    AdaptivePolicy,
    PolicyKind,
    PolicyStatus,
)
from .policy_manager import AdaptivePolicyManager


class PersistentAdaptivePolicyManager(AdaptivePolicyManager):
    """
    Crash-resilient durable form of AdaptivePolicyManager.

    The full adaptive control-plane state is persisted as one atomic snapshot:
    policies + active pointers + activation history.
    """

    SCHEMA_VERSION = 1

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        super().__init__()
        self.load()

    @staticmethod
    def _policy_from_dict(data: dict) -> AdaptivePolicy:
        return AdaptivePolicy(
            kind=PolicyKind(str(data["kind"])),
            version=int(data["version"]),
            description=str(data["description"]),
            parameters=dict(data.get("parameters") or {}),
            parent_policy_id=(
                str(data["parent_policy_id"])
                if data.get("parent_policy_id") is not None
                else None
            ),
            status=PolicyStatus(str(data["status"])),
            created_at=str(data["created_at"]),
            policy_id=str(data["policy_id"]),
        )

    @staticmethod
    def _record_to_dict(record: ActivationRecord) -> dict:
        return {
            "policy_id": record.policy_id,
            "kind": record.kind.value,
            "previous_policy_id": record.previous_policy_id,
            "action": record.action,
            "reason": record.reason,
            "created_at": record.created_at,
        }

    @staticmethod
    def _record_from_dict(data: dict) -> ActivationRecord:
        return ActivationRecord(
            policy_id=str(data["policy_id"]),
            kind=PolicyKind(str(data["kind"])),
            previous_policy_id=(
                str(data["previous_policy_id"])
                if data.get("previous_policy_id") is not None
                else None
            ),
            action=str(data["action"]),
            reason=str(data["reason"]),
            created_at=str(data["created_at"]),
        )

    def snapshot(self) -> dict:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "policies": [
                self._policies[policy_id].to_dict()
                for policy_id in sorted(self._policies)
            ],
            "active": {
                kind.value: policy_id
                for kind, policy_id in sorted(
                    self._active.items(),
                    key=lambda item: item[0].value,
                )
            },
            "history": [
                self._record_to_dict(record)
                for record in self._history
            ],
        }

    def _validate_loaded_state(self) -> None:
        for kind, policy_id in self._active.items():
            policy = self._policies.get(policy_id)

            if policy is None:
                raise ValueError(
                    "Persistent adaptive state references missing active policy."
                )

            if policy.kind is not kind:
                raise ValueError(
                    "Persistent adaptive active pointer kind mismatch."
                )

            if policy.status is not PolicyStatus.ACTIVE:
                raise ValueError(
                    "Persistent adaptive active pointer references non-ACTIVE policy."
                )

        active_ids = set(self._active.values())

        for policy in self._policies.values():
            if (
                policy.status is PolicyStatus.ACTIVE
                and policy.policy_id not in active_ids
            ):
                raise ValueError(
                    "Persistent adaptive state contains orphan ACTIVE policy."
                )

        for record in self._history:
            if record.policy_id not in self._policies:
                raise ValueError(
                    "Persistent adaptive history references missing policy."
                )

            if (
                record.previous_policy_id is not None
                and record.previous_policy_id not in self._policies
            ):
                raise ValueError(
                    "Persistent adaptive history references missing previous policy."
                )

    def restore(self, payload: dict) -> None:
        if int(payload.get("schema_version", -1)) != self.SCHEMA_VERSION:
            raise ValueError(
                "Unsupported persistent adaptive state schema version."
            )

        policies = {}
        for row in payload.get("policies", []):
            policy = self._policy_from_dict(dict(row))

            if policy.policy_id in policies:
                raise ValueError(
                    "Duplicate policy ID in persistent adaptive state."
                )

            policies[policy.policy_id] = policy

        active = {
            PolicyKind(str(kind)): str(policy_id)
            for kind, policy_id in dict(
                payload.get("active") or {}
            ).items()
        }

        history = [
            self._record_from_dict(dict(row))
            for row in payload.get("history", [])
        ]

        old_policies = self._policies
        old_active = self._active
        old_history = self._history

        self._policies = policies
        self._active = active
        self._history = history

        try:
            self._validate_loaded_state()
        except Exception:
            self._policies = old_policies
            self._active = old_active
            self._history = old_history
            raise

    def load(self) -> None:
        if not self.path.exists():
            return

        payload = json.loads(
            self.path.read_text(encoding="utf-8")
        )
        self.restore(dict(payload))

    def save(self) -> None:
        payload = self.snapshot()
        raw = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ) + "\n"

        temp = self.path.with_name(
            self.path.name + ".tmp"
        )

        with temp.open("w", encoding="utf-8") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temp, self.path)

        # Persist the directory entry where supported.
        try:
            directory_fd = os.open(
                str(self.path.parent),
                os.O_RDONLY,
            )
        except OSError:
            return

        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)

    def _guarded_persist(self, before: dict) -> None:
        try:
            self.save()
        except Exception:
            self.restore(before)
            raise

    def register(self, policy: AdaptivePolicy) -> None:
        before = self.snapshot()
        super().register(policy)
        self._guarded_persist(before)

    def set_shadow(self, policy_id: str) -> None:
        before = self.snapshot()
        super().set_shadow(policy_id)
        self._guarded_persist(before)

    def activate(self, *args, **kwargs):
        before = self.snapshot()
        record = super().activate(*args, **kwargs)
        self._guarded_persist(before)
        return record

    def bootstrap_active(self, policy: AdaptivePolicy) -> None:
        before = self.snapshot()

        # Avoid the inherited self.register() dispatch causing an
        # intermediate persistent state when bootstrap is one logical action.
        if self.active(policy.kind) is not None:
            from .policy_manager import PolicyActivationDenied
            raise PolicyActivationDenied(
                "Active policy already exists for this kind."
            )

        if policy.policy_id not in self._policies:
            AdaptivePolicyManager.register(self, policy)

        policy.status = PolicyStatus.ACTIVE
        self._active[policy.kind] = policy.policy_id

        self._history.append(
            ActivationRecord(
                policy_id=policy.policy_id,
                kind=policy.kind,
                previous_policy_id=None,
                action="BOOTSTRAP",
                reason="known-safe genesis policy",
            )
        )

        self._guarded_persist(before)

    def rollback(self, *args, **kwargs):
        before = self.snapshot()
        record = super().rollback(*args, **kwargs)
        self._guarded_persist(before)
        return record
