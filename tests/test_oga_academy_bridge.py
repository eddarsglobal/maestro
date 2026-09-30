import unittest

from maestro.academy.models import PolicyVariant
from maestro.outcome_governed_adaptation import OutcomeGovernedAdaptation
from maestro.outcome_intelligence import AttributionEffect, AttributionFinding, AttributionTarget, VerifiedOutcome


def outcome(i):
    return VerifiedOutcome(
        task_id=f"T{i}", task_family="DIRECT", system_verdict="JUSTE", ay_verified=True,
        resource_id="r1",
        attributions=(AttributionFinding(AttributionTarget.RESOURCE, AttributionEffect.CREDIT, 0.8, "verified"),),
    )


class AcademyBridgeTests(unittest.TestCase):
    def test_candidate_becomes_shadow_variant_not_active_policy(self):
        engine = OutcomeGovernedAdaptation()
        candidate = engine.propose_from_outcomes([outcome(1), outcome(2), outcome(3)])[0]
        variant = engine.policy_bridge.to_academy_variant(candidate)
        self.assertIsInstance(variant, PolicyVariant)
        self.assertEqual(variant.policy_id, candidate.candidate_id)
        self.assertFalse(variant.parameters["authority_change"])

if __name__ == "__main__":
    unittest.main()
