import unittest

from maestro.outcome_governed_adaptation import OutcomeGovernedAdaptation
from maestro.outcome_intelligence import AttributionEffect, AttributionFinding, AttributionTarget, VerifiedOutcome


def row(i, effect):
    return VerifiedOutcome(
        task_id=f"T{i}", task_family="DIRECT", system_verdict="JUSTE" if effect is AttributionEffect.CREDIT else "FAUTE", ay_verified=True,
        resource_id="r1",
        attributions=(AttributionFinding(AttributionTarget.RESOURCE, effect, 0.9, "evidence"),),
    )


class CounterEvidenceTests(unittest.TestCase):
    def test_material_counter_evidence_blocks_pattern(self):
        outcomes = [row(1, AttributionEffect.CREDIT), row(2, AttributionEffect.CREDIT), row(3, AttributionEffect.CREDIT), row(4, AttributionEffect.BLAME), row(5, AttributionEffect.BLAME)]
        engine = OutcomeGovernedAdaptation()
        self.assertEqual(engine.propose_from_outcomes(outcomes), [])

if __name__ == "__main__":
    unittest.main()
