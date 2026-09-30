import tempfile
import unittest
from maestro.genesis.system import ProductionGenesisSystem

class EconomySystemTests(unittest.TestCase):
    def test_system_has_cognitive_economy(self):
        with tempfile.TemporaryDirectory() as td:
            s=ProductionGenesisSystem(td)
            self.assertIsNotNone(s.cognitive_economy)

if __name__=="__main__":
    unittest.main()
