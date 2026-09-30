import unittest

from maestro.autonomous.provider_adapters import ProviderResponse
from maestro.providers.ollama.client import OllamaClient
from maestro.providers.ollama.models import OllamaModelInfo
from maestro.providers.ollama.sovereign_adapter import (
    OllamaSovereignResourceAdapter,
)
from maestro.sovereign import (
    IntelligenceCapability,
    IntelligenceRequest,
)


class FakeProvider:
    def __init__(self):
        self.last_request = None

    def generate(self, request):
        self.last_request = request
        return ProviderResponse(
            provider="ollama",
            model_id=request.model_id,
            output="OK",
            metadata={},
        )


class SovereignThinkingPolicyTests(unittest.TestCase):

    def test_client_sends_think_at_top_level(self):
        client = OllamaClient()
        captured = {}

        def fake_request(path, payload=None):
            captured["path"] = path
            captured["payload"] = payload
            return {
                "model": "qwen3:0.6b",
                "response": "OK",
                "done": True,
            }

        client._request = fake_request

        client.generate(
            model="qwen3:0.6b",
            prompt="test",
            think=False,
            options={"num_predict": 16},
        )

        self.assertIs(
            captured["payload"]["think"],
            False,
        )

    def test_direct_disables_qwen3_thinking(self):
        model = OllamaModelInfo(
            name="qwen3:0.6b",
            size=522653767,
            digest="test",
            capabilities=("completion", "tools", "thinking"),
        )

        provider = FakeProvider()
        adapter = OllamaSovereignResourceAdapter(model, provider)

        result = adapter.execute(
            IntelligenceRequest(
                task_id="T-DIRECT",
                capability=IntelligenceCapability.DIRECT,
                instruction="test",
                max_tokens=16,
            )
        )

        self.assertIs(
            provider.last_request.context["think"],
            False,
        )

        self.assertIs(
            result.metadata["think_policy"],
            False,
        )

    def test_heavy_reasoning_enables_qwen3_thinking(self):
        model = OllamaModelInfo(
            name="qwen3:8b",
            size=1,
            digest="test",
            capabilities=("completion", "thinking"),
        )

        provider = FakeProvider()
        adapter = OllamaSovereignResourceAdapter(model, provider)

        adapter.execute(
            IntelligenceRequest(
                task_id="T-HEAVY",
                capability=IntelligenceCapability.HEAVY_REASONING,
                instruction="reason",
                max_tokens=256,
            )
        )

        self.assertIs(
            provider.last_request.context["think"],
            True,
        )


if __name__ == "__main__":
    unittest.main()
