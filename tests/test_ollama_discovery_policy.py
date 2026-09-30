import unittest
from maestro.providers.ollama.models import OllamaModelInfo
from maestro.providers.ollama.policy import LocalModelPolicy, TaskClass

class OllamaPolicyTests(unittest.TestCase):
    def setUp(self):
        self.models = [
            OllamaModelInfo("qwen-small", 500, "a", capabilities=("completion","thinking")),
            OllamaModelInfo("qwen-big", 5000, "b", capabilities=("completion","thinking")),
            OllamaModelInfo("coder-small", 1000, "c", capabilities=("completion","tools")),
            OllamaModelInfo("embed-small", 200, "d", capabilities=("embedding",)),
            OllamaModelInfo("vision", 2000, "e", capabilities=("completion","vision")),
        ]
    def test_direct_uses_smallest_completion(self):
        m = LocalModelPolicy().select(TaskClass.DIRECT, self.models)
        self.assertEqual(m.name, "qwen-small")
    def test_code_uses_coder(self):
        m = LocalModelPolicy().select(TaskClass.CODE, self.models)
        self.assertEqual(m.name, "coder-small")
    def test_embedding_uses_embedding_model(self):
        m = LocalModelPolicy().select(TaskClass.EMBEDDING, self.models)
        self.assertEqual(m.name, "embed-small")
    def test_multimodal_uses_vision(self):
        m = LocalModelPolicy().select(TaskClass.MULTIMODAL, self.models)
        self.assertEqual(m.name, "vision")

if __name__ == "__main__":
    unittest.main()
