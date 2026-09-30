import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from maestro.adaptive import (
    AdaptiveController,
    AdaptivePolicy,
    AdaptivePolicyManager,
    PolicyKind,
    PromotionEvidence,
)
from maestro.governed_activation import (
    ActivationState,
    CanaryEvidence,
    GovernedPolicyActivation,
)


CANDIDATE_ID = "OGA-RUNTIME-ROLLBACK-CANDIDATE"


def evidence(candidate_id, replay=0.95, baseline=0.80):
    return PromotionEvidence(
        replay_score=replay,
        baseline_score=baseline,
        regression_count=0,
        shadow_success_rate=1.0,
        evaluation_samples=12,
        academy_recommended=True,
        learning_candidate_id=candidate_id,
    )


def promoted_candidate():
    return SimpleNamespace(
        candidate_id=CANDIDATE_ID,
        task_family="DIRECT",
        status="PROMOTION_READY",
        proposed_change={"authority_change": False},
    )


def build_manager_with_baseline_and_candidate():
    manager = AdaptivePolicyManager()
    controller = AdaptiveController(manager)

    baseline = AdaptivePolicy(
        kind=PolicyKind.MODEL_SELECTION,
        version=1,
        description="known-safe baseline",
        parameters={
            "subject_id": "baseline-resource",
            "source_candidate_id": "BASELINE-SEED",
        },
    )
    controller.stage_candidate(baseline)

    manager.activate(
        baseline.policy_id,
        evidence=evidence("BASELINE-SEED", replay=0.90, baseline=0.70),
        ay_validated=True,
        ex_authorized=True,
    )

    candidate = AdaptivePolicy(
        kind=PolicyKind.MODEL_SELECTION,
        version=2,
        description="candidate policy",
        parameters={
            "subject_id": "candidate-resource",
            "source_candidate_id": CANDIDATE_ID,
        },
    )
    controller.stage_candidate(candidate)

    return manager, baseline, candidate


def activate_candidate(engine, manager, candidate):
    current = manager.active(PolicyKind.MODEL_SELECTION)

    snapshot = engine.propose(
        promoted_candidate(),
        policy_kind=PolicyKind.MODEL_SELECTION.value,
        policy_ref=candidate.policy_id,
        baseline_ref=current.policy_id,
        rollback_ref=current.policy_id,
    )

    engine.ay_validate(
        snapshot,
        verdict="JUSTE",
        evidence_refs=["EVD-AY-ACTIVATE"],
    )
    engine.ex_authorize(
        snapshot,
        authorized=True,
        authority_ref="EX-AUTH-ACTIVATE",
    )
    engine.begin_canary(snapshot)
    engine.observe_canary(
        snapshot,
        CanaryEvidence(
            success_rate=1.0,
            regression_count=0,
            observed_samples=5,
            evidence_refs=("EVD-CANARY-HEALTHY",),
            latency_budget_pass=True,
        ),
    )

    engine.activate_manager(
        snapshot,
        manager,
        evidence=evidence(CANDIDATE_ID),
    )

    return snapshot


class GPARuntimeRollbackBridgeTests(unittest.TestCase):

    def test_rollback_requires_fresh_ex_authorization(self):
        manager, baseline, candidate = build_manager_with_baseline_and_candidate()
        engine = GovernedPolicyActivation()
        snapshot = activate_candidate(engine, manager, candidate)

        with self.assertRaises(PermissionError):
            engine.rollback_manager(
                snapshot,
                manager,
                kind=PolicyKind.MODEL_SELECTION,
                ex_authorized=False,
                ay_acknowledged=True,
                reason="RUNTIME_DEGRADED",
                evidence_ref="EVD-DEGRADED",
                ex_authority_ref="EX-ROLLBACK-DENIED",
                ay_ack_ref="AY-ACK-ROLLBACK",
            )

        self.assertEqual(snapshot.state, ActivationState.ACTIVE)
        self.assertEqual(
            manager.active(PolicyKind.MODEL_SELECTION).policy_id,
            candidate.policy_id,
        )

    def test_rollback_requires_fresh_ay_acknowledgement(self):
        manager, baseline, candidate = build_manager_with_baseline_and_candidate()
        engine = GovernedPolicyActivation()
        snapshot = activate_candidate(engine, manager, candidate)

        with self.assertRaises(PermissionError):
            engine.rollback_manager(
                snapshot,
                manager,
                kind=PolicyKind.MODEL_SELECTION,
                ex_authorized=True,
                ay_acknowledged=False,
                reason="RUNTIME_DEGRADED",
                evidence_ref="EVD-DEGRADED",
                ex_authority_ref="EX-AUTH-ROLLBACK",
                ay_ack_ref="AY-ACK-DENIED",
            )

        self.assertEqual(snapshot.state, ActivationState.ACTIVE)
        self.assertEqual(
            manager.active(PolicyKind.MODEL_SELECTION).policy_id,
            candidate.policy_id,
        )

    def test_real_manager_rollback_restores_baseline_and_persists(self):
        with tempfile.TemporaryDirectory() as td:
            ledger_path = Path(td) / "activation.jsonl"

            manager, baseline, candidate = build_manager_with_baseline_and_candidate()
            engine = GovernedPolicyActivation(ledger_path)
            snapshot = activate_candidate(engine, manager, candidate)

            self.assertEqual(snapshot.state, ActivationState.ACTIVE)
            self.assertEqual(
                manager.active(PolicyKind.MODEL_SELECTION).policy_id,
                candidate.policy_id,
            )

            restored = engine.rollback_manager(
                snapshot,
                manager,
                kind=PolicyKind.MODEL_SELECTION,
                ex_authorized=True,
                ay_acknowledged=True,
                reason="RUNTIME_DEGRADED",
                evidence_ref="EVD-RUNTIME-DEGRADED",
                ex_authority_ref="EX-AUTH-ROLLBACK",
                ay_ack_ref="AY-ACK-ROLLBACK",
            )

            self.assertEqual(snapshot.state, ActivationState.ROLLED_BACK)

            active = manager.active(PolicyKind.MODEL_SELECTION)
            self.assertIsNotNone(active)
            self.assertEqual(active.policy_id, baseline.policy_id)

            self.assertIsNotNone(restored)
            self.assertEqual(restored.policy_id, baseline.policy_id)

            restarted = GovernedPolicyActivation(ledger_path)
            persisted = restarted.ledger.latest(snapshot.contract_id)

            self.assertIsNotNone(persisted)
            self.assertEqual(persisted.state, ActivationState.ROLLED_BACK)
            self.assertEqual(
                persisted.metadata["rollback_reason"],
                "RUNTIME_DEGRADED",
            )
            self.assertEqual(
                persisted.metadata["rollback_evidence_ref"],
                "EVD-RUNTIME-DEGRADED",
            )
            self.assertEqual(
                persisted.metadata["adaptive_runtime_restored_policy_id"],
                baseline.policy_id,
            )

            history = restarted.ledger.history(snapshot.contract_id)
            self.assertEqual(
                [row.state for row in history],
                [
                    ActivationState.PROPOSED,
                    ActivationState.AY_VALIDATED,
                    ActivationState.EX_AUTHORIZED,
                    ActivationState.CANARY,
                    ActivationState.CANARY_VERIFIED,
                    ActivationState.ACTIVE,
                    ActivationState.ROLLED_BACK,
                ],
            )


if __name__ == "__main__":
    unittest.main()
