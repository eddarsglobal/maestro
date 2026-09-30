import unittest

from maestro.intelligence_market import (
    IntelligenceMarketLedger,
    IntelligenceMarketSelector,
    MarketObservation,
    MarketPolicy,
)


def observation(
    scenario_id: str,
    *,
    success: bool = True,
    quality: float = 1.0,
):
    return MarketObservation(
        resource_id="resource-A",
        task_family="DIRECT",
        council_id="EX",
        success=success,
        quality=quality,
        latency_ms=100.0,
        cost_score=0.1,
        context_fit=1.0,
        tool_fit=1.0,
        local=True,
        evidence_ref=scenario_id,
        metadata={
            "scenario_id": scenario_id,
        },
    )


class MarketConfidenceGovernanceTests(unittest.TestCase):

    def selector_with(self, rows):
        ledger = IntelligenceMarketLedger()

        for row in rows:
            ledger.record(row)

        selector = IntelligenceMarketSelector(
            ledger,
            MarketPolicy(
                min_samples_for_confidence=3,
                full_confidence_samples=12,
                full_confidence_scenarios=6,
            ),
        )

        return selector

    def test_three_successes_do_not_mean_full_confidence(self):
        selector = self.selector_with([
            observation("S1"),
            observation("S2"),
            observation("S3"),
        ])

        result = selector.select(
            eligible_resource_ids=["resource-A"],
            task_family="DIRECT",
            council_id="EX",
            allow_exploration=False,
        )

        self.assertAlmostEqual(
            result.confidence,
            0.25,
            places=6,
        )

        self.assertEqual(
            result.rationale["evidence_samples"],
            3,
        )

        self.assertEqual(
            result.rationale["distinct_scenarios"],
            3,
        )

    def test_twelve_samples_six_scenarios_can_reach_full_confidence(self):
        rows = []

        for repeat in range(2):
            for scenario in range(6):
                rows.append(
                    observation(
                        f"S{scenario + 1}",
                    )
                )

        selector = self.selector_with(rows)

        result = selector.select(
            eligible_resource_ids=["resource-A"],
            task_family="DIRECT",
            council_id="EX",
            allow_exploration=False,
        )

        self.assertAlmostEqual(
            result.confidence,
            1.0,
            places=6,
        )

        self.assertEqual(
            result.rationale["evidence_samples"],
            12,
        )

        self.assertEqual(
            result.rationale["distinct_scenarios"],
            6,
        )

    def test_contradictory_evidence_reduces_confidence(self):
        rows = []

        for repeat in range(2):
            for scenario in range(6):
                good = (scenario % 2 == 0)

                rows.append(
                    observation(
                        f"S{scenario + 1}",
                        success=good,
                        quality=1.0 if good else 0.0,
                    )
                )

        selector = self.selector_with(rows)

        result = selector.select(
            eligible_resource_ids=["resource-A"],
            task_family="DIRECT",
            council_id="EX",
            allow_exploration=False,
        )

        self.assertLess(
            result.confidence,
            1.0,
        )

        self.assertEqual(
            result.rationale["evidence_samples"],
            12,
        )

        self.assertEqual(
            result.rationale["distinct_scenarios"],
            6,
        )

        self.assertLess(
            result.rationale["reliability_factor"],
            1.0,
        )


if __name__ == "__main__":
    unittest.main()
