from __future__ import annotations

from .models import ActivationSnapshot, ActivationState


class EXActivationAuthority:
    def authorize(
        self,
        snapshot: ActivationSnapshot,
        *,
        authorized: bool,
        actor: str = "EX",
        authority_ref: str,
    ) -> ActivationSnapshot:
        if actor != "EX":
            raise PermissionError(
                "Only EX control-plane authority may authorize activation."
            )

        if snapshot.state is not ActivationState.AY_VALIDATED:
            raise PermissionError(
                "EX authorization requires prior AY validation."
            )

        if not authority_ref:
            raise ValueError("authority_ref is required")

        if not authorized:
            snapshot.state = ActivationState.BLOCKED
            snapshot.metadata["ex_authorized"] = False
            snapshot.metadata["ex_authority_ref"] = authority_ref
            return snapshot

        snapshot.ex_authorized = True
        snapshot.state = ActivationState.EX_AUTHORIZED
        snapshot.metadata["ex_authorized"] = True
        snapshot.metadata["ex_authority_ref"] = authority_ref
        return snapshot
