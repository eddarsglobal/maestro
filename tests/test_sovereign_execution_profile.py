import unittest

from maestro.sovereign import (
    InferenceExecutionProfile,
    IntelligenceCapability,
    IntelligenceRequest,
)


class SovereignExecutionProfileTests(unittest.TestCase):

    def test_deterministic_profile_is_provider_neutral(self):
        profile = InferenceExecutionProfile(
            temperature=0,
            seed=42,
            thinking=False,
            profile_ref="EVP-ABC",
        )

        self.assertTrue(profile.deterministic)
        self.assertEqual(
            profile.to_dict(),
            {
                "temperature": 0.0,
                "seed": 42,
                "thinking": False,
                "profile_ref": "EVP-ABC",
                "deterministic": True,
            },
        )

    def test_intelligence_request_carries_execution_profile(self):
        profile = InferenceExecutionProfile(
            temperature=0,
            seed=42,
        )

        request = IntelligenceRequest(
            task_id="T1",
            capability=IntelligenceCapability.DIRECT,
            instruction="hello",
            execution_profile=profile,
        )

        self.assertIs(request.execution_profile, profile)


if __name__ == "__main__":
    unittest.main()
