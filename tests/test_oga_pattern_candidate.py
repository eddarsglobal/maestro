import unittest

from maestro.outcome_governed_adaptation import AdaptationDomain, AdaptationStatus, OutcomeGovernedAdaptation
from maestro.outcome_intelligence import AttributionEffect, AttributionFinding, AttributionTarget, VerifiedOutcome


def good(i):
    return VerifiedOutcome(
        task_id=f"T{i}", task_family="DIRECT", system_verdict="JUSTE", ay_verified=True,
        resource_id="r1",
        attributions=(AttributionFinding(AttributionTarget.RESOURCE, AttributionEffect.CREDIT, 0.8, "verified"),),
    )


class PatternCandidateTests(unittest.TestCase):
    def test_three_attributable_outcomes_create_model_candidate(self):
        engine = OutcomeGovernedAdaptation()
        rows = engine.propose_from_outcomes([good(1), good(2), good(3)])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].domain, AdaptationDomain.MODEL_SELECTION)
        self.assertEqual(rows[0].status, AdaptationStatus.ELIGIBLE)
        self.assertEqual(rows[0].support_count, 3)
        self.assertFalse(rows[0].proposed_change["authority_change"])

if __name__ == "__main__":
    unittest.main()
