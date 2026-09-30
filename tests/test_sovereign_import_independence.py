import sys
import unittest

class SovereignImportIndependenceTests(unittest.TestCase):
    def test_sovereign_core_imports_without_loading_ollama_bridge(self):
        import maestro.sovereign as sovereign
        self.assertTrue(hasattr(sovereign, "SovereignIntelligenceRuntime"))

if __name__ == "__main__":
    unittest.main()
