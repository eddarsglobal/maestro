from __future__ import annotations

from maestro.adaptive import AdaptivePolicyManager, PolicyKind


class GovernedRollbackBridge:
    "Delegates rollback to the existing authority-aware adaptive control plane."

    def rollback(
        self,
        manager: AdaptivePolicyManager,
        kind: PolicyKind,
        *,
        ex_authorized: bool,
        ay_acknowledged: bool,
        reason: str,
    ):
        return manager.rollback(
            kind,
            ex_authorized=ex_authorized,
            ay_acknowledged=ay_acknowledged,
            reason=reason,
        )
