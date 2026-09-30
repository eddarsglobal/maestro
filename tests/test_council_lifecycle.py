import unittest

from maestro.os.council_lifecycle import CouncilLifecycleManager, CouncilTemperature


class CouncilLifecycleTests(unittest.TestCase):
    def test_hot_warm_cold(self):
        m = CouncilLifecycleManager()
        r = m.activate("IT")
        self.assertEqual(r.temperature, CouncilTemperature.HOT)
        r = m.release_worker("IT")
        self.assertEqual(r.temperature, CouncilTemperature.WARM)
        r = m.cool("IT")
        self.assertEqual(r.temperature, CouncilTemperature.COLD)
        self.assertEqual(m.hot_count(), 0)


if __name__ == "__main__":
    unittest.main()
