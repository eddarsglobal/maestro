import tempfile
import unittest
from maestro.genesis.system import ProductionGenesisSystem

class GenesisSystemTests(unittest.TestCase):
    def test_start_ready(self):
        with tempfile.TemporaryDirectory() as td:
            system = ProductionGenesisSystem(td)
            result = system.start()
            self.assertEqual(result["status"], "READY")
            self.assertEqual(result["version"], "1.1.0")

if __name__ == "__main__":
    unittest.main()
