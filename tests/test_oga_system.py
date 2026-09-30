import tempfile
import unittest

from maestro import ProductionGenesisSystem
from maestro.outcome_governed_adaptation import OutcomeGovernedAdaptation


class OGASystemTests(unittest.TestCase):
    def test_system_has_outcome_governed_adaptation(self):
        with tempfile.TemporaryDirectory() as td:
            system = ProductionGenesisSystem(td)
            self.assertEqual(system.VERSION, "1.1.0")
            self.assertIsInstance(system.outcome_governed_adaptation, OutcomeGovernedAdaptation)

if __name__ == "__main__":
    unittest.main()
