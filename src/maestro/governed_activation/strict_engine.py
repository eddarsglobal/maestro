from __future__ import annotations

from .authority import (
    GovernanceAction,
    GovernanceAttestation,
    GovernanceAuthority,
)
from .engine import GovernedPolicyActivation
from .models import ActivationSnapshot
from .transaction import (
    RuntimeCommitCoordinator,
    RuntimeCommitJournal,
)


class StrictGovernedPolicyActivation(GovernedPolicyActivation):
    """
    Production GPA surface.

    The legacy base engine remains available for low-level compatibility tests,
    while this production subclass rejects free-form AY/EX authority inputs.
    """

    def __init__(self, *args, **kwargs):
        transaction_path = kwargs.pop(
            "transaction_path",
            None,
        )
        super().__init__(*args, **kwargs)
        self.authority = GovernanceAuthority()
        self.strict_authority = True

        if (
            transaction_path is None
            and self.ledger.path is not None
        ):
            transaction_path = self.ledger.path.with_name(
                "runtime_transactions.jsonl"
            )

        self.runtime_commit_journal = RuntimeCommitJournal(
            transaction_path
        )
        self.runtime_commit_coordinator = RuntimeCommitCoordinator(
            self.runtime_commit_journal
        )
    def issue_ay_validation(
        self,
        snapshot: ActivationSnapshot,
        *,
        verdict: str,
        evidence_refs,
    ) -> GovernanceAttestation:
        return self.authority.issue_ay_validation(
            snapshot,
            verdict=verdict,
            evidence_refs=evidence_refs,
        )

    def issue_ex_authorization(
        self,
        snapshot: ActivationSnapshot,
        *,
        authorized: bool,
        authority_ref: str,
        evidence_refs=(),
    ) -> GovernanceAttestation:
        return self.authority.issue_ex_authorization(
            snapshot,
            authorized=authorized,
            authority_ref=authority_ref,
            evidence_refs=evidence_refs,
        )

    def issue_rollback_ay_ack(
        self,
        snapshot: ActivationSnapshot,
        *,
        acknowledged: bool,
        reason: str,
        evidence_ref: str,
    ) -> GovernanceAttestation:
        return self.authority.issue_rollback_ay_ack(
            snapshot,
            acknowledged=acknowledged,
            reason=reason,
            evidence_ref=evidence_ref,
        )

    def issue_rollback_ex_authorization(
        self,
        snapshot: ActivationSnapshot,
        *,
        authorized: bool,
        reason: str,
        evidence_ref: str,
        authority_ref: str,
        ay_attestation: GovernanceAttestation,
    ) -> GovernanceAttestation:
        return self.authority.issue_rollback_ex_authorization(
            snapshot,
            authorized=authorized,
            reason=reason,
            evidence_ref=evidence_ref,
            authority_ref=authority_ref,
            ay_attestation=ay_attestation,
        )

    def ay_validate(
        self,
        snapshot: ActivationSnapshot,
        *,
        attestation: GovernanceAttestation | None = None,
        **legacy,
    ) -> ActivationSnapshot:
        if attestation is None:
            raise PermissionError(
                "Production GPA requires an AY governance attestation."
            )

        attestation.assert_bound(
            snapshot,
            actor="AY",
            action=GovernanceAction.AY_VALIDATE,
        )

        self.ay.validate(
            snapshot,
            verdict=attestation.decision,
            evidence_refs=attestation.evidence_refs,
            actor="AY",
        )

        snapshot.metadata["ay_attestation_id"] = (
            attestation.attestation_id
        )
        snapshot.metadata["ay_attestation"] = (
            attestation.to_dict()
        )

        self.ledger.checkpoint(snapshot)
        return snapshot

    def ex_authorize(
        self,
        snapshot: ActivationSnapshot,
        *,
        attestation: GovernanceAttestation | None = None,
        **legacy,
    ) -> ActivationSnapshot:
        if attestation is None:
            raise PermissionError(
                "Production GPA requires an EX governance attestation."
            )

        parent = str(
            snapshot.metadata.get("ay_attestation_id") or ""
        )
        if not parent:
            raise PermissionError(
                "EX authorization requires persisted AY attestation."
            )

        attestation.assert_bound(
            snapshot,
            actor="EX",
            action=GovernanceAction.EX_AUTHORIZE,
            parent_attestation_id=parent,
        )

        if attestation.decision not in {
            "AUTHORIZED",
            "DENIED",
        }:
            raise PermissionError(
                "Invalid EX attestation decision."
            )

        self.ex.authorize(
            snapshot,
            authorized=(
                attestation.decision == "AUTHORIZED"
            ),
            authority_ref=str(
                attestation.authority_ref or ""
            ),
            actor="EX",
        )

        snapshot.metadata["ex_attestation_id"] = (
            attestation.attestation_id
        )
        snapshot.metadata["ex_attestation"] = (
            attestation.to_dict()
        )

        self.ledger.checkpoint(snapshot)
        return snapshot

    def _assert_activation_chain(
        self,
        snapshot: ActivationSnapshot,
    ) -> None:
        if not snapshot.metadata.get("ay_attestation_id"):
            raise PermissionError(
                "Production GPA requires AY attestation provenance."
            )
        if not snapshot.metadata.get("ex_attestation_id"):
            raise PermissionError(
                "Production GPA requires EX attestation provenance."
            )

    def begin_canary(
        self,
        snapshot: ActivationSnapshot,
    ) -> ActivationSnapshot:
        self._assert_activation_chain(snapshot)
        return super().begin_canary(snapshot)

    def activate(
        self,
        snapshot: ActivationSnapshot,
    ) -> ActivationSnapshot:
        self._assert_activation_chain(snapshot)
        return super().activate(snapshot)

    def activate_manager(
        self,
        snapshot: ActivationSnapshot,
        manager,
        *,
        evidence,
    ):
        self._assert_activation_chain(snapshot)
        return self.runtime_commit_coordinator.activate(
            self,
            snapshot,
            manager,
            evidence=evidence,
        )

    def recover_runtime_transactions(
        self,
        manager,
    ):
        return self.runtime_commit_coordinator.recover(
            self,
            manager,
        )
    def rollback_manager(
        self,
        snapshot: ActivationSnapshot,
        manager,
        *,
        kind,
        reason: str,
        evidence_ref: str,
        ay_attestation: GovernanceAttestation | None = None,
        ex_attestation: GovernanceAttestation | None = None,
        **legacy,
    ):
        if ay_attestation is None or ex_attestation is None:
            raise PermissionError(
                "Production GPA runtime rollback requires "
                "fresh AY/EX attestations."
            )

        ay_attestation.assert_bound(
            snapshot,
            actor="AY",
            action=GovernanceAction.ROLLBACK_AY_ACK,
            reason=reason,
            evidence_ref=evidence_ref,
        )

        ex_attestation.assert_bound(
            snapshot,
            actor="EX",
            action=GovernanceAction.ROLLBACK_EX_AUTHORIZE,
            parent_attestation_id=ay_attestation.attestation_id,
            reason=reason,
            evidence_ref=evidence_ref,
        )

        if ay_attestation.decision != "ACKNOWLEDGED":
            raise PermissionError(
                "AY rollback attestation does not "
                "acknowledge rollback."
            )

        if ex_attestation.decision != "AUTHORIZED":
            raise PermissionError(
                "EX rollback attestation does not "
                "authorize rollback."
            )

        return self.runtime_commit_coordinator.rollback(
            self,
            snapshot,
            manager,
            kind=kind,
            reason=reason,
            evidence_ref=evidence_ref,
            ay_attestation=ay_attestation,
            ex_attestation=ex_attestation,
        )
