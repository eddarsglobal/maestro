import unittest

from maestro.adaptive.model_policy import (
    ModelObservation,
    ModelPolicyLearner,
    ModelProfile,
)


class ModelPolicyLearnerTests(unittest.TestCase):
    def test_quality_gate_beats_cheapest_model(self):
        learner = ModelPolicyLearner()
        profiles = [
            ModelProfile("small", "A", frozenset({"reasoning"})),
            ModelProfile("strong", "B", frozenset({"reasoning"})),
        ]
        for _ in range(5):
            learner.observe(ModelObservation("small", "AY", "AUDIT", 0.60, True, 10, 0.1))
            learner.observe(ModelObservation("strong", "AY", "AUDIT", 0.95, True, 20, 2.0))

        ranked = learner.rank(
            profiles=profiles,
            council="AY",
            task_family="AUDIT",
            required_capabilities={"reasoning"},
            risk=5,
            min_quality=0.8,
        )
        self.assertEqual(ranked[0].model_id, "strong")


if __name__ == "__main__":
    unittest.main()
