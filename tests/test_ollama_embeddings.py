import unittest
from maestro.providers.ollama.embeddings import OllamaEmbeddingAdapter

class FakeClient:
    def embed(self, **kwargs):
        return {"model":kwargs["model"],"embeddings":[[0.1,0.2]],"total_duration":10,"load_duration":5,"prompt_eval_count":2}

class OllamaEmbeddingTests(unittest.TestCase):
    def test_dimensions(self):
        out = OllamaEmbeddingAdapter(FakeClient()).embed("embed","hello")
        self.assertEqual(out.dimensions, 2)

if __name__ == "__main__":
    unittest.main()
