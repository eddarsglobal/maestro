import unittest
from maestro.sovereign import *

class DegradedModeTests(unittest.TestCase):
    def test_zero_models_keeps_deterministic_mode(self):
        state = DegradedModeController().assess(IntelligenceResourceRegistry())
        self.assertEqual(state.level, DegradedCapability.DETERMINISTIC_ONLY)

if __name__ == "__main__":
    unittest.main()
