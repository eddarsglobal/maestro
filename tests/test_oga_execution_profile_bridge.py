import unittest

from maestro.outcome_governed_adaptation import (
    DeterministicEvaluationProfile,
)


class OGAExecutionProfileBridgeTests(unittest.TestCase):

    def test_evaluation_profile_maps_to_sovereign_contract(self):
        evaluation = DeterministicEvaluationProfile(
            provider_id="ollama",
            route="/api/generate",
            temperature=0,
            seed=42,
            num_predict=64,
            think=False,
            suite_version="academy-v1.1.0-native",
        )

        execution = evaluation.to_execution_profile()

        self.assertTrue(execution.deterministic)
        self.assertEqual(execution.temperature, 0.0)
        self.assertEqual(execution.seed, 42)
        self.assertIs(execution.thinking, False)
        self.assertEqual(
            execution.profile_ref,
            evaluation.profile_id,
        )


if __name__ == "__main__":
    unittest.main()
