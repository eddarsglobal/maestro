from __future__ import annotations

from .models import ActivationSnapshot, ActivationState


class AYActivationGate:
    def validate(
        self,
        snapshot: ActivationSnapshot,
        *,
        verdict: str,
        evidence_refs: list[str] | tuple[str, ...],
        actor: str = "AY",
    ) -> ActivationSnapshot:
        if actor != "AY":
            raise PermissionError("Only AY may issue the activation validation gate.")

        if snapshot.state is not ActivationState.PROPOSED:
            raise ValueError("AY validation requires PROPOSED state.")

        refs = tuple(str(x) for x in evidence_refs if str(x))

        if verdict != "JUSTE" or not refs:
            snapshot.state = ActivationState.BLOCKED
            snapshot.metadata["ay_verdict"] = verdict
            snapshot.metadata["ay_evidence_refs"] = list(refs)
            return snapshot

        snapshot.ay_validated = True
        snapshot.state = ActivationState.AY_VALIDATED
        snapshot.metadata["ay_verdict"] = "JUSTE"
        snapshot.metadata["ay_evidence_refs"] = list(refs)
        return snapshot
