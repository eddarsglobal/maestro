import unittest
from maestro.autonomous.provider_adapters import ProviderRequest
from maestro.providers.ollama.provider import OllamaProviderAdapter

class FakeClient:
    def generate(self, **kwargs):
        return {
            "model": kwargs["model"], "response":"MAESTRO OK", "done":True,
            "done_reason":"stop", "total_duration":2_000_000_000,
            "load_duration":500_000_000, "prompt_eval_count":10,
            "eval_count":100, "eval_duration":1_000_000_000,
            "thinking":"transient", "context":[1,2,3],
        }

class OllamaProviderTests(unittest.TestCase):
    def test_provider_strips_thinking_and_context_from_metadata(self):
        p = OllamaProviderAdapter(FakeClient())
        out = p.generate(ProviderRequest("DIRECT","tiny","x",{}))
        self.assertEqual(out.output, "MAESTRO OK")
        self.assertNotIn("thinking", out.metadata)
        self.assertNotIn("context", out.metadata)
        self.assertAlmostEqual(out.metadata["tokens_per_second"], 100.0)

if __name__ == "__main__":
    unittest.main()
