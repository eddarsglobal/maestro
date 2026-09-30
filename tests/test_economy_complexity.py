import unittest
from maestro.cognitive_economy import ComplexityEstimator, MissionComplexity

class EconomyComplexityTests(unittest.TestCase):
    def test_low_risk_reversible_is_light(self):
        p=ComplexityEstimator().estimate(
            task_id="T",
            risk_score=0.1,
            uncertainty_score=0.1,
            reversibility_score=1.0,
            evidence_demand=0.1,
            time_sensitivity=0.1,
        )
        self.assertIn(p.complexity,{MissionComplexity.TRIVIAL,MissionComplexity.LOW})

    def test_high_risk_irreversible_is_deep(self):
        p=ComplexityEstimator().estimate(
            task_id="T",
            risk_score=1.0,
            uncertainty_score=0.9,
            reversibility_score=0.0,
            evidence_demand=1.0,
            time_sensitivity=0.8,
        )
        self.assertEqual(p.complexity,MissionComplexity.CRITICAL)

if __name__=="__main__":
    unittest.main()
