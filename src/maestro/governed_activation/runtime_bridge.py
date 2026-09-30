from __future__ import annotations

from maestro.adaptive import AdaptivePolicyManager, PromotionEvidence

from .models import ActivationSnapshot, ActivationState


class AdaptivePolicyRuntimeBridge:
    """
    Narrow bridge from the GPA control plane to the existing adaptive runtime.

    GPA decides whether runtime activation is permitted.
    AdaptivePolicyManager remains the executor of the actual policy activation.
    """

    def assert_activation_ready(
        self,
        snapshot: ActivationSnapshot,
        evidence: PromotionEvidence,
    ) -> None:
        snapshot.contract.assert_integrity()

        if snapshot.state is not ActivationState.CANARY_VERIFIED:
            raise PermissionError(
                "Adaptive runtime activation requires CANARY_VERIFIED GPA state."
            )

        if not snapshot.ay_validated or not snapshot.ex_authorized:
            raise PermissionError(
                "Adaptive runtime activation requires AY + EX authorization."
            )

        learning_candidate_id = str(
            getattr(evidence, "learning_candidate_id", "") or ""
        )

        if learning_candidate_id != snapshot.candidate_id:
            raise PermissionError(
                "PromotionEvidence candidate does not match activation contract."
            )

    def activate(
        self,
        snapshot: ActivationSnapshot,
        manager: AdaptivePolicyManager,
        *,
        evidence: PromotionEvidence,
    ):
        self.assert_activation_ready(snapshot, evidence)

        return manager.activate(
            snapshot.contract.policy_ref,
            evidence=evidence,
            ay_validated=snapshot.ay_validated,
            ex_authorized=snapshot.ex_authorized,
        )

    def rollback(
        self,
        snapshot: ActivationSnapshot,
        manager: AdaptivePolicyManager,
        *,
        kind,
        ex_authorized: bool,
        ay_acknowledged: bool,
        reason: str,
    ):
        if snapshot.state is not ActivationState.ACTIVE:
            raise PermissionError(
                "Adaptive runtime rollback requires ACTIVE GPA state."
            )

        if not ex_authorized:
            raise PermissionError(
                "Adaptive runtime rollback requires fresh EX authorization."
            )

        if not ay_acknowledged:
            raise PermissionError(
                "Adaptive runtime rollback requires AY acknowledgement."
            )

        if not reason:
            raise ValueError("Rollback reason is required.")

        return manager.rollback(
            kind,
            ex_authorized=bool(ex_authorized),
            ay_acknowledged=bool(ay_acknowledged),
            reason=str(reason),
        )

