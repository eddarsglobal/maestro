import unittest

from maestro.enums import CouncilId, LoopRisk
from maestro.orchestration.retry_ledger import RetryAttempt, RetryLedger


class RetryLedgerTests(unittest.TestCase):
    def test_op_only_writer(self):
        ledger = RetryLedger()
        attempt = RetryAttempt("TASK-X", CouncilId.IT, "AC-01", "same failure", "same strategy")
        with self.assertRaises(PermissionError):
            ledger.record(CouncilId.EX, attempt)

    def test_breakout_on_third_same_failure_and_strategy(self):
        ledger = RetryLedger(breakout_threshold=3)
        last = None
        for _ in range(3):
            last = ledger.record(
                CouncilId.OP,
                RetryAttempt("TASK-X", CouncilId.IT, "AC-01", "Regex mismatch", "Patch same regex"),
            )
        self.assertTrue(last.breakout_recommended)
        self.assertEqual(last.risk, LoopRisk.BREAKOUT_CANDIDATE)

    def test_new_strategy_does_not_inherit_same_pattern_count(self):
        ledger = RetryLedger()
        ledger.record(CouncilId.OP, RetryAttempt("TASK-X", CouncilId.IT, "AC-01", "Failure", "Strategy A"))
        assessment = ledger.record(
            CouncilId.OP,
            RetryAttempt("TASK-X", CouncilId.IT, "AC-01", "Failure", "Strategy B"),
        )
        self.assertEqual(assessment.same_failure_same_strategy_count, 1)
        self.assertFalse(assessment.breakout_recommended)


if __name__ == "__main__":
    unittest.main()
