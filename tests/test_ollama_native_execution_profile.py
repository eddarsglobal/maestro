import unittest
from types import SimpleNamespace

from maestro.providers.ollama.sovereign_adapter import (
    OllamaSovereignResourceAdapter,
)
from maestro.sovereign import (
    InferenceExecutionProfile,
    IntelligenceCapability,
    IntelligenceRequest,
)


class FakeProvider:
    def __init__(self):
        self.last_request = None

    def generate(self, request):
        self.last_request = request
        return SimpleNamespace(
            output="OK",
            metadata={"transport": "fake"},
        )


def fake_adapter(model_name="qwen3:8b", capabilities=("thinking",)):
    provider = FakeProvider()
    adapter = SimpleNamespace(
        model=SimpleNamespace(
            name=model_name,
            capabilities=capabilities,
        ),
        provider=provider,
        resource_id=f"ollama::{model_name}",
        provider_id="ollama",
    )
    return adapter, provider


class OllamaNativeExecutionProfileTests(unittest.TestCase):

    def test_profile_reaches_ollama_context_natively(self):
        adapter, provider = fake_adapter()

        profile = InferenceExecutionProfile(
            temperature=0,
            seed=42,
            thinking=False,
            profile_ref="EVP-NATIVE",
        )

        request = IntelligenceRequest(
            task_id="T1",
            capability=IntelligenceCapability.DIRECT,
            instruction="Return OK",
            max_tokens=64,
            execution_profile=profile,
        )

        response = OllamaSovereignResourceAdapter.execute(
            adapter,
            request,
        )

        self.assertEqual(
            provider.last_request.context["options"],
            {
                "num_predict": 64,
                "temperature": 0.0,
                "seed": 42,
            },
        )
        self.assertIs(
            provider.last_request.context["think"],
            False,
        )
        self.assertEqual(
            response.metadata["execution_profile_ref"],
            "EVP-NATIVE",
        )
        self.assertTrue(
            response.metadata["deterministic_execution"]
        )

    def test_gpt_oss_false_thinking_maps_to_minimum(self):
        adapter, provider = fake_adapter(
            model_name="gpt-oss:20b",
            capabilities=("thinking",),
        )

        request = IntelligenceRequest(
            task_id="T2",
            capability=IntelligenceCapability.DIRECT,
            instruction="Return OK",
            execution_profile=InferenceExecutionProfile(
                temperature=0,
                seed=42,
                thinking=False,
            ),
        )

        OllamaSovereignResourceAdapter.execute(adapter, request)

        self.assertEqual(
            provider.last_request.context["think"],
            "low",
        )


if __name__ == "__main__":
    unittest.main()
