import unittest

from maestro.adaptive import AdaptiveController, AdaptivePolicyManager, PolicyKind, PolicyStatus
from maestro.outcome_governed_adaptation import OutcomeGovernedAdaptation
from maestro.outcome_intelligence import AttributionEffect, AttributionFinding, AttributionTarget, VerifiedOutcome


def outcome(i):
    return VerifiedOutcome(
        task_id=f"T{i}", task_family="DIRECT", system_verdict="JUSTE", ay_verified=True,
        resource_id="r1",
        attributions=(AttributionFinding(AttributionTarget.RESOURCE, AttributionEffect.CREDIT, 0.8, "verified"),),
    )


class ShadowBoundaryTests(unittest.TestCase):
    def test_candidate_may_enter_shadow_but_not_auto_activate(self):
        engine = OutcomeGovernedAdaptation()
        candidate = engine.propose_from_outcomes([outcome(1), outcome(2), outcome(3)])[0]
        manager = AdaptivePolicyManager()
        controller = AdaptiveController(manager)
        policy = engine.stage_shadow(candidate, controller)
        self.assertEqual(policy.status, PolicyStatus.SHADOW)
        self.assertIsNone(manager.active(PolicyKind.MODEL_SELECTION))

if __name__ == "__main__":
    unittest.main()
