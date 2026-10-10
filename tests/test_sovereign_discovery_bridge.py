import unittest

from maestro.providers.ollama.models import OllamaModelInfo
from maestro.providers.ollama.provider import OllamaProviderAdapter
from maestro.providers.ollama.sovereign_discovery_bridge import OllamaSovereignDiscoveryBridge
from maestro.sovereign.registry import IntelligenceResourceRegistry


class FakeDiscovery:
    def list_models(self):
        return [
            OllamaModelInfo(
                "tiny:latest", 123, "abc",
                capabilities=("completion", "tools", "thinking")
            )
        ]


class FakeClient:
    def generate(self, **kwargs):
        return {
            "model": kwargs["model"],
            "response": "OK",
            "done": True,
            "done_reason": "stop",
            "total_duration": 1,
            "load_duration": 1,
            "prompt_eval_count": 1,
            "eval_count": 1,
            "eval_duration": 1,
        }


class SovereignDiscoveryBridgeTests(unittest.TestCase):
    def test_import_ollama_resource(self):
        reg = IntelligenceResourceRegistry()
        provider = OllamaProviderAdapter(FakeClient())
        ids = OllamaSovereignDiscoveryBridge().import_ollama(reg, FakeDiscovery(), provider)
        self.assertEqual(ids, ["ollama::tiny:latest"])
        self.assertEqual(len(reg.all()), 1)


if __name__ == "__main__":
    unittest.main()
