from __future__ import annotations

from .models import ActivationSnapshot, ActivationState, CanaryEvidence


class CanaryController:
    def begin(self, snapshot: ActivationSnapshot) -> ActivationSnapshot:
        snapshot.contract.assert_integrity()
        if snapshot.state is not ActivationState.EX_AUTHORIZED:
            raise PermissionError(
                "CANARY requires AY validation and EX authorization."
            )

        if not snapshot.contract.rollback_ref:
            raise PermissionError(
                "CANARY requires a predeclared rollback reference."
            )

        snapshot.state = ActivationState.CANARY
        return snapshot

    def observe(
        self,
        snapshot: ActivationSnapshot,
        evidence: CanaryEvidence,
        *,
        min_success_rate: float = 0.95,
        min_samples: int = 3,
    ) -> ActivationSnapshot:
        if snapshot.state is not ActivationState.CANARY:
            raise ValueError("Canary evidence requires CANARY state.")

        snapshot.canary_evidence = evidence

        if evidence.healthy(
            min_success_rate=min_success_rate,
            min_samples=min_samples,
        ):
            snapshot.state = ActivationState.CANARY_VERIFIED
        else:
            snapshot.state = ActivationState.ROLLED_BACK
            snapshot.metadata["rollback_reason"] = "CANARY_DEGRADED"

        return snapshot
