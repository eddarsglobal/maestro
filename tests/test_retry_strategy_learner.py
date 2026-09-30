import unittest

from maestro.adaptive.retry_policy import RetryStrategyLearner, RetryStrategyObservation


class RetryStrategyLearnerTests(unittest.TestCase):
    def test_excluded_failed_strategy_is_not_returned(self):
        learner = RetryStrategyLearner()
        for _ in range(5):
            learner.observe(RetryStrategyObservation("AUTH", "same_patch", False, 3, 3))
            learner.observe(RetryStrategyObservation("AUTH", "redesign_boundary", True, 1, 2))

        ranked = learner.rank(
            failure_family="AUTH",
            excluded_strategies={"same_patch"},
        )
        self.assertEqual(ranked[0].strategy, "redesign_boundary")
        self.assertTrue(all(x.strategy != "same_patch" for x in ranked))


if __name__ == "__main__":
    unittest.main()
