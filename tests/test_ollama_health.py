import unittest
from maestro.providers.ollama.health import OllamaHealthInspector

class Good:
    def tags(self): return {"models":[{},{}]}
class Bad:
    def tags(self): raise RuntimeError("down")

class OllamaHealthTests(unittest.TestCase):
    def test_good(self):
        h = OllamaHealthInspector(Good()).inspect()
        self.assertTrue(h.reachable); self.assertEqual(h.model_count,2)
    def test_bad(self):
        h = OllamaHealthInspector(Bad()).inspect()
        self.assertFalse(h.reachable)

if __name__ == "__main__":
    unittest.main()
