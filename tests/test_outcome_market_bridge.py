import unittest

from maestro.enums import CouncilId, VerdictScope, VerdictValue
from maestro.intelligence_market import IntelligenceMarket, IntelligenceMarketLedger
from maestro.models import Mission, Verdict
from maestro.outcome_intelligence import (
    DimensionResult,
    OutcomeDimension,
    OutcomeIntelligence,
)
from maestro.sovereign import IntelligenceResourceRegistry


def make_market():
    return IntelligenceMarket(
        IntelligenceResourceRegistry(),
        ledger=IntelligenceMarketLedger(),
    )


def verified_mission(value, evidence_id="E1"):
    mission = Mission("outcome-market-bridge")
    mission.system_verdict = Verdict(
        task_id=mission.task_id,
        council=CouncilId.AY,
        value=value,
        scope=VerdictScope.SYSTEM,
        evidence_ids=[evidence_id] if evidence_id else [],
    )
    return mission


def market_context():
    return {
        "market_observation": {
            "council_id": "EX",
            "scenario_id": "REAL-001",
            "latency_ms": 125.0,
            "cost_score": 0.25,
            "context_fit": 1.0,
            "tool_fit": 1.0,
            "local": True,
        }
    }


class OutcomeMarketBridgeTests(unittest.TestCase):
    def test_format_only_failure_cannot_modify_market(self):
        oi = OutcomeIntelligence()
        market = make_market()
        mission = verified_mission(VerdictValue.FAUTE)
        outcome = oi.capture_from_mission(
            mission,
            task_family="DIRECT_JSON",
            resource_id="r1",
            dimensions=[
                DimensionResult(OutcomeDimension.SEMANTIC_CORRECTNESS, True, 1.0),
                DimensionResult(OutcomeDimension.FORMAT_COMPLIANCE, False, 0.0),
                DimensionResult(OutcomeDimension.RESOURCE_EXECUTION, True, 1.0),
                DimensionResult(OutcomeDimension.VALIDATOR_INTEGRITY, True, 1.0),
            ],
            metadata=market_context(),
        )
        result = oi.apply_to_market(market, outcome)
        self.assertFalse(result.applied)
        self.assertFalse(result.duplicate)
        self.assertEqual(len(market.ledger.all()), 0)

    def test_verified_resource_failure_can_modify_market(self):
        oi = OutcomeIntelligence()
        market = make_market()
        mission = verified_mission(VerdictValue.FAUTE)
        outcome = oi.capture_from_mission(
            mission,
            task_family="DIRECT",
            resource_id="r1",
            dimensions=[
                DimensionResult(OutcomeDimension.RESOURCE_EXECUTION, False, 0.0),
                DimensionResult(OutcomeDimension.VALIDATOR_INTEGRITY, True, 1.0),
            ],
            metadata=market_context(),
        )
        result = oi.apply_to_market(market, outcome)
        self.assertTrue(result.applied)
        self.assertEqual(len(market.ledger.all()), 1)
        row = market.ledger.all()[0]
        self.assertFalse(row.success)
        self.assertEqual(row.quality, 0.0)
        self.assertEqual(row.metadata["outcome_id"], outcome.outcome_id)
        self.assertEqual(row.evidence_ref, "E1")

    def test_application_is_idempotent(self):
        oi = OutcomeIntelligence()
        market = make_market()
        mission = verified_mission(VerdictValue.FAUTE)
        outcome = oi.capture_from_mission(
            mission,
            task_family="DIRECT",
            resource_id="r1",
            dimensions=[
                DimensionResult(OutcomeDimension.RESOURCE_EXECUTION, False, 0.0),
                DimensionResult(OutcomeDimension.VALIDATOR_INTEGRITY, True, 1.0),
            ],
            metadata=market_context(),
        )
        first = oi.apply_to_market(market, outcome)
        second = oi.apply_to_market(market, outcome)
        self.assertTrue(first.applied)
        self.assertFalse(second.applied)
        self.assertTrue(second.duplicate)
        self.assertEqual(len(market.ledger.all()), 1)

    def test_missing_market_evidence_blocks_update(self):
        oi = OutcomeIntelligence()
        market = make_market()
        mission = verified_mission(VerdictValue.FAUTE)
        outcome = oi.capture_from_mission(
            mission,
            task_family="DIRECT",
            resource_id="r1",
            dimensions=[
                DimensionResult(OutcomeDimension.RESOURCE_EXECUTION, False, 0.0),
                DimensionResult(OutcomeDimension.VALIDATOR_INTEGRITY, True, 1.0),
            ],
        )
        result = oi.apply_to_market(market, outcome)
        self.assertFalse(result.applied)
        self.assertIn("market_observation", result.reason)
        self.assertEqual(len(market.ledger.all()), 0)

    def test_verified_success_can_create_positive_observation(self):
        oi = OutcomeIntelligence()
        market = make_market()
        mission = verified_mission(VerdictValue.JUSTE)
        outcome = oi.capture_from_mission(
            mission,
            task_family="DIRECT",
            resource_id="r1",
            dimensions=[
                DimensionResult(OutcomeDimension.SEMANTIC_CORRECTNESS, True, 1.0),
                DimensionResult(OutcomeDimension.FORMAT_COMPLIANCE, True, 1.0),
                DimensionResult(OutcomeDimension.RESOURCE_EXECUTION, True, 1.0),
                DimensionResult(OutcomeDimension.VALIDATOR_INTEGRITY, True, 1.0),
            ],
            metadata=market_context(),
        )
        result = oi.apply_to_market(market, outcome)
        self.assertTrue(result.applied)
        row = market.ledger.all()[0]
        self.assertTrue(row.success)
        self.assertEqual(row.quality, 1.0)
        self.assertAlmostEqual(row.metadata["attribution_confidence"], 0.60)


if __name__ == "__main__":
    unittest.main()
