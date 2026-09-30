import unittest

from maestro.outcome_governed_adaptation import (
    DeterministicEvaluationProfile,
    OutcomeShadowEvaluator,
)


class DummyRegistry:
    pass


class OutcomeShadowLearningGradeBridgeTests(unittest.TestCase):

    def test_shadow_builds_native_learning_grade_runner(self):
        evaluator = OutcomeShadowEvaluator()

        profile = DeterministicEvaluationProfile(
            provider_id="ollama",
            route="/api/generate",
            temperature=0,
            seed=42,
            num_predict=64,
            think=False,
            suite_version="academy-v1.1.0-shadow-bridge-test",
        )

        runner = evaluator.learning_grade_runner(
            DummyRegistry(),
            profile,
            lambda policy: "r1",
        )

        self.assertEqual(
            runner.profile_id,
            profile.profile_id,
        )
        self.assertTrue(
            runner.execution_profile.deterministic
        )


if __name__ == "__main__":
    unittest.main()
