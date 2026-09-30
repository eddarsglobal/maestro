import unittest

from maestro.councils.registry import COUNCILS, validate_registry
from maestro.enums import CouncilId


class RegistryTests(unittest.TestCase):
    def test_all_18_councils_are_registered(self):
        validate_registry()
        self.assertEqual(len(COUNCILS), 18)
        self.assertEqual(set(COUNCILS), set(CouncilId))


if __name__ == "__main__":
    unittest.main()
