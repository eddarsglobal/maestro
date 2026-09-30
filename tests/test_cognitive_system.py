import tempfile
import unittest
from maestro.genesis.system import ProductionGenesisSystem

class CognitiveSystemTests(unittest.TestCase):
    def test_system_has_cognitive_fabric(self):
        with tempfile.TemporaryDirectory() as td:
            s=ProductionGenesisSystem(td)
            self.assertIsNotNone(s.cognitive_fabric)

if __name__=="__main__":
    unittest.main()
