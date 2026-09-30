import unittest
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


CANDIDATE_ID = "OGA-RUNTIME-CANDIDATE"


def candidate():
    return SimpleNamespace(
        candidate_id=CANDIDATE_ID,
        task_family="DIRECT",
        status="PROMOTION_READY",
        proposed_change={"authority_change": False},
    )


def promotion_evidence(candidate_id=CANDIDATE_ID):
    return PromotionEvidence(
        replay_score=0.95,
        baseline_score=0.80,
        regression_count=0,
        shadow_success_rate=1.0,
        evaluation_samples=12,
        academy_recommended=True,
        learning_candidate_id=candidate_id,
    )


def staged_runtime():
    manager = AdaptivePolicyManager()
    controller = AdaptiveController(manager)

    policy = AdaptivePolicy(
        kind=PolicyKind.MODEL_SELECTION,
        version=1,
        description="runtime bridge test",
        parameters={
            "action": "PREFER_CONDITIONALLY",
            "subject_id": "r1",
            "source_candidate_id": CANDIDATE_ID,
        },
    )

    controller.stage_candidate(policy)
    return manager, policy


def gpa_snapshot(engine, policy_id):
    snapshot = engine.propose(
        candidate(),
        policy_kind=PolicyKind.MODEL_SELECTION.value,
        policy_ref=policy_id,
        baseline_ref="BASELINE-MODEL-SELECTION",
        rollback_ref="BASELINE-MODEL-SELECTION",
    )
    engine.ay_validate(
        snapshot,
        verdict="JUSTE",
        evidence_refs=["EVD-AY-RUNTIME"],
    )
    engine.ex_authorize(
        snapshot,
        authorized=True,
        authority_ref="EX-AUTH-RUNTIME",
    )
    return snapshot


class GPAAdaptiveRuntimeBridgeTests(unittest.TestCase):

    def test_manager_activation_blocked_before_canary_verified(self):
        manager, policy = staged_runtime()
        engine = GovernedPolicyActivation()
        snapshot = gpa_snapshot(engine, policy.policy_id)

        with self.assertRaises(PermissionError):
            engine.activate_manager(
                snapshot,
                manager,
                evidence=promotion_evidence(),
            )

        self.assertIsNone(manager.active(PolicyKind.MODEL_SELECTION))
        self.assertEqual(snapshot.state, ActivationState.EX_AUTHORIZED)

    def test_policy_remains_non_active_during_canary(self):
        manager, policy = staged_runtime()
        engine = GovernedPolicyActivation()
        snapshot = gpa_snapshot(engine, policy.policy_id)

        engine.begin_canary(snapshot)

        self.assertEqual(snapshot.state, ActivationState.CANARY)
        self.assertIsNone(manager.active(PolicyKind.MODEL_SELECTION))

    def test_verified_canary_activates_real_adaptive_manager(self):
        manager, policy = staged_runtime()
        engine = GovernedPolicyActivation()
        snapshot = gpa_snapshot(engine, policy.policy_id)

        engine.begin_canary(snapshot)
        engine.observe_canary(
            snapshot,
            CanaryEvidence(
                success_rate=1.0,
                regression_count=0,
                observed_samples=5,
                evidence_refs=("EVD-CANARY-RUNTIME",),
                latency_budget_pass=True,
            ),
        )

        self.assertEqual(snapshot.state, ActivationState.CANARY_VERIFIED)
        self.assertIsNone(manager.active(PolicyKind.MODEL_SELECTION))

        activated = engine.activate_manager(
            snapshot,
            manager,
            evidence=promotion_evidence(),
        )

        self.assertEqual(snapshot.state, ActivationState.ACTIVE)
        self.assertEqual(activated.policy_id, policy.policy_id)

        active = manager.active(PolicyKind.MODEL_SELECTION)
        self.assertIsNotNone(active)
        self.assertEqual(active.policy_id, policy.policy_id)

    def test_candidate_evidence_mismatch_blocks_runtime_activation(self):
        manager, policy = staged_runtime()
        engine = GovernedPolicyActivation()
        snapshot = gpa_snapshot(engine, policy.policy_id)

        engine.begin_canary(snapshot)
        engine.observe_canary(
            snapshot,
            CanaryEvidence(
                success_rate=1.0,
                regression_count=0,
                observed_samples=5,
                evidence_refs=("EVD-CANARY-RUNTIME",),
                latency_budget_pass=True,
            ),
        )

        with self.assertRaises(PermissionError):
            engine.activate_manager(
                snapshot,
                manager,
                evidence=promotion_evidence("OTHER-CANDIDATE"),
            )

        self.assertEqual(snapshot.state, ActivationState.CANARY_VERIFIED)
        self.assertIsNone(manager.active(PolicyKind.MODEL_SELECTION))


if __name__ == "__main__":
    unittest.main()
