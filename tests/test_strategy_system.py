import tempfile
import unittest
from maestro.genesis.system import ProductionGenesisSystem

class StrategySystemTests(unittest.TestCase):
    def test_system_has_strategic_adaptation(self):
        with tempfile.TemporaryDirectory() as td:
            s=ProductionGenesisSystem(td)
            self.assertIsNotNone(s.strategic_adaptation)

if __name__=="__main__":
    unittest.main()
