from __future__ import annotations

from typing import Any

from .models import ActivationContract


class ActivationContractFactory:
    def create(
        self,
        *,
        candidate_id: str,
        task_family: str,
        policy_kind: str,
        policy_ref: str,
        baseline_ref: str,
        rollback_ref: str,
        canary_fraction: float = 0.10,
        metadata: dict[str, Any] | None = None,
    ) -> ActivationContract:
        return ActivationContract(
            candidate_id=candidate_id,
            task_family=task_family,
            policy_kind=policy_kind,
            policy_ref=policy_ref,
            baseline_ref=baseline_ref,
            rollback_ref=rollback_ref,
            canary_fraction=canary_fraction,
            metadata=dict(metadata or {}),
        )
