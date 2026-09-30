import unittest

from maestro.academy.models import AcademyScenario
from maestro.academy.simulator import MissionSimulator


class SimulatorTests(unittest.TestCase):
    def test_filter_and_adversarial_variants(self):
        sim = MissionSimulator()
        base = AcademyScenario(
            task_family="PAYMENT",
            objective="Handle payment",
            required_councils={"IT", "SC", "FN"},
            difficulty=1,
        )
        sim.register(base)
        self.assertEqual(len(sim.generate(task_family="PAYMENT")), 1)

        variants = sim.adversarial_variants(base, levels=(2, 4))
        self.assertEqual([v.difficulty for v in variants], [2, 4])
        self.assertTrue(all("adversarial" in v.tags for v in variants))


if __name__ == "__main__":
    unittest.main()
