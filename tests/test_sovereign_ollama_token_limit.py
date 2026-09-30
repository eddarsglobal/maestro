import unittest

from maestro.autonomous.provider_adapters import ProviderResponse
from maestro.providers.ollama.models import OllamaModelInfo
from maestro.providers.ollama.sovereign_adapter import OllamaSovereignResourceAdapter
from maestro.sovereign import IntelligenceRequest, IntelligenceCapability


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


class SovereignOllamaTokenLimitTests(unittest.TestCase):

    def test_max_tokens_reaches_ollama_options(self):
        model = OllamaModelInfo(
            name="tiny",
            size=100,
            digest="test",
            capabilities=("completion",),
        )

        provider = FakeProvider()
        adapter = OllamaSovereignResourceAdapter(model, provider)

        adapter.execute(
            IntelligenceRequest(
                task_id="TASK-TEST",
                capability=IntelligenceCapability.DIRECT,
                instruction="test",
                context_ref="CTX:1",
                max_tokens=17,
            )
        )

        self.assertEqual(
            provider.last_request.context["options"]["num_predict"],
            17,
        )

        self.assertEqual(
            provider.last_request.context["context_ref"],
            "CTX:1",
        )


if __name__ == "__main__":
    unittest.main()
