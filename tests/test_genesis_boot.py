import unittest
from maestro.genesis.boot import BootValidator

class GenesisBootTests(unittest.TestCase):
    def test_boot(self):
        result = BootValidator().validate()
        self.assertEqual(result["genesis_councils"], 18)
        self.assertEqual(result["kernel"], "OK")

if __name__ == "__main__":
    unittest.main()
