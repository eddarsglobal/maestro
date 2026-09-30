import unittest

from maestro.autonomous.shadow import LiveShadowEvaluator, ShadowObservation


class ShadowTests(unittest.TestCase):
    def test_summary(self):
        s = LiveShadowEvaluator()
        s.record(ShadowObservation("T1", "P1", "P2", 0.7, 0.9))
        s.record(ShadowObservation("T2", "P1", "P2", 0.8, 0.7))
        out = s.summarize("P2")
        self.assertEqual(out["samples"], 2)
        self.assertEqual(out["wins"], 1)
        self.assertEqual(out["losses"], 1)


if __name__ == "__main__":
    unittest.main()
