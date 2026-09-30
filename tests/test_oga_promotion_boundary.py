import unittest

from maestro.adaptive import AdaptiveController, AdaptivePolicyManager, PolicyKind
from maestro.adaptive.policy_manager import PolicyActivationDenied
from maestro.outcome_governed_adaptation import AdaptationStatus, OutcomeGovernedAdaptation
from maestro.outcome_intelligence import AttributionEffect, AttributionFinding, AttributionTarget, VerifiedOutcome


def outcome(i):
    return VerifiedOutcome(
        task_id=f"T{i}", task_family="DIRECT", system_verdict="JUSTE", ay_verified=True,
        resource_id="r1",
        attributions=(AttributionFinding(AttributionTarget.RESOURCE, AttributionEffect.CREDIT, 0.8, "verified"),),
    )


class PromotionBoundaryTests(unittest.TestCase):
    def test_promotion_evidence_does_not_activate_policy(self):
        engine = OutcomeGovernedAdaptation()
        candidate = engine.propose_from_outcomes([outcome(1), outcome(2), outcome(3)])[0]
        manager = AdaptivePolicyManager()
        controller = AdaptiveController(manager)
        policy = engine.stage_shadow(candidate, controller)
        recommendation, evidence = engine.promotion.prepare(
            candidate,
            replay_score=0.95,
            baseline_score=0.85,
            regression_count=0,
            shadow_success_rate=0.95,
            evaluation_samples=12,
            academy_recommended=True,
        )
        self.assertTrue(recommendation.ready_for_governance)
        self.assertEqual(candidate.status, AdaptationStatus.PROMOTION_READY)
        self.assertIsNone(manager.active(PolicyKind.MODEL_SELECTION))
        with self.assertRaises(PolicyActivationDenied):
            manager.activate(policy.policy_id, evidence=evidence, ay_validated=False, ex_authorized=False)

if __name__ == "__main__":
    unittest.main()
