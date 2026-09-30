import tempfile
import unittest

from maestro import ProductionGenesisSystem
from maestro.governed_activation import GovernedPolicyActivation


class GPASystemTests(unittest.TestCase):
    def test_system_composes_governed_policy_activation(self):
        with tempfile.TemporaryDirectory() as td:
            system = ProductionGenesisSystem(td)

            self.assertEqual(system.VERSION, "1.1.0")
            self.assertIsInstance(
                system.governed_activation,
                GovernedPolicyActivation,
            )


if __name__ == "__main__":
    unittest.main()
