from __future__ import annotations

from .models import ActivationSnapshot, ActivationState


class PolicyActivationGate:
    def activate(self, snapshot: ActivationSnapshot) -> ActivationSnapshot:
        snapshot.contract.assert_integrity()
        if snapshot.state is not ActivationState.CANARY_VERIFIED:
            raise PermissionError(
                "ACTIVE requires a verified healthy CANARY."
            )

        if not snapshot.ay_validated or not snapshot.ex_authorized:
            raise PermissionError(
                "ACTIVE requires AY validation and EX authorization."
            )

        snapshot.state = ActivationState.ACTIVE
        return snapshot
