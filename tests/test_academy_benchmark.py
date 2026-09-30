import unittest

from maestro.academy.benchmarks import CouncilBenchmark
from maestro.academy.models import AcademyScenario, ScenarioResult


class BenchmarkTests(unittest.TestCase):
    def test_detects_family_and_council_weakness(self):
        scenarios = [
            AcademyScenario("PAYMENT", "p1", {"IT", "SC"}),
            AcademyScenario("PAYMENT", "p2", {"IT", "SC"}),
        ]
        results = [
            ScenarioResult(
                s.scenario_id, "P", False,
                selected_councils={"IT"},
                gates_observed=set(),
                human_approval_requested=False,
                evidence_score=0.4,
            )
            for s in scenarios
        ]
        report = CouncilBenchmark().evaluate(scenarios, results)
        self.assertTrue(any(w.key == "PAYMENT" for w in report.weaknesses))
        self.assertTrue(any(w.key == "SC" for w in report.weaknesses))


if __name__ == "__main__":
    unittest.main()
