import unittest
from maestro.strategic_adaptation import StrategyCandidateGenerator

class StrategyGeneratorTests(unittest.TestCase):
    def test_generates_alternatives(self):
        rows=StrategyCandidateGenerator().generate(
            task_id="T",
            objective="ship safely",
            family="RELEASE",
            current_method="CURRENT",
            available_capabilities={"MULTI_RESOURCE"},
        )
        self.assertGreaterEqual(len(rows),4)
        self.assertTrue(all(x.objective=="ship safely" for x in rows))

if __name__=="__main__":
    unittest.main()
