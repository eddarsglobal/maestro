import tempfile
import unittest
from maestro.genesis.system import ProductionGenesisSystem

class MetaSystemTests(unittest.TestCase):
    def test_system_has_meta_cognition(self):
        with tempfile.TemporaryDirectory() as td:
            s=ProductionGenesisSystem(td)
            self.assertIsNotNone(s.meta_cognition)

if __name__=="__main__":
    unittest.main()
