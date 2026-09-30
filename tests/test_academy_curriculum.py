import unittest

from maestro.academy.curriculum import CurriculumEngine
from maestro.academy.models import Weakness


class CurriculumTests(unittest.TestCase):
    def test_critical_weakness_gets_more_repetitions(self):
        weaknesses = [
            Weakness("task_family", "ASYNC", 0.3, 10, "CRITICAL"),
            Weakness("task_family", "CSS", 0.7, 10, "HIGH"),
        ]
        curriculum = CurriculumEngine().build(weaknesses)
        self.assertEqual(curriculum[0].task_family, "ASYNC")
        self.assertGreater(curriculum[0].repetitions, curriculum[1].repetitions)


if __name__ == "__main__":
    unittest.main()
