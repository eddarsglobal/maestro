import unittest
from types import SimpleNamespace

from maestro.academy.learning_grade import (
    LearningGradeAcademyRunner,
)
from maestro.academy.models import (
    AcademyScenario,
    PolicyVariant,
)
from maestro.outcome_governed_adaptation import (
    DeterministicEvaluationProfile,
)


class FakeAdapter:
    def __init__(
        self,
        output,
        *,
        profile_ref=None,
        deterministic=True,
    ):
        self.output = output
        self.profile_ref = profile_ref
        self.deterministic = deterministic
        self.calls = 0
        self.last_request = None

    def execute(self, request):
        self.calls += 1
        self.last_request = request
        return SimpleNamespace(
            output=self.output,
            success=True,
            metadata={
                "total_ms": 12.5,
                "execution_profile_ref": self.profile_ref,
                "deterministic_execution": self.deterministic,
            },
        )


class FakeRegistry:
    def __init__(self, adapters):
        self.adapters = adapters

    def adapter(self, resource_id):
        return self.adapters[resource_id]


def profile():
    return DeterministicEvaluationProfile(
        provider_id="ollama",
        route="/api/generate",
        temperature=0,
        seed=42,
        num_predict=64,
        think=False,
        suite_version="academy-v1.1.0-learning-grade-test",
    )


def scenario(
    expected="97",
    *,
    validator="integer",
):
    return AcademyScenario(
        task_family="DIRECT",
        objective="Compute 17 * 6 - 5. Return only the integer result.",
        required_councils={"AI"},
        required_gates={
            "SEMANTIC_VALIDATION",
            "FORMAT_VALIDATION",
        },
        metadata={
            "expected": expected,
            "validator": validator,
            "format_mode": "exact",
        },
        scenario_id="SCN-LEARNING-GRADE",
    )


def policy(policy_id, resource_id):
    return PolicyVariant(
        policy_id=policy_id,
        version="test",
        description="test",
        parameters={"resource_id": resource_id},
    )


class LearningGradeAcademyRunnerTests(unittest.TestCase):

    def test_native_profile_is_bound_and_verified(self):
        p = profile()
        adapter = FakeAdapter(
            "97",
            profile_ref=p.profile_id,
        )
        registry = FakeRegistry({"r1": adapter})

        runner = LearningGradeAcademyRunner(
            registry,
            p,
            lambda row: row.parameters["resource_id"],
        )

        result = runner(
            policy("P1", "r1"),
            scenario(),
        )

        self.assertTrue(result.success)
        self.assertIn(
            "LEARNING_GRADE_EVIDENCE",
            result.gates_observed,
        )
        self.assertIsNotNone(
            adapter.last_request.execution_profile
        )
        self.assertEqual(
            adapter.last_request.execution_profile.profile_ref,
            p.profile_id,
        )

    def test_profile_ref_mismatch_blocks_success(self):
        p = profile()
        adapter = FakeAdapter(
            "97",
            profile_ref="EVP-WRONG",
        )

        runner = LearningGradeAcademyRunner(
            FakeRegistry({"r1": adapter}),
            p,
            lambda row: row.parameters["resource_id"],
        )

        result = runner(
            policy("P1", "r1"),
            scenario(),
        )

        self.assertFalse(result.success)
        self.assertIn(
            "SEMANTIC_VALIDATION",
            result.gates_observed,
        )
        self.assertIn(
            "FORMAT_VALIDATION",
            result.gates_observed,
        )
        self.assertNotIn(
            "LEARNING_GRADE_EVIDENCE",
            result.gates_observed,
        )

    def test_semantic_and_format_are_separate(self):
        p = profile()
        adapter = FakeAdapter(
            "17 * 6 = 102; 102 - 5 = 97",
            profile_ref=p.profile_id,
        )

        runner = LearningGradeAcademyRunner(
            FakeRegistry({"r1": adapter}),
            p,
            lambda row: row.parameters["resource_id"],
        )

        result = runner(
            policy("P1", "r1"),
            scenario(),
        )

        evidence = runner.evidence(
            "r1",
            "SCN-LEARNING-GRADE",
        )

        self.assertIsNotNone(evidence)
        self.assertTrue(evidence.semantic_pass)
        self.assertFalse(evidence.format_pass)
        self.assertFalse(result.success)
        self.assertIn(
            "SEMANTIC_VALIDATION",
            result.gates_observed,
        )
        self.assertNotIn(
            "FORMAT_VALIDATION",
            result.gates_observed,
        )

    def test_cache_reuses_identical_resource_scenario_profile(self):
        p = profile()
        adapter = FakeAdapter(
            "97",
            profile_ref=p.profile_id,
        )

        runner = LearningGradeAcademyRunner(
            FakeRegistry({"r1": adapter}),
            p,
            lambda row: row.parameters["resource_id"],
        )

        scn = scenario()

        first = runner(policy("P1", "r1"), scn)
        second = runner(policy("P2", "r1"), scn)

        self.assertTrue(first.success)
        self.assertTrue(second.success)
        self.assertEqual(adapter.calls, 1)
        self.assertEqual(second.policy_id, "P2")
        self.assertTrue(
            any(
                "reused identical" in note
                for note in second.notes
            )
        )

    def test_academy_compare_accepts_native_runner(self):
        from maestro.academy import MaestroAcademy

        p = profile()

        baseline_adapter = FakeAdapter(
            "101",
            profile_ref=p.profile_id,
        )
        candidate_adapter = FakeAdapter(
            "97",
            profile_ref=p.profile_id,
        )

        registry = FakeRegistry(
            {
                "baseline": baseline_adapter,
                "candidate": candidate_adapter,
            }
        )

        runner = LearningGradeAcademyRunner(
            registry,
            p,
            lambda row: row.parameters["resource_id"],
        )

        academy = MaestroAcademy()
        scn = scenario()

        baseline = policy("BASE", "baseline")
        candidate = policy("CAND", "candidate")

        replay = academy.compare_policy(
            baseline,
            candidate,
            [scn],
            runner,
        )

        self.assertGreater(
            replay.candidate_score,
            replay.baseline_score,
        )
        self.assertEqual(replay.improvements, 1)
        self.assertEqual(replay.regressions, 0)


if __name__ == "__main__":
    unittest.main()
