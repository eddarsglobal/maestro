import unittest
from maestro.sovereign import SovereigntyGuard, SovereigntyViolation

class SovereigntyGuardTests(unittest.TestCase):
    def test_model_cannot_own_tx_commit(self):
        with self.assertRaises(SovereigntyViolation):
            SovereigntyGuard().assert_model_contract({"tx_commit"})
    def test_bounded_inference_is_allowed(self):
        SovereigntyGuard().assert_model_contract({"inference_output"})

if __name__ == "__main__":
    unittest.main()
