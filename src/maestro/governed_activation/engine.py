from __future__ import annotations

from .activation import PolicyActivationGate
from .ay_gate import AYActivationGate
from .canary import CanaryController
from .contracts import ActivationContractFactory
from .eligibility import ActivationEligibilityGate
from .ex_authority import EXActivationAuthority
from .ledger import ActivationLedger
from .models import ActivationSnapshot, CanaryEvidence
from .observation import RuntimeObservationFactory
from .rollback import GovernedActivationRollback
from .runtime_bridge import AdaptivePolicyRuntimeBridge


class GovernedPolicyActivation:
    """
    Deterministic activation control plane.

    This engine governs lifecycle state only. It does not allow an LLM,
    Academy, or Outcome Intelligence to grant activation authority.
    """

    def __init__(self, ledger_path=None, *, candidate_ledger=None):
        self.ledger = ActivationLedger(ledger_path)
        self.candidate_ledger = candidate_ledger
        self.eligibility = ActivationEligibilityGate()
        self.contracts = ActivationContractFactory()
        self.ay = AYActivationGate()
        self.ex = EXActivationAuthority()
        self.canary = CanaryController()
        self.activation = PolicyActivationGate()
        self.rollback_engine = GovernedActivationRollback()
        self.observations = RuntimeObservationFactory()
        self.runtime_bridge = AdaptivePolicyRuntimeBridge()

    def propose(
        self,
        candidate,
        *,
        policy_kind: str,
        policy_ref: str,
        baseline_ref: str,
        rollback_ref: str,
        canary_fraction: float = 0.10,
        metadata=None,
    ) -> ActivationSnapshot:
        self.eligibility.assert_eligible(
            candidate,
            candidate_ledger=self.candidate_ledger,
        )

        task_family = str(getattr(candidate, "task_family", "") or "")
        candidate_id = str(getattr(candidate, "candidate_id", "") or "")

        contract = self.contracts.create(
            candidate_id=candidate_id,
            task_family=task_family,
            policy_kind=policy_kind,
            policy_ref=policy_ref,
            baseline_ref=baseline_ref,
            rollback_ref=rollback_ref,
            canary_fraction=canary_fraction,
            metadata=dict(metadata or {}),
        )

        lineage = self.ledger.by_candidate(candidate_id)

        conflicting = [
            row
            for row in lineage
            if row.contract_id != contract.contract_id
        ]

        if conflicting:
            existing_ids = ", ".join(
                sorted(
                    {
                        row.contract_id
                        for row in conflicting
                    }
                )
            )
            raise PermissionError(
                "Activation candidate already owns a different "
                "GPA contract lineage: "
                f"candidate={candidate_id} "
                f"existing={existing_ids} "
                f"requested={contract.contract_id}"
            )

        existing = self.ledger.latest(contract.contract_id)
        if existing is not None:
            return existing

        snapshot = ActivationSnapshot(contract=contract)
        self.ledger.checkpoint(snapshot)
        return snapshot

    def ay_validate(
        self,
        snapshot: ActivationSnapshot,
        *,
        verdict: str,
        evidence_refs,
        actor: str = "AY",
    ) -> ActivationSnapshot:
        self.ay.validate(
            snapshot,
            verdict=verdict,
            evidence_refs=evidence_refs,
            actor=actor,
        )
        self.ledger.checkpoint(snapshot)
        return snapshot

    def ex_authorize(
        self,
        snapshot: ActivationSnapshot,
        *,
        authorized: bool,
        authority_ref: str,
        actor: str = "EX",
    ) -> ActivationSnapshot:
        self.ex.authorize(
            snapshot,
            authorized=authorized,
            authority_ref=authority_ref,
            actor=actor,
        )
        self.ledger.checkpoint(snapshot)
        return snapshot

    def begin_canary(
        self,
        snapshot: ActivationSnapshot,
    ) -> ActivationSnapshot:
        self.canary.begin(snapshot)
        self.ledger.checkpoint(snapshot)
        return snapshot

    def observe_canary(
        self,
        snapshot: ActivationSnapshot,
        evidence: CanaryEvidence,
        *,
        min_success_rate: float = 0.95,
        min_samples: int = 3,
    ) -> ActivationSnapshot:
        self.canary.observe(
            snapshot,
            evidence,
            min_success_rate=min_success_rate,
            min_samples=min_samples,
        )
        self.ledger.checkpoint(snapshot)
        return snapshot

    def activate(
        self,
        snapshot: ActivationSnapshot,
    ) -> ActivationSnapshot:
        self.activation.activate(snapshot)
        self.ledger.checkpoint(snapshot)
        return snapshot

    def activate_manager(
        self,
        snapshot: ActivationSnapshot,
        manager,
        *,
        evidence,
    ):
        policy = self.runtime_bridge.activate(
            snapshot,
            manager,
            evidence=evidence,
        )

        self.activation.activate(snapshot)
        snapshot.metadata["adaptive_runtime_policy_id"] = getattr(
            policy,
            "policy_id",
            snapshot.contract.policy_ref,
        )
        self.ledger.checkpoint(snapshot)

        return policy

    def rollback_manager(
        self,
        snapshot: ActivationSnapshot,
        manager,
        *,
        kind,
        ex_authorized: bool,
        ay_acknowledged: bool,
        reason: str,
        evidence_ref: str,
        ex_authority_ref: str,
        ay_ack_ref: str,
    ):
        if not ex_authority_ref:
            raise ValueError("ex_authority_ref is required")

        if not ay_ack_ref:
            raise ValueError("ay_ack_ref is required")

        restored = self.runtime_bridge.rollback(
            snapshot,
            manager,
            kind=kind,
            ex_authorized=ex_authorized,
            ay_acknowledged=ay_acknowledged,
            reason=reason,
        )

        self.rollback_engine.rollback(
            snapshot,
            reason=reason,
            evidence_ref=evidence_ref,
        )

        snapshot.metadata["rollback_ex_authority_ref"] = ex_authority_ref
        snapshot.metadata["rollback_ay_ack_ref"] = ay_ack_ref
        snapshot.metadata["adaptive_runtime_restored_policy_id"] = getattr(
            restored,
            "policy_id",
            None,
        )

        self.ledger.checkpoint(snapshot)
        return restored

    def rollback(
        self,
        snapshot: ActivationSnapshot,
        *,
        reason: str,
        evidence_ref: str,
    ) -> ActivationSnapshot:
        self.rollback_engine.rollback(
            snapshot,
            reason=reason,
            evidence_ref=evidence_ref,
        )
        self.ledger.checkpoint(snapshot)
        return snapshot
