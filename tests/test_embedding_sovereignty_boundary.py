import unittest

from maestro.providers.ollama.models import OllamaModelInfo
from maestro.providers.ollama.sovereign_adapter import descriptor_from_ollama
from maestro.sovereign import IntelligenceCapability


class EmbeddingSovereigntyBoundaryTests(unittest.TestCase):

    def test_embedding_model_cannot_become_reasoning_resource(self):
        model = OllamaModelInfo(
            name="qwen3-embedding:0.6b",
            size=639_000_000,
            digest="test",
            capabilities=("tools", "thinking", "embedding"),
        )

        descriptor = descriptor_from_ollama(model)

        self.assertIn(
            IntelligenceCapability.EMBEDDING,
            descriptor.capabilities,
        )

        self.assertNotIn(
            IntelligenceCapability.DIRECT,
            descriptor.capabilities,
        )

        self.assertNotIn(
            IntelligenceCapability.GENERAL_REASONING,
            descriptor.capabilities,
        )

        self.assertNotIn(
            IntelligenceCapability.HEAVY_REASONING,
            descriptor.capabilities,
        )

        self.assertNotIn(
            IntelligenceCapability.TOOL_USE,
            descriptor.capabilities,
        )


if __name__ == "__main__":
    unittest.main()
