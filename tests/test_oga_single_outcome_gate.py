import unittest

from maestro.outcome_governed_adaptation import OutcomeGovernedAdaptation
from maestro.outcome_intelligence import AttributionEffect, AttributionFinding, AttributionTarget, VerifiedOutcome


class SingleOutcomeGateTests(unittest.TestCase):
    def test_one_outcome_cannot_create_candidate(self):
        outcome = VerifiedOutcome(
            task_id="T1",
            task_family="DIRECT",
            system_verdict="JUSTE",
            ay_verified=True,
            resource_id="r1",
            attributions=(AttributionFinding(AttributionTarget.RESOURCE, AttributionEffect.CREDIT, 0.9, "ok"),),
        )
        engine = OutcomeGovernedAdaptation()
        self.assertEqual(engine.propose_from_outcomes([outcome]), [])

if __name__ == "__main__":
    unittest.main()
