from __future__ import annotations

from .models import ActivationSnapshot, ActivationState


class GovernedActivationRollback:
    ROLLBACKABLE = {
        ActivationState.EX_AUTHORIZED,
        ActivationState.CANARY,
        ActivationState.CANARY_VERIFIED,
        ActivationState.ACTIVE,
    }

    def rollback(
        self,
        snapshot: ActivationSnapshot,
        *,
        reason: str,
        evidence_ref: str,
    ) -> ActivationSnapshot:
        if snapshot.state not in self.ROLLBACKABLE:
            raise ValueError(
                f"State {snapshot.state.value} is not rollbackable."
            )

        if not reason or not evidence_ref:
            raise ValueError("Rollback requires reason and evidence_ref.")

        snapshot.state = ActivationState.ROLLED_BACK
        snapshot.metadata["rollback_reason"] = reason
        snapshot.metadata["rollback_evidence_ref"] = evidence_ref
        return snapshot
