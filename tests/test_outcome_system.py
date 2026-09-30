import tempfile
import unittest

from maestro import ProductionGenesisSystem
from maestro.outcome_intelligence import OutcomeIntelligence


class OutcomeSystemTests(unittest.TestCase):
    def test_system_has_outcome_intelligence(self):
        with tempfile.TemporaryDirectory() as td:
            system = ProductionGenesisSystem(td)
            self.assertEqual(system.VERSION, "1.1.0")
            self.assertIsInstance(system.outcome_intelligence, OutcomeIntelligence)

if __name__ == "__main__":
    unittest.main()
